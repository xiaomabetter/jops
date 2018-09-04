from app import get_logger, get_config,celery
from flask import jsonify,request
from flask_restful import Resource,reqparse
from app.auth import login_required,adminuser_required,get_login_user
from app.utils import trueReturn,falseReturn
from app.models import Asset,Node,Service,Account,Asset_Account,AssetPermission,\
                AssetPerm_Nodes,Asset_Service,Asset_Create_Template,Asset_Node,Asset_Service
from .serializer import AssetSerializer,NodeSerializer,ServiceSerializer,\
                                    AssetCreateTemplateSerializer,AccountSerializer
from app.perm.serializer import AssetPermissionSerializer
from app.task import run_sync_asset_amount,create_asset,run_sync_asset
from app.utils.encrypt import ChaEncrypt
from conf.config import Config
from conf.aliyun_conf import AliConfig
from app.models.base import OpsRedis
import json

logger = get_logger(__name__)
cfg = get_config()

__all__ = ['AssetsApi','AssetInstanceApi','AssetInstanceUserApi','AssetCreateApi',
           'TemplatesApi','TemplateApi','ImagesApi','SecurityGroupsApi','AssetInstanceAccountApi',
           'AssetInstanceAccountInstanceApi','NodesApi','NodeInstanceApi','NodeInstanceAssetApi',
           'ServicesApi','ServiceInstanceApi','ServiceInstanceAssetInstanceApi'
           ]


class AssetsApi(Resource):
    @login_required
    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('limit', type = int,location = 'args').add_argument('offset', type = int,location = 'args') \
            .add_argument('search', type=str, location='args').add_argument('asset_type', type=str, location='args')\
            .add_argument('order', type=str, location='args').add_argument('node_id', type = str, location = 'args')\
            .add_argument('un_node', type=bool, location='args')\
            .add_argument('hostnames', type = str,action='append',location='args') \
            .add_argument('iplist', type=str, action='append',location='args').parse_args()
        if args.get('hostnames'):
            page_query_set = Asset.select().where(Asset.InstanceName.in_(args.get('hostnames')))
        elif args.get('iplist'):
            page_query_set = Asset.select().where(Asset.InnerAddress.in_(args.get('iplist')))
        else:
            node_id  = args.get('node_id') or Node.root().id
            asset_type = args.get('asset_type')
            node = Node.filter(Node.id == node_id).get()
            if node.is_root():
                query_set = Asset.filter(Asset.AssetType == asset_type)
                if args.get('un_node'):
                    assetids = node.get_family_assetids(asset_type)
                    query_set = query_set.filter(Asset.id.not_in(assetids))
            else:
                query_set = node.get_all_assets(asset_type)
            if args.get('search'):
                search = args.get('search')
                query_set = query_set.filter(Asset.InstanceName.contains(search) |
                         Asset.PublicIpAddress.contains(search) |Asset.InnerAddress.contains(search)|
                        Asset.RegionId.contains(search) | Asset.Status.contains(search))
            if args.get('limit')  or args.get('offset') :
                page = (args.get('offset') + args.get('limit')) / args.get('limit')
                page_query_set = query_set.order_by(Asset.InnerAddress).paginate(page, args['limit'])
            else:
                page_query_set = query_set.order_by(Asset.InnerAddress)
        results = json.loads(AssetSerializer(many=True,exclude=['account','node']).dumps(page_query_set).data)
        return jsonify(trueReturn(results))

    @login_required
    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('hostnames', type = str,action='append',location='json') \
            .add_argument('iplist', type=str, action='append', location='json').parse_args()
        if args.get('hostnames'):
            query = Asset.select().where(Asset.InstanceName.in_(args.get('hostnames')))
        elif args.get('iplist'):
            query = Asset.select().where(Asset.InnerAddress.in_(args.get('iplist')))
        else:
            return jsonify(falseReturn('params error'))
        data = json.loads(AssetSerializer(many=True,only=['id']).dumps(query).data) if query else []
        return jsonify(trueReturn(data))

    @login_required
    def delete(self):
        args = reqparse.RequestParser() \
            .add_argument('id_list', type = str,action='append',location='json').parse_args()
        if args.get('id_list'):
            Asset_Account.delete().where(Asset_Account.asset_id.in_(args.get('id_list'))).execute()
            Asset_Service.delete().where(Asset_Service.asset_id.in_(args.get('id_list'))).execute()
            Asset_Node.delete().where(Asset_Node.asset_id.in_(args.get('id_list'))).execute()
            Asset.delete().where(Asset.id.in_(args.get('id_list'))).execute()
        run_sync_asset_amount.delay()
        return jsonify(trueReturn())

