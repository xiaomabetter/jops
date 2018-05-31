# -*- coding: utf-8 -*-
#
from rest_framework import serializers
from rest_framework_bulk.serializers import BulkListSerializer

from common.mixins import BulkSerializerMixin
from ..models import Ecs,Slb,Rds
from .system_user import AssetSystemUserSerializer

__all__ = [
    'EcsSerializer'
]

class EcsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ecs
        fields = ("instanceid","instancename","cost")