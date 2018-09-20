# ~*~ coding: utf-8 ~*~
import json
from aliyunsdkcore import client
from app.models.base import OpsRedis
from aliyunsdkvpc.request.v20160428 import DescribeVSwitchesRequest
from conf import aliyun

__all__ = ['AliSyncVSwitches']

class AliSyncVSwitches(object):
    def __init__(self,AccessKeyId,AccessKeySecret):
        self.AccessKeyId = AccessKeyId
        self.AccessKeySecret = AccessKeySecret
        self.clt_conn_list = [client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region)
                                                        for region in aliyun.RegionId]

    def sync_vswitchs(self):
        results = {}
        sw_vpc = {}
        request = DescribeVSwitchesRequest.DescribeVSwitchesRequest()
        request.set_accept_format('json')
        for clt in self.clt_conn_list:
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber))
            clt_result = json.loads(clt.do_action_with_exception(request))
            for sw in clt_result['VSwitches']['VSwitch']:
                info = {
                        'VSwitchName':sw['VSwitchName'],
                        'VSwitchId':sw['VSwitchId'],
                        'CidrBlock':sw['CidrBlock'],
                        'AvailableIpAddressCount':sw['AvailableIpAddressCount'],
                        'VpcId':sw['VpcId']
                }
                sw_vpc[sw['VSwitchId']] = sw['VpcId']
                if sw['ZoneId'] in results:
                    results[sw['ZoneId']].append(info)
                else:
                    results[sw['ZoneId']] = []
                    results[sw['ZoneId']].append(info)
        OpsRedis.set('aly_vswitches', json.dumps(results))
        OpsRedis.set('aly_vswitches_vpcs', json.dumps(sw_vpc))


if __name__ == '__main__' :
    AccessKeyId = ''
    AccessKeySecret = ''
    asi = AliSyncVSwitches(AccessKeyId,AccessKeySecret)
    asi.sync_vswitchs()