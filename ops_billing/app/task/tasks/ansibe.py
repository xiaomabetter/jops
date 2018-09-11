from app import get_logger,config
from app.task.ansible import AdHocRunner,PlayBookRunner,Inventory,AnsibleError
from celery.signals import worker_process_init
from app.models.base import initcelery

celery = initcelery()

logger = get_logger(__name__)

@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    from multiprocessing import current_process
    try:
        current_process()._config
    except AttributeError:
        current_process()._config = {'semprefix': '/mp'}

@celery.task(name='run_ansible_module')
def run_ansible_module(host_list,tasks):
    inventory = Inventory(host_list=host_list)
    runner = AdHocRunner(inventory)
    try:
        result = runner.run(tasks,'all')
        if result is not None:
            return result.results_raw
    except AnsibleError as e:
        logger.warn("Failed run adhoc {}, {}".format('', e))
        pass

@celery.task(bind=True,name='run_ansible_playbook')
def run_ansible_playbook(self,host_list,playbook):
    taskid = self.request.id
    inventory = Inventory(host_list=host_list)
    playbook_file = config.get('DEFAULT','Ansible_Base_Dir') + '/' + playbook
    print(playbook_file)
    runner = PlayBookRunner(playbook_file=playbook_file,inventory=inventory,taskid=taskid)
    result = runner.run()
    return result