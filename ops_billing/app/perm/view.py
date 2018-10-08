from app import get_logger
from flask import render_template,request,flash
from app.utils import model_to_form
from app.models import SystemUser,AssetPermission,User,Node,PermissionGroups
from .form import Perm_Create_Form,Systemuser_Create_Form,Perm_Groups_Form
from .serializer import AssetPermissionSerializer
from . import perm
from app.auth import login_required
import json

logger = get_logger(__name__)

@perm.route('/perm/permission_group/list',methods=['GET'])
@login_required
def permission_group_list():
    return render_template('perm/permission_group_list.html')

@perm.route('/perm/permission_group/create',methods=['GET','POST'])
@login_required
def permission_group_create():
    form = Perm_Groups_Form(request.form)
    form.users.choices = [(user.id.hex,user.username) for user in User.select()]
    return render_template('perm/permission_group_create.html',form=form)

@perm.route('/perm/permission_group/update/<pgid>',methods=['GET','POST'])
@login_required
def permission_group_update(pgid):
    pg = PermissionGroups.select().where(PermissionGroups.id == pgid)
    form = Perm_Groups_Form(request.form)
    model_to_form(pg,form)
    form.users.choices = [(user.id.hex, user.username) for user in User.select()]
    form.users.data = [user.id.hex for user in pg.get().users.objects()]
    return render_template('perm/permission_group_update.html',**locals())

@perm.route('/perm/systemuser/list',methods=['GET'])
@login_required
def system_user_list():
    return render_template('perm/system_user_list.html')

@perm.route('/perm/systemuser/create',methods=['GET','POST'])
@login_required
def system_user_create():
    form = Systemuser_Create_Form(request.form)
    return render_template('perm/system_user_create.html',form=form)

@perm.route('/perm/systemuser/update/<sysuserid>',methods=['GET','POST'])
@login_required
def system_user_update(sysuserid):
    sysuserid = sysuserid
    sysuser = SystemUser.select().where(SystemUser.id == sysuserid)
    form = Systemuser_Create_Form(request.form)
    model_to_form(sysuser,form)
    return render_template('perm/system_user_update.html',**locals())

@perm.route('/perm/asset_permission/list',methods=['GET'])
@login_required
def asset_permission_list():
    return render_template('perm/asset_permission_list.html')

@perm.route('/perm/asset_permission/create',methods=['GET','POST'])
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

@perm.route('/perm/asset_permission/update/<permissionid>',methods=['GET','POST'])
@login_required
def asset_permission_update(permissionid):
    template_name = 'perm/asset_permission_update.html'
    form = Perm_Create_Form(request.form)
    form.nodes.choices = [(node.id.hex,node.full_value) for node in Node.select()]
    form.system_users.choices = [(sysuser.id.hex,sysuser.username) for sysuser in SystemUser.select()]
    form.users.choices = [(user.id.hex,user.username) for user in User.select()]
    form.groups.choices = [(group.id.hex, group.name) for group in PermissionGroups.select()]
    asset_perm = AssetPermission.select().where(AssetPermission.id == permissionid).get()
    perm_data = json.loads(AssetPermissionSerializer().dumps(asset_perm).data)
    return render_template(template_name, **locals())