class AssetInstanceApi(Resource):
    @login_required
    def get(self,assetid):
        asset = Asset.select().where(Asset.id == assetid).get()
        data = json.loads(AssetSerializer(only=['InnerAddress','PublicIpAddress','Status']).dumps(asset).data)
        if data['Status'] == 'Destroy' :
            return jsonify(falseReturn(data,msg='实例已经不存在,详细信息可能不存在'))
        if OpsRedis.exists(asset.InstanceId):
            try:
                json_data = json.loads(OpsRedis.get(asset.InstanceId).decode())
                for k,v in json_data.items():
                    if k in getattr(AliConfig,f"Instance_{asset.AssetType}_Detail_Attributes"):
                        data[k] = v
                return jsonify(trueReturn(data))
            except Exception as e:
                return jsonify(falseReturn(data,msg='同步到redis的数据异常'))
        else:
            run_sync_asset.delay(asset.AssetType)
            return jsonify(trueReturn(data,msg='redis详细信息不存在,即将同步'))

class AssetInstanceUserApi(Resource):
    @login_required
    @adminuser_required
    def get(self,assetid):
        asset = Asset.select().where(Asset.id == assetid).get()
        related_users = []
        if not asset:
            return jsonify(falseReturn(msg=u'资产不存在'))
        asset_perms  = asset.asset_permissions.objects()
        from_asset_datas = json.loads(AssetPermissionSerializer(many=True, only=['users']).
                                       dumps(asset_perms).data)
        for users in from_asset_datas:
            for user in users['users']:
                related_users.append(user)
        if asset.node :
            parent_keys = []
            for node in asset.node.objects():
                parent_keys = parent_keys + node.get_all_parents
            parent_keys = list(set(parent_keys))
            pids = [n.id.hex for n in Node.select().where(Node.key.in_(parent_keys))]
            node_perms = AssetPermission.select().join(AssetPerm_Nodes).\
                                where(AssetPerm_Nodes.node_id.in_(pids))
            from_node_datas = json.loads(AssetPermissionSerializer(many=True,only=['users']).
                               dumps(node_perms).data)
            for users in from_node_datas:
                for user in users['users']:
                    if user not in related_users:related_users.append(user)
        return jsonify(trueReturn(related_users))

class AssetCreateApi(Resource):
    @login_required
    @adminuser_required
    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('InstanceTemplate', type=str, location='form',required=True) \
            .add_argument('InstanceChargeType', type = str,location='form') \
            .add_argument('InternetMaxBandwidthOut', type=int, location='form') \
            .add_argument('InstanceName',type=str,location='form',required=True)\
            .add_argument('amount',type=int,location='form',required=True)\
            .add_argument('PublicIpAddress', type=bool, location='form').parse_args()
        template = Asset_Create_Template.select().where(Asset_Create_Template.id ==
                                                                        args.get('InstanceTemplate'))
        templatedata = dict(json.loads(AssetCreateTemplateSerializer(many=True).dumps(template).data)[0])
        templatedata['InstanceChargeType'] = args.get('InstanceChargeType') or 'PrePaid'
        templatedata['IoOptimized'] = 'optimized' if templatedata['instance_type'].split('.')[1] \
                                                     in AliConfig.isIoOptimize else None
        amount = args.get('amount') or 1
        for key in ['InstanceName','Description','HostName'] :
            templatedata[key] = args.get('InstanceName')
        if args.get('PublicIpAddress'):
            templatedata['InternetChargeType'] = args.get('InternetChargeType') or 'PayByTraffic'
            templatedata['InternetMaxBandwidthOut'] = args.get('InternetMaxBandwidthOut') or 10
        else:
            templatedata['InternetChargeType'] = None
            templatedata['InternetMaxBandwidthOut'] = None
        current_user = get_login_user()
        created_by = current_user.username
        r = create_asset.delay(created_by,templatedata,amount)
        return jsonify(trueReturn(r.id,msg=u'开始拼命执行创建机器任务'))

