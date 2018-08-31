from app import celery,get_logger,get_basedir
from app.task.ansible import AdHocRunner,PlayBookRunner,Inventory,AnsibleError
from celery.signals import worker_process_init

logger = get_logger(__name__)

@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    from multiprocessing import current_process
    try:
        current_process()._config
    except AttributeError:
        current_process()._config = {'semprefix': '/mp'}

@celery.task
def run_ansible_module(run_as,hostname_list,tasks,run_as_sudo=False):
    inventory = Inventory(
        hostname_list=hostname_list, run_as_sudo=run_as_sudo,run_as=run_as
    )
    runner = AdHocRunner(inventory)
    try:
        result = runner.run(tasks,'all')
        if result is not None:
            return result.results_raw
    except AnsibleError as e:
        logger.warn("Failed run adhoc {}, {}".format('', e))
        pass

@celery.task(bind=True)
def run_ansible_playbook(self,run_as,hostname_list,playbook,run_as_sudo=False):
    taskid = self.request.id
    inventory = Inventory(
        hostname_list=hostname_list, run_as_sudo=run_as_sudo,run_as=run_as
    )
    playbook_file = get_basedir() + '/task/playbooks/' + playbook
    runner = PlayBookRunner(playbook_file=playbook_file,inventory=inventory,taskid=taskid)
    result = runner.run()
    return result