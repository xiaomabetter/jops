# coding:utf-8
from django.conf.urls import url
from .. import api
from rest_framework_bulk.routes import BulkRouter

app_name = 'assets'

router = BulkRouter()
router.register(r'v1/assets', api.AssetViewSet, 'asset')
router.register(r'v1/admin-user', api.AdminUserViewSet, 'admin-user')
router.register(r'v1/system-user', api.SystemUserViewSet, 'system-user')
router.register(r'v1/labels', api.LabelViewSet, 'label')
router.register(r'v1/nodes', api.NodeViewSet, 'node')
router.register(r'v1/nodeslb', api.NodeSlbViewSet, 'nodeslb')
router.register(r'v1/noderds', api.NodeRdsViewSet, 'noderds')
router.register(r'v1/assetslb', api.AssetSlbViewSet, 'assetslb')
router.register(r'v1/assetrds', api.AssetRdsViewSet, 'assetrds')
router.register(r'v1/domain', api.DomainViewSet, 'domain')
router.register(r'v1/gateway', api.GatewayViewSet, 'gateway')

urlpatterns = [
    url(r'^v1/assets-bulk/$', api.AssetListUpdateApi.as_view(), name='asset-bulk-update'),
    url(r'^v1/system-user/(?P<pk>[0-9a-zA-Z\-]{36})/auth-info/', api.SystemUserAuthInfoApi.as_view(),
        name='system-user-auth-info'),
    url(r'^v1/assets/(?P<pk>[0-9a-zA-Z\-]{36})/refresh/$',
        api.AssetRefreshHardwareApi.as_view(), name='asset-refresh'),
    url(r'^v1/assets/(?P<pk>[0-9a-zA-Z\-]{36})/alive/$',
        api.AssetAdminUserTestApi.as_view(), name='asset-alive-test'),
    url(r'^v1/assets/user-assets/$',
        api.UserAssetListView.as_view(), name='user-asset-list'),
    url(r'^v1/admin-user/(?P<pk>[0-9a-zA-Z\-]{36})/nodes/$',
        api.ReplaceNodesAdminUserApi.as_view(), name='replace-nodes-admin-user'),
    url(r'^v1/admin-user/(?P<pk>[0-9a-zA-Z\-]{36})/auth/$',
        api.AdminUserAuthApi.as_view(), name='admin-user-auth'),
    url(r'^v1/admin-user/(?P<pk>[0-9a-zA-Z\-]{36})/connective/$',
        api.AdminUserTestConnectiveApi.as_view(), name='admin-user-connective'),
    url(r'^v1/system-user/(?P<pk>[0-9a-zA-Z\-]{36})/push/$',
        api.SystemUserPushApi.as_view(), name='system-user-push'),
    url(r'^v1/system-user/(?P<pk>[0-9a-zA-Z\-]{36})/connective/$',
        api.SystemUserTestConnectiveApi.as_view(), name='system-user-connective'),
    # Asset slb api
    #url(r'^v1/assetslb/$', api.AssetSlbViewSet.as_view(), name='asset-slblist'),
    # Asset node api
    url(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/children/$', api.NodeChildrenApi.as_view(), name='node-children'),
    url(r'^v1/nodes/children/$', api.NodeChildrenApi.as_view(), name='node-children-2'),
    url(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/children/add/$', api.NodeAddChildrenApi.as_view(), name='node-add-children'),
    url(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/$', api.NodeAssetsApi.as_view(), name='node-assets'),
    url(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/add/$', api.NodeAddAssetsApi.as_view(), name='node-add-assets'),
    url(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/replace/$', api.NodeReplaceAssetsApi.as_view(), name='node-replace-assets'),
    url(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/remove/$', api.NodeRemoveAssetsApi.as_view(), name='node-remove-assets'),
    url(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/refresh-hardware-info/$', api.RefreshNodeHardwareInfoApi.as_view(), name='node-refresh-hardware-info'),
    url(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/test-connective/$', api.TestNodeConnectiveApi.as_view(), name='node-test-connective'),
    # Asset Slb node api
    url(r'^v1/slbnodes/(?P<pk>[0-9a-zA-Z\-]{36})/children/$', api.NodeSlbChildrenApi.as_view(), name='nodeslb-children'),
    url(r'^v1/slbnodes/children/$', api.NodeSlbChildrenApi.as_view(), name='nodeslb-children-2'),
    url(r'^v1/slbnodes/(?P<pk>[0-9a-zA-Z\-]{36})/children/add/$', api.NodeSlbAddChildrenApi.as_view(),
        name='nodeslb-add-children'),
    url(r'^v1/slbnodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/$', api.NodeSlbAssetsApi.as_view(), name='nodeslb-assets'),
    url(r'^v1/slbnodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/add/$', api.NodeSlbAddAssetsApi.as_view(), name='nodeslb-add-assets'),
    url(r'^v1/slbnodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/replace/$', api.NodeSlbReplaceAssetsApi.as_view(),
        name='nodeslb-replace-assets'),
    url(r'^v1/slbnodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/remove/$', api.NodeSlbRemoveAssetsApi.as_view(),
        name='nodeslb-remove-assets'),
    # Asset Rds node api
    url(r'^v1/rdsnodes/(?P<pk>[0-9a-zA-Z\-]{36})/children/$', api.NodeRdsChildrenApi.as_view(),
        name='noderds-children'),
    url(r'^v1/rdsnodes/children/$', api.NodeRdsChildrenApi.as_view(), name='noderds-children-2'),
    url(r'^v1/rdsnodes/(?P<pk>[0-9a-zA-Z\-]{36})/children/add/$', api.NodeRdsAddChildrenApi.as_view(),
        name='noderds-add-children'),
    url(r'^v1/rdsnodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/$', api.NodeRdsAssetsApi.as_view(), name='noderds-assets'),
    url(r'^v1/rdsnodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/add/$', api.NodeRdsAddAssetsApi.as_view(),
        name='noderds-add-assets'),
    url(r'^v1/rdsnodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/replace/$', api.NodeRdsReplaceAssetsApi.as_view(),
        name='noderds-replace-assets'),
    url(r'^v1/rdsnodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/remove/$', api.NodeRdsRemoveAssetsApi.as_view(),
        name='noderds-remove-assets'),

    url(r'^v1/gateway/(?P<pk>[0-9a-zA-Z\-]{36})/test-connective/$', api.GatewayTestConnectionApi.as_view(), name='test-gateway-connective'),
]

urlpatterns += router.urls

