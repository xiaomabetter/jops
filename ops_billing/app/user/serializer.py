from marshmallow import fields,Schema,validates,ValidationError
from app.utils.sshkey import validate_ssh_public_key
from app.models import User,User_Group

class GroupSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    groupname = fields.String(required=True)
    description = fields.String(required=True)
    users = fields.Method('user_num',dump_only=True)

    def user_num(self,obj):
        query = User.select(User.id).join(User_Group).\
            where(User_Group.groups_id == obj.id)
        return [q.id.hex for q in query]

class UserSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    group = fields.Nested(GroupSerializer,many=True,dump_only=True)
    public_key  = fields.String()

    @validates('public_key')
    def validate_quantity(self, value):
        if value and not validate_ssh_public_key(value):
            raise ValidationError('ssh key格式不对.')

    class Meta:
        fields = ("id","username", "email","public_key","role",
                  "phone","wechat","ding","is_active","group","comment")

class UserModelSerializer(Schema):
    id = fields.Method("get_user_id")
    def get_user_id(self,obj):
        if isinstance(obj,dict):
            if obj.get('id') :
                return obj['id']
            else:
                return None
        else:
            return str(obj.id)