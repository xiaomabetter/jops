from marshmallow import fields,Schema
from app.models import Service,Account
from app.utils.encrypt import ChaEncrypt
import json

class NodeSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    full_value = fields.Function(lambda obj: obj.full_value)
    parent = fields.Function(lambda obj: obj.parent.id.hex)
    open = fields.Function(lambda obj: True if obj.level <= 2 else False)

    class Meta:
        fields = ("id","key", "value", "full_value", "parent","open")

class AccountSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    username = fields.String(required=True)
    password = fields.Method("decrypt",dump_only=True)
    assets = fields.Method('relate_assets',dump_only=True)

    def relate_assets(self,obj):
        account = Account.select().where(Account.id == obj.id).get()
        account_objects = account.asset.objects()
        data = json.loads(AssetSerializer(many=True,only=['id','AssetType','InstanceName','InnerAddress']).
                          dumps(account_objects).data)
        return data

    def decrypt(self,obj):
        if obj.password:
            pt = ChaEncrypt(bytes(obj.id.hex,"utf8"))
            decrypt_text = pt.decrypt(obj.password.encode())
            return decrypt_text.decode()
        else:
            return None

    class Meta:
        fields = ("id","username","databases", "buckets", "description", "assets","password")

class ServiceSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    servicename = fields.String(required=True)
    version = fields.String(required=True)
    asset_amount = fields.Method("amount")
    assets = fields.Method('relate_assets')
    description = fields.String()

    def relate_assets(self,obj):
        service = Service.select().where(Service.id == obj.id).get()
        service_objects = service.asset.objects()
        data = json.loads(AssetSerializer(many=True,only=['id','AssetType','InstanceName','InnerAddress']).
                          dumps(service_objects).data)
        return data

    def amount(self,obj):
        service = Service.select().where(Service.id==obj.id).get()
        if  service :return service.asset.count()
        else:return 0

class AssetSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    Address = fields.Method("addr")
    account = fields.Nested(AccountSerializer, many = True,only=['username','password'])
    node = fields.Nested(NodeSerializer, many = True)
    service = fields.Nested(ServiceSerializer,many=True,only=['id','servicename'])

    def addr(self,obj):
        if obj.InnerAddress and obj.PublicIpAddress:
            return '{} | {}'.format(obj.InnerAddress,obj.PublicIpAddress)
        elif obj.InnerAddress:
            return obj.InnerAddress
        elif obj.PublicIpAddress:
            return obj.PublicIpAddress

    class Meta:
        fields = ("id","InstanceName", "InstanceId", "AssetType", "InnerAddress","PublicIpAddress",
                  "Address","RegionId","sshport","account","node","Status"
                  )

class AssetCreateTemplateSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    RegionId = fields.String(required=True)
    ZoneId = fields.String(required=True)
    ImageId = fields.String(required=True)
    InstanceNetworkType = fields.String(required=True)
    instance_type = fields.String(validate=lambda s:' ' not in s,error='不能有空格',required=True)
    SystemDiskCategory = fields.String(required=True)
    SystemDiskSize = fields.Integer(required=True)
    DataDiskinfo = fields.String(required=True,dump_only=True)
    SecurityGroupId  = fields.List(fields.String(),)
    SystemDiskCategorySize = fields.Function(lambda obj:'类型:{0};大小:{1}'.
                            format(obj.SystemDiskCategory,obj.SystemDiskSize),dump_only=True)

    class Meta:
        fields = ("id","name","RegionId", "ZoneId", "ImageId","InstanceNetworkType", "instance_type",
                  "SystemDiskCategory", "SecurityGroupId","SystemDiskCategorySize","SystemDiskSize",
                  "DataDiskinfo","CreateTime","cpu","memory"
                  )