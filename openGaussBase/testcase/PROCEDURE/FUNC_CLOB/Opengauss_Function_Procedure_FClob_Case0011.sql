-- @testpoint: 自定义函数clob数据类型的测试--clob和char/varchar类型的转换

drop table if exists fvt_func_clob_table_011;
create table fvt_func_clob_table_011(
  t1 int,
  t2 clob,
  t3 clob
  );
insert into fvt_func_clob_table_011 values(1,'01010101111100000100000010000000100111111111字符串字符串字符串#￥%……&*（——）（*&……gv个国家级科技控股及港口价格可加工客','ukagcccccccfttttayyygdbbbbuyu7885445112');

--创建自定义函数
create or replace function fvt_func_clob_011(p1 int) return varchar2
is
v1 char(8000);
v2 varchar(8000);
v3 varchar2(8000);
begin
  select t2 into v1 from fvt_func_clob_table_011 where t1=p1;
  select t3 into v2 from fvt_func_clob_table_011 where t1=p1;
  v3:=(rtrim(v1))||v2;
  return v3;
  exception
  when no_data_found
  then
    raise info 'no_data_found';
end;
/
--调用自定义函数
select fvt_func_clob_011(1);

--恢复环境
drop function if exists fvt_func_clob_011;
drop table if exists fvt_func_clob_table_011;
