from flask import jsonify,request
from flask_restful import Resource,reqparse
from apps.auth import login_required,adminuser_required,get_login_user
from apps.models import Platforms,OpsRedis,Catagory
from apps.platform.serializer import PlatformSerializer
from apps.perm.serializer import AuthorizationPlatformSerializer
from apps.utils import trueReturn,falseReturn
from peewee import fn
import json,random,re

__all__ = ['PlatformsApi','PlatformApi','PlatformProxyApi','PlatformCatagoryApi']

class PlatformsApi(Resource):
    @login_required(administrator=False)
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

    @login_required()
    @adminuser_required
    def post(self):
        locations = ['form','json']
        args = reqparse.RequestParser()\
            .add_argument('description', type=str,required=True,location=locations) \
            .add_argument('platform_url', type=str,required=True, location=locations) \
            .add_argument('catagory', type=str, required=True, location=locations) \
            .add_argument('location', type=str, required=True, location=locations).parse_args()
        try:
            maxport = Platforms.select(fn.Max(Platforms.proxyport)).scalar()
            pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            pattern_result = pattern.findall(args.get('platform_url'))
            if not pattern_result:
                return falseReturn(msg="platform_url不合法")
            Platforms.create(description=args.get('description'),location=args.get('location'),
                        platform_url=args.get('platform_url'),catagory=args.get('catagory'),proxyport=int(maxport) + 1)
            return trueReturn(msg='创建成功')
        except Exception as e:
            return falseReturn(msg=str(e))

class PlatformApi(Resource):
    @login_required()
    def get(self,platformid):
        if OpsRedis.exists(platformid):
            data = json.loads(OpsRedis.get(platformid).decode())
        else:
            query_set = Platforms.select().where(Platforms.id == platformid).get()
            data = json.loads(PlatformSerializer().dumps(query_set).data)
            OpsRedis.set(platformid,json.dumps(data))
        return jsonify(trueReturn(data))

    @login_required()
    def put(self,platformid):
        locations = ['form', 'json']
        args = reqparse.RequestParser()\
            .add_argument('description', type=str,required=True,location=locations) \
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

    @login_required()
    def delete(self,platformid):
        try:
            platform = Platforms.select().where(Platforms.id == platformid).get()
            platform.platform_permission.clear()
            Platforms.delete().where(Platforms.id == platformid).execute()
            return jsonify(trueReturn(msg="更新成功"))
        except Exception as e:
            return jsonify(falseReturn(msg="更新失败%s" % str(e)))


class PlatformCatagoryApi(Resource):
    @login_required()
    def post(self):
        locations = ['form', 'json']
        args = reqparse.RequestParser().\
            add_argument('description',type=str,required=True,location=locations).parse_args()
        try:
            Catagory.create(description=args.get('description'))
            return jsonify(trueReturn(msg='创建成功'))
        except Exception as e:
            return jsonify(falseReturn(msg='创建失败%s' % str(e)))

class PlatformProxyApi(Resource):
    @login_required(administrator=False)
    def get(self):
        args = reqparse.RequestParser().\
            add_argument('platform_id', type=str,required=True, location='args').parse_args()
        platform = Platforms.select().where(Platforms.id == args.get('platform_id')).first()
        request_host = request.headers['Host'].split(':')[0]
        platform_proxy = OpsRedis.get('platform_proxy')
        if platform and platform_proxy:
            data = json.loads(PlatformSerializer().dumps(platform).data)
            location = platform.location
            if type(platform_proxy) is bytes:platform_proxy = platform_proxy.decode()
            platform_proxy = json.loads(platform_proxy)
            if location not in platform_proxy:
                return jsonify(falseReturn())
            proxy_binds = platform_proxy[location]
            if not isinstance(proxy_binds,list):
                return jsonify(falseReturn())
            bind_outerips = [bind['outerip'] for bind in proxy_binds]
            if request_host in bind_outerips:
                data['bind'] = request_host
            else:
                proxy_bind = proxy_binds[random.randint(0,len(proxy_binds) -1)]
                if not isinstance(proxy_bind,dict):
                    return jsonify(falseReturn())
                data['bind'] = proxy_bind['domain']
            return jsonify(trueReturn(data))
        else:
            return jsonify(falseReturn())

    @login_required(administrator=False)
    def post(self):
        locations = ['form','json']
        args = reqparse.RequestParser()\
            .add_argument('location',type=str,required=True,location=locations) \
            .add_argument('outerip', type=str, required=True, location=locations) \
            .add_argument('domain', type=str, required=True, location=locations).parse_args()
        location = args.get('location')
        outerip = args.get('outerip')
        domain = args.get('domain')
        platform_proxy = OpsRedis.get('platform_proxy')
        if platform_proxy:
            if type(platform_proxy) is bytes:platform_proxy = platform_proxy.decode()
            platform_proxy = json.loads(platform_proxy)
            if not isinstance(platform_proxy,dict):
                OpsRedis.delete('platform_proxy')
                platform_proxy = dict()
            if location in platform_proxy:
                proxy_binds = platform_proxy[location]
                if not isinstance(proxy_binds,list):
                    platform_proxy[location] = []
                bind_domains = [bind['domain'] for bind in proxy_binds]
                bind_outerips = [bind['outerip'] for bind in proxy_binds]
                if outerip not in bind_outerips and domain not in bind_domains:
                    platform_proxy[location].append({'outerip':outerip,'domain':domain})
            else:
                platform_proxy[location] = [{'outerip':outerip,'domain':domain}]
            OpsRedis.set('platform_proxy', json.dumps(platform_proxy))
        else:
            OpsRedis.set('platform_proxy',json.dumps({location:[{'outerip':outerip,'domain':domain}]}))
        return trueReturn()