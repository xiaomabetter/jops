from flask import Flask
from flask_login import LoginManager
from logging.config import fileConfig
import configparser
import logging
import os

login_manager = LoginManager()
login_manager.session_protection = 'strong'
fileConfig('conf/log-app.conf')

app = Flask(__name__)

def global_config():
    config = configparser.ConfigParser()
    config.read("conf/config.ini")
    return config

config = global_config()

def get_logger(name):
    return logging.getLogger(name)

def get_basedir():
    return os.path.abspath(os.path.dirname(__file__))

def create_app(config_name):
    app.config['SECRET_KEY']  = config.get('DEFAULT','SECRET_KEY')
    app.config['WTF_CSRF_SECRET_KEY'] = config.get('DEFAULT', 'SECRET_KEY')
    login_manager.init_app(app)
    from .asset import asset
    app.register_blueprint(asset)
    from .user import user
    app.register_blueprint(user)
    from .perm import perm
    app.register_blueprint(perm)
    from .task import task
    app.register_blueprint(task)

    return app