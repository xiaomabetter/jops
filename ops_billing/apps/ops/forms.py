# -*- coding: utf-8 -*-
#
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Task,Deploy
from common.utils import get_logger
from assets.models import Node,Asset

logger = get_logger(__file__)
__all__ = ['TaskCreateForm']


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'name','comment','created_by','task_type'
        ]
        help_texts = {
            'name': '* required',
            'comment': '* required',
            'created_by': '* required'
        }

class DeployForm(forms.ModelForm):
    hosts = forms.ModelMultipleChoiceField(
        queryset=Asset.objects.all(), required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'select2', 'data-placeholder': _('Select assets')}
        )
    )
    result = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Deploy
        fields = ['module', 'cmd', 'hosts','result']
