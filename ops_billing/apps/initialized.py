# -*- coding: utf-8 -*-
from playhouse.flask_utils import FlaskDB
from apps import create_app
from .asset.api import *
from .perm.api import *
from .user.api import *
from .task.api import *
from .platform.api import *
from flask_restful import Api
from apps.models.base import db
import os

class MFlaskDB(FlaskDB):
    def connect_db(self):
        if self.database.is_closed():
            self.database.connect()

def initialize():
    initapp = create_app(os.getenv('FLASK_CONFIG') or 'default')
    api = Api(initapp)
    MFlaskDB(initapp, db)
    #asset
    api.add_resource(AssetsApi,'/api/asset/v1/assets',endpoint = 'assets-api.assets_api')
    api.add_resource(AssetApi,'/api/asset/v1/asset/<assetid>',endpoint = 'assets-api.asset_api')
    api.add_resource(AssetCreateApi,'/api/asset/v1/create',endpoint = 'assets-api.asset_create_api')
    api.add_resource(ImagesApi,'/api/asset/v1/images',endpoint = 'assets-api.images_api')
    api.add_resource(VSwitchesApi,'/api/asset/v1/vswitches',endpoint = 'assets-api.vswitches_api')
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
    api.add_resource(SystemUsersApi,'/api/permission/v1/system-users',endpoint = 'perm-api.systemusers_api')
    api.add_resource(SystemUserApi,'/api/permission/v1/system-user/<sysuserid>',endpoint = 'perm-api.systemuser_api')
    api.add_resource(PermissionGroupsApi,'/api/permission/v1/permission_groups',endpoint = 'perm-api.permission_groups_api')
    api.add_resource(PermissionGroupApi,'/api/permission/v1/permission_group/<pgid>',endpoint = 'perm-api.permission_group_api')
    api.add_resource(AssetPermissionsApi,'/api/permission/v1/permissions',endpoint = 'perm-api.asset_permissions_api')
    api.add_resource(AssetPermissionApi,'/api/permission/v1/permission/<permissionid>',endpoint = 'perm-api.asset_permission_api')
    api.add_resource(PlatformAuthorizationsApi,'/api/permission/v1/platforms',endpoint = 'perm-api.platforms_api')
    api.add_resource(PlatformAuthorizationApi,'/api/permission/v1/platform/<platform_permission_id>',endpoint = 'perm-api.platform_api')
    api.add_resource(UserGrantAssets,'/api/permission/v1/user/<uid>/assets',endpoint = 'perm-api.perm_user_assets')
    api.add_resource(UserGrantNodes,'/api/permission/v1/user/<uid>/nodes-assets',endpoint = 'perm-api.perm_user_nodes')
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
    #platform
    api.add_resource(PlatformsApi,'/api/platform/v1/platforms',endpoint = 'platform-api.platforms_api')
    api.add_resource(PlatformApi,'/api/platform/v1/platform/<platformid>',endpoint = 'platform-api.platform_api')
    api.add_resource(PlatformProxyApi,'/api/platform/v1/platformproxy',endpoint = 'platform-api.platforms_proxy_api')
    api.add_resource(PlatformUrlMappingPortApi,'/api/platform/v1/<port>/platform',endpoint = 'platform-api.platform_url_mapping_api')
    return initapp


app = initialize()
