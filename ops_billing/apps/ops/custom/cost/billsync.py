# -*- coding: utf-8 -*-
import oss2
import shutil
import time
import re,os
import uuid
import datetime
from assets.models import Ecs,Rds,Slb,AssetSlb,NodeSlb,Asset


class Bill():
    def __init__(self, AccessKeyId, AccessKeySecret):
        self.current_dir =  os.path.dirname(__file__)
        self.AccessKeyId = AccessKeyId
        self.AccessKeySecret = AccessKeySecret
        self.bucket = oss2.Bucket(self.auth(), 'oss-cn-hangzhou.aliyuncs.com', 'aly-bills')
        self.files = {}
        self.ecs = {}
        self.rds = {}
        self.slb = {}

    def auth(self):
        auth = oss2.Auth(self.AccessKeyId, self.AccessKeySecret)
        return auth

    def generate(self,file):
        filedir = "%s/file" % self.current_dir
        if not os.path.exists(filedir):
            os.mkdir(filedir)
        filename = '%s/file/read.txt' % (self.current_dir)
        filename_backup = '%s/file/temp.txt' % (self.current_dir)
        remote_stream = self.bucket.get_object_to_file(file,filename_backup)
        with open(filename_backup) as f:
            data = f.readlines()
        data_str = ''.join(data)
        data_last = re.sub('\\n;', ';', data_str)
        with open(filename, 'w+') as f:
            f.write(data_last)
        return filename

    def getfiles(self):
        for b in oss2.ObjectIterator(self.bucket):
            kv = b.key.split('/')
            self.files[kv[0]] = b.key
        return self.files

    def k(self,id, name, cost,obj,servtime):
        if id in obj:
            obj[id][1] = round((obj[id][1] + cost), 3)
        else:
            obj[id] = [name, round(cost, 3),servtime]

    def isinsert(self,kid,model,v):
        r = model.objects.filter(instanceid=kid,day=v[2])
        if r.count() == 0 :
            a = model.objects.create(id=str(uuid.uuid4()), instancename=v[0], instanceid=kid, day=v[2], cost=v[1])

    def handle(self,beginday,endday):
        begin = int(time.mktime(time.strptime(beginday, "%Y-%m-%d"))) + 23 * 3600
        end = int(time.mktime(time.strptime(endday, "%Y-%m-%d")) ) + 23 * 3600
        for day,filename in self.getfiles().items():
            timestamp = time.mktime(time.strptime(day, "%Y-%m-%d")) - 24 * 3600
            fileday = time.strftime("%Y-%m-%d 09:00:00", time.localtime(int(timestamp)))
            if timestamp > begin and  timestamp < end  :
                handlefile = self.generate(filename)
                self.ecs = {};self.rds = {};self.slb = {}
                with open(handlefile,'r') as f:
                    next(f)
                    for line in f.readlines():
                        linelist = line.split(',')
                        instance_id = linelist[11]
                        instance_name = linelist[12] or instance_id
                        instance_v = linelist[5]
                        cost = float(linelist[21])

                        if "ECS" in instance_v:
                            self.k(instance_id, instance_name, cost,self.ecs,fileday)
                        elif "RDS" in instance_v:
                            self.k(instance_id, instance_name, cost,self.rds,fileday)
                        elif "SLB" in instance_v:
                            self.k(instance_id, instance_name, cost,self.slb,fileday)

                for k,v in self.rds.items():
                    self.isinsert(k,Rds,v)
                for k, v in self.ecs.items():
                    r = Ecs.objects.filter(instanceid=k, day=v[2])
                    if r.count() == 0:
                        a = Ecs.objects.create(id=str(uuid.uuid4()), instancename=v[0], instanceid=k, day=v[2],
                                                 cost=v[1])
                        b = Asset.objects.filter(instanceid=k).first()
                        if b is not None:
                            b.ecsinfo.add(a.id)
                for k, v in self.slb.items():
                    r = Slb.objects.filter(instanceid=k, day=v[2])
                    if r.count() == 0:
                        a = Slb.objects.create(id=str(uuid.uuid4()), instancename=v[0], instanceid=k, day=v[2],
                                                 cost=v[1])
                        b = AssetSlb.objects.filter(instanceid=k).first()
                        if b is not None:
                            b.slbinfo.add(a.id)

if __name__ == '__main__':
    c = Bill('LTAIvjpauewMGGPa', 'KEIOPsuOVihcqd90ruKsSR1VJJQPav')