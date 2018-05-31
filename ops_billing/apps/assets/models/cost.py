#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

import uuid

from django.db import models
import logging
from django.utils.translation import ugettext_lazy as _
#from assets.models import Asset

__all__ = ['Ecs','Rds','Slb']
logger = logging.getLogger(__name__)


class Ecs(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    instancename = models.CharField(max_length=64,null=False)
    instanceid = models.CharField(max_length=64,null=False)
    day = models.DateTimeField(null=False)
    cost = models.FloatField(max_length=64)
    ecsinfo = models.ManyToManyField('assets.Asset', default='', null=True, related_name='ecsinfo')

class Rds(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    instancename = models.CharField(max_length=64,null=False)
    instanceid = models.CharField(max_length=64,null=False)
    day = models.DateTimeField(null=False)
    cost = models.FloatField(max_length=64)

class Slb(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    instancename = models.CharField(max_length=64,null=False)
    #instanceid = models.ForeignKey("assets.AssetSlb", null=True, blank=True, related_name='slb')
    instanceid = models.CharField(max_length=64, null=False)
    day = models.DateTimeField(null=False)
    cost = models.FloatField(max_length=64)
    slbinfo = models.ManyToManyField('assets.AssetSlb', default='', null=True, related_name='slbinfo')

