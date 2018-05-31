# ~*~ coding: utf-8 ~*~
import uuid
import os,json

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework import viewsets, generics
from rest_framework.views import Response

from .hands import IsSuperUser
from .models import Task, AdHoc, AdHocRunHistory, CeleryTask,RuncmdHistory
from .serializers import TaskSerializer, AdHocSerializer, \
    AdHocRunHistorySerializer,RuncmdSerializer
from .tasks import run_ansible_task,run_cmd_task

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsSuperUser,)

class RuncmdViewSet(viewsets.ModelViewSet):
    queryset = RuncmdHistory.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsSuperUser,)

class TaskRun(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskViewSet
    permission_classes = (IsSuperUser,)

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        t = run_ansible_task.delay(str(task.id))
        return Response({"task": t.id})

class Runcmd(generics.RetrieveAPIView):
    queryset = RuncmdHistory.objects.all()
    serializer_class = RuncmdSerializer
    permission_classes = (IsSuperUser,)

    def retrieve(self, request, *args, **kwargs):
        for i in self.request.query_params:
            body = json.loads(i)
        module = body.get('module')
        cmd = body.get('cmd')
        hosts = body.get('hosts')
        hostname_list = hosts.split(',')
        nodes = body.get('nodes')
        tasks = [{"name": cmd, "action": {"module": module}}]
        t = run_cmd_task.delay(tasks,hostname_list)
        return Response({"task":t.id})

class AdHocViewSet(viewsets.ModelViewSet):
    queryset = AdHoc.objects.all()
    serializer_class = AdHocSerializer
    permission_classes = (IsSuperUser,)

    def get_queryset(self):
        task_id = self.request.query_params.get('task')
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            self.queryset = self.queryset.filter(task=task)
        return self.queryset


class AdHocRunHistorySet(viewsets.ModelViewSet):
    queryset = AdHocRunHistory.objects.all()
    serializer_class = AdHocRunHistorySerializer
    permission_classes = (IsSuperUser,)

    def get_queryset(self):
        task_id = self.request.query_params.get('task')
        adhoc_id = self.request.query_params.get('adhoc')
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            adhocs = task.adhoc.all()
            self.queryset = self.queryset.filter(adhoc__in=adhocs)

        if adhoc_id:
            adhoc = get_object_or_404(AdHoc, id=adhoc_id)
            self.queryset = self.queryset.filter(adhoc=adhoc)
        return self.queryset


class CeleryTaskLogApi(generics.RetrieveAPIView):
    permission_classes = (IsSuperUser,)
    buff_size = 1024 * 10
    end = False
    queryset = CeleryTask.objects.all()

    def get(self, request, *args, **kwargs):
        mark = request.query_params.get("mark") or str(uuid.uuid4())
        task = super().get_object()
        log_path = task.full_log_path

        if not log_path or not os.path.isfile(log_path):
            return Response({"data": _("Waiting ...")}, status=203)

        with open(log_path, 'r') as f:
            offset = cache.get(mark, 0)
            f.seek(offset)
            data = f.read(self.buff_size).replace('\n', '\r\n')
            mark = str(uuid.uuid4())
            cache.set(mark, f.tell(), 5)

            if data == '' and task.is_finished():
                self.end = True
            return Response({"data": data, 'end': self.end, 'mark': mark})

