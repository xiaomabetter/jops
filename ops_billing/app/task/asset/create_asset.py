import json,time
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest,RunInstancesRequest,\
                            JoinSecurityGroupRequest
from app.models.base import OpsRedis
from app.models.asset import Asset
from .sync_node_amount import NodeAmount

class Aly_Create_Asset(object):
    def __init__(self,template_data,amount,AccessKeyId,AccessKeySecret):
        self.template_data = template_data
        self.amount = amount
        self.AccessKeyId = AccessKeyId
        self.AccessKeySecret = AccessKeySecret
        
    def CreateInstanceFromcopy(self):
        template_data = self.template_data
        params = {}
        params['RegionId'] = template_data['RegionId']
        params['ZoneId'] = template_data['ZoneId']
        params['ImageId'] = template_data['ImageId']
        params['InstanceType'] = template_data['instance_type']
        params['SecurityGroupId'] = template_data['SecurityGroupId'][0].split(',')[0]
        params['InstanceName'] = template_data['InstanceName']
        params['Description'] = template_data['Description']
        params['HostName'] = template_data['HostName']
        params['SystemDisk.Category'] = template_data['SystemDiskCategory']
        params['SystemDisk.Size'] = template_data['SystemDiskSize']
        params['InstanceChargeType'] = template_data['InstanceChargeType']
        params['Period'] = 1
        if template_data.get('DataDiskinfo'):
            DataDiskinfo = list(json.loads(template_data['DataDiskinfo']))
            for dataDisk in DataDiskinfo:
                params = dict(params, **dataDisk)
        if self.amount > 1 :
            params['UniqueSuffix'] = True
        if template_data['IoOptimized']:
            params['IoOptimized'] = 'optimized'
        if template_data.get('InternetChargeType') and template_data.get('InternetMaxBandwidthOut'):
            params['InternetChargeType'] = template_data['InternetChargeType']
            params['InternetMaxBandwidthOut'] = template_data['InternetMaxBandwidthOut']
        self.params = params
        clt = client.AcsClient(self.AccessKeyId,self.AccessKeySecret, params['RegionId'])
        self.clt = clt

    def startInstances(self):
        request = RunInstancesRequest.RunInstancesRequest()
        request.set_query_params(self.params)
        request.set_Amount(self.amount)
        instances_list = []
        response = self._send_request(request)
        if response.get('Code') is None:
            instance_ids = response.get('InstanceIdSets').get('InstanceIdSet')
            running_amount = 0
            while running_amount < self.amount:
                time.sleep(6)
                running_amount,instances_list = self.check_instance_running(instance_ids)
            for instance_detail in instances_list:
                PublicIpAddress = instance_detail.get('PublicIpAddress')['IpAddress']
                if instance_detail['InstanceNetworkType'] == 'vpc':
                    InnerAddress = instance_detail['VpcAttributes']['PrivateIpAddress']['IpAddress'][0]
                else:
                    InnerAddress = instance_detail['InnerIpAddress']['IpAddress'][0]
                Asset.create(AssetType='ecs',InnerAddress=InnerAddress,
                        PublicIpAddress=PublicIpAddress[0] if PublicIpAddress else None,
                        InstanceName=instance_detail.get('InstanceName'),
                        InstanceId=instance_detail.get('InstanceId'),
                        RegionId=instance_detail.get('RegionId'),Status=instance_detail.get('Status'))
                OpsRedis.set(instance_detail['InstanceId'], json.dumps(instance_detail))
                if len(self.template_data['SecurityGroupId'][0].split(',')) > 1:
                    for sgid in self.template_data['SecurityGroupId'][0].split(','):
                        self.set_securitygroup(sgid, instance_detail.get('InstanceId'))
                NodeAmount.sync_root_assets()
            return "ecs instance %s is running" % instance_ids

    def check_instance_running(self,instance_ids):
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_InstanceIds(json.dumps(instance_ids))
        response = self._send_request(request)
        if response.get('Code') is None:
            instances_list = response.get('Instances').get('Instance')
            running_count = 0
            for instance_detail in instances_list:
                if instance_detail.get('Status') == "Running":
                    running_count += 1
            return running_count,instances_list

    def set_securitygroup(self,SecurityGroupId,InstanceId):
        request = JoinSecurityGroupRequest.JoinSecurityGroupRequest()
        request.set_query_params(dict(RegionId=self.params.get('RegionId'),
                            SecurityGroupId=SecurityGroupId,InstanceId=InstanceId))
        self._send_request(request)

    def _send_request(self,request):
        request.set_accept_format('json')
        print(request.get_query_params())
        try:
            response_str = self.clt.do_action_with_exception(request)
            print(response_str)
            response_detail = json.loads(response_str)
            return response_detail
        except Exception as e:
            print(e)