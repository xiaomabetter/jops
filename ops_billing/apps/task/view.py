from flask import render_template
from wtforms import StringField
from wtforms.widgets import CheckboxInput
from apps.auth import login_required
from .form import Task_Ansible_Form
from apps import get_basedir
from . import task
import os

@task.route('/ansible/run',methods=['GET'])
@login_required()
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
