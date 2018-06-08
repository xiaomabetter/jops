# ~*~ coding: utf-8 ~*~
#!/usr/bin/env python
import sys
import json
import base64
import requests
import configparser
from aliyunsdkcore import client
from aliyunsdkr_kvstore.request.v20150101 import DescribeInstanceAttributeRequest
from aliyunsdkr_kvstore.request.v20150101 import DescribeInstancesRequest
from django.forms.models import model_to_dict
#from assets.models import Asset,AssetSlb,AssetRds
import logging,uuid

__all__ = ['Aliyun_kv']

class Aliyun_kv(object):
    def __init__(self):
        self.AccessKeyId = 'LTAIvjpauewMGGPa'
        self.AccessKeySecret = 'KEIOPsuOVihcqd90ruKsSR1VJJQPav'
        self.RegionId = ['cn-hangzhou','cn-beijing']

    def get_redis_instances(self,pageSize = 100):
        result = []
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        attributeRequest = DescribeInstanceAttributeRequest.DescribeInstanceAttributeRequest()
        attributeRequest.set_accept_format(accept_format='json')
        attributectl = client.AcsClient(self.AccessKeyId, self.AccessKeySecret)
        for region in self.RegionId:
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
            clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region)
            clt_result = json.loads(clt.do_action_with_exception(request))
            print(clt_result)
            totalCount = clt_result['TotalCount']
            while totalCount > (pageNumber -1 )* pageSize:
                request.set_PageSize(pageSize)
                request.set_PageNumber(pageNumber)
                clt_result = json.loads(clt.do_action_with_exception(request),encoding='utf-8')
                for Instance in clt_result['Items']['DBInstance']:
                    print(Instance)
                    attributeRequest.add_query_param("action_name","DescribeDBInstanceAttribute")
                    attributeRequest.add_query_param("DBInstanceId", Instance['DBInstanceId'])
                    r = json.loads(attributectl.do_action_with_exception(attributeRequest))
                pageNumber += 1
        return result

if __name__ == '__main__' :
    kv = Aliyun_kv()
    kv.get_redis_instances()

