--  @testpoint:openGauss关键字pad(非保留)，同时作为表名和列名带引号，并进行dml操作,pad列的值最终显示为1000

drop table if exists "pad";
create table "pad"(
	c_id int, c_int int, c_integer integer, c_bool int, c_boolean int, c_bigint integer,
	c_real real, c_double real,
	c_decimal decimal(38), c_number number(38), c_numeric numeric(38),
	c_char char(50) default null, c_varchar varchar(20), c_varchar2 varchar2(4000),
	c_date date, c_datetime date, c_timestamp timestamp,
	"pad" varchar(100) default 'pad'
)
PARTITION BY RANGE (c_integer)
(
	partition P_20180121 values less than (0),
	partition P_20190122 values less than (50000),
	partition P_20200123 values less than (100000),
	partition P_max values less than (maxvalue)
);



insert into "pad"(c_id,"pad") values(1,'hello');
insert into "pad"(c_id,"pad") values(2,'china');
update "pad" set "pad"=1000 where "pad"='hello';
delete from "pad" where "pad"='china';
select "pad" from "pad" where "pad"!='hello' order by "pad";

drop table "pad";

