from app import get_logger
from flask import jsonify
from werkzeug.datastructures import FileStorage
from flask_restful import Resource,reqparse
from app.auth import login_required
from app.models import SystemUser,AssetPermission,AssetPerm_Users,AssetPerm_Groups,\
                    AssetPerm_SystemUser,AssetPerm_Nodes,AssetPerm_Assets,PermissionGroups,\
                    PermissionGroups_User
from app.utils import trueReturn,falseReturn
from .serializer import AssetPermissionSerializer,SystemUserSerializer,PermissionGroupSerializer
from app.utils.sshkey import ssh_pubkey_gen,ssh_key_gen,validate_ssh_private_key
from app.auth import get_login_user
import json

logger = get_logger(__name__)

__all__ = ['SystemUsersApi','SystemUserApi','AssetPermissionsApi','AssetPermissionApi',
           'UserGrantAssets','UserGrantNodes','PermissionGroupsApi','PermissionGroupApi']

class PermissionGroupsApi(Resource):
    @login_required
    def get(self):
        args = reqparse.RequestParser().add_argument('search', type=str, location='args').parse_args()
        query_set = PermissionGroups.select()
        if args.get('search'):
            search = args.get('search')
            query_set = PermissionGroups.filter(PermissionGroups.name.contains(search))
        query_set = query_set.order_by(PermissionGroups.name)
        data = json.loads(PermissionGroupSerializer(many=True).dumps(query_set).data)
        return jsonify(trueReturn(data))

    @login_required
    def post(self):
        locations = ['form', 'json']
        args = reqparse.RequestParser().add_argument('name', type=str,required=True,location=locations) \
            .add_argument('users', type=str, action='append',required=True, location=locations)\
            .add_argument('comment', type=str, location=locations).parse_args()
        data, errors = PermissionGroupSerializer(exclude=['users']).load(args)
        pgroup = PermissionGroups.create(**data)
        try:
            if args.get('users'):
                for userid in args.get('users'):
                    print(userid)
                    pgroup.users.add(userid)
            return jsonify(trueReturn(msg='创建成功'))
        except Exception as e:
            return jsonify(falseReturn(msg=e))

class PermissionGroupApi(Resource):
    @login_required
    def put(self,pgid):
        locations = ['form', 'json']
        args = reqparse.RequestParser().add_argument('name', type=str,required=True,location=locations) \
            .add_argument('users', type=str, action='append',required=True, location=locations)\
            .add_argument('comment', type=str, location=locations).parse_args()
        pgroup = PermissionGroups.select().where(PermissionGroups.id == pgid).get()
        try:
            if args.get('name'):
                pgroup.name = args.get('name')
            if args.get('comment'):
                pgroup.name = args.get('comment')
            if args.get('users'):
                current_users = set([user.id.hex for user in pgroup.users.objects()])
                new_users = set(args.get('users'))
                if current_users - new_users:
                    for uid in list(current_users - new_users): pgroup.users.remove(uid)
                elif new_users - current_users:
                    for uid in list(new_users - current_users):pgroup.users.add(uid)
            pgroup.save()
            return jsonify(trueReturn(msg='更新成功'))
        except Exception as e:
            print(e)
            return jsonify(falseReturn(msg='更新失败'))

class SystemUsersApi(Resource):
    @login_required
    def get(self):
        args = reqparse.RequestParser().add_argument('search', type=str, location='args') \
            .add_argument('order', type=str, location='args').parse_args()
        query_set = SystemUser.select()
        if args.get('search'):
            search = args.get('search')
            query_set = SystemUser.filter(SystemUser.username.contains(search))
        query_set = query_set.order_by(SystemUser.username)
        data = json.loads(SystemUserSerializer(many=True).dumps(query_set).data)
        return jsonify(trueReturn(data))

    @login_required
    def post(self):
        locations = ['form','json']
        parse = reqparse.RequestParser()
        for arg in ('name', 'username', 'protocol', 'password' ,'sudo','comment','shell'):
            args = parse.add_argument(arg,type=str,location=locations).parse_args()
        for arg in ('auto_generate_key','auto_push') :
            args = parse.add_argument(arg,type=bool,location=locations).parse_args()
        if not args.get('auto_generate_key') :
            args = parse.add_argument('private_key', type=FileStorage,location='files').parse_args()
        data,errors = SystemUserSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=u'参数验证失败%s' % errors))
        if args.get('auto_generate_key'):
            data['private_key'], data['public_key'] = ssh_key_gen()
        else:
            private_key = args.get('private_key').read().strip().decode()
            if validate_ssh_private_key(private_key):
                data['private_key'] = args.get('private_key').read().strip().decode()
                data['public_key'] = ssh_pubkey_gen(private_key=private_key)
            else:
                return falseReturn(msg='private_key文件不合法')
        SystemUser.create(**data)
        return jsonify(trueReturn(msg='创建成功'))

