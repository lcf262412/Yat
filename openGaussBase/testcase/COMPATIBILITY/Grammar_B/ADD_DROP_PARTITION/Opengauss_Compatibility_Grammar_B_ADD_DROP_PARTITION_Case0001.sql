-- @testpoint: 验证增删分区原语法和MySQL兼容语法对普通表执行，合理报错
drop table if exists t_b_add_drop_par_0001;
create table t_b_add_drop_par_0001(c1 int,c2 text);
insert into t_b_add_drop_par_0001 values(1,'a'),(2,'b'),(3,'c');
-- 原语法合理报错
alter table t_b_add_drop_par_0001 add partition p1 values less than (1); 
alter table t_b_add_drop_par_0001 add partition p1 values(1);
alter table t_b_add_drop_par_0001 add partition p1 values(1),add partition p2 values(2);
alter table t_b_add_drop_par_0001 drop partition p1,drop partition p2;
-- MySQL语法合理报错
alter table t_b_add_drop_par_0001 add partition (partition p1 values less than (1));
alter table t_b_add_drop_par_0001 add partition (partition p1 values(1));
alter table t_b_add_drop_par_0001 add partition (partition p1 values(1),partition p2 values(2));
alter table t_b_add_drop_par_0001 drop partition p1,p2;
drop table t_b_add_drop_par_0001;
