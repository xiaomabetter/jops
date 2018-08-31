# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf import csrf
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, PasswordField,DateTimeField,IntegerField,FileField,SelectMultipleField
from wtforms.widgets import CheckboxInput,TextInput,FileInput
from wtforms.validators import Length, Email, Regexp, DataRequired
from conf.config import Config
from app.models import SystemUser
from app.models import User,Groups
from app.models import Asset,Node
from datetime import datetime

class Perm_Base_Form(FlaskForm):
    name = StringField(u'名称', [DataRequired(message=u'必须填写规则名称')],
                            widget=TextInput(), render_kw={"class": "form-control","placeholder":"填写规则名称"})
    is_active = BooleanField(u'激活中', widget=CheckboxInput(), render_kw={"class": "form-control", 'checked': 'true'})
    date_start = DateTimeField('date_start', default=datetime.now().strftime('%Y-%m-%d'))
    date_expired = DateTimeField('date_expired')
    comment = TextAreaField('备注', render_kw={"class": "form-control"})

class Perm_Create_Form(Perm_Base_Form):
    assets_choices = []
    nodes_choices = [(node.id.hex,node.full_value) for node in Node.select()]
    systemusers_choices = [(sysuser.id.hex,sysuser.username) for sysuser in SystemUser.select()]
    users_choices = [(user.id.hex,user.email) for user in User.select()]
    groups_choices = [(group.id.hex, group.groupname) for group in Groups.select()]
    users = SelectMultipleField(u'用户',choices=users_choices,render_kw={"class":"form-control select2","multiple":"multiple",
                                           "data-placeholder":"选择用户"})
    groups = SelectMultipleField(u'用户组',choices=groups_choices,render_kw={"class":"form-control select2","multiple":"multiple",
                                           "data-placeholder":"选择用户组"})
    assets = SelectMultipleField(u'资产',choices=assets_choices,render_kw={"class":"form-control select2",
                                            "multiple":"multiple","data-placeholder":"选择资产"})
    nodes = SelectMultipleField(u'节点',choices=nodes_choices,render_kw={"class":"form-control select2",
                                           "multiple":"multiple","data-placeholder":"选择节点"})
    system_users = SelectMultipleField(u'系统用户', choices=systemusers_choices,validators=[DataRequired()],
                                       render_kw={"class": "form-control select2",
                                           "multiple": "multiple","data-placeholder":"系统用户"})


class Systemuser_Create_Form(FlaskForm):
    protocol_choices = [('ssh','ssh'),('rdp','rdp')]
    #name = StringField(u'名称',[DataRequired()],widget=TextInput(),render_kw={"class":"form-control"})
    username = StringField(u'用户名',[DataRequired()],widget=TextInput(),render_kw={"class":"form-control"})
    priority = IntegerField(u'优先级',widget=TextInput(),default=1,render_kw={"class":"form-control"})
    protocol = SelectField(u'协议',choices=protocol_choices,default='ssh',render_kw={"class":"form-control"})
    auto_generate_key = BooleanField(u'自动生成密钥',widget=CheckboxInput(),render_kw={"class":"form-control",'checked':'true'})
    private_key = FileField(u'ssh密钥',widget=FileInput(),render_kw={"class":"form-control",'checked':'true'})
    password = PasswordField(u'密码',widget=TextInput(),render_kw={"class":"form-control",'type':'password'})
    auto_push = BooleanField(u'自动推送', widget=CheckboxInput(),render_kw={"class":"form-control",'checked':'true'})
    sudo = TextAreaField('Sudo',render_kw={"class":"form-control"})
    shell = StringField('Shell',default='/bin/bash',render_kw={"class":"form-control"})
    comment = StringField('备注',render_kw={"class":"form-control"})