-- @testpoint: openGauss保留关键字verbose作为列名带引号并且排序时使用该列,建表成功，verbose列按字母大小排序
drop table if exists test_tbl;
create table test_tbl(
	c_id int, c_int int, c_integer integer, c_bool int, c_boolean int, c_bigint integer, 
	c_real real, c_double real, 
	c_decimal decimal(38), c_number number(38), c_numeric numeric(38), 
	c_char char(50) default null, c_varchar varchar(20), c_varchar2 varchar2(4000),
	c_date date, c_datetime date, c_timestamp timestamp,
	"verbose" varchar(100) default 'verbose'
) 
PARTITION BY RANGE (c_integer)
(
	partition P_20180121 values less than (0),
	partition P_20190122 values less than (50000),
	partition P_20200123 values less than (100000),
	partition P_max values less than (maxvalue)
);

--插入数据
insert into test_tbl(c_id,"verbose") values(1,'hello');
insert into test_tbl(c_id) values(2);

--查看表数据
select c_id,"verbose" from test_tbl order by "verbose";

--清理环境
drop table test_tbl;