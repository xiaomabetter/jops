# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-29 07:03
from __future__ import unicode_literals

import common.utils
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetPermission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('date_start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date start')),
                ('date_expired', models.DateTimeField(default=common.utils.date_expired_default, verbose_name='Date expired')),
                ('created_by', models.CharField(blank=True, max_length=128, verbose_name='Created by')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
            ],
        ),
        migrations.CreateModel(
            name='NodePermission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('date_expired', models.DateTimeField(default=common.utils.date_expired_default, verbose_name='Date expired')),
                ('created_by', models.CharField(blank=True, max_length=128, verbose_name='Created by')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.Node', verbose_name='Node')),
                ('system_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.SystemUser', verbose_name='System user')),
            ],
            options={
                'verbose_name': 'Asset permission',
            },
        ),
    ]
