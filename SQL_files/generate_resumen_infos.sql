set pagesize 50000
set linesize 1500
set head off
set FEEDBACK off
set ECHO off
set VERIFY off
set TERMOUT off
SET COLSEP ','
SPOOL generate_resumen_infos.csv

SELECT
    fs.franchise,
    fs.billing_operator,    
    fs.rating_component,
    bp.name,
    fs.time_premium,
    tch.GET_RATE_FROM_TO( 'RATE_FED', '&1' , '&2','&3', '&4','&5', '&6', '&7', '&8', '&9', '&10') as FED,
    tch.GET_RATE_FROM_TO( 'RATE_LED', '&1' , '&2','&3', '&4','&5', '&6', '&7', '&8', '&9', '&10') as LED,
    fs.unit_cost_used,
    SUM(fs.amount),
    SUM(fs.start_call_count)
FROM
    financial_summary fs
    INNER JOIN billing_period    bp
    on fs.billing_period=bp.id
WHERE
        fs.rating_component = '&5'
        and fs.component_direction='&7'
        and fs.unit_cost_used='&10'
    AND 
    bp.name = to_char(to_date('&1','DD-MON-RR'),'YYYYMM')
    AND bp.fk_orga_fran = '&3'
    AND bp.fk_orga_oper = '&4'
    AND bp.fk_pgrp = 'ITX'
    AND bp.fk_sdir = 'S'
GROUP BY
    fs.billing_operator,
    fs.franchise,
    fs.rating_component,
    bp.name,
    fs.time_premium,
    tch.GET_RATE_FROM_TO( 'RATE_FED', '&1' , '&2','&3', '&4','&5', '&6', '&7', '&8', '&9', '&10'),
    tch.GET_RATE_FROM_TO( 'RATE_LED', '&1' , '&2','&3', '&4','&5', '&6', '&7', '&8', '&9', '&10'),
    fs.unit_cost_used;

SPOOL OFF
exit;