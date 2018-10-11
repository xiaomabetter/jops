from app import get_logger,config
from flask import render_template,request,flash
from peewee import fn
from app.utils import Pagination
from datetime import datetime,timedelta
from app.models import Node,Bill,Service,Asset,Asset_Create_Template
from app.models.base import OpsRedis
from . import asset
from .serializer import AssetCreateTemplateSerializer
from .form import Service_Form,Aly_Create_Instance_Form,Aly_Create_Instance_Template
from app.auth import login_required
import json

logger = get_logger(__name__)

@asset.route('/asset/<asset_type>/list',methods=['GET'])
@login_required
def asset_list(asset_type):
    return render_template('asset/asset_list.html',asset_type=asset_type)

@asset.route('/asset/<assetid>/detail',methods=['GET'])
@login_required
def asset_detail(assetid):
    asset = Asset.select().where(Asset.id == assetid).get()
    nodes = asset.node.objects()
    services = asset.service.objects()
    return render_template('asset/asset_detail.html',**locals())

@asset.route('/asset/create',methods=['GET'])
@login_required
def asset_create():
    form = Aly_Create_Instance_Form()
    Zones = OpsRedis.get('aly_zones').decode()
    return render_template('asset/asset_create.html',**locals())

@asset.route('/asset/create/template',methods=['GET'])
@login_required
def asset_create_template():
    form = Aly_Create_Instance_Template()
    Zones = OpsRedis.get('aly_zones').decode()
    return render_template('asset/asset_create_template.html',**locals())

@asset.route('/asset/create/template/list',methods=['GET'])
@login_required
def asset_create_template_list():
    form = Aly_Create_Instance_Template()
    Zones = OpsRedis.get('aly_zones').decode()
    return render_template('asset/asset_create_template_list.html',**locals())

@asset.route('/asset/create/template/update/<templateid>',methods=['GET'])
@login_required
def asset_create_template_update(templateid):
    template = Asset_Create_Template.select().where(Asset_Create_Template.id == templateid)
    templatedata = dict(json.loads(AssetCreateTemplateSerializer(many=True).dumps(template).data)[0])
    if templatedata['DataDiskinfo']:
        DataDiskinfo = list(json.loads(templatedata['DataDiskinfo']))
        for dataDisk in DataDiskinfo:
            templatedata = dict(templatedata,**dataDisk)
    templatedata['ImageId'] = '{0}-join-{1}'.format(templatedata['ImageId'],templatedata['RegionId'])
    form = Aly_Create_Instance_Template()
    Zones = OpsRedis.get('aly_zones').decode()
    return render_template('asset/asset_create_template_update.html',**locals())

@asset.route('/asset/service/list',methods=['GET'])
@login_required
def service_list():
    return render_template('asset/service_list.html')

@asset.route('/asset/service/create',methods=['GET','POST'])
@login_required
def service_create():
    form = Service_Form(request.form)
    if request.method == 'POST' and form.validate():
        formdata = request.form.to_dict()
        formdata.pop('csrf_token')
        try:
            Service.create(**formdata)
            flash(u'服务创建成功!', category='success')
        except:
            flash(u'服务创建失败!', category='error')
    return render_template('asset/service_create.html',form=form)

@asset.route('/asset/service/update/<serviceid>',methods=['GET','POST'])
@login_required
def service_update(serviceid):
    serviceid = serviceid
    form = Service_Form(request.form)
    service = Service.select().where(Service.id == serviceid).get()
    form.servicename.data = service.servicename
    form.version.data = service.version
    form.description.data = service.description
    return render_template('asset/service_update.html',**locals())

@asset.route('/asset/bill/list',methods=['GET'])
@login_required
def bill_list():
    limit = config.get('DEFAULT','ITEMS_PER_PAGE')
    page = int(request.args.get('page',1))
    nodeid = request.args.get('nodeid','')
    date_from = request.args.get('date_from','')
    date_to = request.args.get('date_to', '')
    asset_type = request.args.get('asset_type','ALL')
    query_set = Bill.select()
    if not date_from or not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')
        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    query_set = query_set.filter(Bill.day.between(date_from, date_to))
    if query_set.count() != 0:
        if asset_type != 'ALL':
            query_set = query_set.filter(Bill.instance_type.contains(asset_type))
        if nodeid :
            node = Node.filter(Node.id==nodeid).get()
            if not node.is_root():
                instance_ids = [q.InstanceId for q in node.get_all_assets(asset_type.lower())]
                query_set = query_set.filter(Bill.instance_id.in_(instance_ids))
    bill_list = query_set.order_by(Bill.day.desc()).paginate(page, int(limit))
    total_count = query_set.count()
    sumcost = query_set.select(fn.SUM(Bill.cost)).scalar()
    page_obj = Pagination(page,limit,total_count)
    return render_template('asset/bill_list.html',**locals())
