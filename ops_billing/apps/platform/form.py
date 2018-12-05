# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,SelectMultipleField,SelectField,BooleanField
from wtforms.widgets import TextInput,CheckboxInput
from wtforms.validators import DataRequired

class Platform_Form(FlaskForm):
    description = StringField('Descripion', [DataRequired(message=u'必须填写规则名称')],
                        widget=TextInput(), render_kw={"class": "form-control","placeholder":"填写平台描述"})
    platform_url = StringField(u'Platform_url',widget=TextInput(),
                               render_kw={"class":"form-control","placeholder":"填写平台的url"})
    catagory = SelectField('Catagory', choices=[],render_kw={"class": "form-control select2"})
    location = SelectField('Location', choices=[], render_kw={"class": "form-control select2"})
    isproxy = BooleanField(u'是否使用代理', widget=CheckboxInput(),
                                   render_kw={"class": "form-control"})
    proxyport = SelectField('Proxyport', choices=[], render_kw={"class": "form-control select2"})