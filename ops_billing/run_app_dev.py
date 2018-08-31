# -*- coding: utf-8 -*-
from app import create_app
from app.asset.api import *
from app.perm.api import *
from app.user.api import *
from app.task.api import *
from app.terminal.api import *
from flask_restful import Api
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
api = Api(app)
#asset
api.add_resource(AssetsApi,'/api/asset/v1/assets',endpoint = 'assets-api.assets_api')
api.add_resource(AssetInstanceApi,'/api/asset/v1/asset/<assetid>',endpoint = 'assets-api.asset_api')
api.add_resource(AssetCreateApi,'/api/asset/v1/create',endpoint = 'assets-api.asset_create_api')
api.add_resource(ImagesApi,'/api/asset/v1/images',endpoint = 'assets-api.images_api')
api.add_resource(SecurityGroupsApi,'/api/asset/v1/secgroup',endpoint = 'assets-api.securitygroups_api')
api.add_resource(TemplatesApi,'/api/asset/v1/templates',endpoint = 'assets-api.templates_api')
api.add_resource(TemplateApi,'/api/asset/v1/template/<templateid>',endpoint = 'assets-api.template_api')
api.add_resource(AssetInstanceAccountApi,'/api/asset/v1/asset/<assetid>/account',
                 endpoint = 'assets-api.asset_instance_account_api')
api.add_resource(ServicesApi,'/api/asset/v1/services',endpoint = 'assets-api.services_api')
api.add_resource(ServiceInstanceApi,'/api/asset/v1/service/<serviceid>',endpoint = 'assets-api.service_api')
api.add_resource(ServiceInstanceAssetInstanceApi,'/api/asset/v1/service/<serviceid>/asset/<assetid>',
                 endpoint = 'assets-api.service_instance_asset_instance_api')
api.add_resource(AssetInstanceAccountInstanceApi,'/api/asset/v1/asset/<assetid>/account/<accountid>',
                 endpoint = 'assets-api.asset_instance_account_instance_api')
api.add_resource(AssetInstanceUserApi,'/api/asset/v1/asset/<assetid>/user',
                 endpoint = 'assets-api.asset_instance_user_api')
api.add_resource(NodesApi,'/api/asset/v1/nodes',endpoint = 'assets-api.nodes_api')
api.add_resource(NodeInstanceApi,'/api/asset/v1/node/<nodeid>',endpoint = 'assets-api.node_api')
api.add_resource(NodeInstanceAssetApi,'/api/asset/v1/node/<nodeid>/asset',endpoint = 'assets-api.node_asset_api')
#perm
api.add_resource(SystemUsersApi,'/api/asset_permission/v1/system-user/list',
                 endpoint = 'perm-api.systemusers_api')
api.add_resource(SystemUserApi,'/api/asset_permission/v1/system-user/<sysuserid>',
                 endpoint = 'perm-api.systemuser_api')
api.add_resource(AssetPermissionsApi,'/api/asset_permission/v1/permissions',
                 endpoint = 'perm-api.asset_permissions_api')
api.add_resource(AssetPermissionApi,'/api/asset_permission/v1/permission/<permissionid>',
                 endpoint = 'perm-api.asset_permission_api')
api.add_resource(UserGrantAssets,'/api/asset_permission/v1/user/<uid>/assets',
                 endpoint = 'perm-api.perm_user_assets')
api.add_resource(UserGrantNodes,'/api/asset_permission/v1/user/<uid>/nodes-assets',
                 endpoint = 'perm-api.perm_user_nodes')
#user
api.add_resource(UsersApi,'/api/user/v1/users',endpoint = 'user-api.users_api')
api.add_resource(UserApi,'/api/user/v1/user/<userid>',endpoint = 'user-api.user_api')
api.add_resource(GroupsApi,'/api/v1/group/groups',endpoint = 'user-api.groups_api')
api.add_resource(GroupApi,'/api/v1/group/<groupid>',endpoint = 'user-api.group_api')
api.add_resource(UserAuth,'/api/user/v1/auth',endpoint = 'user-api.user-auth')
api.add_resource(AuthToken,'/api/user/v1/token',endpoint = 'user-api.auth-token')
#task
api.add_resource(TasksApi,'/api/task/v1/tasks',endpoint = 'task-api.tasks_api')
api.add_resource(TaskApi,'/api/task/v1/task/<taskid>',endpoint = 'task-api.task_api')
api.add_resource(AlySyncApi,'/api/task/v1/alysync',endpoint = 'task-api.aly-sync-task')
api.add_resource(TaskAnsRunApi,'/api/task/v1/ansible/run',endpoint = 'task-api.task_ansrun_api')
#terminal
api.add_resource(TerminalListApi,'/api/terminal/v1/list',endpoint = 'terminal-api.terminal-list')
api.add_resource(TerminalDetailApi,'/api/terminal/v1/<tid>/detail',endpoint = 'terminal-api.terminal-detail')
api.add_resource(TerminalRegisterApi,'/api/terminal/v1/register',endpoint = 'terminal-api.terminal-register')
api.add_resource(TerminalTokenApi,'/api/terminal/v1/access-key',endpoint = 'terminal-api.terminal-access-key')
api.add_resource(TerminalStatusApi,'/api/terminal/v1/status',endpoint = 'terminal-api.terminal-status')
api.add_resource(SessionCommandApi,'/api/terminal/v1/command',endpoint = 'terminal-api.session-command')
api.add_resource(SessionListApi,'/api/terminal/v1/sessions',endpoint = 'terminal-api.session-list')
api.add_resource(SessionReplayApi,'/api/terminal/v1/sessions/<sid>/replay',endpoint = 'terminal-api.session-replay')
api.add_resource(TaskReplayApi,'/api/terminal/v1/task/<task_id>',endpoint = 'terminal-api.task-replay')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5050)
