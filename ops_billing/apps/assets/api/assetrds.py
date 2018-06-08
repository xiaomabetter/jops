# -*- coding: utf-8 -*-
#
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_bulk import BulkModelViewSet
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status

from common.mixins import IDInFilterMixin
from common.utils import get_logger
from ..hands import IsSuperUser, IsValidUser, IsSuperUserOrAppUser,NodePermissionUtil
from ..models import  AssetRds,NodeRds
from .. import serializers
import json

logger = get_logger(__file__)
__all__ = [
    'AssetRdsViewSet'
]

class AssetRdsViewSet(BulkModelViewSet):
    filter_fields = ("DBInstanceDescription", "ConnectionString")
    search_fields = filter_fields
    ordering_fields = ("ConnectionString", "ConnectionString")
    queryset = AssetRds.objects.all()
    serializer_class = serializers.AssetRdsSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsSuperUserOrAppUser,)

    def get_queryset(self):
        queryset = super().get_queryset()
        node_id = self.request.query_params.get("node_id")
        tonode = self.request.query_params.get('tonode')
        if tonode:
            queryset = queryset.filter(nodes=None)
        if node_id:
            node = get_object_or_404(NodeRds, id=node_id)
            if not node.is_root():
                queryset = queryset.filter(
                    nodes__key__regex='{}(:[0-9]+)*$'.format(node.key),
                ).distinct()
        return queryset

    def bulk_destroy(self, request, *args, **kwargs):
        del_ids = self.request.query_params.get('id__in')
        qs = self.get_queryset().filter(id__in=json.loads(del_ids))

        filtered = self.filter_queryset(qs)
        if not self.allow_bulk_destroy(qs, filtered):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        self.perform_bulk_destroy(filtered)

        return Response(status=status.HTTP_204_NO_CONTENT)