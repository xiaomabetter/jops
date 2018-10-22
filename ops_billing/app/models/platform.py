# -*- coding: utf-8 -*-
from peewee import CharField,UUIDField,DateTimeField
import uuid,datetime
from .base import BaseModel

class Platforms(BaseModel):
    id = UUIDField(default=uuid.uuid4, primary_key=True)
    description = CharField(max_length=400,unique=True,null=False)
    platform_url = CharField(max_length=255,unique=True,null=False)
    catagory = CharField(max_length=255,null=False)
    location = CharField(max_length=255,null=False,default="hangzhou")
    date_created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'platform_platforms'