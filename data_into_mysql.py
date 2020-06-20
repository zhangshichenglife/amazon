import pymysql
from config import *


class MysqlSave:

    def __init__(self):
        # mysql 数据库配置
        self.mysql_connect = pymysql.connect(host=HOST,
                                             port=PORT,
                                             user=USER,
                                             password=PASSWORD,
                                             database=DATABASE,
                                             charset='utf8')
    pass

