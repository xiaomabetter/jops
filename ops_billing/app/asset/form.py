# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm,csrf
from wtforms import StringField,TextAreaField,SelectField,IntegerField,SelectMultipleField,BooleanField
from wtforms.widgets import CheckboxInput,TextInput,SubmitInput
from wtforms.validators import DataRequired

class Service_Form(FlaskForm):
    servicename = StringField(u'服务名称', [DataRequired(message=u'必须填写服务名称')],
                            widget=TextInput(), render_kw={"class": "form-control","placeholder":"服务名称"})
    version = StringField(u'版本', widget=TextInput(), render_kw={"class": "form-control","placeholder":"版本"})
    description = TextAreaField('描述', render_kw={"class": "form-control"})

class Aly_Instance_Form(FlaskForm):
    InstanceChargeTypes = [('PrePaid',u'预付费'),('PostPaid',u'按量付费')]
    InternetChargeTypes = [('PayByTraffic',u'按使用流量付费'),('PayByBandwidth',u'按固定带宽付费')]
    InstanceTemplate = SelectMultipleField(u'实例模板',choices=[],
                        render_kw={"class":"form-control select2",
                                            "data-placeholder":"选择创建实例模板"})
    InstanceChargeType = SelectField(u'选择计费方式',choices=InstanceChargeTypes,
                                                                    render_kw={"class":"form-control",})
    InstanceName = StringField(u'新实例名称',widget=TextInput(),
                               render_kw={"class":"form-control","placeholder": u"新实例名称"})
    amount  = IntegerField(u'创建资产数量',widget=TextInput(),default=1,
                           render_kw={"class":"form-control","placeholder": u"创建机器数量,默认1台"})
    PublicIpAddress = BooleanField(u'绑定公网',widget=CheckboxInput(),render_kw={"class":"form-control"})
    InternetChargeType = SelectField(u'公网带宽计费类型',choices=InternetChargeTypes,
                                     render_kw={"class":"form-control"})
    InternetMaxBandwidthOut = IntegerField(u'带宽大小',widget=TextInput(),default=0,
                                render_kw={"class":"form-control","placeholder": u"带宽大小,单位M"})

class Aly_Instance_Template(FlaskForm):
    image_categorys = [('self',u'自有镜像'),('system',u'系统镜像')]
    disk_categorys = [('cloud_efficiency',u'高效云盘'),('cloud_ssd',u'SSD云盘')]
    InstanceNetworkTypes = [('classic', u'经典网络'), ('vpc', u'专有网络')]
    VSwitchId = SelectField(u'选择交换机', choices=[], render_kw={"class": "form-control"})
    name = StringField(u'实例模板名称',render_kw={"class":"form-control","placeholder":"实例模板名称"})
    RegionId = SelectField(u'选择区域',choices=[],render_kw={"class":"form-control"})
    ZoneId = SelectField(u'选择可用区',choices=[],render_kw={"class":"form-control"})
    InstanceNetworkType = SelectField(u'网络类型',choices=InstanceNetworkTypes,
                                      render_kw={"class":"form-control"})
    instance_type = StringField(u'实例规格',render_kw={"class":"form-control","placeholder": u"实例规格"})
    image_category = SelectField(u'镜像类型',choices=image_categorys,render_kw={"class":"form-control"})
    ImageId = SelectMultipleField(u'镜像',choices=[],render_kw={"class":"form-control select2",
                                                            "data-placeholder":"选择镜像"})
    SecurityGroupId = SelectMultipleField(u'安全组',choices=[],render_kw={"class":"form-control select2",
                                                            "data-placeholder":"选择安全组"})
    disk_category = SelectField(u'硬盘类型', choices=disk_categorys, render_kw={"class": "form-control"})
    System_disk = StringField(u'系统盘',render_kw={"class":"form-control"})
    System_data_disk = IntegerField(u'数据盘', render_kw={"class": "form-control"})
