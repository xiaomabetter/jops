from app import get_logger, get_config
from flask import render_template
from wtforms import StringField
from wtforms.widgets import CheckboxInput
from app.auth import login_required
from app.utils.utils import model_to_form
from .form import Task_Ansible_Form,Task_Create_Form,Syncbill_Form
from app import get_basedir
from app.models.task import Tasks
from . import task
import os

logger = get_logger(__name__)
cfg = get_config()

@task.route('/task/tasks/list',methods=['GET'])
@login_required
def task_list():
    return render_template('task/task_list.html')

@task.route('/task/tasks/create',methods=['GET'])
@login_required
def task_create():
    form = Task_Create_Form()
    return render_template('task/task_create.html',form=form)

@task.route('/task/tasks/update/<taskid>',methods=['GET'])
@login_required
def task_update(taskid):
    form = Task_Create_Form()
    task = Tasks.select().where(Tasks.id == taskid)
    model_to_form(task,form)
    return render_template('task/task_update.html',form=form,taskid=taskid)

@task.route('/task/tasks/run/<taskid>',methods=['GET'])
@login_required
def task_run(taskid):
    task = Tasks.select().where(Tasks.id == taskid).get()
    form = Syncbill_Form()
    form.task_name.data = task.taskname
    return render_template('task/task_run.html',form=form,taskname=task.taskname)

@task.route('/task/ansible/run',methods=['GET'])
@login_required
def ansible_run():
    roles = {}
    role_path = get_basedir() + '/task/playbooks/roles'
    categorys = os.listdir(role_path)
    for category in categorys:
        rolelist = os.listdir(role_path + '/' + category)
        roles[category] = rolelist
        for role in rolelist:
            setattr(Task_Ansible_Form, role, StringField(role,widget=CheckboxInput(),render_kw={"class":"form-control"}))
    form = Task_Ansible_Form()
    return render_template('task/task_adhoc.html',form=form)