# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,SelectMultipleField,SelectField,\
                BooleanField,TextAreaField
from wtforms.widgets import CheckboxInput,TextInput,FileInput
from wtforms.validators import Length, Email, Regexp, DataRequired
from app.models import SystemUser

class Task_Ansible_Form(FlaskForm):
    assets_choices = []
    systemusers_choices = [(sysuser.id, sysuser.username) for sysuser in SystemUser.select()]
    module_choices = [(module,module) for module in ['shell','command']]
    playbook_choices = [('test.yml','test.yml'),('initserver.yml','initserver.yml')]
    name = StringField(u'任务名称', [DataRequired(message=u'task 名称')],
                            widget=TextInput(), render_kw={"class": "form-control",
                                                           "autocomplete":"off","placeholder":"task 名称"})
    assets = SelectMultipleField(u'目标资产', choices=assets_choices, render_kw={"class": "form-control select2",
                                                    "multiple": "multiple","data-placeholder": "选择资产"})
    ismodule = BooleanField(u'模块运行',widget=CheckboxInput(),render_kw={"class":"form-control",
                                                                        'checked':'true'})
    module = SelectField(u'模块', choices=module_choices, render_kw={"class": "form-control select2",
                                                    "data-placeholder": "选择Ansible模块"})
    command = StringField(u'命令', widget=TextInput(),
                         render_kw={"class": "form-control","autocomplete":"off","placeholder":"命令"})
    playbook = SelectField(u'运行剧本', choices=playbook_choices, validators=[DataRequired()],
                         render_kw={"class": "form-control select2"})
    run_as = SelectField(u'系统用户', choices=systemusers_choices, validators=[DataRequired()],
                                       render_kw={"class": "form-control select2"})
    run_as_sudo = BooleanField(u'sudo执行', widget=CheckboxInput(),render_kw={"class":"form-control",'checked':'true'})

class Task_Create_Form(FlaskForm):
    taskname = StringField(u'任务名称', [DataRequired(message=u'任务名称')],widget=TextInput(),
                           render_kw={"class": "form-control","placeholder":"任务名称"})
    comment = TextAreaField('备注', render_kw={"class": "form-control"})


class Syncbill_Form(FlaskForm):
    asset_types = [(t,t) for t in ('ecs','slb','rds','redis','oss')]
    task_name = StringField(u'任务名称', render_kw={"class": "form-control", "placeholder": "任务名称"})
    day_from = StringField(u'开始时间',render_kw={"class": "form-control","placeholder":"开始时间"})
    day_to = StringField(u'结束时间', render_kw={"class": "form-control","placeholder":"结束时间"})
    asset_type = SelectField(u'资产类型', choices=asset_types, validators=[DataRequired()],
                             render_kw={"class": "form-control select2","data-placeholder": "资产类型"})