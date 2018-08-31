from app import celery,get_logger
from app.task.asset import SyncBills,SyncAliAssets,NodeAmount,\
        Aly_Create_Asset,AliSyncImages,AliSyncZones,AliSyncSecurityGroup,AliSyncInstanceTypes
from celery.signals import worker_process_init
from conf.aliyun_conf import AliConfig
from app.models.asset import Asset_Create_Record
from datetime import datetime
logger = get_logger(__name__)

AccessKeyId = AliConfig.AccessKeyId
AccessKeySecret = AliConfig.AccessKeySecret


@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    from multiprocessing import current_process
    try:
        current_process()._config
    except AttributeError:
        current_process()._config = {'semprefix': '/mp'}

@celery.task(bind=True)
def run_sync_bill(self,username,day_from,day_to):
    sync_bill = SyncBills(username,AccessKeyId, AccessKeySecret, day_from, day_to)
    sync_bill.handle()

@celery.task
def run_sync_asset(asset_type):
    sync_asset = SyncAliAssets(AccessKeyId, AccessKeySecret)
    sync_asset.aly_sync_asset(asset_type)

@celery.task
def run_sync_images():
    sync_asset = AliSyncImages(AccessKeyId, AccessKeySecret)
    sync_asset.sync_images()

@celery.task
def run_sync_zones():
    sync_zone = AliSyncZones(AccessKeyId, AccessKeySecret)
    sync_zone.sync_zones()

@celery.task
def run_sync_instancetypes():
    sync_instancetype = AliSyncInstanceTypes(AccessKeyId, AccessKeySecret)
    sync_instancetype.sync_instancetype()

@celery.task
def run_sync_securitygroup():
    sync_securitygroup = AliSyncSecurityGroup(AccessKeyId, AccessKeySecret)
    sync_securitygroup.sync_security_group()

@celery.task(bind=True)
def run_sync_asset_amount(self,nodeid=None):
    if nodeid:
        NodeAmount.sync_node_assets(nodeid)
    else:
        NodeAmount.sync_root_assets()

@celery.task(bind=True)
def create_asset(self,created_by,template_data,amount):
    taskid = self.request.id
    createtask = Asset_Create_Record.create(
        taskid=taskid,
        amount=amount,AssetType='ecs',InstanceName=template_data['InstanceName'],
        RegionId=template_data['RegionId'],created_by=created_by,
        CreateTime=datetime.now()
    )
    aly_create = Aly_Create_Asset(template_data,amount,AccessKeyId, AccessKeySecret)
    aly_create.CreateInstanceFromcopy()
    aly_create.startInstances()
    createtask.isSuccess = True
    createtask.save()