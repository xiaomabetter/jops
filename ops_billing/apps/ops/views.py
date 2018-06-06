# ~*~ coding: utf-8 ~*~

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
from .models import Task, AdHoc, AdHocRunHistory, CeleryTask, Deploy
from .hands import AdminUserRequiredMixin
from .forms import  TaskCreateForm,DeployForm
from .utils import update_or_create_ansible_task
from .tasks import run_sync_assets_task,run_sync_bill_task


class TaskListView(AdminUserRequiredMixin, DatetimeSearchMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    model = Task
    ordering = ('-date_created',)
    context_object_name = 'task_list'
    template_name = 'ops/task_list.html'
    keyword = ''

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.keyword = self.request.GET.get('keyword', '')
        self.queryset = self.queryset.filter(
            date_created__gt=self.date_from,
            date_created__lt=self.date_to
        )

        if self.keyword:
            self.queryset = self.queryset.filter(
                name__icontains=self.keyword,
            )
        return self.queryset

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': _('Task list'),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'keyword': self.keyword,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class TaskDeployView(AdminUserRequiredMixin, CreateView):
    model = Deploy
    template_name = 'ops/task_deploy.html'
    form_class = DeployForm
    success_url = reverse_lazy('ops:task-deploy')
    success_message = create_success_msg

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': '执行命令',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class TaskCustomView(AdminUserRequiredMixin,TemplateView):
    paginate_by = settings.DISPLAY_PER_PAGE
    template_name = 'ops/customtask_list.html'
    keyword = ''

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': '定制任务',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
    def get(self, request, *args, **kwargs):
        taskname = self.request.GET.get('taskname')
        if taskname == 'sync_bill':
            day_from  = self.request.GET.get('day_from')
            day_to = self.request.GET.get('day_to')
            if not day_from  or not day_to:
                print('nn')
            else:
                t = run_sync_bill_task.delay(day_from,day_to)
        if taskname == 'sync_asset':
            asset_category = self.request.GET.get('asset_category')
            if asset_category:
                r = run_sync_assets_task.delay(asset_category)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

'''
class TaskCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = 'ops/task_create.html'
    success_url = reverse_lazy('ops:task-create')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('ops'),
            'action': _('Create task'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return create_success_msg % ({"name": cleaned_data["name"]})
'''

class TaskDetailView(AdminUserRequiredMixin, DetailView):
    model = Task
    template_name = 'ops/task_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': _('Task detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class TaskAdhocView(AdminUserRequiredMixin, DetailView):
    model = Task
    template_name = 'ops/task_adhoc.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': _('Task versions'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class TaskHistoryView(AdminUserRequiredMixin, DetailView):
    model = Task
    template_name = 'ops/task_history.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': _('Task run history'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class AdHocDetailView(AdminUserRequiredMixin, DetailView):
    model = AdHoc
    template_name = 'ops/adhoc_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': 'Task version detail',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class AdHocHistoryView(AdminUserRequiredMixin, DetailView):
    model = AdHoc
    template_name = 'ops/adhoc_history.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': _('Version run history'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class AdHocHistoryDetailView(AdminUserRequiredMixin, DetailView):
    model = AdHocRunHistory
    template_name = 'ops/adhoc_history_detail.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': _('Run history detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CeleryTaskLogView(AdminUserRequiredMixin, DetailView):
    template_name = 'ops/celery_task_log.html'
    model = CeleryTask
