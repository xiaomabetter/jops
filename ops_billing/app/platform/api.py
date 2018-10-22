from app import get_logger
from flask import jsonify,request
from flask_restful import Resource,reqparse
from app.auth import login_required,adminuser_required,get_login_user
from app.models import Platforms,OpsRedis
from app.platform.serializer import PlatformSerializer
from app.perm.serializer import AuthorizationPlatformSerializer
from app.utils import trueReturn,falseReturn
import json

logger = get_logger(__name__)

__all__ = ['PlatformsApi','PlatformApi','PlatformsProxyApi']

class PlatformsApi(Resource):
    @login_required
    def get(self):
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
                        print(platform_auth_query_set.count())
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
            .add_argument('catagory', type=str, required=True, location=locations).parse_args()
        try:
            Platforms.create(description=args.get('description'),
                                        platform_url=args.get('platform_url'),catagory=args.get('catagory'))
            return trueReturn(msg='创建成功')
        except Exception as e:
            return falseReturn(msg=str(e))

class PlatformApi(Resource):
    @login_required
    def get(self,platformid):
        query_set = Platforms.select().where(Platforms.id == platformid).get()
        data = json.loads(PlatformSerializer().dumps(query_set).data)
        return jsonify(trueReturn(data))

    @login_required
    def put(self,platformid):
        locations = ['form', 'json']
        args = reqparse.RequestParser().add_argument('description', type=str,required=True,location=locations) \
            .add_argument('platform_url', type=str,required=True, location=locations) \
            .add_argument('catagory', type=str, required=True, location=locations).parse_args()
        try:
            Platforms.update(description=args.get('description'),platform_url=args.get('platform_url'),
                             catagory=args.get('catagory')).where(Platforms.id == platformid).execute()
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

class PlatformsProxyApi(Resource):
    @login_required
    def get(self):
        proxy_port = OpsRedis.get('platform_proxy_port')
        if proxy_port:
            return jsonify(trueReturn(proxy_port.decode()))
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