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
Case Type   : tools
Case Name   : 通过gaussdb启动数据库进程时，不另开一个窗口启动进程
Description :
    1.关闭正在运行的数据库
    gs_ctl stop -D /opt/openGauss_zl/cluster/dn1
    2.查看进程，确定关闭成功
    ps -ef|grep zl
    3.使用gaussdb工具运行进程
    gaussdb -D /opt/openGauss_zl/cluster/dn1 -p 19701  -M primary
    4.换窗口查看进程，确定gaussdb进程运行成功
    ps -ef|grep zl
Expect      :
    1.关闭正在运行的数据库成功
    2.查看进程，数据库连接进程不存在，数据库关闭成功
    3.使用gaussdb工具后台启动数据库成功，但无法退出运行过程（除非ctrl+c强制退出）
    4.换窗口查看进程，zl用户下有gaussdb进程正在运行，gaussdb进程运行成功
History     :
"""
import unittest
from testcase.utils.ComThread import ComThread
from yat.test import Node
from yat.test import macro
from testcase.utils.Logger import Logger


class Tools(unittest.TestCase):
    def setUp(self):
        self.logger = Logger()
        self.logger.info('--Opengauss_Function_Tools_Gaussdb_Case0003 start--')
        self.userNode = Node('PrimaryDbUser')
        self.userNode2 = Node('PrimaryDbUser')
        self.DB_ENV_PATH = macro.DB_ENV_PATH
        self.DB_INSTANCE_PATH = macro.DB_INSTANCE_PATH


    def test_systools(self):
        self.logger.info("--------关闭正在运行的数据库--------")
        excute_cmd1 = f'source {self.DB_ENV_PATH};' \
                      f'gs_ctl stop -D {self.DB_INSTANCE_PATH}'
        self.logger.info(excute_cmd1)
        msg1 = self.userNode.sh(excute_cmd1).result()
        self.logger.info(msg1)
        self.logger.info('--------查看进程，确定关闭成功--------')
        excute_cmd2 = f'ps -ef|grep {self.userNode.ssh_user}'
        self.logger.info(excute_cmd2)
        msg2 = self.userNode.sh(excute_cmd2).result()
        self.logger.info(msg2)
        self.assertFalse(self.DB_INSTANCE_PATH in msg2)
        self.logger.info('--------使用gaussdb工具后台运行进程--------')
        excute_cmd3 = f'source {self.DB_ENV_PATH};' \
                      f'gaussdb -D {self.DB_INSTANCE_PATH} -p' \
                      f' {self.userNode.db_port} -M primary'
        self.logger.info(excute_cmd3)
        thread_2 = ComThread(self.userNode2.sh, args=(excute_cmd3,))
        thread_2.setDaemon(True)
        thread_2.start()
        thread_2.join(10)
        msg_result_2 = thread_2.get_result()
        self.logger.info(msg_result_2)
        self.logger.info('--------查看进程，确定gaussdb进程运行成功--------')
        excute_cmd4 = f'ps -ef|grep {self.userNode.ssh_user}'
        self.logger.info(excute_cmd4)
        msg4 = self.userNode.sh(excute_cmd4).result()
        self.logger.info(msg4)
        execute_cmd5 = f'source {self.DB_ENV_PATH};gs_om -t status --detail'
        msg5 = self.userNode.sh(execute_cmd5).result()
        self.logger.info(msg5)
        self.assertTrue(msg5.find('P Primary Normal') > -1)

    def tearDown(self):
        self.logger.info('-Opengauss_Function_Tools_Gaussdb_Case0003 finish-')
