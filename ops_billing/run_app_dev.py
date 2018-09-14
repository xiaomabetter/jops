# -*- coding: utf-8 -*-
from playhouse.flask_utils import FlaskDB
from app import create_app
from app.asset.api import *
from app.perm.api import *
from app.user.api import *
from app.task.api import *
from flask_restful import Api
from app.models.base import db
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
api = Api(app)
FlaskDB(app, db)
#asset
api.add_resource(AssetsApi,'/api/asset/v1/assets',endpoint = 'assets-api.assets_api')
api.add_resource(AssetApi,'/api/asset/v1/asset/<assetid>',endpoint = 'assets-api.asset_api')
api.add_resource(AssetCreateApi,'/api/asset/v1/create',endpoint = 'assets-api.asset_create_api')
api.add_resource(ImagesApi,'/api/asset/v1/images',endpoint = 'assets-api.images_api')
api.add_resource(SecurityGroupsApi,'/api/asset/v1/secgroup',endpoint = 'assets-api.securitygroups_api')
api.add_resource(TemplatesApi,'/api/asset/v1/templates',endpoint = 'assets-api.templates_api')
api.add_resource(TemplateApi,'/api/asset/v1/template/<templateid>',endpoint = 'assets-api.template_api')
api.add_resource(AssetAccountsApi,'/api/asset/v1/asset/<assetid>/account',
                                                endpoint = 'assets-api.asset_accounts_api')
api.add_resource(ServicesApi,'/api/asset/v1/services',endpoint = 'assets-api.services_api')
api.add_resource(ServiceApi,'/api/asset/v1/service/<serviceid>',endpoint = 'assets-api.service_api')
api.add_resource(ServiceAssetApi,'/api/asset/v1/service/<serviceid>/asset/<assetid>',
                                                            endpoint = 'assets-api.service_asset_api')
api.add_resource(AssetAccountApi,'/api/asset/v1/asset/<assetid>/account/<accountid>',
                                                                endpoint = 'assets-api.asset_account_api')
api.add_resource(AssetUserApi,'/api/asset/v1/asset/<assetid>/user',endpoint = 'assets-api.asset_users_api')
api.add_resource(NodesApi,'/api/asset/v1/nodes',endpoint = 'assets-api.nodes_api')
api.add_resource(NodeApi,'/api/asset/v1/node/<nodeid>',endpoint = 'assets-api.node_api')
api.add_resource(NodeAssetApi,'/api/asset/v1/node/<nodeid>/asset',endpoint = 'assets-api.node_assets_api')
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
api.add_resource(UserLogin,'/api/user/v1/token',endpoint = 'user-api.user-login-api')
#task
api.add_resource(TaskApi,'/api/task/v1/task/<taskid>',endpoint = 'task-api.task_api')
api.add_resource(AlySyncApi,'/api/task/v1/alysync',endpoint = 'task-api.aly-sync-task')
api.add_resource(TaskAnsRunApi,'/api/task/v1/ansible/run',endpoint = 'task-api.task_ansrun_api')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5050)
