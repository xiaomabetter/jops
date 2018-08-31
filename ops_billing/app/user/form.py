# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf import csrf
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, PasswordField,DateTimeField,IntegerField,FileField,SelectMultipleField
from wtforms.widgets import CheckboxInput,TextInput,FileInput
from wtforms.validators import Length, Email, Regexp, DataRequired
from wtforms.csrf.core import CSRF
from hashlib import md5
from flask import request
from conf.config import Config
from app.models import User,Groups

class MyCSRF(CSRF):
    def setup_form(self, form):
        self.csrf_context = form.meta.csrf_context()
        self.csrf_secret = form.meta.csrf_secret
        return super(MyCSRF, self).setup_form(form)

    def generate_csrf_token(self, csrf_token):
        gid = self.csrf_secret + self.csrf_context
        token = md5(gid.encode('utf-8')).hexdigest()
        return token

    def validate_csrf_token(self, form, field):
        print(field.data, field.current_token)
        if field.data != field.current_token:
            raise ValueError('Invalid CSRF')

class User_Base_Form(FlaskForm):
    username = StringField(u'用户名',[DataRequired()],widget=TextInput(),
                           render_kw={"class":"form-control","placeholder":"用户名"})
    email = StringField(u'邮箱',widget=TextInput(),
                        render_kw={"class":"form-control","placeholder":"邮箱"})
    public_key = TextAreaField('ssh公钥', render_kw={"class": "form-control","placeholder":"粘贴你的ssh公钥"})
    password = PasswordField(u'密码',widget=TextInput(),
                             render_kw={"class":"form-control",'type':'password',"autocomplete":"off","placeholder":"密码，不填写默认邮件发送"})
    phone = StringField('手机',render_kw={"class":"form-control"})
    wechat = StringField('微信',render_kw={"class": "form-control"})
    ding = StringField('钉钉', render_kw={"class": "form-control"})
    comment = TextAreaField('备注',render_kw={"class":"form-control"})

    class Meta:
        csrf = True
        csrf_filed_name = 'csrf_token'
        csrf_secret = Config.SECRET_KEY
        csrf_context = lambda x: request.url
        csrf_class = MyCSRF

class User_Update_Form(User_Base_Form):
    group_list = [(ug.id,ug.groupname) for ug in Groups.select()]
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

    class Meta:
        csrf = True
        csrf_filed_name = 'csrf_token'
        csrf_secret = Config.SECRET_KEY