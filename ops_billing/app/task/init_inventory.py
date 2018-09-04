# -*- coding: utf-8 -*-
from app.models import Asset,SystemUser
from app import get_basedir
import os,stat

__all__ = [
    'InitInventory'
]

class InitInventory(object):
    def __init__(self, hostname_list, run_as_sudo=False, run_as=None):
        self.hostname_list = hostname_list
        self.using_root = run_as_sudo
        self.run_as = run_as

    def get_hostlist(self):
        host_list = []
        assets = Asset.select().where(Asset.id.in_(self.hostname_list))
        for asset in assets:
            info = self.convert_to_ansible(asset, run_as_sudo=self.using_root)
            host_list.append(info)
        if self.run_as:
            run_user_info = self.get_run_user_info()
            for host in host_list:
                host.update(run_user_info)
        return host_list

    def convert_to_ansible(self, asset, run_as_sudo=False):
        info = {
            'id': asset.id.hex,
            'hostname': asset.InstanceName,
            'regionid':asset.RegionId,
            'ip': asset.InnerAddress,
            'port': asset.sshport,
            'vars': dict(),
            'groups': [],
        }
        if run_as_sudo:
            info['become'] = {'method':'sudo','user':'root','pass':''}

        for node in asset.node.objects():
            info["groups"].append(node.value)
        return info

    def get_run_user_info(self):
        system_user = SystemUser.get_or_none(id=self.run_as)
        if not system_user:
            return {}
        else:
            return system_user._to_secret_json()