# ~*~ coding: utf-8 ~*~
import sys,json
from aliyunsdkcore import client
from app.models.base import OpsRedis
from aliyunsdkecs.request.v20140526 import DescribeImagesRequest

__all__ = ['AliSyncImages']

class AliSyncImages(object):
    def __init__(self,AccessKeyId,AccessKeySecret):
        self.AccessKeyId = AccessKeyId
        self.AccessKeySecret = AccessKeySecret
        self.RegionId = ['cn-hangzhou','cn-beijing','us-west-1','cn-hongkong']
        self.clt_conn_list = [client.AcsClient(self.AccessKeyId, self.AccessKeySecret, r)
                              for r in self.RegionId]

    def sync_images(self,pageSize=100):
        results = []
        request = DescribeImagesRequest.DescribeImagesRequest()
        request.set_accept_format('json')
        for clt in self.clt_conn_list:
            result = []
            pageNumber = 1
            request.set_query_params(dict(PageNumber=pageNumber,PageSize=pageSize,Status='Available'))
            clt_result = json.loads(clt.do_action_with_exception(request))
            result += clt_result['Images']['Image']
            totalCount = clt_result['TotalCount']
            while totalCount > pageNumber * pageSize:
                pageNumber += 1
                request.set_query_params(dict(PageSize=pageSize))
                clt_result = json.loads(clt.do_action_with_exception(request))
                result += clt_result['Images']['Image']
            for index,value in enumerate(result):
                value['RegionId'] = clt.get_region_id()
                result[index] = value
            results += result
        OpsRedis.set('aly_images',json.dumps(results))

if __name__ == '__main__' :
    AccessKeyId = ''
    AccessKeySecret = ''
    asi = AliSyncImages(AccessKeyId,AccessKeySecret)
    asi.sync_images()