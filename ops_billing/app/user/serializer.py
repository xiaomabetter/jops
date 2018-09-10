from marshmallow import fields,Schema,validates,ValidationError
from app.utils.sshkey import validate_ssh_public_key
from app.models.user import  User

class UserSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    public_key  = fields.String()

    @validates('public_key')
    def validate_quantity(self, value):
        if value and not validate_ssh_public_key(value):
            raise ValidationError('ssh key格式不对.')

    class Meta:
        fields = ("id","username", "email","public_key","role",'is_ldap_user',
                  "phone","wechat","ding","is_active","comment")


class GroupSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    key = fields.String(required=True,dump_only=True)
    value = fields.String(required=True)
    parent_id = fields.Function(lambda obj: obj.parent.id.hex)
    parent_key = fields.Function(lambda obj:obj.parent.key)
    description = fields.String()
    user = fields.Nested(UserSerializer,many=True)
    user_amount = fields.Function(lambda obj:len(obj.user) if obj.key != '0' else User.select().count())
    open = fields.Boolean(default=True)

    class Meta:
        fields = ('id','value','parent_id','key','parent_key','user_amount','open','user')