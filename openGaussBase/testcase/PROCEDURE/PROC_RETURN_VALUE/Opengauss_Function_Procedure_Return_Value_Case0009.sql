-- @testpoint: 测试存储过程返回值类型——int，且传入类型为real的情况 合理报错

--创建存储过程
create or replace procedure proc_return_value_009(p1 in number)  as
v_num int;
begin
    v_num:=p1;
    raise info 'v_num=:%',v_num;
    exception
    when no_data_found
    then raise info 'no_data_found';
end;
/
--调用存储过程
declare
    v1 number:=2147483647.00;
begin
    proc_return_value_009(v1);
end;
/
--调用存储过程
declare
    v2 number:=2147483647.001;
begin
    proc_return_value_009(v2);
end;
/
--调用存储过程
declare
    v3 number:=2147483646.5;
begin
    proc_return_value_009(v3);
end;
/
--调用存储过程
declare
    v4 number:=-2147483648.001;
begin
    proc_return_value_009(v4);
end;
/
--调用存储过程
declare
    v5 number:=-2147483648.581;
begin
    proc_return_value_009(v5);
end;
/
--清理环境
drop procedure proc_return_value_009;