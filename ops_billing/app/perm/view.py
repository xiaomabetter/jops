from app import get_logger, get_config
from flask import render_template,request,flash
from app.utils import model_to_form
from app.models import SystemUser,AssetPermission
from .form import Perm_Create_Form,Systemuser_Create_Form
from .serializer import AssetPermissionSerializer
from . import perm
from app.auth import login_required
import json

logger = get_logger(__name__)
cfg = get_config()

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

@perm.route('/perm/permission-create',methods=['GET','POST'])
@login_required
def asset_permission_create():
    template_name = 'perm/asset_permission_create.html'
    form = Perm_Create_Form(request.form)
    node_id = request.args.get('nodes')
    form.nodes.data = [node_id]
    return render_template(template_name,form=form)

@perm.route('/perm/permission-update/<permissionid>',methods=['GET','POST'])
@login_required
def asset_permission_update(permissionid):
    template_name = 'perm/asset_permission_update.html'
    form = Perm_Create_Form(request.form)
    asset_perm = AssetPermission.select().where(AssetPermission.id == permissionid).get()
    perm_data = json.loads(AssetPermissionSerializer().dumps(asset_perm).data)
    return render_template(template_name, **locals())