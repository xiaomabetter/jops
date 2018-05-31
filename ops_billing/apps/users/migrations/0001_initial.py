# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-29 07:03
from __future__ import unicode_literals

import common.utils
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=128, unique=True, verbose_name='Username')),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('email', models.EmailField(max_length=128, unique=True, verbose_name='Email')),
                ('role', models.CharField(blank=True, choices=[('Admin', 'Administrator'), ('User', 'User'), ('App', 'Application')], default='User', max_length=10, verbose_name='Role')),
                ('avatar', models.ImageField(null=True, upload_to='avatar', verbose_name='Avatar')),
                ('wechat', models.CharField(blank=True, max_length=128, verbose_name='Wechat')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone')),
                ('otp_level', models.SmallIntegerField(choices=[(0, 'Disable'), (1, 'Enable'), (2, 'Force enable')], default=0, verbose_name='MFA')),
                ('_otp_secret_key', models.CharField(blank=True, max_length=128, null=True)),
                ('_private_key', models.CharField(blank=True, max_length=5000, verbose_name='Private key')),
                ('_public_key', models.CharField(blank=True, max_length=5000, verbose_name='Public key')),
                ('comment', models.TextField(blank=True, max_length=200, verbose_name='Comment')),
                ('is_first_login', models.BooleanField(default=True)),
                ('date_expired', models.DateTimeField(blank=True, default=common.utils.date_expired_default, null=True, verbose_name='Date expired')),
                ('created_by', models.CharField(default='', max_length=30, verbose_name='Created by')),
            ],
            options={
                'verbose_name': 'User',
                'ordering': ['username'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AccessKey',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='AccessKeyID')),
                ('secret', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='AccessKeySecret')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_key', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='LoginLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=20, verbose_name='Username')),
                ('type', models.CharField(choices=[('W', 'Web'), ('T', 'Terminal')], max_length=2, verbose_name='Login type')),
                ('ip', models.GenericIPAddressField(verbose_name='Login ip')),
                ('city', models.CharField(blank=True, max_length=254, null=True, verbose_name='Login city')),
                ('user_agent', models.CharField(blank=True, max_length=254, null=True, verbose_name='User agent')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='Date login')),
            ],
            options={
                'ordering': ['-datetime', 'username'],
            },
        ),
        migrations.CreateModel(
            name='PrivateToken',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='Key')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='auth_token', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Private Token',
            },
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('is_discard', models.BooleanField(default=False, verbose_name='is discard')),
                ('discard_time', models.DateTimeField(blank=True, null=True, verbose_name='discard time')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('created_by', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'User group',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='users', to='users.UserGroup', verbose_name='User group'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
