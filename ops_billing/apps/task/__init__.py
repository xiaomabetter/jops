from flask import Blueprint

task = Blueprint('task', __name__)

from .view import *

from .tasks.ansibe import run_ansible_playbook,run_ansible_module
from .tasks.asset import *