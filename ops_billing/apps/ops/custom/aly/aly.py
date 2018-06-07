# ~*~ coding: utf-8 ~*~
#!/usr/bin/env python
import sys
import json
import base64
import requests
import configparser
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeDisksRequest, \
    DescribeInstancesRequest, CreateInstanceRequest, StartInstanceRequest, \
    StopInstanceRequest, RebootInstanceRequest, \
    AllocatePublicIpAddressRequest, JoinSecurityGroupRequest
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancersRequest
from aliyunsdkrds.request.v20140815 import DescribeDBInstancesRequest,DescribeDBInstanceAttributeRequest
from django.forms.models import model_to_dict
from assets.models import Asset,AssetSlb
import logging,uuid

__all__ = ['Aliyun']

class Aliyun(object):
    def __init__(self):
        self.AccessKeyId = 'LTAIvjpauewMGGPa'
        self.AccessKeySecret = 'KEIOPsuOVihcqd90ruKsSR1VJJQPav'
        self.RegionId = ['cn-hangzhou','cn-beijing']

    def get_instances(self,pageSize=100):
        result = []
        for region in self.RegionId:
            pageNumber = 1
            request = DescribeInstancesRequest.DescribeInstancesRequest()
            request.set_accept_format('json')
            request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
            clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region)
            clt_result = json.loads(clt.do_action_with_exception(request))
            totalCount = clt_result['TotalCount']

            while totalCount > (pageNumber -1 )* pageSize :
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request))
                for Instance in clt_result['Instances']['Instance']:
                    if Instance['InstanceNetworkType'] == 'vpc':
                        priip = Instance['VpcAttributes']['PrivateIpAddress']['IpAddress'][0]
                    elif Instance['InstanceNetworkType'] == 'classic':
                        priip = Instance['InnerIpAddress']['IpAddress'][0]
                    result.append({
                        'id':str(uuid.uuid4()),
                        'ip':priip,
                        'InstanceNetworkType':Instance['InstanceNetworkType'],
                        'hostname':Instance['InstanceName'],
                        'instanceid':Instance['InstanceId'],
                        'port':3299,
                        'platform':'Linux',
                        'is_active':True,
                        'zoneid':Instance['RegionId'],
                        'public_ip':str(Instance['PublicIpAddress']['IpAddress']).strip('[|]'),
                        'cpu_count':Instance['Cpu'],
                        'memory':Instance['Memory']
                    })
                pageNumber += 1
        return result

    def get_slb_instances(self, pageSize=100):
        result = []
        for region in self.RegionId:
            pageNumber = 1
            request = DescribeLoadBalancersRequest.DescribeLoadBalancersRequest()
            request.set_accept_format('json')
            request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
            clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region)
            clt_result = json.loads(clt.do_action_with_exception(request))
            totalCount = clt_result['TotalCount']
            while totalCount > (pageNumber -1 )* pageSize:
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request),encoding='utf-8')
                for Instance in clt_result['LoadBalancers']['LoadBalancer']:
                    result.append({
                        'id': str(uuid.uuid4()),
                        'instanceid':Instance['LoadBalancerId'],
                        'slb_name':Instance.get('LoadBalancerName',''),
                        'slb_addr':Instance['Address'],
                        'slb_region':Instance['RegionId'],
                        'create_time':Instance['CreateTime']
                    })
                pageNumber += 1
        return result

    def get_rds_instances(self, pageSize=100):
        result = []
        for region in self.RegionId:
            pageNumber = 1
            request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
            request.set_accept_format('json')
            request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
            clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region)
            clt_result = json.loads(clt.do_action_with_exception(request))
            totalCount = clt_result['PageRecordCount']
            while totalCount > (pageNumber -1 )* pageSize:
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request),encoding='utf-8')
                for Instance in clt_result['Items']['DBInstance']:
                    result.append(
                        {
                            'id':str(uuid.uuid4()),
                            'DBInstanceId':Instance['DBInstanceId'],
                            'RegionId':Instance['RegionId'],
                            'DBInstanceDescription':Instance['DBInstanceDescription']
                        }
                    )
                pageNumber += 1
        return result

    def aly_sync_asset(self):
        instances = self.get_instances()
        ids = Asset.objects.all().values('instanceid')
        inids = [ i['instanceid']  for i in ids ]
        newids = []
        for instance in instances:
            newids.append(instance['instanceid'])
            if instance['instanceid'] in inids:
                Asset.objects.filter(instanceid=instance['instanceid']).update(hostname=instance['hostname'])
            else:
                asset = Asset(**instance)
                asset.save()
        oids = list(set(inids) - set(newids))
        if oids:
            for i in oids:
                Asset.objects.filter(instanceid=i).update(is_active=False)

    def aly_sync_assetslb(self):
        instances = self.get_slb_instances()
        ids = AssetSlb.objects.all().values('instanceid')
        inids = [i['instanceid'] for i in ids]
        newids = []
        for instance in instances:
            newids.append(instance['instanceid'])
            if instance['instanceid'] in inids:
                AssetSlb.objects.filter(instanceid=instance['instanceid']).update(slb_name=instance['slb_name'])
            else:
                assetslb = AssetSlb(**instance)
                assetslb.save()
        oids = list(set(inids) - set(newids))
        if oids:
            for i in oids:
                AssetSlb.objects.filter(instanceid=i).update(is_active=False)

