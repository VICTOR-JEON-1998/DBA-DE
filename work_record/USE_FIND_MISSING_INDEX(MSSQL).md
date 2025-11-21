Finding and Creating Missing Indexes
``` sql
select *
FROM (
SELECT DB_NAME(MID.database_id) AS DB_NAME
     , MIGS.group_handle  
   , MIGS.unique_compiles  
   , OBJECT_NAME(MID.OBJECT_ID) AS TABLE_NAME
   , ROUND(CONVERT (decimal (28, 1), migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans) ),0) AS ESTIMATED_IMPROVEMENT, ROUND(MIGS.avg_total_user_cost * MIGS.avg_user_impact * (MIGS.user_seeks + MIGS.user_scans),0) AS TOTAL_COST
   , MID.equality_columns  
   , MID.inequality_columns  
   , MID.included_columns  
   , MIGS.user_seeks  
   --, MISQ.USER_SEEKS AS MISQ_USER_SEEKS
   , MIGS.user_scans  
   --, MISQ.USER_SCANS AS MISQ_USER_SCANS
   , MIGS.last_user_seek  
   --, MISQ.last_user_seek AS MISQL_last_user_seek   
   , MIGS.last_user_scan  
   --, MISQ.last_user_scan AS MISQL_last_user_scan
   , MIGS.avg_user_impact  
   --0, MISQ.avg_user_impact  MISQ_avg_user_impact  
   , MIGS.avg_total_user_cost
   --, MISQ.avg_total_user_cost AS MISQ_avg_total_user_cost
   --, CASE WHEN MIGS.avg_total_user_cost  = MISQ.avg_total_user_cost  THEN '' ELSE 'DIFF' END AS COMP_MIGS_MISQ
   , MIGS.system_seeks  
   , MIGS.system_scans  
   , MIGS.last_system_seek  
   , MIGS.last_system_scan  
   , MIGS.avg_total_system_cost  
   , MIGS.avg_system_impact  
   , MID.statement  
   , MIC.column_id  
   , MIC.column_name  
   , MIC.column_usage  
   ,'==============================' AS SEP1
   ,    SUBSTRING
    (
            sql_text.text,
            misq.last_statement_start_offset / 2 + 1,
            (
            CASE misq.last_statement_start_offset
                WHEN -1 THEN DATALENGTH(sql_text.text)
                ELSE misq.last_statement_end_offset
            END - misq.last_statement_start_offset
            ) / 2 + 1
    ) AS SQL_TEXT
  ,'==============================' AS SEP2
  --, MISQ.*
  --,'==============================' AS SEP3
   ,'CREATE INDEX [IX_' + OBJECT_NAME(MID.OBJECT_ID,MID.database_id) + '_'
     + REPLACE(REPLACE(REPLACE(ISNULL(MID.equality_columns,''),', ','_'),'[',''),']','') 
     + CASE WHEN MID.equality_columns IS NOT NULL AND MID.inequality_columns IS NOT NULL THEN '_'
       ELSE '' END
       + REPLACE(REPLACE(REPLACE(ISNULL(MID.inequality_columns,''),', ','_'),'[',''),']','')
     + ']'
     + ' ON ' + MID.statement
     + ' (' + ISNULL (MID.equality_columns,'')
     + CASE WHEN MID.equality_columns IS NOT NULL AND MID.inequality_columns IS NOT NULL THEN ',' ELSE '' END
     + ISNULL (MID.inequality_columns, '')
     + ')'
     + ISNULL (' INCLUDE (' + MID.included_columns + ')', '') AS CREATE_STATEMENT
  FROM sys.dm_db_missing_index_group_stats MIGS WITH(NOLOCK)
  JOIN sys.dm_db_missing_index_groups MIG WITH(NOLOCK)
    ON MIGS.GROUP_HANDLE = MIG.INDEX_GROUP_HANDLE
  LEFT OUTER JOIN sys.dm_db_missing_index_group_stats_query AS MISQ
    ON MIGS.GROUP_HANDLE = MISQ.GROUP_HANDLE
  JOIN sys.dm_db_missing_index_details MID WITH(NOLOCK) 
    ON MIG.INDEX_HANDLE = MID.INDEX_HANDLE
CROSS APPLY SYS.DM_DB_MISSING_INDEX_COLUMNS(MID.INDEX_HANDLE) MIC
CROSS APPLY sys.dm_exec_sql_text(MISQ.last_sql_handle) AS sql_text
) A
WHERE 1=1
AND DB_NAME = 'ERP'

```

You can improve database performance using the query above.



Execution Strategy:

Prioritize: Focus on indexes that are executed frequently (USER_SEEKS) and have a high improvement score (ESTIMATED_IMPROVEMENT).

Caution: Creating indexes can take a long time. Please monitor the system while executing these scripts to ensure you do not cause blocking locks that affect other operations.

Evaluation Criteria: Make your judgments based on ESTIMATED_IMPROVEMENT and USER_SEEKS.

⚠️ Important: Before Creating Indexes
Although the query provides a CREATE INDEX statement, do not execute it immediately. You must consider the following three factors:

1. Identify Index Intersections (Consolidation)
If multiple missing indexes are suggested for the same table, do not blindly create all of them.

Logic: Look for a superset. If the columns in one suggested index cover the columns of another (e.g., the "top" suggestion includes the "bottom" suggestion in your example), you only need to create the larger, inclusive index.

Action: Create the index that acts as the superset (the one containing the intersection of columns) rather than creating two separate, overlapping indexes.

2. Adhere to Naming Conventions
Action: Do not rely solely on the auto-generated name. Rename the index to match the existing Index Naming Rules of your database.

3. Specify the Filegroup
Action: Ensure the index is stored in the specific filegroup: FG_ER_IDX.

Note: You will need to append ON [FG_ER_IDX] to the end of your CREATE statement.
