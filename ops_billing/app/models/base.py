# -*- coding: utf-8 -*-
from peewee import MySQLDatabase, Model
from celery import Celery,platforms
from app import global_config
import json,ldap
from redis import ConnectionPool,Redis

config = global_config()

pool0 = ConnectionPool(host=config.get('DEFAULT','REDIS_HOST'),port=config.get('DEFAULT','REDIS_PORT'),
                db=config.get('DEFAULT','REDIS_DEFAULT_DB'),password=config.get('DEFAULT','REDIS_PASS'))

pool1 = ConnectionPool(host=config.get('DEFAULT','REDIS_HOST'), port=config.get('DEFAULT','REDIS_PORT'),
                db=config.get('DEFAULT','REDIS_CELERY_DB'),password=config.get('DEFAULT','REDIS_PASS'))

OpsRedis = Redis(connection_pool=pool0)
OpsCeleryRedis = Redis(connection_pool=pool1)

db = MySQLDatabase(host=config.get('DEFAULT','DB_HOST'), user=config.get('DEFAULT','DB_USER'),
                passwd=config.get('DEFAULT','DB_PASSWD'),database=config.get('DEFAULT','DB_DATABASE'))

def LdapConnection():
    conn = ldap.initialize(config.get('LDAP','LDAP_SERVER'))
    conn.simple_bind_s(config.get('LDAP','ROOT_DN'),config.get('LDAP','ROOT_DN_PASS'))
    return conn

ldap_conn = LdapConnection()

def initcelery():
    celery = Celery('worker', broker=config.get('CELERY','CELERY_BROKER_URL'),
                                            backend=config.get('CELERY','CELERY_RESULT_BACKEND'))
    celery.conf.CELERY_TIMEZONE = config.get('CELERY','CELERY_TIMEZONE')
    celery.conf.CELERY_TASK_SERIALIZER = config.get('CELERY','CELERY_TASK_SERIALIZER')
    celery.conf.CELERY_RESULT_SERIALIZER = config.get('CELERY','CELERY_RESULT_SERIALIZER')
    platforms.C_FORCE_ROOT = True
    return celery

class BaseModel(Model):
    class Meta:
        database = db

    def __str__(self):
        r = {}
        for k in self._data.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        return json.dumps(r, ensure_ascii=False)