class SystemUserApi(Resource):
    @login_required
    def get(self,sysuserid):
        sysuser = SystemUser.select().where(SystemUser.id == sysuserid).get()
        data = SystemUserSerializer().dumps(sysuser).data
        return jsonify(trueReturn(data))

    @login_required
    def put(self,sysuserid):
        locations = ['form','json']
        parse = reqparse.RequestParser()
        for arg in ('name', 'username', 'protocol', 'password' ,'sudo','comment','shell'):
            args = parse.add_argument(arg,type=str,location=locations).parse_args()
        for arg in ('auto_generate_key','auto_push') :
            args = parse.add_argument(arg,type=bool,location=locations).parse_args()
        if not args.get('auto_generate_key') :
            args = parse.add_argument('private_key', type=FileStorage,location='files').parse_args()
        data,errors = SystemUserSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=u'参数验证失败%s' % errors))
        if args.get('auto_generate_key'):
            data['private_key'], data['public_key'] = ssh_key_gen()
        else:
            private_key = args.get('private_key').read().strip().decode()
            if validate_ssh_private_key(private_key):
                data['private_key'] = private_key
                data['public_key'] = ssh_pubkey_gen(private_key=private_key)
            else:
                return falseReturn(msg='private_key文件不合法')
        SystemUser.update(**data).where(SystemUser.id == sysuserid).execute()
        return jsonify(trueReturn(msg='更新成功'))

    @login_required
    def delete(self,sysuserid):
        try:
            sysuser = SystemUser.select().where(SystemUser.id == sysuserid).get()
            if sysuser.asset_permissions.exists() :
                return jsonify(falseReturn(msg='有相关的授权规则，不能直接删除'))
            else:
                SystemUser.delete().where(SystemUser.id == sysuserid).execute()
                return jsonify(trueReturn(msg='删除成功'))
        except Exception as e:
            return jsonify(falseReturn(msg='删除失败'))

class AssetPermissionsApi(Resource):
    @login_required
    def get(self):
        query_set = AssetPermission.select()
        data = json.loads(AssetPermissionSerializer(many=True).dumps(query_set).data)
        return jsonify(trueReturn(data))

    @login_required
    def post(self):
        locations = ['form','json']
        parse = reqparse.RequestParser()
        for arg in ('users','groups','system_users','assets','nodes'):
            parse.add_argument(arg,type=str,action='append',location=locations)
        args = parse.add_argument('name', type=str,location=locations,required=True) \
                .add_argument('is_active', type=bool, default=True,location=locations) \
            .add_argument('comment', type=bool, location=locations).parse_args()
        if not args.get('users') and not args.get('groups'):
            return jsonify(falseReturn(msg=u'用户和用户组，必须选择一项'))
        elif not args.get('assets') and not args.get('nodes'):
            return jsonify(falseReturn(msg=u'资产和节点，必须选择一项'))
        data,errors = AssetPermissionSerializer(only=['name','is_active','comment']).load(args)
        if errors:
            return jsonify(falseReturn(msg=u'参数验证失败%s' % errors))
        current_user = get_login_user()
        data['created_by'] = current_user.username
        try:
            asset_permission = AssetPermission.create(**data)
        except Exception as e:
            return jsonify(falseReturn(msg=str(e)))
        for item in ('system_users','users','groups','assets','nodes'):
            if args.get(item):
                for id in args.get(item):
                    getattr(asset_permission, item).add(id)
        return jsonify(trueReturn(msg='授权规则添加成功'))

    @login_required
    def delete(self):
        args = reqparse.RequestParser().add_argument('id', type=str, location='json').parse_args()
        for model in [AssetPerm_SystemUser, AssetPerm_Users, AssetPerm_Nodes, AssetPerm_Groups, AssetPerm_Assets]:
            model.delete().where(model.assetpermission_id == args.get('id')).execute()
        AssetPermission.delete().where(AssetPermission.id==args.get('id')).execute()
        return  jsonify(trueReturn(msg='删除成功'))

