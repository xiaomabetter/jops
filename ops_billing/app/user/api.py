from app import get_logger, get_config
from flask import request,jsonify,g
from flask_restful import Api,Resource,reqparse
from app.models import User,Groups,User_Group,AssetPerm_Users
from app.auth import Auth,login_required,adminuser_required
from app.utils import  trueReturn,falseReturn
from .serializer import UserSerializer,GroupSerializer
from app.utils.encrypt import encryption_md5
import json,time,uuid

class UsersApi(Resource):
    @login_required
    def get(self):
        query_set = User.select()
        data = json.loads(UserSerializer(many=True,exclude=['password']).dumps(query_set).data)
        return jsonify(trueReturn(data))

    @login_required
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
        return jsonify(trueReturn(msg='更新成功'))

    @login_required
    @adminuser_required
    def delete(self,userid):
        User_Group.delete().where(User_Group.user_id == userid).execute()
        AssetPerm_Users.delete().where(AssetPerm_Users.user_id == userid).execute()
        User.delete().where(User.id == userid).execute()
        return jsonify(trueReturn(msg='删除成功'))

    @login_required
    def patch(self,userid):
        user = User.select().where(User.id == userid).get()
        if user.role != 'administrator':
            user.is_active = 0
            user.save()
        return jsonify(trueReturn(msg='禁用成功'))

class GroupsApi(Resource):
    @login_required
    def get(self):
        query_set = Groups.select()
        data = json.loads(GroupSerializer(many=True).dumps(query_set).data)
        return jsonify(trueReturn(data))

    @login_required
    @adminuser_required
    def post(self):
        args = reqparse.RequestParser()\
            .add_argument('groupname', type=str,location=['form'],required=True) \
            .add_argument('description', type=str, location=['form']).parse_args()
        data,errors = GroupSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=str(errors)))
        else:
            Groups.create(**data)
        return jsonify(trueReturn(msg='创建成功'))

class GroupApi(Resource):
    @login_required
    @adminuser_required
    def delete(self,groupid):
        User_Group.delete().where(User_Group.groups_id == groupid).execute()
        r = Groups.delete().where(Groups.id == groupid).execute()
        return jsonify(trueReturn('已经删除'))

    @login_required
    @adminuser_required
    def put(self,groupid):
        args = reqparse.RequestParser()\
            .add_argument('groupname', type=str,location=['form'],required=True) \
            .add_argument('description', type=str, location=['form']).parse_args()
        data,errors = GroupSerializer().load(args)
        if errors:
            return jsonify(falseReturn(msg=str(errors)))
        else:
            Groups.update(**data).where(Groups.id == groupid).execute()
        return jsonify(trueReturn(msg='更新成功'))

class AuthToken(Resource):
    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('username', type=str, location='json', required=True, help="用户名不能为空") \
            .add_argument("password", type=str, location='json', required=True, help="密码不能为空") \
            .parse_args()
        try:
            user = User.select().where((User.email == args.get('username')) |
                                                    (User.username == args.get('username'))).get()
        except Exception as e:
            return falseReturn(msg=str('e'))
        if user and user.verify_password(args['password']):
            token = Auth.encode_auth_token(user.id.hex,int(time.time()))
            if isinstance(token,bytes):
                token = token.decode()
            return jsonify(trueReturn({"token": token}))
        else:
            return falseReturn(msg='username or password is invalid!')


