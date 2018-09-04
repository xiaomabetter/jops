from flask import request,make_response,redirect,flash,g
from functools import wraps
import jwt, datetime, time
from flask import jsonify
from app.models import User,Terminal
from conf.config import Config
from app.utils import trueReturn,falseReturn

def get_login_user():
    token = request.cookies.get('access_token') or request.headers.get('Authorization')
    data = Auth.decode_auth_token(token)
    uid = data.get('data')['id']
    current_user = User.filter(User.id == uid).first()
    return  current_user

def adminuser_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token_id = request.cookies.get('access_token') or request.headers.get('Authorization')
        dt = Auth.decode_auth_token(token_id)
        userid = dt.get('data')['id']
        user = User.select().where(User.id == userid).get()
        if not user.administrator :
            falseReturn(msg=u'非管理员用户')
        return func(*args, **kwargs)
    return decorated_function

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'access_token' in  request.cookies:
            token = request.cookies.get('access_token')
            response = make_response(redirect(Config.SECURITY_LOGIN_URL))
            data = Auth.decode_auth_token(token)
            if data['status']:
                uid = data.get('data')['id']
                user = User.filter(User.id == uid).first()
                if not user:
                    return response
                elif not user.is_active:
                    return response
                g.user = user
                g.is_adminuser = user.administrator
            else:
                return response
        elif request.headers.get('Authorization') :
            token = request.headers.get('Authorization')
            data = Auth.decode_auth_token(token)
            if data['status']:
                uid = data.get('data')['id']
                user = User.filter(User.id == uid).first()
                if not user:
                    return falseReturn(msg=u'用户不存在')
                elif not user.is_active:
                    return falseReturn(msg=u'用户被禁用')
            else:
                return falseReturn(msg=data['msg'])
        else:
            if 'Mozilla' in request.headers.get('User-Agent'):
                return  make_response(redirect(Config.SECURITY_LOGIN_URL))
            else:
                falseReturn(msg=u'请先获取token')
        return func(*args, **kwargs)
    return decorated_function

def terminal_auth_token(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token :
            payload = Auth.decode_auth_token(token,expire=False)
            if not payload:
                return False
            tid = payload.get('data')['id']
            terminal = Terminal.filter(Terminal.id==tid).first()
            if not terminal :
                return False
        else:
            return False
        return func(*args, **kwargs)
    return decorated_function

class Auth():
    @staticmethod
    def encode_auth_token(user_id, login_time,ulimit=True):
        try:
            payload = {
                'exp': datetime.datetime.now() + datetime.timedelta(days=0, minutes=600),
                'iat': datetime.datetime.now(),
                'iss': 'ken',
                'data': {
                    'id': user_id,'login_time': login_time
                }
            }
            return jwt.encode(
                payload,
                Config.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token,expire=True):
        try:
            if expire:
                payload = jwt.decode(auth_token, Config.SECRET_KEY, options={'verify_exp': True},
                                    leeway=datetime.timedelta(minutes=600))
            else:
                payload = jwt.decode(auth_token, Config.SECRET_KEY, options={'verify_exp': False})
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