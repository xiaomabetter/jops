from flask import render_template, redirect,request,make_response,url_for
from app.models import User,User_Group,Groups
from . import user
from app.auth import Auth
from .form import User_Update_Form,Groups_Form
from app.utils import dict_to_form,model_to_form
from conf.config import Config
from app.auth import login_required
import time

@user.route('/user/login',methods=['GET','POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('user/login_user.html')
    elif request.method == 'POST':
        response = make_response(redirect(Config.SECURITY_LOGIN_URL))
        username = request.form.get('username',False)
        password = request.form.get('password',False)
        if username and password:
            try:
                user = User.select().where((User.email == username) |
                                           (User.username == username)).get()
            except Exception as e:
                print(e)
                return response
            if user and user.verify_password(password) and user.is_active==1:
                success = make_response(redirect(url_for('asset.asset_list',asset_type='ecs')))
                token = Auth.encode_auth_token(user.id.hex,int(time.time()))
                success.set_cookie('access_token',token)
                return success
            else:
                return response
        else:
            return response

@user.route('/user/logout',methods=['GET','POST'])
@login_required
def auth_logout():
    response = make_response(redirect(Config.SECURITY_LOGIN_URL))
    r = response.delete_cookie("access_token")
    return response

@user.route('/user/users/list',methods=['GET','POST'])
@login_required
def users_list():
    return render_template('user/user_list.html')

@user.route('/user/users/detail/<userid>',methods=['GET','POST'])
@login_required
def users_detail(userid):
    userid = userid
    user_object = User.select().where(User.id==userid).first()
    groups = Groups.select()
    ug_object = User.select().join(User_Group).join(Groups).where(User.id==userid).get()
    return render_template('user/user_detail.html',**locals())

@user.route('/user/users/create',methods=['GET','POST'])
@login_required
def users_create():
    form = User_Update_Form()
    return render_template('user/user_create.html', form=form)

@user.route('/user/users/update/<userid>',methods=['GET'])
@login_required
def users_update(userid):
    form = User_Update_Form()
    user = User.select().where(User.id == userid).get()
    dict_to_form(user.to_json(), form,exclude=['password'])
    return render_template('user/user_update.html',form=form,userid=userid)

@user.route('/user/groups/list',methods=['GET','POST'])
@login_required
def groups_list():
    return render_template('user/group_list.html')

@user.route('/user/groups/create',methods=['GET','POST'])
@login_required
def groups_create():
    action = u"创建用户组"
    form = Groups_Form(request.form)
    return render_template('user/user_group_create.html',**locals())

@user.route('/user/groups/update/<gid>',methods=['GET','POST'])
@login_required
def groups_update(gid):
    groupid = gid
    action = u"更新用户组"
    form = Groups_Form()
    group = Groups.select().where(Groups.id == gid)
    model_to_form(group,form)
    return render_template('user/user_group_update.html', **locals())

@user.route('/user/userlog/list',methods=['GET','POST'])
@login_required
def userlogin_log_list():
    return  redirect('/auth/login')
