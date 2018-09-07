# ~*~ coding: utf-8 ~*~
import sys,json
from aliyunsdkcore import client
from app.models.base import OpsRedis
from aliyunsdkecs.request.v20140526 import DescribeSecurityGroupsRequest
from app import config

__all__ = ['AliSyncSecurityGroup']

class AliSyncSecurityGroup(object):
    def __init__(self,AccessKeyId,AccessKeySecret):
        self.AccessKeyId = AccessKeyId
        self.AccessKeySecret = AccessKeySecret
        self.RegionId = ['cn-hangzhou','cn-beijing','us-west-1','cn-hongkong']
        self.clt_conn_list = [client.AcsClient(self.AccessKeyId, self.AccessKeySecret, r)
                              for r in config.get('Aliyun','RegionId')]

    def sync_security_group(self,pageSize=50):
        results = []
        request = DescribeSecurityGroupsRequest.DescribeSecurityGroupsRequest()
        request.set_accept_format('json')
        for clt in self.clt_conn_list:
            result = []
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber,PageSize=pageSize))
            clt_result = json.loads(clt.do_action_with_exception(request))
            result += clt_result['SecurityGroups']['SecurityGroup']
            totalCount = clt_result['TotalCount']
            while totalCount > pageNumber * pageSize:
                pageNumber += 1
                request.set_query_params(dict(PageNumber=pageNumber, PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request))
                result += clt_result['SecurityGroups']['SecurityGroup']
            for index,value in enumerate(result):
                value['RegionId'] = clt.get_region_id()
                result[index] = value
            results += result
        OpsRedis.set('aly_security_groups', json.dumps(results))

if __name__ == '__main__' :
    AccessKeyId = ''
    AccessKeySecret = ''
    asi = AliSyncSecurityGroup(AccessKeyId,AccessKeySecret)
    asi.sync_security_group()