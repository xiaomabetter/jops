from flask import render_template,request,flash
from apps.utils import model_to_form
from apps.models import SystemUser,AssetPermission,User,Node,PermissionGroups,Platforms,PermissionPlatform
from .form import Perm_Create_Form,Systemuser_Create_Form,Perm_Groups_Form,Perm_Platform_Create_Form
from .serializer import AssetPermissionSerializer,AuthorizationPlatformSerializer
from . import perm
from apps.auth import login_required
import datetime
import json

@perm.route('/group/list',methods=['GET'])
@login_required
def permission_group_list():
    return render_template('perm/permission_group_list.html')

@perm.route('/group/create',methods=['GET','POST'])
@login_required
def permission_group_create():
    form = Perm_Groups_Form(request.form)
    form.users.choices = [(user.id.hex,user.username) for user in User.select()]
    return render_template('perm/permission_group_create.html',form=form)

@perm.route('/group/update/<pgid>',methods=['GET','POST'])
@login_required
def permission_group_update(pgid):
    pg = PermissionGroups.select().where(PermissionGroups.id == pgid)
    form = Perm_Groups_Form(request.form)
    model_to_form(pg,form)
    form.users.choices = [(user.id.hex, user.username) for user in User.select()]
    form.users.data = [user.id.hex for user in pg.get().users.objects()]
    return render_template('perm/permission_group_update.html',**locals())

@perm.route('/systemuser/list',methods=['GET'])
@login_required
def system_user_list():
    return render_template('perm/system_user_list.html')

@perm.route('/systemuser/create',methods=['GET','POST'])
@login_required
def system_user_create():
    form = Systemuser_Create_Form(request.form)
    return render_template('perm/system_user_create.html',form=form)

@perm.route('/systemuser/update/<sysuserid>',methods=['GET','POST'])
@login_required
def system_user_update(sysuserid):
    sysuserid = sysuserid
    sysuser = SystemUser.select().where(SystemUser.id == sysuserid)
    form = Systemuser_Create_Form(request.form)
    model_to_form(sysuser,form)
    return render_template('perm/system_user_update.html',**locals())

@perm.route('/asset/list',methods=['GET'])
@login_required
def asset_permission_list():
    return render_template('perm/asset_permission_list.html')

@perm.route('/asset/create',methods=['GET','POST'])
@login_required
def asset_permission_create():
    template_name = 'perm/asset_permission_create.html'
    form = Perm_Create_Form(request.form)
    node_id = request.args.get('nodes')
    form.nodes.data = [node_id]
    form.nodes.choices = [(node.id.hex,node.full_value) for node in Node.select()]
    form.system_users.choices = [(sysuser.id.hex,sysuser.username) for sysuser in SystemUser.select()]
    form.users.choices = [(user.id.hex,user.username) for user in User.select()]
    form.groups.choices = [(group.id.hex, group.name) for group in PermissionGroups.select()]
    return render_template(template_name,form=form)

@perm.route('/asset/update/<permissionid>',methods=['GET','POST'])
@login_required
def asset_permission_update(permissionid):
    template_name = 'perm/asset_permission_update.html'
    form = Perm_Create_Form(request.form)
    form.nodes.choices = [(node.id.hex,node.full_value) for node in Node.select()]
    form.system_users.choices = [(sysuser.id.hex,sysuser.username) for sysuser in SystemUser.select()]
    form.users.choices = [(user.id.hex,user.username) for user in User.select()]
    form.groups.choices = [(group.id.hex, group.name) for group in PermissionGroups.select()]
    form.date_start.data = datetime.datetime.now()
    asset_perm = AssetPermission.select().where(AssetPermission.id == permissionid).get()
    perm_data = json.loads(AssetPermissionSerializer().dumps(asset_perm).data)
    return render_template(template_name, **locals())

@perm.route('/platform/list',methods=['GET'])
@login_required
def platform_list():
    return render_template('perm/platform_permission_list.html')

@perm.route('/platform/create',methods=['GET','POST'])
@login_required
def platform_permission_create():
    template_name = 'perm/platform_permission_create.html'
    form = Perm_Platform_Create_Form(request.form)
    form.platform_urls.choices = [(platform.id.hex,platform.description) for platform in Platforms.select()]
    form.users.choices = [(user.id.hex,user.username) for user in User.select()]
    form.groups.choices = [(group.id.hex, group.name) for group in PermissionGroups.select()]
    return render_template(template_name,form=form)

@perm.route('/platform/update/<permissionid>',methods=['GET','POST'])
@login_required
def platform_permission_update(permissionid):
    template_name = 'perm/platform_permission_update.html'
    form = Perm_Platform_Create_Form(request.form)
    form.platform_urls.choices = [(platform.id.hex,platform.description) for platform in Platforms.select()]
    form.users.choices = [(user.id.hex,user.username) for user in User.select()]
    form.groups.choices = [(group.id.hex, group.name) for group in PermissionGroups.select()]
    platform_perm= PermissionPlatform.select().where(PermissionPlatform.id == permissionid).get()
    form.name.data = platform_perm.name
    form.platform_urls.data = [platform_url.id.hex for platform_url in platform_perm.platform_urls.objects()]
    form.groups.data = [group.id.hex for group in platform_perm.groups.objects() if platform_perm.groups]
    form.users.data = [user.id.hex for user in platform_perm.users.objects() if platform_perm.users]
    return render_template(template_name,form=form,permissionid=permissionid)