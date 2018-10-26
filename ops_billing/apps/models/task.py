# -*- coding: utf-8 -*-
from peewee import CharField,UUIDField,DateTimeField
import os,uuid,datetime,json
from .base import BaseModel

class Tasks(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    taskname = CharField(max_length=32,unique=True,null=False)
    comment = CharField(max_length=600)

class Sync_Bill_History(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    username = CharField(max_length=32)
    day = DateTimeField(null=False)
    filename = CharField(max_length=256,null=False)

    def __str__(self):
        return '{0.username}({0.day})'.format(self)