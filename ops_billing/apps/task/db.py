from apps import global_config
config = global_config()

import pymysql
db = pymysql.connect(host=config.get('DEFAULT','DB_HOST'),user=config.get('DEFAULT','DB_USER'),
                     password=config.get('DEFAULT','DB_PASSWD'),db=config.get('DEFAULT','DB_DATABASE'))

