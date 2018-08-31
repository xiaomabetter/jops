# -*- coding: utf-8 -*-
from peewee import CharField, BooleanField, IntegerField,UUIDField,\
    DateTimeField,TextField,ManyToManyField
from app.utils.encrypt import encryption_md5
import uuid
from .base import BaseModel

class Groups(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    groupname = CharField(unique=True)
    description = TextField(null=True)

    def __str__(self):
        return '{0.groupname}'.format(self)

class User(BaseModel):
    ROLE_CHOICES = (
        ('administrator','administrator'),
        ('user','user')
    )
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    email = CharField(max_length=128,null=True)
    username = CharField(max_length=128,null=True,unique=True)
    password = CharField(max_length=128)
    public_key = TextField(null=True)
    group = ManyToManyField(Groups,backref='user')
    role = CharField(max_length=128, choices=ROLE_CHOICES)
    phone = CharField(max_length=128)
    wechat = CharField(max_length=128)
    ding = CharField(max_length=128)
    is_active = BooleanField(default=True)
    last_login_at = DateTimeField(null=True)
    current_login_at = DateTimeField(null=True)
    last_login_ip = CharField(max_length=128,null=True)
    current_login_ip = CharField(max_length=128,null=True)
    login_count = IntegerField(null=True)
    comment = CharField(max_length=600,null=True)

    def __str__(self):
        return '{0.email}'.format(self)

    def hash_password(self, password):
        self.password = encryption_md5(password)

    def verify_password(self, password):
        return  self.password == encryption_md5(password)

    def verify_public_key(self, public_key):
        return self.public_key == public_key

    @property
    def administrator(self):
        return self.role == 'administrator'

    def to_json(self):
        return dict({
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'groups': [group.id.hex for group in self.group.objects()],
            'wechat': self.wechat,
            'phone': self.phone,
            'comment': self.comment
        })

User_Group = User.group.get_through_model()