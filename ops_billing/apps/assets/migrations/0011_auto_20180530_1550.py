# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-30 07:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0010_auto_20180530_1549'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asset',
            old_name='instanceId',
            new_name='instanceid',
        ),
    ]
