set pagesize 50000
set linesize 1500
set head off
set FEEDBACK off
set ECHO off
set VERIFY off
set TERMOUT off
SET COLSEP ','
SPOOL rating_component_list.csv

SELECT id
FROM rating_component
WHERE id LIKE '%\_%' ESCAPE '\';


SPOOL OFF
exit;