from app import get_logger
from app.task.asset import SyncBills,SyncAliAssets,NodeAmount,\
        Aly_Create_Asset,AliSyncImages,AliSyncZones,AliSyncSecurityGroup,\
        AliSyncInstanceTypes,AliSyncVSwitches
from app.task.user import sync_ldapusers
from celery.signals import worker_process_init
from app.models.base import initcelery
from conf import aliyun
logger = get_logger(__name__)

AccessKeyId = aliyun.AccessKeyId
AccessKeySecret = aliyun.AccessKeySecret

celery = initcelery()

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
def run_sync_asset(asset_type,is_update):
    sync_asset = SyncAliAssets(AccessKeyId, AccessKeySecret)
    sync_asset.aly_sync_asset(asset_type,is_update)

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

@celery.task
def run_sync_vswitches():
    sync_vswitches = AliSyncVSwitches(AccessKeyId, AccessKeySecret)
    sync_vswitches.sync_vswitchs()

@celery.task(bind=True)
def run_sync_asset_amount(self,nodeid=None):
    if nodeid:
        NodeAmount.sync_node_assets(nodeid)
    else:
        NodeAmount.sync_root_assets()

def create_asset_tryRun(template_data,amount):
    aly_create = Aly_Create_Asset(template_data,amount,AccessKeyId, AccessKeySecret)
    aly_create.CreateInstanceFromcopy(DryRun=True)
    tryRun_msg = aly_create.startInstances()
    return tryRun_msg

@celery.task(bind=True)
def create_asset(self,created_by,template_data,amount):
    from app.models.asset import Create_Asset_History
    taskid = self.request.id
    createtask = Create_Asset_History.create(
        taskid=taskid,
        amount=amount,AssetType='ecs',InstanceName=template_data['InstanceName'],
        RegionId=template_data['RegionId'],created_by=created_by
    )
    aly_create = Aly_Create_Asset(template_data,amount,AccessKeyId, AccessKeySecret)
    aly_create.CreateInstanceFromcopy()
    aly_create.startInstances()
    createtask.isSuccess = True
    createtask.save()

@celery.task
def sync_ldap_user():
    sync_ldapusers()