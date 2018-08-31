# ~*~ coding: utf-8 ~*~
from app import get_logger
from collections import namedtuple
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook.play import Play
import ansible.constants as C
from ansible.utils.display import Display
from .callback import AdHocResultCallback,PlaybookResultCallBack
from .exceptions import AnsibleError

__all__ = ["AdHocRunner", "PlayBookRunner"]
C.HOST_KEY_CHECKING = False
logger = get_logger(__name__)

class CustomDisplay(Display):
    def display(self, msg, color=None, stderr=False, screen_only=False, log_only=False):
        pass

display = CustomDisplay()

Options = namedtuple('Options', [
    'listtags', 'listtasks', 'listhosts', 'syntax', 'connection',
    'module_path', 'forks', 'remote_user', 'private_key_file', 'timeout',
    'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
    'scp_extra_args', 'become', 'become_method', 'become_user',
    'verbosity', 'check', 'extra_vars', 'playbook_path', 'passwords',
    'diff', 'gathering', 'remote_tmp',
])

def get_default_options():
    options = Options(
        listtags=False,
        listtasks=False,
        listhosts=False,
        syntax=False,
        timeout=10,
        connection='ssh',
        module_path='',
        forks=10,
        remote_user='root',
        private_key_file=None,
        ssh_common_args="",
        ssh_extra_args="",
        sftp_extra_args="",
        scp_extra_args="",
        become=None,
        become_method=None,
        become_user=None,
        verbosity=None,
        extra_vars=[],
        check=False,
        playbook_path='/etc/ansible/' ,
        passwords=None,
        diff=False,
        gathering='implicit',
        remote_tmp='/tmp/.ansible'
    )
    return options

class PlayBookRunner:
    loader_class = DataLoader
    variable_manager_class = VariableManager
    options = get_default_options()

    def __init__(self, playbook_file,inventory=None,options=None,taskid=None):
        if options:
            self.options = options
        C.RETRY_FILES_ENABLED = False
        self.inventory = inventory
        self.playbook_file = playbook_file
        self.loader = self.loader_class()
        self.results_callback = PlaybookResultCallBack(taskid=taskid)
        self.variable_manager = self.variable_manager_class(
            loader=self.loader, inventory=self.inventory
        )

    def run(self):
        executor = PlaybookExecutor(
            playbooks=[self.playbook_file],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=None,
        )
        executor._tqm._stdout_callback = self.results_callback
        executor.run()
        executor._tqm.cleanup()
        return executor._tqm._stdout_callback.std_lines


class AdHocRunner:
    results_callback_class = AdHocResultCallback
    results_callback = None
    loader_class = DataLoader
    variable_manager_class = VariableManager
    default_options = get_default_options()

    def __init__(self, inventory, options=None):
        self.options = self.update_options(options)
        self.inventory = inventory
        self.loader = DataLoader()
        self.variable_manager = VariableManager(
            loader=self.loader, inventory=self.inventory
        )

    def get_result_callback(self, file_obj=None):
        return self.__class__.results_callback_class(file_obj=file_obj)

    @staticmethod
    def check_module_args(module_name, module_args=''):
        if module_name in C.MODULE_REQUIRE_ARGS and not module_args:
            err = "No argument passed to '%s' module." % module_name
            raise AnsibleError(err)

    def check_pattern(self, pattern):
        if not pattern:
            raise AnsibleError("Pattern `{}` is not valid!".format(pattern))
        if not self.inventory.list_hosts("all"):
            raise AnsibleError("Inventory is empty.")
        if not self.inventory.list_hosts(pattern):
            raise AnsibleError(
                "pattern: %s  dose not match any hosts." % pattern
            )

    def clean_tasks(self, tasks):
        cleaned_tasks = []
        for task in tasks:
            self.check_module_args(task['action']['module'], task['action'].get('args'))
            cleaned_tasks.append(task)
        return cleaned_tasks

    def update_options(self, options):
        if options and isinstance(options, dict):
            options = self.__class__.default_options._replace(**options)
        else:
            options = self.__class__.default_options
        return options

    def run(self, tasks, pattern,play_name='Ansible Ad-hoc', gather_facts='no', file_obj=None):
        self.check_pattern(pattern)
        cleaned_tasks = self.clean_tasks(tasks)

        play_source = dict(
            name=play_name,
            hosts=pattern,
            gather_facts=gather_facts,
            tasks=cleaned_tasks
        )

        play = Play().load(
            play_source,
            variable_manager=self.variable_manager,
            loader=self.loader,
        )

        tqm = TaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=self.options.passwords,
        )
        tqm._stdout_callback = AdHocResultCallback()
        print("Get matched hosts: {}".format(
            self.inventory.get_matched_hosts(pattern)
        ))

        try:
            tqm.run(play)
            return tqm._stdout_callback
        except Exception as e:
            raise AnsibleError(e)
        finally:
            tqm.cleanup()
            self.loader.cleanup_all_tmp_files()
