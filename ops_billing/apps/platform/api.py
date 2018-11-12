from flask import jsonify,request
from flask_restful import Resource,reqparse
from apps.auth import login_required,adminuser_required,get_login_user
from apps.models import Platforms,OpsRedis
from apps.platform.serializer import PlatformSerializer
from apps.perm.serializer import AuthorizationPlatformSerializer
from apps.utils import trueReturn,falseReturn
from peewee import fn
import json

__all__ = ['PlatformsApi','PlatformApi','PlatformProxyApi','PlatformUrlMappingPortApi']

class PlatformsApi(Resource):
    @login_required
    def get(self):
        args = reqparse.RequestParser() \
            .add_argument('limit', type = int,location = 'args') \
            .add_argument('search', type=str, location='args').parse_args()
        current_user = get_login_user()
        if current_user.role == 'administrator':
            query_set = Platforms.select().order_by(Platforms.description)
            data = json.loads(PlatformSerializer(many=True).dumps(query_set).data)
        else:
            data = []
            if current_user.platform_permission:
                platform_auth_query_set = current_user.platform_permission.objects()
                permission_datas = json.loads(AuthorizationPlatformSerializer(many=True).
                                         dumps(platform_auth_query_set).data)
                for permission_data in permission_datas:
                    data = data + permission_data['platform_urls']
            if current_user.permission_group:
                for permission_group in current_user.permission_group.objects():
                    if permission_group.platform_permission:
                        platform_auth_query_set =  permission_group.platform_permission.objects()
                        permission_datas = json.loads(AuthorizationPlatformSerializer(many=True).
                                         dumps(platform_auth_query_set).data)
                        for permission_data in permission_datas:
                            data = data + permission_data['platform_urls']
        return jsonify(trueReturn(data))

    @login_required
    @adminuser_required
    def post(self):
        locations = ['form', 'json']
        args = reqparse.RequestParser().add_argument('description', type=str,required=True,location=locations) \
            .add_argument('platform_url', type=str,required=True, location=locations) \
            .add_argument('catagory', type=str, required=True, location=locations) \
            .add_argument('location', type=str, required=True, location=locations).parse_args()
        try:
            maxport = Platforms.select(fn.Max(Platforms.proxyport)).scalar()
            Platforms.create(description=args.get('description'),location=args.get('location'),
                        platform_url=args.get('platform_url'),catagory=args.get('catagory'),proxyport=int(maxport) + 1)
            return trueReturn(msg='创建成功')
        except Exception as e:
            return falseReturn(msg=str(e))

class PlatformApi(Resource):
    @login_required
    def get(self,platformid):
        if OpsRedis.exists(platformid):
            data = json.loads(OpsRedis.get(platformid).decode())
        else:
            query_set = Platforms.select().where(Platforms.id == platformid).get()
            data = json.loads(PlatformSerializer().dumps(query_set).data)
            OpsRedis.set(platformid,json.dumps(data))
        return jsonify(trueReturn(data))

    @login_required
    def put(self,platformid):
        locations = ['form', 'json']
        args = reqparse.RequestParser().add_argument('description', type=str,required=True,location=locations) \
            .add_argument('platform_url', type=str,required=True, location=locations) \
            .add_argument('catagory', type=str, required=True, location=locations) \
            .add_argument('location', type=str, required=True, location=locations).parse_args()
        try:
            Platforms.update(description=args.get('description'),platform_url=args.get('platform_url'),
                            catagory=args.get('catagory'),location=args.get('location'))\
                            .where(Platforms.id == platformid).execute()
            query_set = Platforms.select().where(Platforms.id == platformid).get()
            data = json.dumps(json.loads(PlatformSerializer().dumps(query_set).data))
            OpsRedis.set(platformid,data)
            return jsonify(trueReturn(msg="更新成功"))
        except Exception as e:
            return jsonify(trueReturn(msg="更新失败%s" % str(e)))

    @login_required
    def delete(self,platformid):
        try:
            platform = Platforms.select().where(Platforms.id == platformid).get()
            if platform.platform_permission:
                permission_names = [permission.name for permission in platform.platform_permission.objects()]
                name = ",".join(permission_names)
                return jsonify(falseReturn(msg="请先将授权规则(%s)中去除此平台" % name))
            Platforms.delete().where(Platforms.id == platformid).execute()
            return jsonify(trueReturn(msg="更新成功"))
        except Exception as e:
            return jsonify(trueReturn(msg="更新失败%s" % str(e)))


class PlatformUrlMappingPortApi(Resource):
    @login_required
    def get(self,port):
        data = ''
        platform_port_dict = json.loads(OpsRedis.get('platform_proxy_port').decode())
        for platform_id,proxy_port in platform_port_dict.items():
            if port == proxy_port:
                if OpsRedis.exists(platform_id):
                    data = json.loads(OpsRedis.get(platform_id).decode())
                else:
                    query_set = Platforms.select().where(Platforms.id == platform_id).get()
                    data = json.loads(PlatformSerializer().dumps(query_set).data)
                    OpsRedis.set(platform_id, json.dumps(data))
                break
        return jsonify(trueReturn(data))

class PlatformProxyApi(Resource):
    @login_required
    def get(self):
        args = reqparse.RequestParser().\
            add_argument('platform_id', type=str,required=True, location='args').parse_args()
        print(args)
        platform_port = None
        if OpsRedis.exists('platform_proxy_port'):
            platform_port_dict = json.loads(OpsRedis.get('platform_proxy_port').decode())
            if args.get('platform_id') in platform_port_dict:
                platform_port = platform_port_dict.get(args.get('platform_id'))
            else:
                for port,platform_id in platform_port_dict.items():
                    if port == '':
                        platform_port = port
                        break
            if not platform_port:
                return jsonify(falseReturn(msg=u'没有富裕的端口'))
            return jsonify(trueReturn(platform_port))
        else:
            return jsonify(falseReturn(msg=u'请先配置或者启动proxy server'))

    @login_required
    def post(self):
        locations = ['form', 'json']
        args = reqparse.RequestParser().add_argument('platform_proxy_port',
                                    type=str,required=True,location=locations).parse_args()
        platform_proxy_port = args.get('platform_proxy_port')
        OpsRedis.set('platform_proxy_url',platform_proxy_port)
        return trueReturn()
