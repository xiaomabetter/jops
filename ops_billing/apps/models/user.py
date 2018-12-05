# -*- coding: utf-8 -*-
from peewee import CharField, BooleanField, IntegerField,UUIDField,\
    DateTimeField,TextField,ManyToManyField,ForeignKeyField
from apps.utils.encrypt import encryption_md5
import uuid
from .base import BaseModel
import hashlib

class Groups(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    key = CharField(unique=True, max_length=64)
    value = CharField(max_length=255,unique=True,null=False)
    child_mark = IntegerField(default=0)
    description = TextField(null=True)
    is_ldap_group = BooleanField(default=False)
    is_node = True

    def __str__(self):
        return self.value

    @property
    def name(self):
        return self.value

    @property
    def parent(self):
        if self.key == "0":
            return self.__class__.root()
        elif not self.key.startswith("0"):
            return self.__class__.root()

        parent_key = ":".join(self.key.split(":")[:-1])
        try:
            parent = self.__class__.get(key=parent_key)
        except Groups.DoesNotExist:
            return self.__class__.root()
        else:
            return parent

    def is_root(self):
        return self.key == '0'

    @parent.setter
    def parent(self, parent):
        self.key = parent.get_next_child_key()

    def get_next_child_key(self):
        mark = self.child_mark
        self.child_mark += 1
        self.save()
        return "{}:{}".format(self.key, mark)

    def create_child(self, value):
        child_key = self.get_next_child_key()
        child = self.__class__.create(key=child_key, value=value)
        return child

    @classmethod
    def root(cls):
        obj, created = cls.get_or_create(
            key='0', defaults={"key": '0', 'value': "ROOT"}
        )
        return obj

class User(BaseModel):
    ROLE_CHOICES = (
        ('administrator','administrator'),
        ('user','user')
    )
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    email = CharField(max_length=128)
    username = CharField(max_length=128,null=True,unique=True)
    chinese_name = CharField(max_length=500,null=True)
    password = CharField(max_length=128)
    public_key = TextField(null=True)
    group = ManyToManyField(Groups,backref='user')
    role = CharField(max_length=128, default='user',choices=ROLE_CHOICES)
    phone = CharField(max_length=128)
    wechat = CharField(max_length=128)
    ding = CharField(max_length=128)
    is_ldap_user = BooleanField(default=False,null=False)
    is_active = BooleanField(default=True,null=False)
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
            'password':self.password,
            'email': self.email,
            'role': self.role,
            'wechat': self.wechat,
            'phone': self.phone,
            'is_active':self.is_active,
            'is_ldap_user':self.is_ldap_user
        })

    def gravatar(self,size=100,default='identicon',rating='g'):
        url = "https://www.gravatar.com/avatar"
        hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,hash=hash,size=size,default=default,rating=rating)

class UserLoginLog(BaseModel):
    username = CharField(max_length=128,null=True)
    login_at = DateTimeField(null=True)
    login_ip = CharField(max_length=128,null=True)

User_Group = User.group.get_through_model()