class AssetPermissionApi(Resource):
    @login_required
    def get(self,permissionid):
        asset_permission = AssetPermission.select().where(AssetPermission.id == permissionid).get()
        data= json.loads(AssetPermissionSerializer().dumps(asset_permission).data)
        return jsonify(trueReturn(data))

    @login_required
    def put(self,permissionid):
        locations = ['form','json']
        parse = reqparse.RequestParser()
        for arg in ('users','groups','system_users','assets','nodes'):
            parse.add_argument(arg,type=str,action='append',location=locations)
        args = parse.add_argument('name', type=str,location=locations,required=True) \
                .add_argument('is_active', type=bool, location=locations) \
            .add_argument('comment', type=bool, location=locations).parse_args()
        if not args.get('users') and not args.get('groups'):
            return jsonify(falseReturn(msg=u'用户和用户组，必须选择一项'))
        elif not args.get('assets') and not args.get('nodes'):
            return jsonify(falseReturn(msg=u'资产和节点，必须选择一项'))
        data,errors = AssetPermissionSerializer(only=['name','is_active','comment']).load(args)
        if errors:
            return jsonify(falseReturn(msg=u'参数验证失败%s' % errors))
        current_user = get_login_user()
        data['created_by'] = current_user.username
        asset_permission = AssetPermission.select().where(AssetPermission.id == permissionid).get()
        asset_permission.update(**data).where(AssetPermission.id == permissionid).execute()
        for item in ('system_users','users','groups','assets','nodes'):
            if hasattr(asset_permission,item):
                getattr(asset_permission,item).clear()
            if args.get(item):
                for id in args.get(item):
                    getattr(asset_permission, item).add(id)
        return jsonify(trueReturn(msg='授权规则更新成功'))

    @login_required
    def delete(self,permissionid):
        try:
            for model in [AssetPerm_SystemUser, AssetPerm_Users, AssetPerm_Nodes, AssetPerm_Groups, AssetPerm_Assets]:
                model.delete().where(model.assetpermission_id == permissionid).execute()
            AssetPermission.delete().where(AssetPermission.id==permissionid).execute()
            return jsonify(trueReturn(msg='删除成功'))
        except Exception as e:
            return jsonify(falseReturn(msg='删除失败'))

class UserGrantAssets(Resource):
    @login_required
    def get(self,uid):
        results = []
        node_result = []
        assetpermissions = AssetPermission.select().join(AssetPerm_Users).\
                                                        where(AssetPerm_Users.user_id == uid)
        if not assetpermissions:
            return jsonify({'data':[]})
        for assetpermission in assetpermissions:
            sys_result = []
            systemusers = assetpermission.system_users.objects()
            for systemuser in systemusers:
                    sys_result.append({
                            'id':systemuser.id.hex,'name':systemuser.name,'username':systemuser.username,
                            'priority': systemuser.priority
                })
            assets = assetpermission.assets.objects()
            for asset in assets:
                ids = [r['id'] for r in results]
                if str(asset.id) not in ids:
                    results.append(
                        {'id': str(asset.id),'hostname': asset.InstanceName,'ip': asset.InnerAddress,
                         'port': asset.sshport,'system_users_granted':sys_result,'is_active': asset.is_active,
                         'nodes': node_result,'platform': 'Linux'}
                    )
        return jsonify({'data':results})

class UserGrantNodes(Resource):
    @login_required
    def get(self,uid):
        results = []
        assetpermissions = AssetPermission.select().join(AssetPerm_Users).\
                                                        where(AssetPerm_Users.user_id == uid)
        if not assetpermissions:
            return jsonify({'data':[]})
        for assetpermission in assetpermissions:
            sys_result = []
            nodes = assetpermission.nodes.objects()
            if not nodes:
                continue
            systemusers = assetpermission.system_users.objects()
            for systemuser in systemusers:
                    sys_result.append({
                            'id':systemuser.id.hex,'name':systemuser.name,'username':systemuser.username,
                            'priority': systemuser.priority, 'protocol': systemuser.protocol
                })
            for node in nodes:
                assets_granted = []
                for asset in node.get_all_assets('ecs'):
                    assets_granted.append(
                        {'id': str(asset.id),'hostname': asset.InstanceName,'ip': asset.InnerAddress,
                         'port': asset.sshport,'system_users_granted':sys_result,'is_active': asset.is_active,
                         'platform': 'Linux'})
                results.append(
                    {
                        'id': str(node.id), 'key': node.key, 'name': node.name, 'value': node.value,
                        'assets_granted': assets_granted, 'parent': str(node.parent_id),
                        'assets_amount': len(assets_granted)
                    }
                )
        return jsonify({'data':results})