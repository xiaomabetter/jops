# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.conf import settings
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from common.mixins import DatetimeSearchMixin
from django.forms.models import model_to_dict
from django.db.models import Count,Sum
from ..models import Ecs,Rds,Slb,NodeSlb,Node,NodeRds

__all__ = (
    "BillEcsListView,BillSlbListView,BillRdsListView"
)

class BillSlbListView(LoginRequiredMixin,DatetimeSearchMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    model = Slb
    ordering = ('-day',)
    context_object_name = 'task_list'
    template_name = 'assets/bill_slb_list.html'
    keyword = ''

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.keyword = self.request.GET.get('keyword', '')
        self.nodeid = self.request.GET.get('nodeid', '')
        self.queryset = self.queryset.filter(
            day__gt=self.date_from,
            day__lt=self.date_to,
        )
        if self.nodeid:
            son = NodeSlb.objects.filter(id=self.nodeid).first()
            slbs = son.get_all_assets()
            q = [slb.instanceid for slb in slbs]
            self.queryset = self.queryset.filter(instanceid__in=q)

        if self.keyword:
            self.queryset = self.queryset.filter(
                instancename__icontains=self.keyword,
            )
        return self.queryset

    def get_context_data(self, **kwargs):
        nodeid = self.request.GET.get('nodeid', '')
        if nodeid:
            node = NodeSlb.objects.filter(id=nodeid).first()
            nodegroup = node.full_value
        else:
            nodegroup = ''
        sumcost = self.queryset.aggregate(cost=Sum('cost'))
        if not sumcost['cost']:
            sumcost['cost'] = 0
        context = {
            'app': _('Ops'),
            'action': "费用记录",
            'date_from': self.date_from,
            'date_to': self.date_to,
            'nodegroup':nodegroup,
            'sumcost': round(sumcost['cost'], 3),
            'asset_category': 'Slb',
            'keyword': self.keyword,
            'nodes': NodeSlb.objects.all().order_by('-key'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class BillEcsListView(DatetimeSearchMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    model = Ecs
    ordering = ('-day',)
    context_object_name = 'task_list'
    template_name = 'assets/bill_ecs_list.html'
    keyword = ''

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.keyword = self.request.GET.get('keyword', '')
        self.nodeid = self.request.GET.get('nodeid', '')
        self.queryset = self.queryset.filter(
            day__gt=self.date_from,
            day__lt=self.date_to,
        )

        if self.nodeid:
            son = Node.objects.filter(id=self.nodeid).first()
            ecs = son.get_all_assets()
            q = [ecs.instanceid for ecs in ecs]
            self.queryset = self.queryset.filter(instanceid__in=q)

        if self.keyword:
            self.queryset = self.queryset.filter(
                instancename__icontains=self.keyword,
            )
        return self.queryset

    def get_context_data(self, **kwargs):
        nodeid = self.request.GET.get('nodeid', '')
        if nodeid:
            nodegroup = Node.objects.filter(id=nodeid).first().full_value
        else:
            nodegroup = ''
        sumcost = self.queryset.aggregate(cost=Sum('cost'))
        if not sumcost['cost']:
            sumcost['cost'] = 0
        context = {
            'app': _('Ops'),
            'action': "费用记录",
            'date_from': self.date_from,
            'date_to': self.date_to,
            'nodegroup':nodegroup,
            'sumcost': round(sumcost['cost'],3),
            'keyword': self.keyword,
            'asset_category': 'Ecs',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class BillRdsListView(DatetimeSearchMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    model = Rds
    ordering = ('-day',)
    context_object_name = 'task_list'
    template_name = 'assets/bill_rds_list.html'
    keyword = ''

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.keyword = self.request.GET.get('keyword', '')
        self.nodeid = self.request.GET.get('nodeid', '')
        self.queryset = self.queryset.filter(
            day__gt=self.date_from,
            day__lt=self.date_to,
        )
        if self.nodeid:
            if self.nodeid:
                son = NodeRds.objects.filter(id=self.nodeid).first()
                rds = son.get_all_assets()
                q = [rds.DBInstanceId for rds in rds]
                self.queryset = self.queryset.filter(instanceid__in=q)

        if self.keyword:
            self.queryset = self.queryset.filter(
                instancename__icontains=self.keyword,
            )
        return self.queryset

    def get_context_data(self, **kwargs):
        nodeid = self.request.GET.get('nodeid', '')
        if nodeid:
            node = NodeRds.objects.filter(id=nodeid).first()
            print(node)
            nodegroup = node.full_value
        else:
            nodegroup = ''
        sumcost = self.queryset.aggregate(cost=Sum('cost'))
        if not sumcost['cost']:
            sumcost['cost'] = 0
        context = {
            'app': _('Ops'),
            'action': _('Task list'),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'sumcost': round(sumcost['cost'], 3),
            'keyword': self.keyword,
            'nodegroup':nodegroup,
            'asset_category': 'Rds',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)