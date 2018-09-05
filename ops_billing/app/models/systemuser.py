# -*- coding: utf-8 -*-
from peewee import CharField, BooleanField, IntegerField,UUIDField,DateTimeField,TextField
from .base import BaseModel
import os,uuid,datetime,json

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