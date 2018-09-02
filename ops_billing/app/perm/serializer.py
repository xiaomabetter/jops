from marshmallow import schema,fields,Schema
from app.asset.serializer import NodeSerializer,AssetSerializer
from app.user.serializer import UserSerializer,GroupSerializer

class SystemUserSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    username = fields.String(required=True)
    password = fields.String(required=True)
    auto_generate_key = fields.Boolean(required=False,dump_only=True)
    class Meta:
        fields = ("id","username", "password", "auto_generate_key","private_key",
                  "public_key",'date_created','date_updated','created_by','priority','protocol',
                  'auto_push','sudo','shell','comment')

class AssetPermissionSerializer(Schema):
    id = fields.Function(lambda obj: str(obj.id))
    name = fields.String(required=True)
    is_active = fields.Boolean()
    assets = fields.Nested(AssetSerializer,exclude=('node','account'),many=True)
    nodes = fields.Nested(NodeSerializer,many=True)
    system_users = fields.Nested(SystemUserSerializer,many=True,only=['id','username','name'])
    users = fields.Nested(UserSerializer,many=True,only=['id','username','phone','wechat','ding','email'])
    groups = fields.Nested(GroupSerializer,many=True)

    class Meta:
        fields = ("id","name","assets","nodes","system_users","users","groups","is_active",
                  "date_start","date_expired","created_by","comment")