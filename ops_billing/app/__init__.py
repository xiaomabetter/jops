from flask import Flask
from conf.config import config,Config
from conf import celery_config
from celery import Celery,platforms
from flask_login import LoginManager
from logging.config import fileConfig
import logging
import os

login_manager = LoginManager()
login_manager.session_protection = 'strong'
fileConfig('conf/log-app.conf')

app = Flask(__name__)

celery = Celery('worker', broker=celery_config.CELERY_BROKER_URL,backend=celery_config.CELERY_RESULT_BACKEND)
celery.config_from_object('conf.celery_config')
platforms.C_FORCE_ROOT = True

def get_logger(name):
    return logging.getLogger(name)

def get_basedir():
    return os.path.abspath(os.path.dirname(__file__))

def get_config():
    return config[os.getenv('FLASK_CONFIG') or 'default']

def create_app(config_name):
    app.config.from_object(config[config_name])
    login_manager.init_app(app)

    from .asset import asset
    app.register_blueprint(asset)
    from .user import user
    app.register_blueprint(user)
    from .perm import perm
    app.register_blueprint(perm)
    from .task import task
    app.register_blueprint(task)
    from .terminal import terminal
    app.register_blueprint(terminal)

    return app