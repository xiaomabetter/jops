# -*- coding: utf-8 -*-
#
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Task,RuncmdHistory
from common.utils import get_logger
from assets.models import Node

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

class RuncmdForm(forms.ModelForm):
    class Meta:
        model = RuncmdHistory
        fields = [
            'module','cmd','hosts','nodes','result'
        ]
        '''
        widgets = {
            'nodes': forms.SelectMultiple(
                choices=tuple(N),
                attrs={
                'class': 'select2', 'data-placeholder': 'Nodes'
            })
        }
        '''

        help_texts = {
            'module': '* required',
            'cmd': '* required'
        }
