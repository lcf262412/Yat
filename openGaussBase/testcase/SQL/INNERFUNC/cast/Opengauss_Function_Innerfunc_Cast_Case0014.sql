-- @testpoint:验证cast函数是否支持索引
DROP TABLE IF EXISTS TEST1;
DROP INDEX IF EXISTS TEST1_INDEX;
CREATE TABLE TEST1(RIQI INT);
CREATE INDEX TEST1_INDEX ON TEST1(RIQI);
SELECT * FROM TEST1 WHERE RIQI<CAST('2018-08-30' AS DATE);
DROP INDEX IF EXISTS TEST1_INDEX;
DROP TABLE IF EXISTS TEST1;