from flask import jsonify,request
from flask_restful import Resource,reqparse
from app.models import User,Groups,User_Group,AssetPerm_Users,UserLoginLog
from app.auth import Auth,login_required,adminuser_required
from app.utils import  trueReturn,falseReturn
from .serializer import UserSerializer,GroupSerializer
from app.models.base import OpsRedis
from app.utils.encrypt import encryption_md5
from .ldapapi import ldapconn
import json,time,uuid,ldap,datetime

class UsersApi(Resource):
    @login_required
    def get(self):
        query_set = User.select()
        data = json.loads(UserSerializer(many=True,exclude=['password']).dumps(query_set).data)
        return jsonify(trueReturn(data))

    @login_required
    @adminuser_required
    def post(self):
        parse = reqparse.RequestParser()
        arg_names = ('ding', 'password', 'wechat', 'role' ,'user', 'username','comment',
                     'email', 'public_key', 'phone','groups')
        for arg in arg_names:
            parse.add_argument(arg,type=str,location='form')
        args = parse.add_argument('is_ldap_user',type=bool,default=False,location='form')\
            .add_argument('password', type=str,required=True,location='form').parse_args()
        data,errors = UserSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg='提交数据验证失败 %s' % errors))
        if args.get('is_ldap_user'):
            department = Groups.select().where(Groups.id == args.get('groups')).get()
            result= ldapconn.ldap_add_user(ou=department.value,username=args.get('username'),
                                   password=args.get('password'),email=args.get('email'),
                                   telephoneNumber=args.get('phone'))
            if not result:return jsonify(falseReturn(msg=ldapconn.gather_result()))
        data['password'] = encryption_md5(args.get('password'))
        user = User.create(**data)
        if args.get('groups') :
            user.group.add(uuid.UUID(args.get('groups')).hex)
        return jsonify(trueReturn(msg='创建成功'))

class UserApi(Resource):
    @login_required
    def get(self,userid):
        user = User.select().where(User.id == userid)
        data = json.loads(UserSerializer(exclude=['password']).dumps(user).data)
        return jsonify(data)

    @login_required
    def put(self,userid):
        parse = reqparse.RequestParser()
        arg_names = ('ding', 'password', 'wechat', 'role' ,'user', 'username','comment','email',
                     'public_key', 'phone','groups')
        for arg in arg_names:
            parse.add_argument(arg,type=str,location=['form','json'])
        args = parse.parse_args()
        user = User.select().where(User.id == userid).get()
        group = Groups.select().where(Groups.id == args.get('groups')).get()
        data,errors = UserSerializer().load(args)
        is_del_userkey = False
        if errors:
            return jsonify(falseReturn(msg='提交数据验证失败 %s' % errors))
        if args.get('password') :
            data['password'] = encryption_md5(args.get('password'))
            is_del_userkey = True
        if args.get('role') and args.get('role') != user.role:
            is_del_userkey = True
        if user.is_ldap_user:
            if group.value != user.group.get().value and not \
                    ldapconn.ldap_move_user(user.username,group.value):
                return jsonify(falseReturn(msg=ldapconn.gather_result()))
            if not ldapconn.ldap_update_user(username=user.username,ou=group.value,
                                             new_password=args.get('password'),
                                      mail=args.get('email'),telephoneNumber=args.get('phone')):
                return jsonify(falseReturn(msg=ldapconn.gather_result()))
            if data.get('username')  and data.get('username') != user.username:
                if not ldapconn.ldap_modify_user(user.username,data.get('username')):
                    return jsonify(falseReturn(msg=ldapconn.gather_result()))
        User.update(**data).where(User.id == userid).execute()
        if args.get('groups') :
            if group.value != user.group.get().value:
                user.group.clear()
                user.group.add(group.id)
        if is_del_userkey:OpsRedis.delete(userid)
        return jsonify(trueReturn(msg='更新成功'))

    @login_required
    @adminuser_required
    def delete(self,userid):
        user = User.select().where(User.id == userid).get()
        if user.is_ldap_user:
            ou = user.group.get().value
            result = ldapconn.ldap_delete_user(ou=ou,username=user.username)
            if not result:
                if ldapconn.conn.result['description'] != 'noSuchObject':
                    return jsonify(falseReturn(msg=ldapconn.gather_result()))
        user.group.clear()
        user.asset_permissions.clear()
        User.delete().where(User.id == userid).execute()
        return jsonify(trueReturn(msg='删除成功'))

    @login_required
    @adminuser_required
    def patch(self,userid):
        user = User.select().where(User.id == userid).get()
        if user.is_active:
            OpsRedis.delete(userid)
            user.is_active = False;msg = '禁用成功'
        else:
            user.is_active = True;msg = '激活成功'
        user.save()
        return jsonify(trueReturn(msg=msg))

class GroupsApi(Resource):
    @login_required
    def get(self):
        args = reqparse.RequestParser()\
            .add_argument('group_id', type=str,location='args').parse_args()
        if args.get('group_id'):
            data = []
            group = Groups.select().where(Groups.id == args.get('group_id'))
            parent_key = group.get().key
            child_mark = group.get().child_mark
            userdata = json.loads(GroupSerializer(many=True,only=['user']).dumps(group).data)[0]['user']
            for user in userdata:
                child_mark = child_mark + 1
                key = f'{parent_key}:{child_mark}'
                data.append(dict(id=user.get('id'), is_node=False, key=key,
                                 parent_key=parent_key,open=False,value=user.get('username')))
            return jsonify(trueReturn(data))
        query_set = Groups.select()
        data = json.loads(GroupSerializer(many=True).dumps(query_set).data)
        return jsonify(trueReturn(data))

    @login_required
    @adminuser_required
    def post(self):
        args = reqparse.RequestParser()\
            .add_argument('value', type=str,location=['form'],required=True) \
            .add_argument('is_ldap_group', type=str, location=['form'], required=True) \
            .add_argument('description', type=str, location=['form']).parse_args()
        data,errors = GroupSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=str(errors)))
        value = data.get('value')  or "新节点"
        value = "{} {}".format(value,Groups.root().get_next_child_key().split(":")[-1])
        if args.get('is_ldap_group') and not ldapconn.ldap_add_ou(value):
            return jsonify(falseReturn(msg=ldapconn.gather_result()))
        Groups.create(**data)
        return jsonify(trueReturn(msg='创建成功'))