class TemplatesApi(Resource):
    @login_required
    def get(self):
        args = reqparse.RequestParser()\
            .add_argument('RegionId',type=str,location='args') \
            .add_argument('Zoneid', type=str, location='args').parse_args()
        query = Asset_Create_Template.select()
        if args.get('RegionId'):
            query = query.filter(Asset_Create_Template.RegionId == args.get('RegionId'))
        if args.get('Zoneid'):
            query = query.filter(Asset_Create_Template.ZoneId == args.get('Zoneid'))
        data = json.loads(AssetCreateTemplateSerializer(many=True).dumps(query).data)
        return jsonify(trueReturn(data))

    @login_required
    @adminuser_required
    def post(self):
        parse = reqparse.RequestParser()
        for arg in ('name','RegionId','ZoneId','InstanceNetworkType','instance_type',
                    'SystemDiskCategory','DataDisk.1.Category','ImageId'):
            parse.add_argument(arg,type=str,location=['form','json'])
        for arg in ('SystemDiskSize','DataDisk.1.Size'):
            parse.add_argument(arg, type=str, location=['form', 'json'])
        args = parse.add_argument('SecurityGroupId',type=str,action='append',location=['form','json'])\
            .parse_args()
        data,errors = AssetCreateTemplateSerializer().load(args)
        if errors:return jsonify(falseReturn(msg=str(errors)))
        try:
            if not OpsRedis.exists('aly_InstanceTypes') :
                return jsonify(falseReturn(msg='先执行同步aly_InstanceTypes任务'))
            instancetypes = json.loads(OpsRedis.get('aly_InstanceTypes').decode())
            if args.get('instance_type') in instancetypes:
                data['cpu'] = instancetypes[args.get('instance_type')]['CpuCoreCount']
                data['memory'] = instancetypes[args.get('instance_type')]['MemorySize']
            else:
                raise Exception
            template = Asset_Create_Template.create(**data)
        except Exception as e:
            return jsonify(falseReturn(msg=str(e)))
        if args.get('DataDisk.1.Size') and args.get('DataDisk.1.Category'):
            template.DataDiskinfo = json.dumps([{
                'DataDisk.1.Category':args.get('DataDisk.1.Category'),
                'DataDisk.1.Size': args.get('DataDisk.1.Size')}])
        template.SecurityGroupId = ','.join(args.get('SecurityGroupId'))
        template.save()
        return jsonify(trueReturn(msg='创建成功'))

class TemplateApi(Resource):
    @login_required
    def get(self,templateid):
        query = Asset_Create_Template.select().where(Asset_Create_Template.id == templateid)
        data = json.loads(AssetCreateTemplateSerializer().dumps(query).data)
        return jsonify(trueReturn(data))

    @login_required
    def put(self,templateid):
        parse = reqparse.RequestParser()
        for arg in ('name','RegionId','ZoneId','InstanceNetworkType','instance_type',
                    'SystemDiskCategory','DataDisk.1.Category','ImageId'):
            parse.add_argument(arg,type=str,location=['form','json'])
        for arg in ('SystemDiskSize','DataDisk.1.Size'):
            parse.add_argument(arg, type=int, location=['form', 'json'])
        args = parse.add_argument('SecurityGroupId', type=str, action='append', location=['form', 'json'])\
            .parse_args()
        data,errors = AssetCreateTemplateSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=str(errors)))
        if not OpsRedis.exists('aly_InstanceTypes'):
            return jsonify(falseReturn(msg='先执行同步aly_InstanceTypes任务'))
        instancetypes = json.loads(OpsRedis.get('aly_InstanceTypes').decode())
        if args.get('instance_type') in instancetypes:
            data['cpu'] = instancetypes[args.get('instance_type')]['CpuCoreCount']
            data['memory'] = instancetypes[args.get('instance_type')]['MemorySize']
        Asset_Create_Template.update(**data).where(Asset_Create_Template.id == templateid).execute()
        template = Asset_Create_Template.select().where(Asset_Create_Template.id == templateid).get()
        if args.get('DataDisk.1.Size') and args.get('DataDisk.1.Category'):
            template.DataDiskinfo = json.dumps([{
                'DataDisk.1.Category':args.get('DataDisk.1.Category'),
                'DataDisk.1.Size': args.get('DataDisk.1.Size')}])
            template.save()
        template.SecurityGroupId = ','.join(args.get('SecurityGroupId'))
        template.save()
        return jsonify(trueReturn(msg='更新成功'))

    @login_required
    def delete(self,templateid):
        try:
            Asset_Create_Template.delete().where(Asset_Create_Template.id == templateid).execute()
            return jsonify(trueReturn(msg='删除成功'))
        except Exception as e:
            return jsonify(falseReturn(msg=f'删除失败{e}'))

