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
Case Type   : GUC
Case Name   : 修改track_thread_wait_status_interval为非法值
Description :
    步骤1:查询track_thread_wait_status_interval默认值
    show track_thread_wait_status_interval;
    show synchronous_commit;
    步骤2:synchronous_commit设置为on，{self.param}设置为60 重启
    gs_guc reload -D {CLUSTER/DN1} -c "{self.param}=''";
    gs_guc reload -D {CLUSTER/DN1} -c "{self.param}=' '";
    gs_guc reload -D {CLUSTER/DN1} -c "{self.param}=
    ten minutes";
    gs_guc reload -D {CLUSTER/DN1} -c "{self.param}=1天";
    show track_thread_wait_status_interval;
    步骤3:恢复默认值
    gs_guc reload -D {CLUSTER/DN1} -c
    "track_thread_wait_status_interval='30min'";
Expect      :
    步骤1:显示默认值30min
    步骤2:设置成功，重启Normal
    步骤3:恢复默认值
History     :
"""

import unittest

from testcase.utils.CommonSH import CommonSH
from testcase.utils.Constant import Constant
from testcase.utils.Logger import Logger

LOGGER = Logger()
COMMONSH = CommonSH("PrimaryDbUser")


class GucTestCase(unittest.TestCase):
    def setUp(self):
        LOGGER.info("==Opengauss_Function_Guc_Run_Statistics_Case0065开始执行==")
        self.constant = Constant()
        status = COMMONSH.get_db_cluster_status()
        self.assertTrue("Degraded" in status or "Normal" in status)
        self.param = "track_thread_wait_status_interval"

    def test_guc(self):
        LOGGER.info("步骤1:查询{self.param} 期望：默认值30min")
        sql_cmd = COMMONSH.execut_db_sql(f"show {self.param};")
        LOGGER.info(sql_cmd)
        self.assertEqual("30min", sql_cmd.splitlines()[-2].strip())

        LOGGER.info("步骤2:修改参数{self.param}设置为空浮点数字母NULL等")
        temp_list = ["''", "' '", 'ten minutes', '1天', '60000ms', '3600s']
        for i in temp_list:
            result = COMMONSH.execute_gsguc("set",
                                           self.constant.GSGUC_SUCCESS_MSG,
                                           f"{self.param}={i}")
            self.assertFalse(result)
            result = COMMONSH.execute_gsguc("reload",
                                           self.constant.GSGUC_SUCCESS_MSG,
                                           f"{self.param}={i}")
            self.assertFalse(result)

        LOGGER.info("步骤3:恢复默认值")
        del temp_list
        result = COMMONSH.execute_gsguc("reload",
                                       self.constant.GSGUC_SUCCESS_MSG,
                                       f"{self.param}='30min'")
        self.assertTrue(result)
        COMMONSH.restart_db_cluster()
        result = COMMONSH.get_db_cluster_status()
        self.assertTrue("Degraded" in result or "Normal" in result)

    def tearDown(self):
        LOGGER.info("恢复默认值")
        sql_cmd = COMMONSH.execut_db_sql(f"show {self.param};")
        if "30min" != sql_cmd.splitlines()[-2].strip():
            COMMONSH.execute_gsguc("reload",
                                  self.constant.GSGUC_SUCCESS_MSG,
                                  f"{self.param}='30min'")
            COMMONSH.restart_db_cluster()
        status = COMMONSH.get_db_cluster_status()
        self.assertTrue("Degraded" in status or "Normal" in status)
        LOGGER.info("==Opengauss_Function_Guc_Run_Statistics_Case0065执行结束==")
