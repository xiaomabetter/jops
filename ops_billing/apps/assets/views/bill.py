# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.urls import reverse_lazy
from django.conf import settings
from django.views.generic import ListView, DetailView, TemplateView,CreateView
from django.views.generic import FormView
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from common.const import create_success_msg, update_success_msg
from common.mixins import DatetimeSearchMixin
from django.forms.models import model_to_dict
from django.db.models import Count,Sum
from ..models import Ecs,Rds,Slb,NodeSlb,Node

__all__ = (
    "BillEcsListView,BillSlbListView,BillRdsListView"
)

class BillSlbListView(LoginRequiredMixin,DatetimeSearchMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    model = Slb
    ordering = ('-day',)
    context_object_name = 'task_list'
    template_name = 'assets/bill_list.html'
    keyword = ''

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.keyword = self.request.GET.get('keyword', '')
        self.nodegroup = self.request.GET.get('nodegroup', '')
        self.queryset = self.queryset.filter(
            day__gt=self.date_from,
            day__lt=self.date_to,
        )
        if self.nodegroup:
            q  = []
            son = NodeSlb.objects.filter(value=self.nodegroup.lstrip()).first()
            slbs = son.get_all_assets()
            for slb in slbs:
                q.append(slb.instanceid)
            self.queryset = self.queryset.filter(instanceid__in=q)

        if self.keyword:
            self.queryset = self.queryset.filter(
                instancename__icontains=self.keyword,
            )
        return self.queryset

    def get_context_data(self, **kwargs):
        nodes = NodeSlb.objects.all().values('value')
        nodegroup = self.request.GET.get('nodegroup', '')
        sumcost = self.queryset.aggregate(cost=Sum('cost'))
        context = {
            'app': _('Ops'),
            'action': "费用记录",
            'date_from': self.date_from,
            'date_to': self.date_to,
            'nodes':nodes,
            'nodegroup':nodegroup,
            'sumcost': round(sumcost['cost'], 3),
            'keyword': self.keyword,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class BillEcsListView(DatetimeSearchMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    model = Ecs
    ordering = ('-day',)
    context_object_name = 'task_list'
    template_name = 'assets/bill_list.html'
    keyword = ''

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.keyword = self.request.GET.get('keyword', '')
        self.nodegroup = self.request.GET.get('nodegroup', '')
        self.queryset = self.queryset.filter(
            day__gt=self.date_from,
            day__lt=self.date_to,
        )

        if self.nodegroup:
            q  = []
            son = Node.objects.filter(value=self.nodegroup.lstrip()).first()
            slbs = son.get_all_assets()
            for slb in slbs:
                q.append(slb.instanceid)
            self.queryset = self.queryset.filter(instanceid__in=q)

        if self.keyword:
            self.queryset = self.queryset.filter(
                instancename__icontains=self.keyword,
            )
        return self.queryset

    def get_context_data(self, **kwargs):
        nodes = Node.objects.all().values('value')
        nodegroup = self.request.GET.get('nodegroup', '')
        sumcost = self.queryset.aggregate(cost=Sum('cost'))
        if not sumcost['cost']:
            sumcost['cost'] = 0
        context = {
            'app': _('Ops'),
            'action': "资产列表",
            'date_from': self.date_from,
            'date_to': self.date_to,
            'nodes':nodes,
            'nodegroup':nodegroup,
            'sumcost': round(sumcost['cost'],3),
            'keyword': self.keyword,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class BillRdsListView(DatetimeSearchMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    model = Rds
    ordering = ('-day',)
    context_object_name = 'task_list'
    template_name = 'assets/bill_list.html'
    keyword = ''

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.keyword = self.request.GET.get('keyword', '')
        self.nodegroup = self.request.GET.get('nodegroup', '')
        self.queryset = self.queryset.filter(
            day__gt=self.date_from,
            day__lt=self.date_to,
        )
        if self.nodegroup:
            if '/' in self.nodegroup:
                q  = []
                son = NodeSlb.objects.filter(value=self.nodegroup.split('/')[1].lstrip()).first()
                slbs = son.get_all_assets()
                for slb in slbs:
                    q.append(slb.instanceid)
                self.queryset = self.queryset.filter(instanceid__in=q)

        if self.keyword:
            self.queryset = self.queryset.filter(
                instancename__icontains=self.keyword,
            )
        return self.queryset

    def get_context_data(self, **kwargs):
        N = []
        nodes = NodeSlb.objects.all()
        for node in nodes:
            N.append(node)
        context = {
            'app': _('Ops'),
            'action': _('Task list'),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'nodes':N,
            'keyword': self.keyword,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)