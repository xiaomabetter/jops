# coding: utf-8
from celery import shared_task, subtask

from common.utils import get_logger, get_object_or_none
from .models import Task
from .ansible import AdHocRunner, AnsibleError,CommandRunner
from .inventory import JMSInventory
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
def run_cmd_task(tasks,hostname_list, callback=None, **kwargs):
    _option = {"timeout": 10, "forks": 10}
    inventory = JMSInventory(hostname_list)
    print(inventory)
    runner = AdHocRunner(inventory, options=_option)
    try:
        result = runner.run(tasks=tasks,pattern='all')
    except AnsibleError as e:
        logger.warn("Failed run adhoc {}".format(e))
        pass


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

@shared_task
def hello(name, callback=None):
    print("Hello {}".format(name))
    if callback is not None:
        subtask(callback).delay("Guahongwei")


@shared_task
def hello_callback(result):
    print(result)
    print("Hello callback")
