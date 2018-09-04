# ~*~ coding: utf-8 ~*~
import sys,json
from aliyunsdkcore import client
from app.models.base import OpsRedis
from aliyunsdkecs.request.v20140526 import DescribeInstanceTypesRequest,\
                            DescribeInstanceTypeFamiliesRequest
from conf.aliyun_conf import AliConfig

__all__ = ['AliSyncInstanceTypes']

class AliSyncInstanceTypes(object):
    def __init__(self,AccessKeyId,AccessKeySecret):
        self.AccessKeyId = AccessKeyId
        self.AccessKeySecret = AccessKeySecret
        self.clt_conn_list = [client.AcsClient(self.AccessKeyId, self.AccessKeySecret, r)
                              for r in AliConfig.RegionId]

    def sync_instancetype(self):
        results = {}
        request = DescribeInstanceTypeFamiliesRequest.DescribeInstanceTypeFamiliesRequest()
        request.set_accept_format('json')
        for clt in self.clt_conn_list:
            clt_result = json.loads(clt.do_action_with_exception(request))
            for family in clt_result['InstanceTypeFamilies']['InstanceTypeFamily']:
                request_t = DescribeInstanceTypesRequest.DescribeInstanceTypesRequest()
                request_t.set_query_params(dict(InstanceTypeFamily=family['InstanceTypeFamilyId']))
                clt_result_t = json.loads(clt.do_action_with_exception(request_t))
                for result in clt_result_t['InstanceTypes']['InstanceType']:
                    results[result['InstanceTypeId']] = result
        OpsRedis.set('aly_InstanceTypes', json.dumps(results))

if __name__ == '__main__' :
    AccessKeyId = ''
    AccessKeySecret = ''
    asi = AliSyncInstanceTypes(AccessKeyId,AccessKeySecret)
    asi.sync_instancetype()
