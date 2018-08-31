# ~*~ coding: utf-8 ~*~
import sys,json
from aliyunsdkcore import client
from app.models.base import OpsRedis
from aliyunsdkecs.request.v20140526 import DescribeZonesRequest

__all__ = ['AliSyncZones']

class AliSyncZones(object):
    def __init__(self,AccessKeyId,AccessKeySecret):
        self.AccessKeyId = AccessKeyId
        self.AccessKeySecret = AccessKeySecret
        self.RegionId = ['cn-hangzhou', 'cn-beijing', 'us-west-1', 'cn-hongkong']
        self.clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret)

    def sync_zones(self):
        results = {}
        request = DescribeZonesRequest.DescribeZonesRequest()
        request.set_accept_format('json')
        for region in self.RegionId:
            request.set_query_params(dict(RegionId=region))
            clt_result = json.loads(self.clt.do_action_with_exception(request))
            results[region] = [{'ZoneId':r['ZoneId'],'LocalName':r['LocalName']}
                      for r in clt_result['Zones']['Zone']]
        OpsRedis.set('aly_zones', json.dumps(results))

if __name__ == '__main__' :
    AccessKeyId = ''
    AccessKeySecret = ''
    asi = AliSyncZones(AccessKeyId,AccessKeySecret)
    asi.sync_zones()