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
Case Type   : 数据库系统
Case Name   : LocalDateTime类型getObject并发用例
Description :
    1.写配置文件
    2.编译java工具
    3.建表并插入数据
    4.并发执行java脚本
    6.重复step5 50次
Expect      :
History     :
"""
import unittest
import os
import datetime
import time
from yat.test import Node
from yat.test import macro
from testcase.utils.Logger import Logger
from testcase.utils.Common import Common
from testcase.utils.CommonSH import CommonSH
from testcase.utils.Constant import Constant
from testcase.utils.ComThread import ComThread


class Jdbcisreadonly(unittest.TestCase):

    def setUp(self):
        self.log = Logger()
        self.db_primary_user_node = Node(node='PrimaryDbUser')
        self.db_primary_root_node = Node(node='PrimaryRoot')
        self.log.info("-----------this is setup-----------")
        self.log.info("Opengauss_Function_JDBC_Set_Get_Object_Case0019 start")
        self.targetpath = "/home/jdbc_test"
        self.properties = os.path.join(self.targetpath,
                                       "jdbc_case0001.properties")
        self.sql_path = os.path.join(self.targetpath, "jdbc_set_get_object")
        self.java_name = "jdbc_set_get_object_case0019"
        self.tb_name = "jdbc_set_get_object_case0019"
        self.common = Common()
        self.constant = Constant()
        self.commonshpri = CommonSH('PrimaryDbUser')

    def test_index(self):
        self.log.info('--------1.写配置文件-------')
        self.common.scp_file(self.db_primary_root_node,
                             f"{self.java_name}.java", self.targetpath)
        result = self.db_primary_root_node.sh(
            f"touch {self.properties}").result()
        self.log.info(result)
        config = f'echo "password=' \
            f'{self.db_primary_user_node.db_password}"> {self.properties}'
        self.db_primary_root_node.sh(config)
        config = f'echo "port={self.db_primary_user_node.db_port}">> ' \
            f'{self.properties}'
        self.db_primary_root_node.sh(config)
        config = f'echo "hostname={self.db_primary_user_node.db_host}">> ' \
            f'{self.properties}'
        self.db_primary_root_node.sh(config)
        config = f'echo "user={self.db_primary_user_node.db_user}">> ' \
            f'{self.properties}'
        self.db_primary_root_node.sh(config)
        config = f'echo "dbname={self.db_primary_user_node.db_name}">> ' \
            f'{self.properties}'
        self.db_primary_root_node.sh(config)
        config = f'echo "stringtype=unspecified">> {self.properties}'
        self.db_primary_root_node.sh(config)
        config = f'cat {self.properties}'
        result = self.db_primary_root_node.sh(config).result()
        self.assertTrue("password=" in result and "port=" in result
                        and "hostname=" in result and "user=" in result
                        and "dbname=" in result)

        self.log.info('--------------2. 编译java工具------------------')
        self.db_primary_root_node.scp_put(macro.JDBC_PATH,
                                          f"{self.targetpath}/postgresql.jar")
        cmd = f"javac -encoding utf-8 -cp " \
            f"{os.path.join(self.targetpath, 'postgresql.jar')} " \
            f"{os.path.join(self.targetpath, f'{self.java_name}.java')}"
        self.log.info(cmd)
        result = self.db_primary_root_node.sh(cmd).result()
        self.log.info(result)

        self.log.info("---------------3.创建表并插入数据----------------------")
        cmd = f"drop table if exists {self.tb_name};" \
            f"create table {self.tb_name}(t_time timestamp);"
        result = self.commonshpri.execut_db_sql(cmd)
        self.log.info(result)
        self.assertIn(self.constant.CREATE_TABLE_SUCCESS, result)

        result_time = self.db_primary_root_node.sh(
            "date '+%y-%m-%dT%H:%M'").result()
        self.log.info(result_time)
        now = []
        now.append((datetime.datetime.strptime(
            result_time, '%y-%m-%dT%H:%M') -
                    datetime.timedelta(minutes=1)
                    ).strftime('%y-%m-%dT%H:%M'))
        now.append((datetime.datetime.strptime(
            result_time, '%y-%m-%dT%H:%M') -
                    datetime.timedelta(minutes=-1)
                    ).strftime('%y-%m-%dT%H:%M'))
        now.append((datetime.datetime.strptime(
            result_time, '%y-%m-%dT%H:%M')).strftime('%y-%m-%dT%H:%M'))
        self.log.info(f"now is {now}")

        cmd = f"insert into {self.tb_name} values('infinity'), " \
            f"('2020-02-29 23:59:59'), ('now');"
        result = self.commonshpri.execut_db_sql(cmd)
        self.log.info(result)
        self.assertIn('INSERT', result)

        self.log.info("-------------4.运行java工具---------------------")
        for index in range(50):
            self.log.info(f"======round {index}========")
            cmd = f" java -cp " \
                f"{os.path.join(self.targetpath, 'postgresql.jar')}" \
                f":{self.targetpath} " \
                f"{self.java_name} -F {self.properties}"
            self.log.info(cmd)
            insert_thread = []
            for i in range(9):
                insert_thread.append(ComThread(
                    self.common.get_sh_result,
                    args=(self.db_primary_root_node, cmd)))
                insert_thread[i].setDaemon(True)
                insert_thread[i].start()

            for i in range(9):
                insert_thread[i].join(30)
                select_result = insert_thread[i].get_result()
                self.assertIn(f"第0行结果：+999999999-12-31T23:59:59.999999999",
                              select_result)
                self.assertIn(f"第1行结果：2020-02-29T23:59:59", select_result)
                self.assertTrue((select_result.count(now[0]) +
                                 select_result.count(now[1]) +
                                 select_result.count(now[2])) == 1)
            time.sleep(3)

    def tearDown(self):
        self.log.info('------------this is tearDown-------------')
        self.log.info('------------------清理环境-------------')
        cmd = f"drop table if exists {self.tb_name};"
        result = self.commonshpri.execut_db_sql(cmd)
        self.log.info(result)
        cmd = f"rm -rf {self.targetpath}"
        self.log.info(cmd)
        self.db_primary_root_node.sh(cmd)
        self.log.info("-Opengauss_Function_JDBC_Set_Get_Object_Case0019 end-")
