from flask import render_template,flash,redirect,request,make_response,url_for
from apps.models import User,User_Group,Groups,OpsRedis,UserLoginLog
from . import user
from apps.auth import Auth
from .form import User_Form,Groups_Form,User_Create_Form,Ldap_User_Form,Local_User_Form
from apps.utils import model_to_form,encryption_md5
from .ldapapi import ldapconn
from apps.auth import login_required
from apps import config
import time,json,datetime

@user.route('/login',methods=['GET','POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('user/login_user.html')
    else:
        response = make_response(redirect(config.get('DEFAULT','SECURITY_LOGIN_URL')))
        username = request.form.get('username',False)
        password = request.form.get('password',False)
        is_ldap_login = request.form.get('is_ldap_login',False)
        def redirectResponse(role):
            if role == 'user':
                return make_response(redirect(url_for('platform.platform_list')))
            else:
                return make_response(redirect("/"))

        if is_ldap_login:
            ldapuser = ldapconn.ldap_search_user(username)
            if not ldapuser:
                flash(message='ldapuser不存在',category='error')
                return response
            else:
                ldapuser = ldapuser[0]
            department = ldapuser['department'];ldapuser.pop('department')
            if password == ldapuser['password']:
                user = User.select().where(User.username == username).first()
                if not user:
                    ldapuser['password'] = encryption_md5(ldapuser['password'])
                    user = User.create(**ldapuser)
                group = Groups.select().where(Groups.value == department and Groups.is_ldap_group == True).first()
                if not group:
                    ROOT = Groups.root()
                    group = Groups.create(value=department, key=0, is_ldap_login = True)
                    group.parent = ROOT; group.save()
                    user.group.add(group.id)
                else:
                    user_group = user.group.select().where(Groups.value == department)
                    if user_group.count() == 0:user.group.add(group.id)
                success = redirectResponse(user.role)
                OpsRedis.set(user.id.hex,json.dumps(user.to_json()))
                remote_addr = request.headers.get('X-Forwarded-For') or request.remote_addr
                UserLoginLog.create(username=user.username,login_at=datetime.datetime.now(),login_ip=remote_addr)
                token = Auth.encode_auth_token(user_id=user.id.hex,password=user.password)
                token = token.decode() if isinstance(token, bytes) else token
                success.set_cookie('access_token', token,max_age=int(config.get('DEFAULT', 'SECURITY_TOKEN_MAX_AGE')))
                return success
            else:
                flash(message='密码不正确', category='error')
                response.delete_cookie('access_token')
                return response
        else:
            user = User.select().where((User.is_ldap_user == False)&(User.username == username)).first()
            if user and user.verify_password(password):
                OpsRedis.set(user.id.hex,json.dumps(user.to_json()))
                success = redirectResponse(user.role)
                token = Auth.encode_auth_token(user_id=user.id.hex,password=user.password)
                success.set_cookie('access_token', token,max_age=int(config.get('DEFAULT', 'SECURITY_TOKEN_MAX_AGE')))
                if  isinstance(token,bytes) : token.decode()
                return success
            else:
                flash(message='用户名或者密码不正确', category='error')
                return response

@user.route('/logout',methods=['GET','POST'])
@login_required(administrator=False)
def auth_logout():
    response = make_response(redirect(config.get('DEFAULT','SECURITY_LOGIN_URL')))
    response.delete_cookie("access_token")
    return response

@user.route('/users/list',methods=['GET','POST'])
@login_required()
def users_list():
    return render_template('user/user_list.html')

@user.route('/users/detail/<userid>',methods=['GET','POST'])
@login_required()
def users_detail(userid):
    userid = userid
    user_object = User.select().where(User.id==userid).first()
    groups = Groups.select()
    ug_object = User.select().join(User_Group).join(Groups).where(User.id==userid).get()
    return render_template('user/user_detail.html',**locals())

@user.route('/users/create',methods=['GET','POST'])
@login_required()
def users_create():
    form = User_Create_Form()
    form.ldap_groups.choices = [(ug.id.hex,ug.value) for ug in  Groups.select().
                                where(Groups.is_ldap_group == True)]
    form.local_groups.choices = [(ug.id.hex, ug.value) for ug in Groups.select().
                                where(Groups.is_ldap_group == False) if ug != Groups.root()]
    return render_template('user/user_create.html', form=form)

@user.route('/users/update/<userid>',methods=['GET'])
@login_required()
def users_update(userid):
    user = User.select().where(User.id == userid)
    if user.get().is_ldap_user:
        form = Ldap_User_Form()
        form.groups.choices = [(ug.id.hex, ug.value) for ug in Groups.select().
            where(Groups.is_ldap_group == True)]
    else:
        form = Local_User_Form()
        form.groups.choices = [(ug.id.hex, ug.value) for ug in Groups.select().
            where(Groups.is_ldap_group == False) if ug != Groups.root()]
    model_to_form(user,form,exclude=['password'])
    form.groups.data = user.get().group.get().id.hex
    return render_template('user/user_update.html',form=form,userid=userid)

@user.route('/groups/list',methods=['GET','POST'])
@login_required()
def groups_list():
    return render_template('user/group_list.html')

@user.route('/groups/create',methods=['GET','POST'])
@login_required()
def groups_create():
    action = u"创建用户组"
    form = Groups_Form(request.form)
    return render_template('user/user_group_create.html',**locals())

@user.route('/groups/update/<gid>',methods=['GET','POST'])
@login_required()
def groups_update(gid):
    groupid = gid
    action = u"更新用户组"
    form = Groups_Form()
    group = Groups.select().where(Groups.id == gid)
    model_to_form(group,form)
    return render_template('user/user_group_update.html', **locals())

@user.route('/userlog/list',methods=['GET','POST'])
@login_required()
def userlogin_log_list():
    return  redirect('/auth/login')
