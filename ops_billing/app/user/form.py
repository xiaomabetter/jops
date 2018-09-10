# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,PasswordField,SelectMultipleField
from wtforms.widgets import TextInput
from wtforms.validators import DataRequired
from wtforms.csrf.core import CSRF
from hashlib import md5
from flask import request
from app.models import Groups

class User_Base_Form(FlaskForm):
    username = StringField(u'用户名',[DataRequired()],widget=TextInput(),
                           render_kw={"class":"form-control","placeholder":"用户名"})
    email = StringField(u'邮箱',widget=TextInput(),
                        render_kw={"class":"form-control","placeholder":"邮箱"})
    public_key = TextAreaField('ssh公钥', render_kw={"class": "form-control","placeholder":"粘贴你的ssh公钥"})
    password = PasswordField(u'密码',widget=TextInput(),
                             render_kw={"class":"form-control",'type':'password',"autocomplete":"off",
                                        "placeholder":"请填写你的密码"})
    phone = StringField('手机',render_kw={"class":"form-control"})
    wechat = StringField('微信',render_kw={"class": "form-control"})
    ding = StringField('钉钉', render_kw={"class": "form-control"})
    comment = TextAreaField('备注',render_kw={"class":"form-control"})


class User_Update_Form(User_Base_Form):
    group_list = [(ug.id,ug.value) for ug in Groups.select()]
    ROLE_CHOICES = [('administrator', 'administrator'),('user', 'user')]
    groups = SelectMultipleField(u'用户组',choices=group_list,
                                            render_kw={"class":"form-control select2",
                                                    "multiple":"multiple","data-placeholder":"选择用户组"})
    role = SelectMultipleField(u'角色',choices=ROLE_CHOICES,
                                            render_kw={"class":"form-control select2",
                                                    "multiple":"multiple","data-placeholder":"角色"})

class Groups_Form(FlaskForm):
    groupname = StringField(u'用户名',[DataRequired()],
                           widget=TextInput(),render_kw={"class":"form-control","placeholder":"组名称"})
    description = TextAreaField('描述',render_kw={"class":"form-control","rows": 6,"placeholder":"描述"})