class GroupApi(Resource):
    @login_required
    def get(self,groupid):
        group = Groups.select().where(Groups.id == groupid)
        if group.get().is_root() :
            query_set = User.select()
            data = json.loads(UserSerializer(many=True, exclude=['password']).dumps(query_set).data)
        else:
            data = json.loads(GroupSerializer(many=True,only=['user']).dumps(group).data)[0]['user']
        return jsonify(trueReturn(data))

    @login_required
    @adminuser_required
    def post(self,groupid):
        args = reqparse.RequestParser() \
            .add_argument('is_ldap_group', type=bool, location=['form','json'], required=True) \
            .add_argument('value', location='json').parse_args()
        instance = Groups.filter(Groups.id == groupid).first()
        value = args.get('value')  or "新节点"
        value = "{} {}".format(value,Groups.root().get_next_child_key().split(":")[-1])
        if args.get('is_ldap_group') and not ldapconn.ldap_add_ou(value):
            return jsonify(falseReturn(msg=ldapconn.gather_result()))
        try:
            group = instance.create_child(value=value)
            if args.get('is_ldap_group'):
                group.is_ldap_group = True;group.save()
            data = json.loads(GroupSerializer().dumps(group).data)
        except Exception as e:
            return jsonify(trueReturn(msg=str(e)))
        return jsonify(trueReturn(data))

    @login_required
    @adminuser_required
    def delete(self,groupid):
        group = Groups.select().where(Groups.id == groupid).first()
        if group and group.user.count() > 0:
            return jsonify(trueReturn('该组下有用户,需先移除用户'))
        if group.is_ldap_group:
            ldapconn.ldap_delete_ou(group.value)
        Groups.delete().where(Groups.id == groupid).execute()
        return jsonify(trueReturn('已经删除'))

    @login_required
    @adminuser_required
    def put(self,groupid):
        args = reqparse.RequestParser()\
            .add_argument('value', type=str,location=['form','json']) \
            .add_argument('description', type=str, location=['form','json']).parse_args()
        data,errors = GroupSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=str(errors)))
        group = Groups.select().where(Groups.id == groupid).get()
        if args.get('value') and args.get('value') != group.value and group.is_ldap_group:
            if not ldapconn.ldap_modify_ou(group.value,data.get('value')):
                return jsonify(falseReturn(msg=ldapconn.gather_result()))
        Groups.update(**data).where(Groups.id == groupid).execute()
        return jsonify(trueReturn(msg='更新成功'))

class UserLogin(Resource):
    @login_required
    def get(self):
        return jsonify(trueReturn(1))

    def post(self):
        location = ['form','json']
        args = reqparse.RequestParser() \
            .add_argument('username', type=str, location=location, required=True, help="用户名不能为空") \
            .add_argument("password", type=str, location=location, required=True, help="密码不能为空")\
            .add_argument('is_ldap_login',type=bool,default=True,location=location)\
            .parse_args()
        if args.get('is_ldap_login'):
            ldapuser = ldapconn.ldap_search_user(args.get('username'))
            if not ldapuser :
                return jsonify(falseReturn(msg='username is not exist!'))
            else:ldapuser = ldapuser[0]
            department = ldapuser['department'];ldapuser.pop('department')
            if args.get('password') == ldapuser.get('password'):
                user = User.select().where(User.username == args.get('username')).first()
                if not user :
                    ldapuser['password'] = encryption_md5(ldapuser['password'])
                    user = User.create(**ldapuser)
                group = Groups.select().where(Groups.value == department).first()
                if group:
                    user_group = user.group.select().where(Groups.value == department)
                    if user_group.count() == 0:user.group.add(group.id)
                else:
                    ROOT = Groups.root(); group = Groups.create(value=department,key=0)
                    group.parent = ROOT; group.save()
                    user.group.add(group.id)
                OpsRedis.set(user.id.hex,json.dumps(user.to_json()))
                remote_addr = request.headers.get('X-Forwarded-For') or request.remote_addr
                UserLoginLog.create(username=user.username,login_at=datetime.datetime.now(),
                                    login_ip=remote_addr)
                token = Auth.encode_auth_token(user.id.hex+user.password,int(time.time()))
                return jsonify(trueReturn(dict(token=token.decode() if isinstance(token, bytes) else token)))
            else:
                return jsonify(falseReturn(msg='password is invalid!'))
        else:
            user = User.select().where((User.is_ldap_user == False)&(User.username == args.get('username'))).first()
            if user and user.verify_password(args.get('password')):
                OpsRedis.set(user.id.hex,json.dumps(user.to_json()))
                token = Auth.encode_auth_token(user.id.hex+user.password,int(time.time()))
                if  isinstance(token,bytes) :  token = token.decode()
                return jsonify(trueReturn({"token": token}))
            else:
                return falseReturn(msg='username or password is invalid!')