from flask import request,make_response,redirect,g,flash
from functools import wraps
import jwt, datetime
from flask import jsonify
from app.models import User,OpsRedis
from app.utils import trueReturn,falseReturn
from app import config
import json

def get_login_user():
    token = request.cookies.get('access_token') or request.headers.get('Authorization')
    data = Auth.decode_auth_token(token)
    user_id = data['data']['id'][:32]
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
        return response
    else:
        return jsonify(falseReturn(msg=msg))

def adminuser_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token_id = request.cookies.get('access_token') or request.headers.get('Authorization')
        if token_id:
            data = Auth.decode_auth_token(token_id)
            user_id = data['data']['id'][:32]
            if OpsRedis.exists(user_id):
                userinfo = json.loads(OpsRedis.get(user_id).decode())
                if userinfo.get('role') != 'administrator':
                    return jsonify(falseReturn(msg='非管理员用户'))
            user = User.select().where(User.id == user_id).get()
            if not user.administrator :
                return jsonify(falseReturn(msg='非管理员用户'))
        return func(*args, **kwargs)
    return decorated_function

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('access_token') or request.headers.get('Authorization')
        if token:
            data = Auth.decode_auth_token(token)
            if data['status']:
                user_id = data['data']['id'][:32]
                password = data['data']['id'][32:]
                if OpsRedis.exists(user_id):
                    userinfo = json.loads(OpsRedis.get(user_id).decode())
                    if not userinfo.get('is_active'):return return_response(msg='用户被禁用')
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

class Auth():
    @staticmethod
    def encode_auth_token(user_id, login_time,ulimit=True):
        try:
            payload = {
                'exp': datetime.datetime.now() + datetime.timedelta(days=0,
                                    seconds=int(config.get('DEFAULT', 'SECURITY_TOKEN_MAX_AGE'))),
                'iat': datetime.datetime.now(),
                'iss': 'ken',
                'data': {'id': user_id,'login_time': login_time}
            }
            return jwt.encode(payload,config.get('DEFAULT','SECRET_KEY'),algorithm='HS256')
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token,expire=True):
        try:
            if expire:
                payload = jwt.decode(auth_token, config.get('DEFAULT','SECRET_KEY'),
                                     options={'verify_exp': True},
                                    leeway=datetime.timedelta(minutes=600))
            else:
                payload = jwt.decode(auth_token, config.get('DEFAULT','SECRET_KEY'),
                                     options={'verify_exp': False})
            if ('data' in payload and 'id' in payload['data']):
                payload['status'] = True
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return dict(status=False,msg='token过期')
        except jwt.InvalidTokenError:
            return dict(status=False, msg=u'无效token')

    def authenticate(self, username, password):
        user = User.filter(User.username==username or User.email == username).first()
        if (user is None):
            return jsonify(falseReturn('', '找不到用户'))
        else:
            if password:
                if not user.verify_password(password):
                    return jsonify(falseReturn('', u'密码不正确'))
            user.last_login_at = datetime.datetime.now()
            user.login_count = user.login_count + 1
            user.save()
            token = self.encode_auth_token(user.id.hex)
            return jsonify(trueReturn(token, '登录成功'))