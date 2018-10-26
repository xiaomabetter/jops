# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf import csrf
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, PasswordField,DateTimeField,IntegerField,FileField,SelectMultipleField
from wtforms.widgets import CheckboxInput,TextInput,FileInput
from wtforms.validators import Length, Email, Regexp, DataRequired
from conf.config import Config

class Terminal_Form(FlaskForm):
    name = StringField(u'名称',[DataRequired()],widget=TextInput(),render_kw={"class":"form-control"})
    remote_addr = StringField(u'远端地址',render_kw={"class":"form-control"})
    command_storage = SelectField(u'命令存储',choices=[('default','default')],
                                  render_kw={"class":"form-control","width":"100px"})
    replay_storage = SelectField(u'录像存储',choices=[('default','default',)],
                                 render_kw={"class":"form-control","width":"100px"})
    comment = TextAreaField('备注',render_kw={"class":"form-control"})

    class Meta:
        csrf = True
        csrf_filed_name = 'csrf_token'
        csrf_secret = Config.SECRET_KEY