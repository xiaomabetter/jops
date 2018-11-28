from flask import render_template,request,flash
from . import platform
from apps.auth import login_required
from .form import Platform_Form
from apps.models.platform import Platforms,Catagory

@platform.route('/platforms/list',methods=['GET'])
@login_required(administrator=False)
def platform_list():
    catagorys =  [p.description for p in Catagory.select()]
    return render_template('platform/platform_list.html',**locals())

@platform.route('/platforms/update/<platformid>',methods=['GET'])
@login_required()
def platform_update(platformid):
    form = Platform_Form(request.form)
    platform = Platforms.select().where(Platforms.id == platformid).get()
    form.catagory.choices = [(p.description,p.description) for p in Catagory.select()]
    form.location.choices = [("beijing",u"北京"),("hangzhou",u"杭州")]
    form.platform_url.data = platform.platform_url
    form.description.data = platform.description
    form.catagory.data = platform.catagory
    form.location.data = platform.location
    return render_template('platform/platform_update.html',form=form,platformid=platformid)
