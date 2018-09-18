# ~*~ coding: utf-8 ~*~
import oss2,time,re
from app import get_logger
from app.models import Bill
from app.models import db
from app.models import Sync_Bill_History

logger = get_logger(__name__)

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

    def get_sync_files(self):
        sync_files = []
        begin_timestamp = int(time.mktime(time.strptime(self.day_from, "%Y-%m-%d")))
        end_timestamp = int(time.mktime(time.strptime(self.day_to, "%Y-%m-%d")) )
        for b in oss2.ObjectIterator(self.bucket):
            fileday,filename = b.key.split('/')
            if not re.search(r"(\d{4}-\d{1,2}-\d{1,2})",fileday):
                continue
            file_timestamp = time.mktime(time.strptime(fileday, "%Y-%m-%d")) - 24 * 3600
            synced = self.is_synced(filename=filename,fileday=fileday)
            if file_timestamp >= begin_timestamp and file_timestamp <= end_timestamp and not synced:
                sync_files.append(b.key)
        return sync_files

    def is_synced(self,filename,fileday):
        synced = Sync_Bill_History.select().where((Sync_Bill_History.filename == filename) |
                                                        (Sync_Bill_History.day == fileday)).first()
        if synced and not synced.filename:
            synced.filename = filename;synced.save()
        return True if synced else False

    def handle(self):
        for filename in self.get_sync_files():
            content = self.bucket.get_object(filename).read().decode()
            bill_list = content.split('\r\n')[1:]
            result = {}
            for line in bill_list:
                try:
                    linelist = line.split(',')
                    day = linelist[2]
                    instanceid = linelist[11].strip()
                    instancename = linelist[12] or instanceid
                    instancetype = linelist[5]
                    cost = float(linelist[21])
                except Exception:
                    print(line)
                    continue
                if instanceid in result:
                    result[instanceid]['cost'] = round((result[instanceid]['cost'] + cost), 3)
                    result[instanceid]['day'] = day
                else:
                    result[instanceid] = {'instance_id': instanceid,
                        'instance_type': instancetype,'instance_name': instancename,
                        'cost': cost,'day': day}
            with db.atomic():
                Bill.insert_many(list(result.values())).execute()
                file_day,file_name = filename.split('/')
                Sync_Bill_History.create(username=self.username,filename=file_name,day=file_day)



'''
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
        print(oss2.ObjectIterator(self.bucket))
        for b in oss2.ObjectIterator(self.bucket):
            print(b)
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
            if  timestamp < begin or  timestamp > end :
                continue
            is_synced = Sync_Bill_History.select().where(Sync_Bill_History.filename == filename |
                                                         Sync_Bill_History.day == fileday).first()
            if is_synced:
                is_synced.filename = filename
                is_synced.save()
                continue
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
                    Sync_Bill_History.create(username=self.username,day=fileday,filename=filename)
'''