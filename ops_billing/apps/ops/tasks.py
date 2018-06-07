# coding: utf-8
from celery import shared_task, subtask

from common.utils import get_logger, get_object_or_none
from .models import Task
from assets.models import Asset
from .ansible import AdHocRunner, AnsibleError,CommandRunner
from .ansible.inventory import BaseInventory
from .custom.cost import Bill
from .custom.aly  import Aliyun

logger = get_logger(__file__)

def rerun_task():
    pass

@shared_task
def run_ansible_task(tid, callback=None, **kwargs):
    """
    :param tid: is the tasks serialized data
    :param callback: callback function name
    :return:
    """
    task = get_object_or_none(Task, id=tid)
    if task:
        result = task.run()
        if callback is not None:
            subtask(callback).delay(result, task_name=task.name)
        return result
    else:
        logger.error("No task found")

@shared_task
def cmd_deploy_run(module,cmd,hostids,callback=None, **kwargs):
    host_data = []
    obs = Asset.objects.filter(id__in=hostids)
    for i in obs:
        host_data.append(
            {
                "hostname":i.hostname,
                "ip":i.ip,
                "port":i.port,
                "username":"easemob",
                "password":''
            }
        )
    inventory = BaseInventory(host_data)
    runner = CommandRunner(inventory)
    res = runner.execute(cmd, 'all')
    if res:
        print(res.results_command)
        print(res.results_raw)

@shared_task
def run_sync_bill_task(day_from,day_to, callback=None, **kwargs):
    r = Bill('LTAIvjpauewMGGPa','KEIOPsuOVihcqd90ruKsSR1VJJQPav')
    r.handle(day_from,day_to)

@shared_task
def run_sync_assets_task(asset_category, callback=None, **kwargs):
    r = Aliyun()
    if asset_category == 'ecs':
        r.aly_sync_asset()
    elif asset_category == 'slb':
        r.aly_sync_assetslb()
    elif asset_category == 'rds':
        r.aly_sync_assetrds()