class ImagesApi(Resource):
    @login_required
    def get(self):
        args = reqparse.RequestParser()\
            .add_argument('image_category',type=str,location='args')\
            .add_argument('RegionId',type=str,location='args').parse_args()
        if not OpsRedis.exists('aly_images'):
            return jsonify(falseReturn(msg='先执行同步aly_images任务'))
        result = json.loads(OpsRedis.get('aly_images').decode())
        if args.get('image_category') and args.get('RegionId'):
            data = [dict(ImageName=r['ImageName'],ImageId=r['ImageId'],Description=r['Description'],OSName=r['OSName'])
                    for r in result if r['RegionId'] == args.get('RegionId')
                    and r['ImageOwnerAlias'] == args.get('image_category') ]
        elif args.get('image_category') :
            data = [dict(ImageName=r['ImageName'],ImageId=r['ImageId'],Description=r['Description'],OSName=r['OSName'])
                    for r in result if r['ImageOwnerAlias'] == args.get('image_category') ]
        elif args.get('RegionId') :
            data = [dict(ImageName=r['ImageName'],ImageId=r['ImageId'],Description=r['Description'],OSName=r['OSName'])
                    for r in result if r['RegionId'] == args.get('RegionId')  ]
        else:
            data = [dict(ImageName=r['ImageName'],ImageId=r['ImageId'],Description=r['Description'],OSName=r['OSName'])
                    for r in result ]
        return jsonify(trueReturn(data))

class SecurityGroupsApi(Resource):
    @login_required
    def get(self):
        args = reqparse.RequestParser()\
            .add_argument('RegionId',type=str,location='args').parse_args()
        if not OpsRedis.exists('aly_security_groups'):
            return jsonify(falseReturn(msg='先执行同步aly_security_groups任务'))
        result = json.loads(OpsRedis.get('aly_security_groups').decode())
        if args.get('RegionId') :
            data = [dict(SecurityGroupId=r['SecurityGroupId'],SecurityGroupName=r['SecurityGroupName'],RegionId=r['RegionId'],
                CreationTime=r['CreationTime']) for r in result if r['RegionId'] == args.get('RegionId')]
        else:
            data = [dict(SecurityGroupId=r['SecurityGroupId'],SecurityGroupName=r['SecurityGroupName'],
                RegionId=r['RegionId'],CreationTime=r['CreationTime']) for r in result ]
        return jsonify(trueReturn(data))

class AssetInstanceAccountApi(Resource):
    @login_required
    @adminuser_required
    def get(self,assetid):
        args = reqparse.RequestParser()\
            .add_argument('username', type=str,location='args').parse_args()
        if args.get('username'):
            query = Asset.select().join(Asset_Account).join(Account).\
                where(Account.username==args.get('username'))
            data = json.loads(AssetSerializer(only=['account']).dumps(query).data)
        else:
            asset = Asset.select().where(Asset.id == assetid)
            data = json.loads(AssetSerializer(many=True,only=['account']).dumps(asset).data)
        return jsonify(trueReturn(data))

    @login_required
    def post(self,assetid):
        args = reqparse.RequestParser() \
            .add_argument('username', type = str,location='json', required=True) \
            .add_argument('password', type=str, location='json', required=True) \
            .add_argument('databases', type=str, location='json')\
            .add_argument('buckets', type=str, location='json')\
            .add_argument('description', type=str, location='json').parse_args()
        data,errors = AccountSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=errors))
        try:
            account = Account.create(**data)
            pt = ChaEncrypt(bytes(account.id.hex, encoding = "utf8"))
            encrypt = pt.encrypt(bytes(args.get('password'), encoding = "utf8"))
            account.password = encrypt.decode()
            account.save()
            asset = Asset.select().where(Asset.id == assetid).get()
            asset.account.add(account.id)
            return jsonify(trueReturn(data={'id':account.id.hex},msg='create success'))
        except Exception as e:
            return jsonify(falseReturn(msg=str(e)))

