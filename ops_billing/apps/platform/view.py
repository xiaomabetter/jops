from flask import render_template,request,flash
from . import platform
from apps.auth import login_required
from .form import Platform_Form
from apps.models.platform import Platforms
from peewee import fn
import json

@platform.route('/platforms/list',methods=['GET'])
@login_required
def platform_list():
    return render_template('platform/platform_list.html')

@platform.route('/platforms/update/<platformid>',methods=['GET'])
@login_required
def platform_update(platformid):
    form = Platform_Form(request.form)
    platform = Platforms.select().where(Platforms.id == platformid).get()
    form.catagory.choices = [("kefu_monitor",u"客服监控"),("kefu",u"客服系统")]
    form.location.choices = [("beijing",u"北京"),("hangzhou",u"杭州")]
    form.platform_url.data = platform.platform_url
    form.description.data = platform.description
    form.catagory.data = platform.catagory
    form.location.data = platform.location
    return render_template('platform/platform_update.html',form=form,platformid=platformid)