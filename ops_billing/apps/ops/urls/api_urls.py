# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals

from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from .. import api

app_name = "ops"

router = DefaultRouter()
router.register(r'v1/tasks', api.TaskViewSet, 'task')
router.register(r'v1/adhoc', api.AdHocViewSet, 'adhoc')
router.register(r'v1/deploy', api.DeployViewSet, 'deploy')
router.register(r'v1/history', api.AdHocRunHistorySet, 'history')

urlpatterns = [
    url(r'^v1/tasks/(?P<pk>[0-9a-zA-Z\-]{36})/run/$', api.TaskRun.as_view(), name='task-run'),
    url(r'^v1/deploy/(?P<pk>[0-9a-zA-Z\-]{36})/run/$', api.DeployTaskApi.as_view(), name='task-run1'),
    url(r'^v1/celery/task/(?P<pk>[0-9a-zA-Z\-]{36})/log/$', api.CeleryTaskLogApi.as_view(), name='celery-task-log'),
]

urlpatterns += router.urls
