from __future__ import unicode_literals

import uuid,datetime
from peewee import CharField, BooleanField, IntegerField,PrimaryKeyField,UUIDField,IPField,\
    DateTimeField,ManyToManyField,ForeignKeyField,FloatField
import os,uuid,datetime,json
from .base import BaseModel
from .user import User
from conf.config import Config

class Terminal(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    name = CharField(max_length=32)
    remote_addr = IPField(null=False)
    ssh_port = IntegerField(default=2222)
    http_port = IntegerField(default=5000)
    command_storage = CharField(max_length=128, default='default')
    replay_storage = CharField(max_length=128, default='default')
    access_key = CharField(max_length=256,null=True)
    is_accepted = BooleanField(default=False)
    is_deleted = BooleanField(default=False)
    date_created = DateTimeField(default=datetime.datetime.now)
    last_update_date = DateTimeField(null=True)
    comment = CharField(max_length=600,null=True)

    def get_common_storage(self):
        storage_all = Config.TERMINAL_COMMAND_STORAGE
        if self.command_storage in storage_all:
            storage = storage_all.get(self.command_storage)
        else:
            storage = storage_all.get('default')
        return {"TERMINAL_COMMAND_STORAGE": storage}

    def get_replay_storage(self):
        storage_all = Config.TERMINAL_REPLAY_STORAGE
        if self.replay_storage in storage_all:
            storage = storage_all.get(self.replay_storage)
        else:
            storage = storage_all.get('default')
        return {"TERMINAL_REPLAY_STORAGE": storage}

    @property
    def config(self):
        configs = {}
        for k in dir(Config):
            if k.startswith('TERMINAL'):
                configs[k] = getattr(Config, k)
        configs.update(self.get_common_storage())
        configs.update(self.get_replay_storage())
        return configs

    def __str__(self):
        status = "Active"
        if not self.is_accepted:
            status = "NotAccept"
        elif self.is_deleted:
            status = "Deleted"
        return '%s: %s' % (self.name, status)

class Status(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    session_online = IntegerField(default=0)
    cpu_used = FloatField()
    memory_used = FloatField()
    connections = IntegerField()
    threads = IntegerField()
    boot_time = FloatField()
    terminal = ManyToManyField(Terminal,backref='status')
    date_created = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.date_created.strftime("%Y-%m-%d %H:%M:%S")


class Session(BaseModel):
    LOGIN_FROM_CHOICES = (
        ('ST', 'SSH Terminal'),
        ('WT', 'Web Terminal'),
    )
    PROTOCOL_CHOICES = (
        ('ssh', 'ssh'),
        ('rdp', 'rdp')
    )

    id = UUIDField(default=uuid.uuid4, primary_key=True)
    user = CharField(max_length=128)
    asset = CharField(max_length=1024)
    system_user = CharField(max_length=128)
    login_from = CharField(max_length=2, choices=LOGIN_FROM_CHOICES, default="ST")
    remote_addr = CharField(max_length=15,null=True)
    is_finished = BooleanField(default=False)
    has_replay = BooleanField(default=False)
    has_command = BooleanField(default=False)
    terminal = ManyToManyField(Terminal, backref='session')
    protocol = CharField(choices=PROTOCOL_CHOICES, default='ssh', max_length=8)
    date_last_active = DateTimeField(default=datetime.datetime.now)
    date_start = DateTimeField(default=datetime.datetime.now,index=True)
    date_end = DateTimeField(null=True)

    def __str__(self):
        return "{0.id} of {0.user} to {0.asset}".format(self)


class Task(BaseModel):
    NAME_CHOICES = (
        ("kill_session", "Kill Session"),
    )

    id = UUIDField(default=uuid.uuid4, primary_key=True)
    name = CharField(max_length=128, choices=NAME_CHOICES)
    args = CharField(max_length=1024)
    terminal = ManyToManyField(Terminal, backref='task')
    is_finished = BooleanField(default=False)
    date_created = DateTimeField(default=datetime.datetime.now)
    date_finished = DateTimeField(null=True)

class Command(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    user = CharField(max_length=64)
    asset = CharField(max_length=128)
    system_user = CharField(max_length=128)
    input = CharField(max_length=256)
    output = CharField(max_length=1024)
    session = CharField(max_length=36)
    timestamp = IntegerField()

Status_Terminal  = Status.terminal.get_through_model()
Session_Terminal = Session.terminal.get_through_model()
Task_Terminal = Task.terminal.get_through_model()