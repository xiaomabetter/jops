# -*- coding: utf-8 -*-
from peewee import MySQLDatabase, Model
from conf.config import Config
from conf import celery_config
import os,uuid,datetime,json
from redis import ConnectionPool,Redis

pool0 = ConnectionPool(host=Config.REDIS_HOST, port=Config.REDIS_PORT,db=Config.REDIS_DB)
pool1 = ConnectionPool(host=celery_config.REDIS_HOST,
                                port=celery_config.REDIS_PORT,db=celery_config.REDIS_DB)
OpsRedis = Redis(connection_pool=pool0)
OpsCeleryRedis = Redis(connection_pool=pool1)

db = MySQLDatabase(host=Config.DB_HOST, user=Config.DB_USER, passwd=Config.DB_PASSWD,
                   database=Config.DB_DATABASE)

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
