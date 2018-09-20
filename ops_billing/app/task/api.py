from app import get_logger,config
from flask import jsonify
from flask_restful import Resource,reqparse
from app.auth import login_required,get_login_user
from app.utils import falseReturn,trueReturn
from app.models import OpsCeleryRedis
from .tasks.asset import run_sync_bill,run_sync_asset,run_sync_securitygroup,\
    run_sync_zones,run_sync_images,run_sync_instancetypes,run_sync_vswitches
from .tasks.ansibe import run_ansible_module,run_ansible_playbook
from .tasks.asset import sync_ldap_user
from .init_inventory import InitInventory
import json

logger = get_logger(__name__)

__all__ = ['TaskApi','AlySyncApi','TaskAnsRunApi']

class TaskApi(Resource):
    @login_required
    def get(self,taskid):
        args = reqparse.RequestParser().add_argument('length', type=int,location='args').parse_args()
        celery_task_id = f'celery-task-meta-{taskid}'
        length = args.get('length')
        if length is not None:
            is_over = OpsCeleryRedis.get(celery_task_id)
            if OpsCeleryRedis.exists(taskid):
                present_length = OpsCeleryRedis.llen(taskid)
                if present_length > length:
                    results = OpsCeleryRedis.lrange(taskid, -present_length, -length)
                    data = dict(results=[r.decode() for r in results],is_suspended=False, length=present_length)
                elif present_length <= length and not is_over:
                    data = dict(results=[], is_suspended=False, length=present_length)
                else:
                    result = json.loads(is_over.decode())['result']
                    data = dict(results=[result], is_suspended=True, length=present_length)
                return jsonify(trueReturn(data))
            else:
                return jsonify(trueReturn(dict(results=[], is_suspended=False, length=0)))
        else:
            if OpsCeleryRedis.exists(celery_task_id):
                return jsonify(trueReturn(json.loads(OpsCeleryRedis.get(celery_task_id))))
            else:
                return jsonify(falseReturn())

class AlySyncApi(Resource):
    @login_required
    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('task_name', type=str, location=['json', 'form'],required=True) \
            .add_argument('day_from', type=str, location=['json', 'form']) \
            .add_argument('day_to', type=str, location=['json', 'form']) \
            .add_argument('asset_type', type=str, location=['json','form']).parse_args()
        task_name = args.get('task_name')
        default_queue = config.get('CELERY', 'CELERY_DEFAULT_QUEUE')
        if task_name == 'syncasset':
            if not args.get('asset_type'):
                return jsonify(falseReturn(msg=u'确少参数'))
            r = run_sync_asset.apply_async([args.get('asset_type')],queue=default_queue)
        elif task_name == 'syncbill':
            if not args.get('day_from') or not args.get('day_to'):
                return jsonify(falseReturn(msg=u'确少参数'))
            user = get_login_user()
            username = user.username
            r = run_sync_bill.apply_async([username, args.get('day_from'),args.get('day_to')],queue=default_queue)
        elif task_name == 'sync_instance_types':
            r = run_sync_instancetypes.apply_async(queue=default_queue)
        elif task_name == 'sync_instance_securitygroup':
            r = run_sync_securitygroup.apply_async(queue=default_queue)
        elif task_name == 'sync_instance_zones':
            r = run_sync_zones.apply_async(queue=default_queue)
        elif task_name == 'sync_instance_images':
            r = run_sync_images.apply_async(queue=default_queue)
        elif task_name == 'sync_vswitches':
            r = run_sync_vswitches.apply_async(queue=default_queue)
        elif task_name == 'sync_ldapusers':
            r = sync_ldap_user.apply_async(queue=default_queue)
        return jsonify(trueReturn(r.id,msg='任务提交成功'))

class TaskAnsRunApi(Resource):
    @login_required
    def post(self):
        parse = reqparse.RequestParser()
        for arg in ('name','run_as'):
            parse.add_argument(arg, type=str,location='form', required=True)
        for arg in ('module','command','playbook'):
            parse.add_argument(arg,type=str,location='form')
        args = parse.add_argument('assets', type=str, action='append', location='form', required=True) \
            .add_argument('ismodule', type=bool, location='form')\
            .add_argument('run_as_sudo', type=bool,location='form').parse_args()

        inventory = InitInventory(hostname_list=args.get('assets'),
                              run_as_sudo=args.get('run_as_sudo'),
                              run_as=args.get('run_as'))
        host_list = inventory.get_hostlist()
        regin_host_list = {}
        task_ids = []
        for host in host_list:
            if not isinstance(regin_host_list.get(host.get('regionid')),list):
                regin_host_list[host.get('regionid')] = []
            regin_host_list[host.get('regionid')].append(host)

        if args.get('ismodule') :
            if not args.get('command')  and not args.get('module') :
                return jsonify(falseReturn(msg=u'缺少参数,选择执行模块及命令'))
            else:
                tasks = [{"action": {"module": args.get('module'), "args":
                    args.get('command')}, "name": args.get('name')}]
                for region,host_list in regin_host_list.items():
                    r = run_ansible_module.apply_async([host_list,tasks],queue=region)
                    task_ids.append(r.id)
                return jsonify(trueReturn(dict(taskid=task_ids,ismodule=True)))
        else:
            if not args.get('playbook') :
                return jsonify(falseReturn(msg='需选择执行的playbook'))
            for region, host_list in regin_host_list.items():
                r = run_ansible_playbook.apply_async([host_list, args.get('playbook')], queue=region)
                task_ids.append(r.id)
            return jsonify(trueReturn(dict(taskid=task_ids, ismodule=False)))


