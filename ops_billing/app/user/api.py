from flask import jsonify,request
from flask_restful import Resource,reqparse
from app.models import User,Groups,User_Group,AssetPerm_Users,UserLoginLog
from app.models.base import OpsRedis
from app.auth import Auth,login_required,adminuser_required
from app.utils import  trueReturn,falseReturn
from .serializer import UserSerializer,GroupSerializer
from app.models.base import OpsRedis,ldap_conn
from app.utils.encrypt import encryption_md5
import json,time,uuid,ldap,datetime
from app import config

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
                     'email', 'public_key', 'phone')
        for arg in arg_names:
            parse.add_argument(arg,type=str,location='form')
        args = parse.add_argument('groups', type=str,action='append', location='form').parse_args()
        data,errors = UserSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg='提交数据验证失败 %s' % errors))
        if args.get('password') :
            data['password'] = encryption_md5(args.get('password'))
        user = User.create(**data)
        if args.get('groups') :
            groups = [uuid.UUID(g).hex for g in args.get('groups')]
            for gid in groups:
                user.group.add(gid)
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
                     'public_key', 'phone')
        for arg in arg_names:
            parse.add_argument(arg,type=str,location='form')
        args = parse.add_argument('groups', type=str,action='append', location='form').parse_args()
        data,errors = UserSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg='提交数据验证失败 %s' % errors))
        if args.get('password') :
            data['password'] = encryption_md5(args.get('password'))
        user = User.select().where(User.id == userid).get()
        User.update(**data).where(User.id == userid).execute()
        if args.get('groups') :
            groups = [uuid.UUID(g).hex for g in args.get('groups')]
            user_groups = [g.id.hex for g in user.group.objects()]
            for gid in list(set(groups) - set(user_groups)):
                user.group.add(gid)
            for gid in list(set(user_groups) - set(groups)):
                user.group.remove(gid)
        if args.get('password'):OpsRedis.delete(userid)
        return jsonify(trueReturn(msg='更新成功'))

    @login_required
    @adminuser_required
    def delete(self,userid):
        User_Group.delete().where(User_Group.user_id == userid).execute()
        AssetPerm_Users.delete().where(AssetPerm_Users.user_id == userid).execute()
        User.delete().where(User.id == userid).execute()
        return jsonify(trueReturn(msg='删除成功'))

    @login_required
    @adminuser_required
    def patch(self,userid):
        user = User.select().where(User.id == userid).get()
        if user.role != 'administrator':
            user.is_active = 0
            user.save()
        return jsonify(trueReturn(msg='禁用成功'))

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
            .add_argument('description', type=str, location=['form']).parse_args()
        data,errors = GroupSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=str(errors)))
        else:
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
            .add_argument('value', location='json').parse_args()
        instance = Groups.filter(Groups.id == groupid).first()
        value = args.get('value')  or "新节点"
        value = "{} {}".format(value,Groups.root().get_next_child_key().split(":")[-1])
        try:
            group = instance.create_child(value=value)
            data = json.loads(GroupSerializer().dumps(group).data)
        except Exception as e:
            return jsonify(trueReturn(msg=str(e)))
        return jsonify(trueReturn(data))

    @login_required
    @adminuser_required
    def delete(self,groupid):
        User_Group.delete().where(User_Group.groups_id == groupid).execute()
        Groups.delete().where(Groups.id == groupid).execute()
        return jsonify(trueReturn('已经删除'))

    @login_required
    @adminuser_required
    def put(self,groupid):
        args = reqparse.RequestParser()\
            .add_argument('value', type=str,location=['form','json'],required=True) \
            .add_argument('description', type=str, location=['form','json']).parse_args()
        data,errors = GroupSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=str(errors)))
        r = Groups.update(**data).where(Groups.id == groupid).execute()
        return jsonify(trueReturn(msg='更新成功'))

class UserLogin(Resource):
    def post(self):
        location = ['form','json']
        args = reqparse.RequestParser() \
            .add_argument('username', type=str, location=location, required=True, help="用户名不能为空") \
            .add_argument("password", type=str, location=location, required=True, help="密码不能为空")\
            .add_argument('is_ldap_login',type=bool,default=True,location=location)\
            .parse_args()
        username = args.get('username');password = args.get('password')
        if args.get('is_ldap_login'):
            ldapuser = ldap_conn.search_s(config.get('LDAP','BASE_DN'), ldap.SCOPE_SUBTREE, f'(uid={username})')
            if len(ldapuser) == 1 :
                mail = ldapuser[0][1]['mail'][0];userpass = ldapuser[0][1]['userPassword'][0]
                phone = ldapuser[0][1]['telephoneNumber'][0];groupname = ldapuser[0][0].split(',')[1].split('=')[1]
                userinfo = {
                    'username':username,'is_ldap_user':True,
                    'mail':mail.decode() if isinstance(mail,bytes) else mail,
                    'phone':phone.decode() if isinstance(phone,bytes) else phone
                }
                if isinstance(userpass,bytes): userpass = userpass.decode()
                if userpass == password:
                    user = User.select().where(User.username == username).first()
                    if not user :
                        userinfo['password'] = encryption_md5(userpass)
                        user = User.create(**userinfo)
                    group = Groups.select().where(Groups.value == groupname).first()
                    if not group:
                        ROOT = Groups.root(); group = Groups.create(value=groupname,key=0)
                        group.parent = ROOT; group.save()
                        user.group.add(group.id)
                    else:
                        user_group = user.group.select().where(Groups.value == groupname)
                        if user_group.count() == 0:user.group.add(group.id)
                    OpsRedis.set(user.id.hex,json.dumps(user.to_json()))
                    remote_addr = request.headers.get('X-Forwarded-For') or request.remote_addr
                    UserLoginLog.create(user_id=user.id,login_at=datetime.datetime.now(),login_ip=remote_addr)
                    token = Auth.encode_auth_token(user.id.hex+user.password,int(time.time()))
                    if isinstance(token, bytes):  token.decode()
                    return jsonify(trueReturn(dict(token=token)))
                else:
                    return jsonify(falseReturn(msg='password is invalid!'))
            else:
                return jsonify(falseReturn(msg='username is not exist!'))
        else:
            user = User.select().where((User.email == username)|(User.username == username)).first()
            if user and user.verify_password(password):
                OpsRedis.set(user.id.hex,json.dumps(user.to_json()))
                token = Auth.encode_auth_token(user.id.hex+user.password,int(time.time()))
                if  isinstance(token,bytes) :  token = token.decode()
                return jsonify(trueReturn({"token": token}))
            else:
                return falseReturn(msg='username or password is invalid!')


