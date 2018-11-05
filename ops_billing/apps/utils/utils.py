# -*- coding: utf-8 -*-
import html
import json
import datetime
from urllib.parse import unquote
from flask import Response, flash,request
from Crypto.PublicKey import RSA
from Crypto import Random

def trueReturn(data='', msg=''):
    return {
        "status": True,
        "data": data,
        "msg": msg
    }

def falseReturn(data='', msg=''):
    return {
        "status": False,
        "data": data,
        "msg": msg
    }

def str_to_dict(dict_str):
    if isinstance(dict_str, str) and dict_str != '':
        new_dict = json.loads(dict_str)
    else:
        new_dict = ""
    return new_dict

def urldecode(raw_str):
    return unquote(raw_str)

# HTML解码
def html_unescape(raw_str):
    return html.unescape(raw_str)

## 键值对字符串转JSON字符串
def kvstr_to_jsonstr(kvstr):
    kvstr = urldecode(kvstr)
    kvstr_list = kvstr.split('&')
    json_dict = {}
    for kvstr in kvstr_list:
        key = kvstr.split('=')[0]
        value = kvstr.split('=')[1]
        json_dict[key] = value
    json_str = json.dumps(json_dict, ensure_ascii=False, default=datetime_handler)
    return json_str

# 字典转对象
def dict_to_obj(dict, obj, exclude=None):
    for key in dict:
        if exclude:
            if key in exclude:
                continue
        setattr(obj, key, dict[key])
    return obj

# peewee转dict
def obj_to_dict(obj, exclude=None):
    dict = list(obj.dicts())[0]
    if exclude:
        for key in exclude:
            if key in dict: dict.pop(key)
    return dict

# JSON中时间格式处理
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.strftime("%Y-%m-%d %H:%M:%S")
    raise TypeError("Unknown type")

# wtf表单转peewee模型
def form_to_model(form, model):
    dict = obj_to_dict(model)
    for wtf in form:
        if wtf.name in dict:
            model.__setattr__(wtf.name, wtf.data)
    return model

# peewee模型转表单
def model_to_form(model, form,exclude=[]):
    dict = list(model.dicts())[0]
    form_key_list = [k for k in form.__dict__]
    for k, v in dict.items():
        if k in form_key_list and v and k not in exclude:
            field = form.__getitem__(k)
            field.data = v
            form.__setattr__(k, field)

def dict_to_form(data, form,exclude=[]):
    form_key_list = [k for k in form.__dict__]
    for k, v in data.items():
        if k in form_key_list and v and k not in exclude:
            field = form.__getitem__(k)
            field.data = v
            form.__setattr__(k, field)

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("字段 [%s] 格式有误,错误原因: %s" % (
                getattr(form, field).label.text,
                error
            ))

def generate_rsa_keys():
    random_generator = Random.new().read
    key = RSA.generate(1024, random_generator)
    pub_key = key.publickey()

    public_key = pub_key.exportKey("PEM")
    private_key = key.exportKey("PEM")
    return public_key, private_key