class AssetInstanceAccountInstanceApi(Resource):
    @login_required
    def put(self,assetid,accountid):
        args = dict()
        parse= reqparse.RequestParser()
        for arg in ('password','username','databases','buckets','description'):
            args = parse.add_argument(arg,type=str, location='json').parse_args()
        data,errors = AccountSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=errors))
        if args.get('password'):
            pt = ChaEncrypt(Config.EncryptSecret)
            encrypt = pt.encrypt(args.get('password'))
            data = dict(data,password=encrypt)
        try:
            Account.update(**data).where(Account.id == accountid).execute()
            return trueReturn(msg='update success')
        except Exception as e:
            return falseReturn(msg=str(e))

    @login_required
    def delete(self,assetid,accountid):
        try:
            asset = Asset.select().where(Asset.id == assetid).get()
            asset.account.remove(accountid)
            return trueReturn(data=accountid, msg='success')
        except Exception as e:
            return trueReturn(msg=str(e))

class NodesApi(Resource):
    @login_required
    def get(self):
        args = reqparse.RequestParser()\
            .add_argument('asset_type',type=str,choices=Asset.asset_type(),location='args',required=True)\
            .add_argument('simple', type=bool,location='args').parse_args()
        asset_type = args.get('asset_type')
        Node.asset_type  = asset_type
        data = json.loads(NodeSerializer(many=True,exclude=['full_value']).dumps(Node.select()).data)
        if args.get('simple'):
            for index, item in enumerate(data):
                data[index]['assets_amount'] = 0
            return jsonify(trueReturn(data))
        node_redis_keys = ['{}_{}'.format(asset_type,node['value'])  for node in data]
        assets_amounts = OpsRedis.mget(node_redis_keys)
        for index,item in enumerate(data):
            key = '{}_{}'.format(asset_type, item['value'])
            if key in node_redis_keys:
                amounts = assets_amounts[node_redis_keys.index(key)]
                if amounts:
                    data[index]['assets_amount'] = amounts.decode()
                else:
                    node = Node.select().where(Node.id == item['id']).get()
                    amounts = node.get_all_assets(asset_type).count()
                    OpsRedis.set(key,amounts)
                    data[index]['assets_amount'] = amounts
        return jsonify(trueReturn(data))

class NodeInstanceApi(Resource):
    @login_required
    def get(self,nodeid):
        args = reqparse.RequestParser() \
            .add_argument('asset_type', type=str,choices=Asset.asset_type(),required=True, location='args')\
            .parse_args()
        node = Node.select().where(Node.id == nodeid)
        if not node:
            return jsonify(falseReturn(msg='nodeid不存在!'))
        assets = node.get().get_all_assets(args.get('asset_type'))
        data = json.loads(AssetSerializer(many=True,
            only=['id','InstanceName','InstanceId','Address','is_active']).dumps(assets).data)
        return jsonify(trueReturn(data))

    @login_required
    def post(self,nodeid):
        args = reqparse.RequestParser() \
            .add_argument('value', location='json').parse_args()
        instance = Node.filter(Node.id == nodeid).first()
        nodename = args.get('value')  or "新节点"
        value = "{} {}".format(nodename,Node.root().get_next_child_key().split(":")[-1])
        node = instance.create_child(value=value)
        data = json.loads(NodeSerializer().dumps(node).data)
        return jsonify(trueReturn(data))

    @login_required
    def patch(self,nodeid):
        args = reqparse.RequestParser() \
            .add_argument('value',type=str,location='json',required=True).parse_args()
        try:
            query = Node.update(value=args.get('value')).where(Node.id ==nodeid).execute()
            run_sync_asset_amount.delay(query.id.hex)
            return jsonify(trueReturn(msg=u'重命名为{0}成功'.format(args.get('value'))))
        except Exception as e:
            return jsonify(falseReturn(msg=u'重命名为{0}失败'.format(args.get('value'))))

    @login_required
    def delete(self, nodeid):
        try:
            Node.delete().where(Node.id == nodeid).query.execute()
            return jsonify(trueReturn(msg='删除成功'))
        except Exception as e:
            return jsonify(falseReturn(msg=f'删除失败{e}'))

    @login_required
    def put(self,nodeid):
        args = reqparse.RequestParser() \
            .add_argument('targetid', type=str,required=True,location='json').parse_args()
        instance = Node.filter(Node.id == args.get('targetid')).first()
        children = [Node.get_or_none(Node.id==pk) for pk in nodeid.split(',')]
        for node in children:
            if node:node.parent = instance  ; node.save()
        run_sync_asset_amount.delay(instance.id.hex)
        return jsonify(trueReturn())

