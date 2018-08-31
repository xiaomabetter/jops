# -*- coding: utf-8 -*-
from peewee import CharField, BooleanField,UUIDField,DateTimeField,ManyToManyField
import os,uuid,datetime,json
from .user import User,Groups
from .asset import Asset,Node
from .base import BaseModel
from .systemuser import SystemUser

class AssetPermission(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    name = CharField(max_length=128, unique=True)
    users = ManyToManyField(User,backref='asset_permissions')
    groups = ManyToManyField(Groups, backref='asset_permissions')
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

AssetPerm_Nodes = AssetPermission.nodes.get_through_model()
AssetPerm_Assets = AssetPermission.assets.get_through_model()
AssetPerm_Users = AssetPermission.users.get_through_model()
AssetPerm_Groups = AssetPermission.groups.get_through_model()
AssetPerm_SystemUser = AssetPermission.system_users.get_through_model()