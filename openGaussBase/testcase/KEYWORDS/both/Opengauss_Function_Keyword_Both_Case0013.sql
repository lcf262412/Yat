--  @testpoint:openGauss保留关键字Both同时作为表名和列名带引号，与union结合查询合并两个SELECT 语句查询
drop table if exists "Both";
create table "Both"(
	c_id int, c_int int, c_integer integer, c_bool int, c_boolean int, c_bigint integer,
	c_real real, c_double real,
	c_decimal decimal(38), c_number number(38), c_numeric numeric(38),
	c_char char(50) default null, c_varchar varchar(20), c_varchar2 varchar2(4000),
	c_date date, c_datetime date, c_timestamp timestamp,
	"Both" varchar(100) default 'Both'
)
PARTITION BY RANGE (c_integer)
(
	partition P_20180121 values less than (0),
	partition P_20190122 values less than (50000),
	partition P_20200123 values less than (100000),
	partition P_max values less than (maxvalue)
);

--插入数据
insert into "Both"(c_id,"Both") values(1,'hello');
insert into "Both"(c_id,"Both") values(2,'china');
insert into "Both"(c_id,"Both") values(3,'gauss');

---两个select语句合并查询，查询结果显示hello、china、gauss，对括号中的select子句取limit 2
select "Both" from "Both" where "Both"='hello'
union all (select "Both" from "Both" where "Both"!='hello' order by "Both" limit 2);

--清理环境
drop table "Both";