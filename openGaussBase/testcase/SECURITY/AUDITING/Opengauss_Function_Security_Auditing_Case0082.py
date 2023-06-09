"""
Copyright (c) 2022 Huawei Technologies Co.,Ltd.

openGauss is licensed under Mulan PSL v2.
You can use this software according to the terms and conditions of the Mulan PSL v2.
You may obtain a copy of Mulan PSL v2 at:

          http://license.coscl.org.cn/MulanPSL2

THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
See the Mulan PSL v2 for more details.
"""
"""
Case Type   : security-auditing
Case Name   : 开启COPY审计功能，设置audit_copy_exec=1
Description :
    1.查看参数默认值：show audit_copy_exec;
    2.登录数据库，创建表table003,create table table003(id int,name char(10));
    3.将表中数据拷贝到文件中，COPY table003 TO '/home/mode.dat';
    4.删除表，drop table003; 删除文件
    5.登录数据库，查看审计日志SELECT * FROM pg_query_audit('$start_time',
    '$end_time');时间设在最接近登录数据库的时间
Expect      :
    1.返回值：1
    2.创建成功
    3.执行成功
    4.删除成功
    5.查询到copy操作的信息
History     :
"""
import unittest
from yat.test import Node
from yat.test import macro
from testcase.utils.Common import Common
from testcase.utils.CommonSH import *
from testcase.utils.Logger import Logger


class Auditing(unittest.TestCase):
    def setUp(self):
        self.logger = Logger()
        self.logger.info(
            '-----Opengauss_Function_Security_Auditing_Case0082 start-----')
        self.sh_primy = CommonSH('PrimaryDbUser')
        self.userNode = Node('PrimaryDbUser')
        self.path = os.path.join(macro.DB_INSTANCE_PATH, 'test.txt')
        self.common = Common()
        self.DB_ENV_PATH = macro.DB_ENV_PATH

    def test_security(self):
        excute_cmd1 = f'touch {self.path}'
        msg1 = self.userNode.sh(excute_cmd1).result()
        self.logger.info(msg1)
        excute_cmd2 = f'show audit_copy_exec;'
        msg2 = self.sh_primy.execut_db_sql(excute_cmd2)
        self.logger.info(msg2)
        self.common.equal_sql_mdg(msg2, 'audit_copy_exec', '1', '(1 row)',
                                  flag='1')
        start_time_msg = self.sh_primy.execut_db_sql("SELECT sysdate;")
        start_time = start_time_msg.splitlines()[2].strip()
        time.sleep(5)
        sql_cmd2 = f'create table table003(id int,name char(10));' \
                   f'copy table003 to \'{self.path}\';' \
                   f'drop table table003;'
        msg2 = self.sh_primy.execut_db_sql(sql_cmd2)
        self.logger.info(msg2)
        time.sleep(5)
        end_time_msg = self.sh_primy.execut_db_sql('SELECT sysdate;')
        end_time = end_time_msg.splitlines()[2].strip()
        sql_cmd3 = f'select * from pg_query_audit(\'{start_time}\',\
                   \'{end_time}\');'
        excute_cmd3 = f'source {self.DB_ENV_PATH};' \
                      f'gsql -d {self.userNode.db_name} -p ' \
                      f'{self.userNode.db_port} -c "{sql_cmd3}"'
        msg3 = self.userNode.sh(excute_cmd3).result()
        self.logger.info(msg3)
        self.assertTrue(msg3.find('copy table003 to') > -1)

    def tearDown(self):
        excute_cmd1 = f'rm -rf {self.path}'
        msg1 = self.userNode.sh(excute_cmd1).result()
        self.logger.info(msg1)
        self.logger.info(
            '------Opengauss_Function_Security_Auditing_Case0082 end------')
