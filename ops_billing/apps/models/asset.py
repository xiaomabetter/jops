# -*- coding: utf-8 -*-
from peewee import CharField, BooleanField, IntegerField,UUIDField,IPField,\
    DateTimeField,ManyToManyField,ForeignKeyField,FloatField
import os,uuid,datetime,json
from .base import BaseModel

class Service(BaseModel):
    id = UUIDField(default=uuid.uuid4,primary_key=True)
    servicename = CharField(max_length=64,null=False)
    version = CharField(max_length=64,null=False)
    description = CharField(max_length=600,null=True)
    class Meta:
        indexes = (
            (('servicename', 'version'), True),
        )
        table_name = 'assets_service'

class Account(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    username = CharField(max_length=64,null=False)
    password = CharField(max_length=128,null=True)
    databases = CharField(max_length=128,null=True)
    buckets = CharField(max_length=128,null=True)
    description = CharField(max_length=600,null=True)

    class Meta:
        indexes = (
            (('username', 'password','databases'), True),
            (('username', 'password','buckets'), True),
        )
        table_name = 'assets_account'

class Node(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    key = CharField(unique=True, max_length=64)
    value = CharField(max_length=128, unique=True)
    child_mark = IntegerField(default=0)
    date_create = DateTimeField(default=datetime.datetime.now)
    is_node = True

    def __str__(self):
        return self.full_value

    @property
    def name(self):
        return self.value

    @property
    def full_value(self):
        if self == self.__class__.root():
            return self.value
        else:
            return '{} / {}'.format(self.parent.full_value, self.value)

    @property
    def level(self):
        return len(self.key.split(':'))

    def get_next_child_key(self):
        mark = self.child_mark
        self.child_mark += 1
        self.save()
        return "{}:{}".format(self.key, mark)

    def create_child(self, value):
        child_key = self.get_next_child_key()
        child = self.__class__.create(key=child_key, value=value)
        return child

    def get_children(self):
        return self.__class__.filter(Node.key.regexp(r'{}:[0-9]+$'.format(self.key)))

    def get_all_children(self):
        return self.__class__.filter(Node.key.startswith('{}:'.format(self.key)))

    def get_family(self):
        children = list(self.get_all_children())
        children.append(self)
        return children

    def get_family_nodeids(self):
        nodeids = []
        for node in self.get_family():
            nodeids.append(node.id)
        return nodeids

    def get_family_assetids(self,asset_type):
        assetids = []
        for asset in Asset.filter(Asset.AssetType==asset_type).join(Asset_Node):
            assetids.append(asset.id)
        return assetids

    def get_all_assets(self,asset_type):
        if self.is_root():
            assets = Asset.filter(Asset.AssetType==asset_type)
        else:
            nodeids = self.get_family_nodeids()
            if asset_type == 'all':
                assets = Asset.select().join(Asset_Node).where(Asset_Node.node_id.in_(nodeids))
            else:
                assets = Asset.filter(Asset.AssetType==asset_type).join(Asset_Node).\
                    where(Asset_Node.node_id.in_(nodeids))
        return assets

    def is_root(self):
        return self.key == '0'

    @property
    def parent(self):
        if self.key == "0":
            return self.__class__.root()
        elif not self.key.startswith("0"):
            return self.__class__.root()

        parent_key = ":".join(self.key.split(":")[:-1])
        try:
            parent = self.__class__.get(key=parent_key)
        except Node.DoesNotExist:
            return self.__class__.root()
        else:
            return parent

    @property
    def get_all_parents(self):
        keys = []
        if self.key == "0":
            return [str(self.__class__.root().id)]
        elif not self.key.startswith("0"):
            return [str(self.__class__.root().id)]
        level = self.level
        keys.append(self.key)
        for i in range(level):
            if self.key.split(":")[:-i] :
                keys.append(":".join(self.key.split(":")[:-i]))
        return keys

    @property
    def parent_id(self):
        if self.key == "0":
            return self.__class__.root()
        elif not self.key.startswith("0"):
            return self.__class__.root()

        parent_key = ":".join(self.key.split(":")[:-1])
        try:
            parent = self.__class__.get(key=parent_key)
        except Node.DoesNotExist:
            return self.__class__.root()
        else:
            return parent.id

    @parent.setter
    def parent(self, parent):
        self.key = parent.get_next_child_key()

    @property
    def ancestor(self):
        if self.parent == self.__class__.root():
            return [self.__class__.root()]
        else:
            return [self.parent, *tuple(self.parent.ancestor)]

    @property
    def ancestor_with_node(self):
        ancestor = self.ancestor
        ancestor.insert(0, self)
        return ancestor

    @classmethod
    def root(cls):
        obj, created = cls.get_or_create(
            key='0', defaults={"key": '0', 'value': "ROOT"}
        )
        return obj

    class Meta:
        table_name = 'assets_node'

class Asset(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    AssetType = CharField(max_length=128, null=False)
    InnerAddress = CharField(max_length=128, null=True)
    PublicIpAddress = CharField(max_length=128, null=True)
    InstanceName = CharField(max_length=128, null=True)
    InstanceId = CharField(max_length=128,unique=True,null=False)
    RegionId = CharField(max_length=128, unique=False,null=False)
    Status = CharField(max_length=128,null=False)
    sshport = IntegerField(default=3299,null=True)
    is_connective = BooleanField(default=True)
    node = ManyToManyField(Node,backref='asset')
    service = ManyToManyField(Service,backref='asset')
    account = ManyToManyField(Account,backref='asset')

    def __str__(self):
        return '{0.InstanceName}({0.InnerAddress})'.format(self)

    @property
    def full_name(self):
        return '{0.InstanceName}({0.InnerAddress})'.format(self)

    @property
    def is_valid(self):
        if self.Status == 'Destory':
            return False
        else:
            return True

    @classmethod
    def asset_type(cls):
        results = Asset.select(Asset.AssetType).distinct()
        return tuple([result.AssetType for result in results])

    def is_ecs(self):
        if self.AssetType == 'ecs':
            return True
        else:
            return False

    class Meta:
        table_name = 'assets_asset'

class Bill(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    instance_id = CharField(max_length=64,null=False)
    instance_name = CharField(max_length=64,null=False)
    instance_type = CharField(max_length=64,null=False)
    type_alias_name = CharField(max_length=64, null=True)
    day = DateTimeField(null=False)
    cost = FloatField()

    class Meta:
        table_name = 'assets_bill'

class Sync_Bill_History(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    username = CharField(max_length=32)
    day = DateTimeField(null=False)
    filename = CharField(max_length=256,null=False)

    def __str__(self):
        return '{0.username}({0.day})'.format(self)

    class Meta:
        table_name = 'assets_bill_sync_history'


class Create_Asset_History(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    taskid = CharField(max_length=128, null=False)
    amount = IntegerField(default=1)
    AssetType = CharField(max_length=128, null=False)
    InstanceName = CharField(max_length=128, null=True)
    RegionId = CharField(max_length=128, null=False)
    created_by = CharField(max_length=128, null=False)
    isSuccess = BooleanField(default=False,null=False)
    CreateTime = DateTimeField(null=False,default=datetime.datetime.now())

    class Meta:
        table_name = 'assets_create_history'

class Asset_Create_Template(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    name = CharField(max_length=128,unique=True,null=False)
    RegionId = CharField(max_length=128, null=False)
    ZoneId = CharField(max_length=128, null=False)
    ImageId = CharField(max_length=128,null=False)
    cpu = IntegerField(null=True)
    memory = IntegerField(null=True)
    InstanceNetworkType = CharField(max_length=128, null=True)
    VSwitchId = CharField(max_length=256, null=True)
    instance_type = CharField(max_length=128, null=False)
    SecurityGroupId = CharField(max_length=600,null=False,default=[])
    SystemDiskCategory = CharField(max_length=128, null=False)
    SystemDiskSize = IntegerField(null=False)
    DataDiskinfo = CharField(max_length=600, null=False,default=[])
    CreateTime = DateTimeField(null=False,default=datetime.datetime.now())

    class Meta:
        table_name = 'assets_create_templates'

Asset_Node = Asset.node.get_through_model()
Asset_Service = Asset.service.get_through_model()
Asset_Account = Asset.account.get_through_model()
