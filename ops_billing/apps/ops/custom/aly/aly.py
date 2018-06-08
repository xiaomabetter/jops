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
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancersRequest,DescribeLoadBalancerAttributeRequest
from aliyunsdkrds.request.v20140815 import DescribeDBInstancesRequest,DescribeDBInstanceAttributeRequest
from aliyunsdkr_kvstore.request.v20150101 import DescribeInstanceAttributeRequest as kvAttrRequest
from aliyunsdkr_kvstore.request.v20150101 import DescribeInstancesRequest as kvRequest
from django.forms.models import model_to_dict
from django.db import transaction
from assets.models import Asset,AssetSlb,AssetRds,AssetRedis
import logging,uuid

__all__ = ['Aliyun']

class Aliyun(object):
    def __init__(self):
        self.AccessKeyId = 'LTAIvjpauewMGGPa'
        self.AccessKeySecret = 'KEIOPsuOVihcqd90ruKsSR1VJJQPav'
        self.RegionId = ['cn-hangzhou','cn-beijing']

    def get_instances(self,pageSize=100):
        result = []
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        for region in self.RegionId:
            pageNumber = 1
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
        request = DescribeLoadBalancersRequest.DescribeLoadBalancersRequest()
        request.set_accept_format('json')
        attributeRequest = DescribeLoadBalancerAttributeRequest.DescribeLoadBalancerAttributeRequest()
        attributeRequest.set_accept_format('json')
        for region in self.RegionId:
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
            attributectl = client.AcsClient(self.AccessKeyId, self.AccessKeySecret,region_id=region)
            clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region)
            clt_result = json.loads(clt.do_action_with_exception(request))
            totalCount = clt_result['TotalCount']
            while totalCount > (pageNumber -1 )* pageSize:
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request),encoding='utf-8')
                for Instance in clt_result['LoadBalancers']['LoadBalancer']:
                    #attributeRequest.add_query_param("action_name","DescribeLoadBalancerAttribute")
                    #attributeRequest.add_query_param("LoadBalancerId", Instance['LoadBalancerId'])
                    #r = json.loads(attributectl.do_action_with_exception(attributeRequest))
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
        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        request.set_accept_format('json')
        attributeRequest = DescribeDBInstanceAttributeRequest.DescribeDBInstanceAttributeRequest()
        attributeRequest.set_accept_format('json')
        attributectl = client.AcsClient(self.AccessKeyId, self.AccessKeySecret)
        for region in self.RegionId:
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
            clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region)
            clt_result = json.loads(clt.do_action_with_exception(request))
            totalCount = clt_result['PageRecordCount']
            while totalCount > (pageNumber -1 )* pageSize:
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request),encoding='utf-8')
                for Instance in clt_result['Items']['DBInstance']:
                    attributeRequest.add_query_param("action_name","DescribeDBInstanceAttribute")
                    attributeRequest.add_query_param("DBInstanceId", Instance['DBInstanceId'])
                    r = json.loads(attributectl.do_action_with_exception(attributeRequest))
                    attr = r['Items']['DBInstanceAttribute'][0]
                    result.append({
                            'id':str(uuid.uuid4()),
                            'DBInstanceId':Instance['DBInstanceId'],
                            'RegionId':Instance['RegionId'],
                            'DBInstanceDescription':Instance['DBInstanceDescription'],
                            'ConnectionString':attr["ConnectionString"],
                            "DBInstanceCPU": attr["DBInstanceCPU"],
                            'DBInstanceType': attr['DBInstanceType'],
                            'CreationTime':attr['CreationTime']
                        })
                pageNumber += 1
        return result

    def get_redis_instances(self):
        result = []
        request = kvRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        for region in self.RegionId:
            clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region)
            clt_result = json.loads(clt.do_action_with_exception(request))
            for Instance in clt_result['Instances']['KVStoreInstance']:
                result.append(
                    {
                        'InstanceId':Instance['InstanceId'],
                        'UserName':Instance['UserName'],
                        'ConnectionDomain':Instance['ConnectionDomain'],
                        'InstanceName':Instance['InstanceName'],
                        'RegionId': Instance['RegionId'],
                        'Capacity':Instance['Capacity'],
                        'CreateTime':Instance['CreateTime']
                    }
                )
        return result


    @transaction.atomic()
    def aly_sync_asset(self):
        ids = Asset.objects.all().values('instanceid')
        instances = self.get_instances()
        inids = [ i['instanceid']  for i in ids ]
        newids = []
        for instance in instances:
            newids.append(instance['instanceid'])
            if instance['instanceid'] in inids:
                Asset.objects.filter(instanceid=instance['instanceid']).update(
                    hostname=instance['hostname'])
            else:
                asset = Asset(**instance)
                asset.save()
        oids = list(set(inids) - set(newids))
        if oids:
            for i in oids:
                Asset.objects.filter(instanceid=i).update(is_active=False)

    @transaction.atomic()
    def aly_sync_assetslb(self):
        ids = AssetSlb.objects.all().values('instanceid')
        instances = self.get_slb_instances()
        inids = [i['instanceid'] for i in ids]
        newids = []
        for instance in instances:
            newids.append(instance['instanceid'])
            if instance['instanceid'] in inids:
                AssetSlb.objects.filter(instanceid=instance['instanceid']).update(
                    slb_name=instance['slb_name'])
            else:
                assetslb = AssetSlb(**instance)
                assetslb.save()
        oids = list(set(inids) - set(newids))
        if oids:
            for i in oids:
                AssetSlb.objects.filter(instanceid=i).update(is_active=False)

    @transaction.atomic()
    def aly_sync_assetrds(self):
        ids = AssetRds.objects.all().values('DBInstanceId')
        instances = self.get_rds_instances()
        inids = [i['DBInstanceId'] for i in ids]
        newids = []
        for instance in instances:
            newids.append(instance['DBInstanceId'])
            if instance['DBInstanceId'] in inids:
                AssetRds.objects.filter(DBInstanceId=instance['DBInstanceId']).update(
                    DBInstanceDescription=instance['DBInstanceDescription'])
            else:
                assetrds = AssetRds(**instance)
                assetrds.save()
        oids = list(set(inids) - set(newids))
        if oids:
            for i in oids:
                AssetRds.objects.filter(DBInstanceId=i).update(is_active=False)


    @transaction.atomic()
    def aly_sync_assetredis(self):
        ids = AssetRedis.objects.all().values('InstanceId')
        instances = self.get_redis_instances()
        inids = [i['InstanceId'] for i in ids]
        newids = []
        for instance in instances:
            newids.append(instance['InstanceId'])
            if instance['InstanceId'] in inids:
                AssetRedis.objects.filter(InstanceId=instance['InstanceId']).update(
                    ConnectionDomain=instance['ConnectionDomain'])
            else:
                assetredis = AssetRedis(**instance)
                assetredis.save()
        oids = list(set(inids) - set(newids))
        if oids:
            for i in oids:
                AssetRedis.objects.filter(InstanceId=i).update(is_active=False)