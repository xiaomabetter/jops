# ~*~ coding: utf-8 ~*~
import uuid
import os,json

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework import viewsets, generics
from rest_framework.views import Response

from ..models import Ecs,Rds,Slb
from ..serializers import EcsSerializer
from ..tasks import bill_compute

class BillCompute(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        print(self.request)