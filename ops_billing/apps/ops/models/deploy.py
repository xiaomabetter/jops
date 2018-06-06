# ~*~ coding: utf-8 ~*~
import json
import uuid
import os
import time
import datetime

from celery import current_task
from django.db import models
from django.conf import settings
from django.utils import timezone
from ..ansible import AdHocRunner, AnsibleError
from assets.models import Asset

class Deploy(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    module = models.CharField(max_length=128, null=False)
    cmd = models.CharField(max_length=128,null=False)
    hosts = models.TextField(blank=True,null=True)  # ['hostname1', 'hostname2']
    date_start = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(blank=True, null=True)
    timedelta = models.FloatField(default=0.0,null=True)
    is_success = models.BooleanField(default=False)
    result = models.TextField(blank=True, null=True)