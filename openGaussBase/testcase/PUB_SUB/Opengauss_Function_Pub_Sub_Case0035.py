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
Case Type   : 基础功能
Case Name   : 同一数据库创建多个发布内容不全相同且publish不相同的订阅发布
Description :
    1.在两个集群创建表
    2.创建发布端
    3.创建订阅
    4.修改表数据
    5.查询是否同步
    6.修改表数据
    7.查询是否同步
    8.修改表数据
    9.查询是否同步
Expect      :
    1.成功
    2.成功
    3.成功
    4.成功
    5.s_pubsub_case035_1.tb_pubsub_case035_2未同步，其余同步
    6.成功
    7.s_pubsub_case035_1.tb_pubsub_case035_2未同步，其余同步
    8.成功
    9.s_pubsub_case035_2.tb_pubsub_case035_1未同步，其余同步
History     :
"""
import unittest
import os
from yat.test import macro
from yat.test import Node
from testcase.utils.Logger import Logger
from testcase.utils.CommonSH import CommonSH
from testcase.utils.Common import Common
from testcase.utils.Constant import Constant

Primary_SH = CommonSH('PrimaryDbUser')


@unittest.skipIf(3 != Primary_SH.get_node_num(), '非1+2环境不执行')
class Pubsubclass(unittest.TestCase):
    def setUp(self):
        self.log = Logger()
        self.log.info("-----------this is setup-----------")
        self.log.info(f"-----{os.path.basename(__file__)[:-3]} start-----")
        self.pri_userdb_pub = Node(node='PrimaryDbUser')
        self.pri_userdb_sub = Node(node='remote1_PrimaryDbUser')
        self.constant = Constant()
        self.commsh_pub = CommonSH('PrimaryDbUser')
        self.commsh_sub = CommonSH('remote1_PrimaryDbUser')
        self.com_pub = Common()
        self.tb_name1 = 'tb_pubsub_case035_1'
        self.tb_name2 = 'tb_pubsub_case035_2'
        self.schema_name1 = 's_pubsub_case035_1'
        self.schema_name2 = 's_pubsub_case035_2'
        self.tbs_name = 'tbs_pubsub_case035'
        self.subname1 = "sub_case035_1"
        self.subname2 = "sub_case035_2"
        self.pubname1 = "pub_case035_1"
        self.pubname2 = "pub_case035_2"
        self.port = str(int(self.pri_userdb_pub.db_port) + 1)
        self.wal_level = self.com_pub.show_param("wal_level")
        self.user_param_pub = f'-U {self.pri_userdb_pub.db_user} ' \
            f'-W {self.pri_userdb_pub.db_password}'
        self.user_param_sub = f'-U {self.pri_userdb_sub.db_user} ' \
            f'-W {self.pri_userdb_sub.db_password}'

    def test_pubsub(self):
        text = '--step:预置条件,修改pg_hba expect:成功'
        self.log.info(text)
        guc_res = self.commsh_pub.execute_gsguc(
            'reload', self.constant.GSGUC_SUCCESS_MSG, '',
            'all', False, False, '',
            f'host    replication  {self.pri_userdb_sub.db_user} '
            f'{self.pri_userdb_sub.db_host}/32 sha256')
        self.log.info(guc_res)
        self.assertTrue(guc_res, '执行失败:' + text)
        if 'logical' != self.wal_level:
            result = self.commsh_pub.execute_gsguc(
                'set', self.constant.GSGUC_SUCCESS_MSG, 'wal_level=logical')
            self.assertTrue(result, '执行失败:' + text)
            result = self.commsh_pub.restart_db_cluster(True)
            flg = self.constant.START_SUCCESS_MSG in result \
                  or 'Degrade' in result
            self.assertTrue(flg, '执行失败:' + text)
        guc_res = self.commsh_sub.execute_gsguc(
            'reload', self.constant.GSGUC_SUCCESS_MSG, '',
            'all', False, False, macro.DB_INSTANCE_PATH_REMOTE1,
            f'host    replication  {self.pri_userdb_pub.db_user} '
            f'{self.pri_userdb_pub.db_host}/32 sha256',
            macro.DB_ENV_PATH_REMOTE1)
        self.log.info(guc_res)
        self.assertTrue(guc_res, '执行失败:' + text)

        text = '--step1:两个集群均创建表 expect:成功--'
        self.log.info(text)
        sql = f"create schema {self.schema_name1};" \
            f"create table {self.schema_name1}.{self.tb_name1}" \
            f"(i int primary key, t text);" \
            f"create table {self.schema_name1}.{self.tb_name2}" \
            f"(i int primary key, id int, " \
            f"c varchar(10), constraint fk_id foreign key(id) " \
            f"references {self.schema_name1}.{self.tb_name1}(i));" \
            f"create schema {self.schema_name2};" \
            f"CREATE TABLE {self.schema_name2}.{self.tb_name1}" \
            f"(id int primary key CONSTRAINT id_nn NOT NULL," \
            f"use_filename VARCHAR2(20),filename VARCHAR2(255)," \
            f"text VARCHAR2(2000))PARTITION BY RANGE(id)" \
            f"(PARTITION P1 VALUES LESS THAN(30)," \
            f"PARTITION P2 VALUES LESS THAN(60)," \
            f"PARTITION P3 VALUES LESS THAN(90)," \
            f"  PARTITION P4 VALUES LESS THAN(MAXVALUE));" \
            f"create tablespace {self.tbs_name} " \
            f"RELATIVE LOCATION '{self.tbs_name}';" \
            f"create table {self.tb_name1}(i int primary key, t text) " \
            f"TABLESPACE {self.tbs_name};" \
            f"insert into {self.schema_name1}.{self.tb_name1} " \
            f"values(1, 'first'),(2, 'second');" \
            f"insert into {self.schema_name1}.{self.tb_name2} " \
            f"values(1, 1, 'first'),(2, 2, 'second');" \
            f"insert into {self.schema_name2}.{self.tb_name1} " \
            f"values (1, 's_pubsub_case035_2', '%一', '[]');" \
            f"insert into {self.tb_name1} values(1, 'first');" \
            f"select pg_switch_xlog();"
        result = self.commsh_pub.execut_db_sql(
            sql, sql_type=self.user_param_pub)
        self.log.info(result)
        self.assertEqual(result.count(self.constant.TABLE_CREATE_SUCCESS),
                         9, '执行失败:' + text)
        self.assertEqual(result.count(self.constant.INSERT_SUCCESS_MSG),
                         4, '执行失败:' + text)
        result = self.commsh_sub.execut_db_sql(sql, self.user_param_sub, None,
                                               macro.DB_ENV_PATH_REMOTE1)
        self.log.info(result)
        self.assertEqual(result.count(self.constant.TABLE_CREATE_SUCCESS),
                         9, '执行失败:' + text)
        self.assertEqual(result.count(self.constant.INSERT_SUCCESS_MSG),
                         4, '执行失败:' + text)

        text = '--step2:创建发布端 expect:成功--'
        self.log.info(text)        
        sql = f"CREATE PUBLICATION {self.pubname1}  " \
            f"FOR  TABLE  {self.tb_name1}," \
            f"{self.schema_name1}.{self.tb_name1}," \
            f"{self.schema_name1}.{self.tb_name2} " \
            f"with (publish='insert'); " \
            f"CREATE PUBLICATION {self.pubname2} " \
            f"FOR TABLE  {self.tb_name1}, " \
            f"only {self.schema_name1}.{self.tb_name1}," \
            f"{self.schema_name2}.{self.tb_name1} " \
            f"with (publish='update,delete');"
        result = self.commsh_pub.execut_db_sql(sql,
                                               sql_type=self.user_param_pub)
        self.log.info(result)
        self.assertIn(self.constant.create_pub_succ_msg, result,
                      '执行失败:' + text)
        self.assertNotIn(self.constant.SQL_WRONG_MSG[1], result,
                         '执行失败:' + text)

        text = '--step3:创建订阅 expect:成功--'
        self.log.info(text)
        result = self.commsh_sub.execute_generate(
            macro.COMMON_PASSWD, env_path=macro.DB_ENV_PATH_REMOTE1)
        self.assertIn('', result, '执行失败:' + text)
        sql = f"CREATE SUBSCRIPTION {self.subname1} CONNECTION " \
            f"'host={self.pri_userdb_pub.db_host} " \
            f"port={self.port} " \
            f"user={self.pri_userdb_pub.db_user} " \
            f"dbname={self.pri_userdb_pub.db_name} " \
            f"password={self.pri_userdb_pub.ssh_password}' " \
            f"PUBLICATION {self.pubname1};"\
            f"CREATE SUBSCRIPTION {self.subname2} CONNECTION " \
            f"'host={self.pri_userdb_pub.db_host} " \
            f"port={self.port} " \
            f"user={self.pri_userdb_pub.db_user} " \
            f"dbname={self.pri_userdb_pub.db_name} " \
            f"password={self.pri_userdb_pub.ssh_password}' " \
            f"PUBLICATION {self.pubname2};" \
            f"select pg_sleep(10);"
        result = self.commsh_sub.execut_db_sql(sql, self.user_param_sub, None,
                                               macro.DB_ENV_PATH_REMOTE1)
        self.log.info(result)
        self.assertEqual(result.count(self.constant.create_sub_succ_msg), 2,
                         '执行失败:' + text)

        text = '--step4:修改表数据 expect:成功--'
        self.log.info(text)
        sql = f"update  {self.schema_name1}.{self.tb_name2} " \
            f"set c= 'update' where i <2;select pg_sleep(5.5);" \
            f"update  {self.tb_name1} set t= 'update';" \
            f"update  {self.schema_name1}.{self.tb_name1} " \
            f"set t= 'update' where i <2;" \
            f"update  {self.schema_name2}.{self.tb_name1} " \
            f"set filename= 'update123';" \
            f"select * from pg_replication_slots ;"
        result = self.commsh_pub.execut_db_sql(sql,
                                               sql_type=self.user_param_pub)
        self.log.info(result)
        self.assertEqual(result.count(self.constant.UPDATE_SUCCESS_MSG),
                         4, '执行失败' + text)

        text = "--step5:查询是否同步 " \
               "expect:s_pubsub_case035_1.tb_pubsub_case035_2未同步，其余同步--"
        self.log.info(text)
        sql_select = f"select * from {self.schema_name1}.{self.tb_name1};" \
            f"select * from {self.schema_name1}.{self.tb_name2};" \
            f"select * from {self.schema_name2}.{self.tb_name1};" \
            f"select * from {self.tb_name1};"
        result = self.commsh_sub.execut_db_sql(sql_select,
                                               self.user_param_sub,
                                               None,
                                               macro.DB_ENV_PATH_REMOTE1)
        self.log.info(result)
        self.assertEqual(result.count('1 | update'),
                         2, '执行失败' + text)
        self.assertIn('2 | second', result, '执行失败' + text)
        self.assertIn('1 |  1 | first', result, '执行失败' + text)
        self.assertIn('2 |  2 | second', result, '执行失败' + text)
        self.assertIn('1 | s_pubsub_case035_2 | update123 | []',
                      result, '执行失败' + text)
        self.assertEqual(result.count('2 rows'), 2, '执行失败' + text)
        self.assertEqual(result.count('1 row'), 2, '执行失败' + text)

        text = '--step6:修改表数据 expect:成功--'
        self.log.info(text)
        sql = f"delete from {self.schema_name1}.{self.tb_name2};" \
            f"delete from {self.schema_name1}.{self.tb_name1};" \
            f"delete from {self.schema_name2}.{self.tb_name1};" \
            f"delete from {self.tb_name1};"
        result = self.commsh_pub.execut_db_sql(sql,
                                               sql_type=self.user_param_pub)
        self.log.info(result)
        self.assertEqual(result.count(self.constant.DELETE_SUCCESS_MSG),
                         4, '执行失败' + text)

        text = "--step7:查询是否同步 " \
               "expect:s_pubsub_case035_1.tb_pubsub_case035_2未同步，其余同步--"
        self.log.info(text)
        result = self.commsh_sub.execut_db_sql(sql_select,
                                               self.user_param_sub,
                                               None,
                                               macro.DB_ENV_PATH_REMOTE1)
        self.log.info(result)
        self.assertEqual(result.count('0 rows'), 3, '执行失败' + text)
        self.assertEqual(result.count('2 rows'), 1, '执行失败' + text)
        self.assertIn('1 |  1 | first', result, '执行失败' + text)
        self.assertIn('2 |  2 | second', result, '执行失败' + text)

        text = '--step8:修改表数据 expect:成功--'
        self.log.info(text)
        sql = f"insert into {self.schema_name1}.{self.tb_name1} " \
            f"values(1, 'first'),(2, 'second');" \
            f"insert into {self.schema_name1}.{self.tb_name2} " \
            f"values(3, 1, 'first'),(4, 2, 'second');" \
            f"insert into {self.schema_name2}.{self.tb_name1} " \
            f"values (1, 's_pubsub_case035_2', '%一', '[]');" \
            f"insert into {self.tb_name1} values(1, 'first');"
        result = self.commsh_pub.execut_db_sql(sql,
                                               sql_type=self.user_param_pub)
        self.log.info(result)
        self.assertEqual(result.count(self.constant.INSERT_SUCCESS_MSG),
                         4, '执行失败' + text)

        text = "--step9:查询是否同步 " \
               "expect:s_pubsub_case035_2.tb_pubsub_case035_1未同步，其余同步--"
        self.log.info(text)
        result = self.commsh_sub.execut_db_sql(sql_select,
                                               self.user_param_sub,
                                               None,
                                               macro.DB_ENV_PATH_REMOTE1)
        self.log.info(result)
        self.assertEqual(result.count('0 rows'), 1, '执行失败' + text)
        self.assertEqual(result.count('2 rows'), 1, '执行失败' + text)
        self.assertEqual(result.count('4 rows'), 1, '执行失败' + text)
        self.assertEqual(result.count('1 row'), 1, '执行失败' + text)

    def tearDown(self):
        self.log.info('------------this is tearDown-------------')
        text = '--清理环境--'
        self.log.info(text)
        sql = f"DROP PUBLICATION if exists {self.pubname1};" \
            f"DROP PUBLICATION if exists {self.pubname2};"
        drop_pub_result = self.commsh_pub.execut_db_sql(
            sql, sql_type=self.user_param_pub)
        self.log.info(drop_pub_result)
        sql = f"DROP SUBSCRIPTION  {self.subname1};" \
            f"DROP SUBSCRIPTION  {self.subname2}"
        drop_sub_result = self.commsh_sub.execut_db_sql(
            sql, self.user_param_sub, None, macro.DB_ENV_PATH_REMOTE1)
        self.log.info(drop_sub_result)
        sql = f"DROP table if exists {self.schema_name1}.{self.tb_name2};" \
            f"DROP table if exists {self.schema_name1}.{self.tb_name1};" \
            f"DROP table if exists {self.schema_name2}.{self.tb_name1};" \
            f"DROP table if exists {self.tb_name1};" \
            f"drop schema {self.schema_name1};" \
            f"drop schema {self.schema_name2};" \
            f"drop tablespace {self.tbs_name};"
        result = self.commsh_sub.execut_db_sql(sql, self.user_param_sub, None,
                                               macro.DB_ENV_PATH_REMOTE1)
        self.log.info(result)
        result = self.commsh_pub.execut_db_sql(sql, 
                                               sql_type=self.user_param_pub)
        self.log.info(result)
        guc_res1 = self.commsh_pub.execute_gsguc(
            'reload', self.constant.GSGUC_SUCCESS_MSG, '',
            'all', False, False, '',
            f'host    replication  {self.pri_userdb_sub.db_user} '
            f'{self.pri_userdb_sub.db_host}/32')
        self.log.info(guc_res1)
        guc_res = self.commsh_sub.execute_gsguc(
            'reload', self.constant.GSGUC_SUCCESS_MSG, '',
            'all', False, False, macro.DB_INSTANCE_PATH_REMOTE1,
            f'host    replication  {self.pri_userdb_pub.db_user} '
            f'{self.pri_userdb_pub.db_host}/32',
            macro.DB_ENV_PATH_REMOTE1)
        self.log.info(guc_res)
        self.assertTrue(guc_res, '执行失败:' + text)
        self.assertTrue(guc_res1, '执行失败:' + text)
        self.assertIn(self.constant.drop_pub_succ_msg, drop_pub_result,
                      '执行失败' + text)
        self.assertIn(self.constant.drop_sub_succ_msg, drop_sub_result,
                      '执行失败' + text)
        self.log.info(f"-----{os.path.basename(__file__)[:-3]} end-----")