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
Case Name   : 分区表标创建索引后basebackup备份数据，进行alter操作后恢复数据
Description :
    1.执行create_partition.sql创建数据
    2.创建索引
    3.备份数据库
    4.进行alter等操作
    5.stop数据库
    6.恢复数据库
    7.重启数据库
    8.查询索引
    9.查询
Expect      :
    1.创建表并插入数据成功
    2.创建索引成功
    3.数据库备份成功
    4. alter成功
    5.停止数据库成功
    6.恢复数据成功
    7.重启数据库成功
    8.索引存在
    9.结果正确
History     :
"""
import os
import unittest
from yat.test import Node
from yat.test import macro
import sys
sys.path.append(sys.path[0] + "/../")
from testcase.utils.Logger import Logger
from testcase.utils.Constant import Constant
from testcase.utils.Common import Common
from testcase.utils.CommonSH import CommonSH

logger = Logger()
common = Common()

class set_search_limit(unittest.TestCase):
    dbPrimaryUserNode = Node(node='PrimaryDbUser')
    dbPrimaryRootNode = Node(node='PrimaryRoot')
    DB_INSTANCE_PATH = macro.DB_INSTANCE_PATH
    commsh = CommonSH('PrimaryDbUser')
    target_path = macro.DB_INSTANCE_PATH + '/testscript'
    sql_path = target_path + '/create_partition.sql'
    dump_file_name = 'Opengauss_Gin_Index_0057.tar' 
    backup_path = macro.PG_LOG_PATH + '/back'

    def setUp(self):
        logger.info("-----------this is setup-----------")
        logger.info("-----------Opengauss_Gin_Index_0057 start-----------")
        self.Constant = Constant()
        logger.info("-----------------get number of node------------------------")
        self.nodelist = ['Standby1DbUser', 'Standby2DbUser']
        result = self.commsh.get_db_cluster_status('detail')
        logger.info(result)
        self.node_num = result.count('Standby Normal') + 1
        self.comshsta = []
        logger.info(self.node_num)
        for i in range(int(self.node_num) - 1):
            self.comshsta.append(CommonSH(self.nodelist[i]))

    def test_set_search_limit(self):
        
        logger.info('---------------execute create_partition.sql---------------------')
        common.scp_file(self.dbPrimaryUserNode, 'create_partition.sql', self.target_path)
        sql_bx_cmd = f'''
                        source {macro.DB_ENV_PATH};    
                        gsql -d {self.dbPrimaryUserNode.db_name} -p {self.dbPrimaryUserNode.db_port}  -f {self.sql_path}
                       
                        '''
        logger.info(sql_bx_cmd)
        sql_bx_msg = self.dbPrimaryUserNode.sh(sql_bx_cmd).result()
        logger.info(sql_bx_msg)
        
        logger.info('------------------create index-------------------------')
        sql = 'CREATE INDEX test_gin_student_index_row2 ON test_gin_student_row USING     GIN(to_tsvector(\'english\', data1)) LOCAL         (    PARTITION data2_index_1,    PARTITION data2_index_2,    PARTITION data2_index_3 ) ;'
        msg = self.commsh.execut_db_sql(sql)
        logger.info(msg)
        self.assertTrue(msg.find(self.Constant.CREATE_INDEX_SUCCESS_MSG)>-1)
        
        logger.info('--------------------basebackup-------------------------')
        shell_cmd = f'rm -rf {self.backup_path}; mkdir {self.backup_path}'
        logger.info(shell_cmd)
        result = self.dbPrimaryUserNode.sh(shell_cmd).result()
        logger.info(result)
        dumpCmd = f"source {macro.DB_ENV_PATH};" \
            f"gs_basebackup -D {self.backup_path} -h " \
            f"{self.dbPrimaryUserNode.db_host} -p " \
            f"{self.dbPrimaryUserNode.db_port} -U " \
            f"{self.dbPrimaryUserNode.ssh_user} -t 3600"
        logger.info(dumpCmd)
        dumpMsg = self.dbPrimaryUserNode.sh(dumpCmd).result()
        logger.info(dumpMsg)
        self.assertTrue(dumpMsg.find('success') > -1)

        logger.info('----------------alter index-----------------------')
        sql = 'alter index test_gin_student_index_row2 rename to test_gin_2_first_name;'
        msg = self.commsh.execut_db_sql(sql)
        logger.info(msg)
        self.assertTrue(msg.find(self.Constant.ALTER_INDEX_SUCCESS_MSG)>-1)

        logger.info('--------------------restore database-------------------------')
        result = self.commsh.stop_db_cluster()
        self.assertTrue(result)
        cmd = 'rm -rf ' + macro.DB_INSTANCE_PATH + '/*'
        logger.info(cmd)
        self.dbPrimaryUserNode.sh(cmd)
        cmd = 'cp -r ' + self.backup_path + '/* ' + macro.DB_INSTANCE_PATH
        logger.info(cmd)
        self.dbPrimaryUserNode.sh(cmd)

        logger.info("-----------start opengauss-----------")
        result = self.commsh.start_db_cluster(True)
        logger.info(result)
        result = ('Degraded' in result) or (self.Constant.START_SUCCESS_MSG in result)
        self.assertTrue(result)

        for i in range(int(self.node_num) - 1):
            result = self.comshsta[i].execute_gsctl('build', self.Constant.BUILD_SUCCESS_MSG, '-b full')
            self.assertTrue(result)

        logger.info('------------------check index-------------------------')
        sql = '\di'
        msg = self.commsh.execut_db_sql(sql)
        logger.info(msg)
        self.assertTrue(msg.find('test_gin_student_index_row2') > -1)

        logger.info('------------------querry-------------------------')
        sql = "SET ENABLE_SEQSCAN=off;explain SELECT * FROM test_gin_student_row WHERE to_tsvector(\'english\', data1) @@ to_tsquery(\'english\', 'Mexico') ORDER BY num, data1, data2;SELECT * FROM test_gin_student_row WHERE to_tsvector(\'english\', data1) @@ to_tsquery(\'english\', \'Mexico\') ORDER BY num, data1, data2;"
        msg = self.commsh.execut_db_sql(sql)
        logger.info(msg)
        self.assertTrue(msg.find(
            '13 | Mexico, officially the United Mexican States, is a federal republic in the southern part of North America. | Mexico') > -1)
        self.assertTrue(msg.find(
            '14 | Mexico, officially the United Mexican States, is a federal republic in the southern part of North America. | Mexico') > -1)
        self.assertTrue(msg.find(
            '5001 | Mexico, officially the United Mexican States, is a federal republic in the southern part of North America. | Mexico') > -1)
        self.assertTrue(msg.find('Bitmap Index Scan on test_gin_student_index_row2') > -1)

    def tearDown(self):
        logger.info('----------------this is tearDown-----------------------')
        logger.info('-------------------build standby-----------------------')
        for i in range(int(self.node_num) - 1):
            result = self.comshsta[i].execute_gsctl('build', self.Constant.BUILD_SUCCESS_MSG, '-b full')
            self.assertTrue(result)
        logger.info('----------------drop table-----------------------')
        sql = 'drop table test_gin_student_row;'
        msg = self.commsh.execut_db_sql(sql)
        logger.info(msg)
        logger.info("-----------delete scripts-----------")
        cmd = 'rm -rf ' + self.target_path
        self.dbPrimaryRootNode.sh(cmd)
        logger.info("-----------delete backup-----------")
        cmd = 'rm -rf ' + self.backup_path
        self.dbPrimaryUserNode.sh(cmd)
        logger.info("-----------Opengauss_Gin_Index_0057 end-----------")
