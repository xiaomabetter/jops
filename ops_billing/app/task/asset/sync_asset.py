# ~*~ coding: utf-8 ~*~
import json,uuid,oss2
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest,\
    DescribeDisksRequest
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancersRequest
from aliyunsdkrds.request.v20140815 import DescribeDBInstancesRequest,\
    DescribeDBInstanceAttributeRequest
from aliyunsdkr_kvstore.request.v20150101 import DescribeInstancesRequest as kvInstancesRequest
from aliyunsdkr_kvstore.request.v20150101 import  DescribeInstanceAttributeRequest
from .sync_node_amount import NodeAmount
from app.models import Asset,db,OpsRedis
from conf import aliyun

__all__ = ['SyncAliAssets']

class SyncAliAssets(object):
    def __init__(self,AccessKeyId,AccessKeySecret):
        self.AccessKeyId = AccessKeyId
        self.AccessKeySecret = AccessKeySecret
        self.clt_conn_list = [AcsClient(self.AccessKeyId, self.AccessKeySecret, r) for r in aliyun.RegionId]

    def get_ecs_result(self,result):
        insert_result = []
        for Instance in result:
            if Instance['InstanceNetworkType'] == 'vpc':
                InnerAddress = Instance['VpcAttributes']['PrivateIpAddress']['IpAddress'][0]
            elif Instance['InstanceNetworkType'] == 'classic':
                InnerAddress = Instance['InnerIpAddress']['IpAddress'][0]
            else:
                InnerAddress = None
            if Instance['PublicIpAddress']['IpAddress']:
                PublicIpAddress = Instance['PublicIpAddress']['IpAddress'][0]
            else:
                PublicIpAddress = None
            insert_result.append({
                'AssetType': 'ecs','InnerAddress': InnerAddress,'PublicIpAddress': PublicIpAddress,
                'InstanceName': Instance['InstanceName'],'InstanceId': Instance['InstanceId'],
                'RegionId': Instance['RegionId'],'sshport': 3299,'Status': Instance['Status']
            })
        return insert_result

    def get_ecs_instances(self, pageSize=100):
        result = []
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        for clt in self.clt_conn_list:
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber,PageSize=pageSize))
            clt_result = json.loads(clt.do_action_with_exception(request))
            result += clt_result['Instances']['Instance']
            totalCount = clt_result['TotalCount']
            while totalCount > pageNumber * pageSize:
                pageNumber += 1
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request))
                result += clt_result['Instances']['Instance']
        result_dict = {}
        for r in result:
            result_dict[r['InstanceId']] = r
        result_dict_keys = result_dict.keys()
        images = self.get_image_list()
        for disk in images:
            if disk['InstanceId'] and disk['InstanceId'] in result_dict_keys:
                result_dict[disk['InstanceId']].setdefault('images', [])
                result_dict[disk['InstanceId']]['images'].append(disk)
        for instanceid,value in result_dict.items():
            OpsRedis.set(instanceid,json.dumps(value))
        return self.get_ecs_result(result)

    def get_image_list(self,pageSize=100):
        result = []
        request = DescribeDisksRequest.DescribeDisksRequest()
        request.set_accept_format('json')
        for clt in self.clt_conn_list:
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
            clt_result = json.loads(clt.do_action_with_exception(request))
            result += clt_result['Disks']['Disk']
            totalCount = clt_result['TotalCount']
            while totalCount > pageNumber * pageSize:
                pageNumber += 1
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request))
                result += clt_result['Disks']['Disk']
        return result

    def get_slb_instances(self,pageSize=100):
        result = []
        insert_result = []
        request = DescribeLoadBalancersRequest.DescribeLoadBalancersRequest()
        request.set_accept_format('json')
        for clt in self.clt_conn_list:
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
            clt_result = json.loads(clt.do_action_with_exception(request))
            result = result + clt_result['LoadBalancers']['LoadBalancer']
            totalCount = clt_result['TotalCount']
            while totalCount > pageNumber * pageSize:
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request),encoding='utf-8')
                result = result + clt_result['LoadBalancers']['LoadBalancer']
                pageNumber += 1
        for Instance in result:
            insert_result.append({
                'AssetType': 'slb',
                'InstanceId': Instance['LoadBalancerId'],
                'InstanceName': Instance.get('LoadBalancerName', ''),
                'PublicIpAddress': Instance['Address'],
                'RegionId': Instance['RegionId'],
                'Status': Instance['LoadBalancerStatus']
            })
            OpsRedis.set(Instance['LoadBalancerId'], json.dumps(Instance))
        return insert_result

    def get_rds_instances(self,pageSize=100):
        result = []
        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        request.set_accept_format('json')
        attributeRequest = DescribeDBInstanceAttributeRequest.DescribeDBInstanceAttributeRequest()
        attributeRequest.set_accept_format('json')
        for clt in self.clt_conn_list:
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
            clt_result = json.loads(clt.do_action_with_exception(request))
            region_result = clt_result['Items']['DBInstance']
            totalCount = clt_result['PageRecordCount']
            while totalCount > pageNumber * pageSize:
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request),encoding='utf-8')
                region_result = region_result + clt_result['Items']['DBInstance']
                pageNumber += 1
            for Instance in region_result:
                attributeRequest.add_query_param("action_name", "DescribeDBInstanceAttribute")
                attributeRequest.add_query_param("DBInstanceId", Instance['DBInstanceId'])
                r = json.loads(clt.do_action_with_exception(attributeRequest))
                attr = r['Items']['DBInstanceAttribute'][0]
                result.append({
                    'InstanceId': attr['DBInstanceId'],
                    'AssetType': 'rds',
                    'RegionId': attr['RegionId'],
                    'InstanceName': attr['DBInstanceDescription'],
                    'InnerAddress': attr["ConnectionString"],
                    'Status': attr['DBInstanceStatus']
                })
                OpsRedis.set(Instance['DBInstanceId'], json.dumps(attr))
        return result

    def get_redis_instances(self,pageSize=50):
        result = []
        request = kvInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        attributeRequest = DescribeInstanceAttributeRequest.DescribeInstanceAttributeRequest()
        attributeRequest.set_accept_format('json')
        for clt in self.clt_conn_list:
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
            clt_result = json.loads(clt.do_action_with_exception(request))
            region_result = clt_result['Instances']['KVStoreInstance']
            totalCount = clt_result['TotalCount']
            while totalCount > pageNumber * pageSize:
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request))
                region_result = region_result + clt_result['Instances']['KVStoreInstance']
                pageNumber += 1
            for Instance in region_result:
                attributeRequest.add_query_param("action_name", "DescribeInstanceAttribute")
                attributeRequest.add_query_param("InstanceId", Instance['InstanceId'])
                r = json.loads(clt.do_action_with_exception(attributeRequest))
                attr = r['Instances']['DBInstanceAttribute'][0]
                result.append({
                    'InstanceId': attr['InstanceId'],
                    'AssetType': 'redis',
                    'InnerAddress': attr['ConnectionDomain'],
                    'InstanceName': attr['InstanceName'],
                    'RegionId': attr['RegionId'],
                    'Status':attr['InstanceStatus']
                })
                OpsRedis.set(attr['InstanceId'],json.dumps(attr))
        return result

    def get_oss_instances(self):
        result = []
        auth = oss2.Auth(self.AccessKeyId,self.AccessKeySecret)
        fuc_buckets = oss2.Service(auth, 'oss-cn-hangzhou.aliyuncs.com').list_buckets(max_keys=200)
        for Instance in fuc_buckets.buckets:
            result.append({
                'InstanceId':Instance.name,
                'AssetType': 'oss',
                'InnerAddress': '.'.join([Instance.name,Instance.location])+'-internal.aliyuncs.com',
                'PublicIpAddress':'.'.join([Instance.name,Instance.location,'aliyuncs.com']),
                'InstanceName': Instance.name,
                'RegionId': Instance.location.strip('oss-'),
                })
        return result

    def aly_sync_asset(self,asset_type,update=True):
        insert_many = []
        new_InstanceIds = []
        query_set = Asset.filter(Asset.AssetType==asset_type)
        InstanceIds = [asset.InstanceId for asset in query_set if query_set]

        if asset_type == 'ecs':
            instances = self.get_ecs_instances()
        elif asset_type == 'rds':
            instances = self.get_rds_instances()
        elif asset_type == 'slb':
            instances = self.get_slb_instances()
        elif asset_type == 'redis':
            instances = self.get_redis_instances()
        elif asset_type == 'oss':
            instances = self.get_oss_instances()
        else:
            return

        for instance in instances:
            new_InstanceIds.append(instance['InstanceId'])
            if instance['InstanceId'] in InstanceIds and update:
                with db.atomic():
                    Asset.update(**instance).where(Asset.InstanceId ==instance['InstanceId']).execute()
            else:
                insert_many.append(instance)
        ids = list(set(InstanceIds) - set(new_InstanceIds) )
        if ids:
            with db.atomic():
                Asset.update(Status = 'Destroy').where(Asset.InstanceId.in_(ids)).execute()
        last_insert_many = self.pop_duplicate(insert_many) if not insert_many  else insert_many
        if last_insert_many :
            with db.atomic():
                Asset.insert_many(last_insert_many).execute()
        NodeAmount.sync_root_assets()
        NodeAmount.sync_all_node_assets()

    def pop_duplicate(self,asset_list):
        new_asset_list = []
        for i,item in enumerate(asset_list):
            if item['InstanceId'] not in [asset['InstanceId'] for asset in new_asset_list]:
                new_asset_list.append(item)
        return new_asset_list