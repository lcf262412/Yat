-- @testpoint: 函数嵌套
drop table if exists atan_test_01;
create table atan_test_01(f1 int,f2 bigint,f3 integer,f4 binary_integer,f5 bigint,
                          f6 real,f7 float,f8 binary_double,f9 decimal,f10 number,f11 numeric);
insert into atan_test_01(f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11) values(11,22,33,44,55,11.1,22.2,33.3,44.4,55.5,66.6);
insert into atan_test_01(f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11) values(66,77,88,99,00,'11.1','22.2','33.3','44.4','55.5','66.6');
select atan(atan(atan(atan(atan(1234567890))))) from sys_dummy;
select atan(atan(atan(atan(atan(f2))))),atan(f3) from atan_test_01 where atan(atan(atan(f2))) <> 0;

select atan(cos(180 * 3.14159265359/180)) from sys_dummy;
select atan(exp(3)) from sys_dummy;
select avg(atan(0-f1))from atan_test_01;
drop table if exists atan_test_01;