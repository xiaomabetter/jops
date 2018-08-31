#!/usr/bin/env python
# coding: utf-8
from ansible.plugins.callback.default import CallbackModule
from .display import TeeObj
from ansible.plugins.callback import CallbackBase
from ansible.executor.task_result import TaskResult as TypeTaskResult
from ansible.executor.stats import AggregateStats as TypeAggregateStats
from ansible.playbook.task import Task as TypeTask
from ansible.playbook.play import Play as TypePlay
from app.models.base import OpsCeleryRedis
import logging,sys

class AdHocResultCallback(CallbackModule):
    def __init__(self, display=None, options=None,file_obj=None):
        self.results_raw = dict(ok={}, failed={}, unreachable={}, skipped={})
        self.results_summary = dict(contacted=[], dark={})
        super().__init__()
        if file_obj is not None:
            sys.stdout = TeeObj(file_obj)

    def gather_result(self, t, res):
        self._clean_results(res._result, res._task.action)
        host = res._host.get_name()
        task_name = res.task_name
        task_result = res._result

        if self.results_raw[t].get(host):
            self.results_raw[t][host][task_name] = task_result
        else:
            self.results_raw[t][host] = {task_name: task_result}
        self.clean_result(t, host, task_name, task_result)

    def clean_result(self, t, host, task_name, task_result):
        contacted = self.results_summary["contacted"]
        dark = self.results_summary["dark"]
        if t in ("ok", "skipped") and host not in dark:
            if host not in contacted:
                contacted.append(host)
        else:
            if dark.get(host):
                dark[host][task_name] = task_result.values
            else:
                dark[host] = {task_name: task_result}
            if host in contacted:
                contacted.remove(host)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.gather_result("failed", result)
        super().v2_runner_on_failed(result, ignore_errors=ignore_errors)

    def v2_runner_on_ok(self, result):
        self.gather_result("ok", result)
        super().v2_runner_on_ok(result)

    def v2_runner_on_skipped(self, result):
        self.gather_result("skipped", result)
        super().v2_runner_on_skipped(result)

    def v2_runner_on_unreachable(self, result):
        self.gather_result("unreachable", result)
        super().v2_runner_on_unreachable(result)


class PlaybookResultCallBack(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'webscocket'
    CALLBACK_NEEDS_WHITELIST = True

    RC_SUCC = 0
    RC_FAIL = 1

    ITEM_STATUS = ('failed', 'changed', 'skipped', 'unreachable', 'ok')

    def __init__(self,taskid=None):
        super(PlaybookResultCallBack, self).__init__()
        self.current_taskname = ''
        self.std_lines = dict()
        self.taskid = taskid

    def reset_output(self):
        self.std_lines.clear()

    def gather_result(self, result):
        if self.taskid :
            OpsCeleryRedis.lpush(self.taskid, result)

    def v2_on_any(self, *args, **kwargs):
        for crucial in args:
            if isinstance(crucial, TypeTaskResult) :
                item = self._fill_item_from_taskresult(
                    init_data=dict(
                        host=crucial._host.get_name(),
                        task_name=crucial._task.get_name(),
                        rc=self.RC_SUCC
                    ), detail=crucial._result)
                self.gather_result(item)
            elif isinstance(crucial, TypeTask):
                pass
            elif isinstance(crucial, TypePlay):
                pass
            elif isinstance(crucial, TypeAggregateStats):
                hosts = sorted(crucial.processed.keys())
                rmsg = dict(
                    task_name=self.current_taskname,
                    msg=dict(kind='play_summarize', list=dict())
                )
                for h in hosts:
                    t = crucial.summarize(h)
                    rmsg['msg']['list'][h] = dict(
                        host=h,unreachable=t[
                            'unreachable'], skipped=t['skipped'],
                        ok=t['ok'], changed=t[
                            'changed'], failures=t['failures']
                    )
                self.std_lines = rmsg
            elif isinstance(crucial, str):
                wsmsg = dict(
                    rc=self.RC_SUCC,
                    task_name=self.current_taskname,
                    msg=dict(kind='desc', unique=crucial)
                )
                self.gather_result(wsmsg)
            else:
                logging.info(
                    'Found a new type in result [%s]' % (type(crucial)))

    def _fill_item_from_taskresult(self, init_data, detail):
        item = dict()
        if isinstance(init_data, dict):
            item = init_data

        if detail.get('rc'):
            item['rc'] = detail['rc']

        for s in self.ITEM_STATUS:
            if detail.get(s):
                item[s] = detail[s]
                if s in ('failed', 'unreachable'):
                    item['rc'] = self.RC_FAIL

        if detail.get('stdout') and detail['stdout'] != '':
            item['stdout'] = detail['stdout']

        if detail.get('stderr') and detail['stderr'] != '':
            item['stderr'] = detail['stderr']

        if detail.get('msg') and detail['msg'] != '':
            item['msg'] = detail['msg']

        if detail.get('invocation') and detail['invocation'].get('module_args') and detail['invocation']['module_args'].get('_raw_params'):
            item['cmd'] = detail['invocation'][
                'module_args']['_raw_params']
        return item

    def v2_playbook_on_task_start(self, task, is_conditional):
        wsmsg = dict(
            task_name=self.current_taskname,
            msg=dict(kind='task_start', value=task.get_name())
        )
        self.gather_result(wsmsg['msg'])

    def v2_playbook_on_play_start(self, play):
        palyname = play.get_name().strip()
        task = list()
        host = list()
        for t in play.get_tasks():
            tmp = [i.get_name() for i in t]
            task = list(set(task + tmp))
        for h_str in play._attributes.get('hosts'):
            h = h_str.split(',')
            host = list(set(host + h))

        self.current_taskname = palyname
        wsmsg = dict(
            task_name=palyname,
            task_list = task,
            host_list = host,
            msg=dict(kind='play_start', value=palyname)
        )
        self.gather_result(wsmsg['msg'])
        self.reset_output()