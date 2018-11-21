from marshmallow import schema,fields,Schema
from apps.asset.serializer import NodeSerializer,AssetSerializer
from apps.user.serializer import UserSerializer
from apps.platform.serializer import PlatformSerializer
from apps.models import PermissionGroups,PermissionPlatform
import json

class SystemUserSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    username = fields.String(required=True)
    password = fields.String(required=True)
    auto_generate_key = fields.Boolean(required=False,dump_only=True)

    class Meta:
        fields = ("id","username", "password", "auto_generate_key","private_key",
                  "public_key",'date_created','date_updated','created_by','priority','protocol',
                  'auto_push','sudo','shell','comment')

class PermissionGroupSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    users = fields.Nested(UserSerializer, many=True,
                          only=['id','username', 'phone', 'wechat', 'ding', 'email'])
    asset_permissions = fields.Method('relateAssetPerm',dump_only=True)
    platform_permissions = fields.Method('relatePlatformPerm',dump_only=True)

    def relateAssetPerm(self,obj):
        result = {}
        group = PermissionGroups.select().where(PermissionGroups.id == obj.id).first()
        if group :
            objects = group.asset_permissions.objects()
            result = json.loads(AssetPermissionSerializer(many=True,only=['name']).dumps(objects).data)
        return result

    def relatePlatformPerm(self,obj):
        result = {}
        group = PermissionGroups.select().where(PermissionGroups.id == obj.id).first()
        if group :
            objects = group.platform_permission.objects()
            result = json.loads(AuthorizationPlatformSerializer(many=True,only=['name']).dumps(objects).data)
        return result

    class Meta:
        fields = ("id","name","users",'date_created','date_updated','created_by','comment',
                  'asset_permissions','platform_permissions')


class AssetPermissionSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    name = fields.String(required=True)
    is_active = fields.Boolean()
    assets = fields.Nested(AssetSerializer,exclude=('node','account'),many=True)
    nodes = fields.Nested(NodeSerializer,many=True)
    system_users = fields.Nested(SystemUserSerializer,many=True,only=['id','username','name'])
    users = fields.Nested(UserSerializer,many=True,
                          only=['id','username','phone','wechat','ding','email'])
    groups = fields.Nested(PermissionGroupSerializer,only=['id','users','name'],many=True)

    class Meta:
        fields = ("id","name","assets","nodes","system_users","users","groups","is_active",
                  "created_by","comment")

class AuthorizationPlatformSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    name = fields.String(required=True)
    is_active = fields.Boolean()
    users = fields.Nested(UserSerializer,many=True,only=['id','username','email'])
    groups = fields.Nested(PermissionGroupSerializer,only=['id','name'],many=True)
    platform_urls = fields.Nested(PlatformSerializer,many=True)

    class Meta:
        fields = ("id","name","users","groups","platform_urls","is_active")