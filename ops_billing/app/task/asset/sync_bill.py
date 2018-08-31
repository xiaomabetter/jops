# ~*~ coding: utf-8 ~*~
import oss2
import shutil,time,re,os
from app.models import Bill
from app.models import db
from app.models import SyncBillInfo
from app import get_basedir

class SyncBills():
    def __init__(self,username,AccessKeyId,AccessKeySecret,day_from,day_to):
        self.username = username
        self.AccessKeyId = AccessKeyId
        self.AccessKeySecret = AccessKeySecret
        self.day_from = day_from
        self.day_to = day_to
        self.bucket = oss2.Bucket(self.auth(), 'oss-cn-hangzhou.aliyuncs.com', 'aly-bills')
        self.result = {}

    def auth(self):
        auth = oss2.Auth(self.AccessKeyId, self.AccessKeySecret)
        return auth

    def generate(self,file):
        filedir = "{0}/task/asset/file".format(get_basedir())
        if not os.path.exists(filedir):
            os.mkdir(filedir)
        filename = '{0}/read.txt'.format(filedir)
        filename_backup = '{0}/temp.txt'.format(filedir)
        self.bucket.get_object_to_file(file,filename_backup)
        with open(filename_backup) as f:
            data = f.readlines()
        data_str = ''.join(data)
        data_last = re.sub('\\n;', ';', data_str)
        with open(filename, 'w+') as f:
            f.write(data_last)
        return filename

    def getfiles(self):
        billfiles = {}
        for b in oss2.ObjectIterator(self.bucket):
            kv = b.key.split('/')
            billfiles[kv[0]] = b.key
        return billfiles

    def handle(self):
        begin = int(time.mktime(time.strptime(self.day_from, "%Y-%m-%d")))
        end = int(time.mktime(time.strptime(self.day_to, "%Y-%m-%d")) )
        for fileday,filename in self.getfiles().items():
            try:
                timestamp = time.mktime(time.strptime(fileday, "%Y-%m-%d")) - 24 * 3600
            except:
                continue
            is_synced = SyncBillInfo.select().where(SyncBillInfo.day == fileday)
            if timestamp >= begin and  timestamp <= end and not is_synced :
                handlefile = self.generate(filename)
                result = {}
                with open(handlefile,'r') as f:
                    next(f)
                    for line in f.readlines():
                        linelist = line.split(',')
                        day = linelist[2]
                        instanceid = linelist[11].strip()
                        instancename = linelist[12] or instanceid
                        instancetype = linelist[5]
                        cost = float(linelist[21])
                        if instanceid in result:
                            result[instanceid]['cost'] = round((result[instanceid]['cost'] + cost), 3)
                            result[instanceid]['day'] = day
                        else:
                            result[instanceid] = {
                                'instance_id': instanceid,
                                'instance_type': instancetype,
                                'instance_name': instancename,
                                'cost': cost,
                                'day': day
                            }
                    f.close()
                with db.atomic():
                    for k,v in result.items():
                        Bill.create(**v)
                    SyncBillInfo.create(username=self.username,day=fileday)


if __name__ == '__main__':
    c = SyncBills(day_from="2018-06-19",day_to="2018-06-20")
    c.handle()