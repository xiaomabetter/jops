# -*- coding: utf-8 -*-
from peewee import CharField, BooleanField,UUIDField,DateTimeField,ManyToManyField,\
                        TextField,IntegerField
import uuid,datetime
from .user import User,Groups
from .asset import Asset,Node
from .base import BaseModel
from .platform import Platforms

class SystemUser(BaseModel):
    SSH_PROTOCOL = 'ssh'
    RDP_PROTOCOL = 'rdp'
    PROTOCOL_CHOICES = (
        (SSH_PROTOCOL, 'ssh'),
        (RDP_PROTOCOL, 'rdp'),
    )
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    name = CharField(max_length=128, unique=True)
    username = CharField(max_length=32)
    password = CharField(max_length=256, null=True)
    auto_generate_key = BooleanField(default=False)
    private_key = TextField(null=True)
    public_key = TextField(null=True)
    date_created = DateTimeField(default=datetime.datetime.now)
    date_updated = DateTimeField(default=datetime.datetime.now)
    created_by = CharField(max_length=128, null=True)
    priority = IntegerField(default=10)
    protocol = CharField(max_length=16, choices=PROTOCOL_CHOICES, default='ssh')
    auto_push = BooleanField(default=True)
    sudo = TextField(default='/bin/whoami')
    shell = CharField(max_length=64,  default='/bin/bash')
    comment = CharField(max_length=600, null=True)

    def __str__(self):
        return '{0.name}({0.username})'.format(self)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'protocol': self.protocol,
            'priority': self.priority,
            'auto_push': self.auto_push,
        }

    def _to_secret_json(self):
        return dict({
            'name': self.name,
            'username': self.username,
            'password': self.password,
            'private_key': self.private_key,
        })

    def get_assets(self):
        assets = set(self.assets.objects())
        return assets

    def is_need_push(self):
        if self.auto_push and self.protocol == self.__class__.SSH_PROTOCOL:
            return True
        else:
            return False

    class Meta:
        table_name = 'permission_systemusers'

class PermissionGroups(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    name = CharField(max_length=128, unique=True)
    users = ManyToManyField(User,backref='permission_group')
    date_created = DateTimeField(default=datetime.datetime.now)
    date_updated = DateTimeField(default=datetime.datetime.now)
    created_by = CharField(max_length=128, null=True)
    comment = CharField(max_length=600, null=True)

    class Meta:
        table_name = 'permission_groups'

class AssetPermission(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    name = CharField(max_length=128, unique=True)
    users = ManyToManyField(User,backref='asset_permissions')
    groups = ManyToManyField(PermissionGroups, backref='asset_permissions')
    assets = ManyToManyField(Asset, backref='asset_permissions')
    nodes = ManyToManyField(Node, backref='asset_permissions')
    system_users = ManyToManyField(SystemUser, backref='asset_permissions')
    is_active = BooleanField(default=True)
    date_start = DateTimeField(default=datetime.datetime.now)
    date_expired = DateTimeField(default=datetime.datetime.now)
    created_by = CharField(max_length=128)
    date_created = DateTimeField(default=datetime.datetime.now)
    comment = CharField(max_length=600, null=True)

    def __str__(self):
        return self.name

    @property
    def id_str(self):
        return str(self.id)

    @property
    def is_valid(self):
        if self.date_expired > datetime.datetime.now > self.date_start and self.is_active:
            return True
        return False

    class Meta:
        table_name = 'permission_asset'

class PermissionPlatform(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    name = CharField(max_length=128, unique=True)
    users = ManyToManyField(User,backref='platform_permission')
    groups = ManyToManyField(PermissionGroups, backref='platform_permission')
    platform_urls = ManyToManyField(Platforms, backref='platform_permission')
    is_active = BooleanField(default=True)
    date_created = DateTimeField(default=datetime.datetime.now)
    description = CharField(max_length=600, null=True)

    class Meta:
        table_name = 'permission_platform'

PermissionGroups_User = PermissionGroups.users.get_through_model()
AssetPerm_Nodes = AssetPermission.nodes.get_through_model()
AssetPerm_Assets = AssetPermission.assets.get_through_model()
AssetPerm_Users = AssetPermission.users.get_through_model()
AssetPerm_Groups = AssetPermission.groups.get_through_model()
AssetPerm_SystemUser = AssetPermission.system_users.get_through_model()
PermissionPlatform_Users = PermissionPlatform.users.get_through_model()
PermissionPlatform_Groups = PermissionPlatform.groups.get_through_model()
PermissionPlatform_Platform_urls = PermissionPlatform.platform_urls.get_through_model()