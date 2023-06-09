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
Case Type   : 系统内部使用工具
Case Name   : gs_ctl status使用-D指定正确数据库实例目录查看备机运行状态是否成功
Description :
    1.gs_ctl status指定-D设置参数为正确的数据库实例目录
Expect      :
    1.gs_ctl status指定-D设置参数为正确的数据库实例目录成功
History     :
"""

import unittest

from testcase.utils.Constant import Constant
from testcase.utils.Logger import Logger
from yat.test import Node
from yat.test import macro

LOG = Logger()


class SystemInternalTools(unittest.TestCase):
    def setUp(self):
        LOG.info('--------------------this is setup----------------------')
        LOG.info('---Opengauss_Function_Tools_gs_ctl_Case0059开始执行-----')
        self.constant = Constant()
        self.PrimaryNode = Node('PrimaryDbUser')

    def test_system_internal_tools(self):
        LOG.info('-------若为单机环境，后续不执行，直接通过-------')
        query_cmd = f'''source {macro.DB_ENV_PATH};
            gs_om -t status --detail;
            '''
        LOG.info(query_cmd)
        query_msg = self.PrimaryNode.sh(query_cmd).result()
        LOG.info(query_msg)
        if 'Standby' not in query_msg:
            return '单机环境，后续不执行，直接通过'
        else:
            self.user_node = Node('Standby1DbUser')

        LOG.info('--------------------查看备机状态---------------')
        query_cmd = f'''source {macro.DB_ENV_PATH};
            gs_ctl status -D {macro.DB_INSTANCE_PATH} ;
            '''
        LOG.info(query_cmd)
        query_msg = self.user_node.sh(query_cmd).result()
        LOG.info(query_msg)
        self.assertIn(self.constant.gs_ctl_status_running, query_msg)

    def tearDown(self):
        LOG.info('------------this is tearDown--------------')
        # 无需清理环境
        LOG.info('---Opengauss_Function_Tools_gs_ctl_Case0059执行完成----')