class NodeInstanceAssetApi(Resource):
    @login_required
    def post(self,nodeid):
        args = reqparse.RequestParser() \
            .add_argument('assetids',action='append',location='json',required=True)\
            .parse_args()
        node = Node.filter(Node.id == nodeid).get()
        try:
            for assetid in args.get('assetids') :
                node.asset.add(assetid)
            r = run_sync_asset_amount.delay(nodeid)
            return jsonify(trueReturn())
        except Exception as e:
            return jsonify(falseReturn(msg=str(e)))

    @login_required
    def delete(self,nodeid):
        args = reqparse.RequestParser()\
            .add_argument('assetids',location='json',action='append',required=True)\
            .parse_args()
        node = Node.filter(Node.id == nodeid).get()
        try:
            for assetid in args.get('assetids') :
                node.asset.remove(assetid)
            run_sync_asset_amount.delay(node.id.hex)
            return jsonify(trueReturn())
        except Exception as e:
            return jsonify(falseReturn(msg=str(e)))

class ServicesApi(Resource):
    @login_required
    def get(self):
        query_set = Service.select()
        serializer = ServiceSerializer(many=True)
        data = json.loads(serializer.dumps(query_set).data)
        return jsonify(trueReturn(data))

    @login_required
    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('servicename', type=str, location=['json','form'], required=True) \
            .add_argument('version', type=str, location=['json','form'], required=True) \
            .add_argument('description', type=str, location=['json','form']).parse_args()
        data,errors = ServiceSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg='提交数据验证失败 %s' % errors))
        try:
            Service.create(**data)
            return  jsonify(trueReturn(msg='创建成功'))
        except Exception as e:
            return  jsonify(falseReturn(msg=str(e)))

    @login_required
    def delete(self):
        args = reqparse.RequestParser()\
            .add_argument('serviceid',type=str,action='append',location='json',required=True).parse_args()
        service = Service.select().where(Service.id == args.get('serviceid')).get()
        if service.asset.count() > 0:
            for asset in service.asset.objects():
                service.asset.remove(str(asset.id))
        try:
            Service.delete().where(Service.id == args.get('serviceid')).execute()
            return jsonify(trueReturn(msg=u'已经删除'))
        except Exception as e:
            return falseReturn(msg=str(e))

class ServiceInstanceApi(Resource):
    @login_required
    def get(self,serviceid):
        service = Service.select().where(Service.id == serviceid).get()
        if service:
            data = json.loads(ServiceSerializer().dumps(service).data)
            return jsonify(trueReturn(data))
        else:
            return jsonify(falseReturn(msg='服务不存在'))

    @login_required
    def put(self,serviceid):
        args = reqparse.RequestParser() \
            .add_argument('servicename', type=str, location=['json','form']) \
            .add_argument('version', type=str, location=['json','form']) \
            .add_argument('description', type=str, location=['json','form']).parse_args()
        data,errors = ServiceSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg='提交数据验证失败 %s' % errors))
        try:
            Service.update(**data).where(Service.id == serviceid).execute()
            return jsonify(trueReturn(msg=u'更新成功'))
        except Exception as e:
            return falseReturn(msg=str(e))

    @login_required
    def delete(self,serviceid):
        try:
            Asset_Service.delete().where(Asset_Service.service_id == serviceid).execute()
            Service.delete().where(Service.id == serviceid).execute()
            return jsonify(trueReturn(msg='删除成功'))
        except Exception as e:
            return jsonify(falseReturn(msg='删除失败%s' % str(e)))

class ServiceInstanceAssetInstanceApi(Resource):
    @login_required
    def post(self,serviceid,assetid):
        try:
            service = Service.select().where(Service.id == serviceid).get()
            service.asset.add(assetid)
            return trueReturn(msg='success')
        except Exception as e:
            return trueReturn(msg=str(e))

    @login_required
    def delete(self,serviceid,assetid):
        try:
            service = Service.select().where(Service.id == serviceid).get()
            service.asset.remove(assetid)
            return trueReturn(msg='success')
        except Exception as e:
            return trueReturn(msg=str(e))