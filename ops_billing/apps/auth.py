from flask import request,make_response,redirect,g,flash
from functools import wraps
import jwt, datetime
from flask import jsonify
from apps.models import User,OpsRedis
from apps.utils import falseReturn
from apps import config
import json

def get_login_user():
    token = request.cookies.get('access_token') or request.headers.get('Authorization')
    data = Auth.decode_auth_token(token)
    user_id = data['user_id']
    current_user = User.filter(User.id == user_id).first()
    return  current_user

def is_browser_user():
    if 'Mozilla' in request.headers.get('User-Agent'):
        return True

def return_response(msg='',isflash=True):
    if is_browser_user():
        if isflash:
            flash(message=msg,category='error')
        response = make_response(redirect(config.get('DEFAULT', 'SECURITY_LOGIN_URL')))
        response.delete_cookie("access_token")
        return response
    else:
        return jsonify(falseReturn(msg=msg))

def login_required(administrator=True,users=list()):
    def adminlogin(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            token = request.cookies.get('access_token') or request.headers.get('Authorization')
            if token:
                data = Auth.decode_auth_token(token)
                if data['status']:
                    user_id = data['user_id']
                    password = data['password']
                    if OpsRedis.exists(user_id):
                        userinfo = json.loads(OpsRedis.get(user_id).decode())
                        if not userinfo.get('is_active'):return return_response(msg='用户被禁用')
                        if administrator is True and userinfo.get('role') != 'administrator':
                            return return_response(msg='非管理员用户')
                        if users and userinfo.get('username') not in users:
                            return return_response(msg='你没有权限啊')
                        if userinfo.get('password') != password:return return_response(msg='密码有变化,请重新登录')
                        if is_browser_user():g.user = userinfo
                    else:
                        user = User.select().where(User.id == user_id).first()
                        if not user:return return_response(msg='用户不存在')
                        if not user.is_active:return return_response(msg='用户被禁用')
                        if user.password != password:return return_response(msg='密码有变化,请重新登录')
                        if is_browser_user():g.user = user.to_json()
                        OpsRedis.set(user_id,json.dumps(user.to_json()))
                else:
                    return return_response(msg=data['msg'],isflash=False)
            else:
                return return_response('请先登录',isflash=False)
            return func(*args, **kwargs)
        return decorated_function
    return adminlogin

class Auth():
    @staticmethod
    def encode_auth_token(user_id,password):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=int(config.get('DEFAULT', 'SECURITY_TOKEN_MAX_AGE'))),
                'iat': datetime.datetime.utcnow(),
                'iss': 'ken',
                'user_id':user_id,
                'password':password
            }
            return jwt.encode(payload,config.get('DEFAULT','SECRET_KEY'),algorithm='HS256')
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token,expire=True):
        try:
            if expire:
                payload = jwt.decode(auth_token, config.get('DEFAULT','SECRET_KEY'),
                                     options={'verify_exp': True})
            else:
                payload = jwt.decode(auth_token, config.get('DEFAULT','SECRET_KEY'),
                                     options={'verify_exp': False})
            if ('user_id' in payload and 'password' in payload):
                payload['status'] = True
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return dict(status=False,msg='token过期')
        except jwt.InvalidTokenError:
            return dict(status=False, msg=u'无效token')