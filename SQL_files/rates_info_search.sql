set pagesize 50000
set linesize 1500
set head off
set FEEDBACK off
set ECHO off
set VERIFY off
set TERMOUT off
SET COLSEP ','
SPOOL rates_info_search.csv

SELECT
    fs.franchise,
    fs.billing_operator,    
    fs.rating_component,
    fs.component_direction,
    fs.billed_product,
    fs.tier,
    bp.name,
    bp.FED,
    bp.LED,
    fs.time_premium,
    to_number(fs.unit_cost_used),
    round(sum(amount)),
    sum(start_call_count)
FROM
    financial_summary fs
    INNER JOIN billing_period    bp
    on fs.billing_period=bp.id
WHERE
    bp.fk_orga_fran = '&1'
    AND bp.fk_orga_oper = '&2'
    AND bp.name = '&3'
    AND bp.fk_pgrp = 'ITX'
    AND bp.fk_sdir = 'S'
    AND fs.rating_component = '&4'
    AND fs.component_direction='&5'
    AND fs.tier<>'CERO'
group by fs.billing_operator,
    fs.franchise,
    fs.rating_component,
    fs.component_direction,
    fs.billed_product,
    fs.tier,
    bp.name,
    bp.FED,
    bp.LED,
    fs.time_premium,
    to_number(fs.unit_cost_used)
;

SPOOL OFF
exit;