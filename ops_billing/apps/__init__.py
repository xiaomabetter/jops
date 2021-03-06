from flask import Flask
from flask_login import LoginManager
import configparser
import logging
import os

login_manager = LoginManager()
login_manager.session_protection = 'strong'

app = Flask(__name__)

def global_config():
    config = configparser.ConfigParser()
    config.read("conf/config.ini")
    return config

config = global_config()

def get_basedir():
    return os.path.abspath(os.path.dirname(__file__))

def create_app(config_name):
    handler = logging.FileHandler('logs/flask.log', encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)
    app.config['SECRET_KEY']  = config.get('DEFAULT','SECRET_KEY')
    app.config['WTF_CSRF_SECRET_KEY'] = config.get('DEFAULT', 'SECRET_KEY')
    login_manager.init_app(app)
    from .asset import asset
    app.register_blueprint(asset,url_prefix='/asset')
    from .user import user
    app.register_blueprint(user,url_prefix='/user')
    from .perm import perm
    app.register_blueprint(perm,url_prefix='/permission')
    from .task import task
    app.register_blueprint(task,url_prefix='/task')
    from .platform import platform
    app.register_blueprint(platform,url_prefix='/platform')
    from .index import index
    app.add_url_rule('/',index)

    return app