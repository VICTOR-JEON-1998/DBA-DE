# DBA Daily Work Notes

## Things to Check After Arrival

### SQL Server Error Log Check

Execute the following stored procedures to review error logs:

```sql
-- Check for Korean error keywords
sp_readerrorlog 0,1,오류
sp_readerrorlog 0,1,에러

-- Check for English error keywords
sp_readerrorlog 0,1,error

-- Read error log in descending order
xp_readerrorlog 0,1,null,null,null,null,'desc'
```

**Notes:**
- `sp_readerrorlog` / `xp_readerrorlog`: Read SQL Server error log files
- First parameter: Log file number (0 = current, 1 = previous, etc.)
- Second parameter: Log type (1 = error log)
- Third parameter: Search string filter
- Last parameter for `xp_readerrorlog`: Sort order ('asc' or 'desc')

---

## Extract Actual SQL Statement from Plan Handle

### Stored Procedure: sp_dba_get_sql

**Create the stored procedure:**

```sql
CREATE PROCEDURE sp_dba_get_sql
    @plan_handle VARBINARY(64)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        st.text AS [SQL Text],
        qp.query_plan
    FROM sys.dm_exec_cached_plans AS cp
    CROSS APPLY sys.dm_exec_query_plan(cp.plan_handle) AS qp
    CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) AS st
    WHERE cp.plan_handle = @plan_handle;
END
```

**Usage example:**

```sql
EXEC sp_dba_get_sql @plan_handle = 0x06000A006599B33580B73A106A02000001000000000000000000000000000000000000000000000000000000
```

**Benefits:**
- Simplified syntax - just pass the plan handle as parameter
- Reusable across sessions and databases
- Easy to integrate into scripts or monitoring tools

---

### Direct Query Method (Alternative)

**Query to Get SQL Text Using Plan Handle:**

```sql
SELECT
    st.text AS [SQL Text],
    qp.query_plan
FROM sys.dm_exec_cached_plans AS cp
CROSS APPLY sys.dm_exec_query_plan(cp.plan_handle) AS qp
CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) AS st
WHERE cp.plan_handle = 0x06000A006599B33580B73A106A02000001000000000000000000000000000000000000000000000000000000
```

**Explanation:**
- `sys.dm_exec_cached_plans`: Contains cached execution plans
- `sys.dm_exec_sql_text(plan_handle)`: Extracts the SQL text from a plan handle
- `sys.dm_exec_query_plan(plan_handle)`: Extracts the query execution plan XML
- Replace the `plan_handle` value (hexadecimal) with the actual handle you want to query

**Alternative: Search by SQL text pattern**

```sql
-- Find plan handles containing specific text
SELECT
    cp.plan_handle,
    st.text AS [SQL Text],
    qp.query_plan
FROM sys.dm_exec_cached_plans AS cp
CROSS APPLY sys.dm_exec_query_plan(cp.plan_handle) AS qp
CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) AS st
WHERE st.text LIKE '%YourTableName%'
```

---

## Additional Useful Queries

### Check Current Running Queries

```sql
SELECT
    session_id,
    start_time,
    status,
    command,
    blocking_session_id,
    wait_type,
    wait_time,
    cpu_time,
    total_elapsed_time,
    st.text AS [SQL Text]
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) st
WHERE r.status IN ('running', 'runnable', 'suspended')
ORDER BY r.total_elapsed_time DESC
```

### Find Most Resource-Intensive Queries

```sql
SELECT TOP 10
    st.text AS [SQL Text],
    qs.execution_count,
    qs.total_elapsed_time / 1000 AS [Total Elapsed Time (ms)],
    qs.total_physical_reads,
    qs.total_logical_reads,
    qs.total_logical_writes,
    qs.creation_time,
    qs.last_execution_time
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY qs.total_elapsed_time DESC
```

---

## Viewing Execution Plans for Query Tuning

Execution plans are essential for understanding how SQL Server executes queries and identifying performance bottlenecks.

### Method 1: SSMS Graphical Execution Plans (Recommended)

**Display Estimated Execution Plan:**
- **Shortcut:** `Ctrl + L`
- **Menu:** Query → Display Estimated Execution Plan
- Shows the plan **without executing** the query
- Useful for quick analysis before running expensive queries
- Based on statistics, not actual execution

**Include Actual Execution Plan:**
- **Shortcut:** `Ctrl + M`
- **Menu:** Query → Include Actual Execution Plan
- Shows the plan **after executing** the query
- Provides actual row counts and runtime statistics
- More accurate but requires query execution

**Usage:**
```sql
-- Enable actual execution plan (Ctrl+M)
-- Then run your query
SELECT * FROM dbo.YourTable WHERE Column = 'Value';

-- The execution plan will appear in a separate tab
```

**Key Information in Graphical Plans:**
- **Cost percentage:** Relative cost of each operation
- **Operator types:** Table Scan, Index Seek, Sort, etc.
- **Actual vs Estimated rows:** Shows if statistics are outdated
- **Warnings:** Missing indexes, implicit conversions, etc.
- **Properties:** Tooltip shows detailed information (logical reads, CPU time, etc.)

---

### Method 2: SET STATISTICS XML

**Enable XML Execution Plan:**
```sql
-- Enable XML execution plan
SET STATISTICS XML ON;

-- Run your query
SELECT * FROM dbo.YourTable WHERE Column = 'Value';

-- Disable after testing
SET STATISTICS XML OFF;
```

**Benefits:**
- Returns actual execution plan as XML
- Can be saved to `.sqlplan` file and opened in SSMS
- More detailed than graphical plans
- Can be shared with others
- Production-friendly (can be enabled per session)

**Save Plan to File:**
```sql
SET STATISTICS XML ON;
SELECT * FROM dbo.YourTable WHERE Column = 'Value';
-- Copy the XML result and save as .sqlplan file
-- Open in SSMS to view graphically
SET STATISTICS XML OFF;
```

---

### Method 3: SET SHOWPLAN (Text/All)

**Showplan Text (Simple text format):**
```sql
SET SHOWPLAN_TEXT ON;
GO

-- Your query here (won't execute, only shows plan)
SELECT * FROM dbo.YourTable WHERE Column = 'Value';
GO

SET SHOWPLAN_TEXT OFF;
GO
```

**Showplan All (Detailed text format with statistics):**
```sql
SET SHOWPLAN_ALL ON;
GO

-- Your query here (won't execute, only shows plan)
SELECT * FROM dbo.YourTable WHERE Column = 'Value';
GO

SET SHOWPLAN_ALL OFF;
GO
```

**Notes:**
- Queries are **not executed** - only the plan is shown
- Useful for understanding plan structure without running queries
- Text format is less visual but can be easier to parse programmatically

---

### Method 4: Query Cached Plans Using DMVs

**Get execution plan from plan cache:**
```sql
-- Find execution plan by SQL text
SELECT 
    cp.plan_handle,
    st.text AS [SQL Text],
    qp.query_plan,
    qs.execution_count,
    qs.total_elapsed_time / 1000 AS [Total Elapsed Time (ms)],
    qs.total_logical_reads,
    qs.total_physical_reads
FROM sys.dm_exec_cached_plans AS cp
CROSS APPLY sys.dm_exec_query_plan(cp.plan_handle) AS qp
CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) AS st
LEFT JOIN sys.dm_exec_query_stats AS qs
    ON cp.plan_handle = qs.plan_handle
WHERE st.text LIKE '%YourTableName%'
ORDER BY qs.total_elapsed_time DESC;
```

**Get plan for specific plan handle:**
```sql
-- Using the stored procedure
EXEC sp_dba_get_sql @plan_handle = 0x06000A006599B33580B73A106A02000001000000000000000000000000000000000000000000000000000000;
```

---

### Method 5: Query Store (SQL Server 2016+)

**Query Store provides historical execution plans:**
```sql
-- View query plans in Query Store
SELECT 
    qsq.query_id,
    qsq.query_sql_text,
    qsp.plan_id,
    qsp.query_plan,
    qrs.avg_duration / 1000 AS [Avg Duration (ms)],
    qrs.avg_logical_io_reads,
    qrs.execution_count
FROM sys.query_store_query qsq
INNER JOIN sys.query_store_plan qsp
    ON qsq.query_id = qsp.query_id
INNER JOIN sys.query_store_runtime_stats qrs
    ON qsp.plan_id = qrs.plan_id
WHERE qsq.query_sql_text LIKE '%YourTableName%'
ORDER BY qrs.avg_duration DESC;
```

**Benefits:**
- Historical execution plans
- Plan regression analysis
- Compare multiple plan versions
- No need to capture plans in real-time

---

### Comparing Execution Plans

**To compare plans side by side:**
1. Save both plans as `.sqlplan` files
2. Open both in SSMS
3. Compare:
   - Operator types (Seek vs Scan)
   - Estimated vs Actual rows
   - Cost percentages
   - Missing index warnings
   - Parameter sniffing issues

**Common Plan Issues to Look For:**
- **Table Scan:** Missing index or wrong index
- **Key Lookup:** Missing covering index
- **Large Estimated vs Actual rows:** Outdated statistics
- **Sort operations:** Missing ORDER BY in index
- **Implicit conversions:** Data type mismatches
- **Parameter sniffing:** Different plans for same query

---

### Best Practices

1. **For Development/Tuning:**
   - Use `Ctrl + M` (Actual Execution Plan) for accurate analysis
   - Enable `SET STATISTICS IO ON` and `SET STATISTICS TIME ON` together
   - Compare before/after plans

2. **For Production Analysis:**
   - Use `SET STATISTICS XML ON` to capture plans without affecting UI
   - Query Query Store for historical analysis
   - Use DMVs to find problematic plans

3. **Before Making Changes:**
   - Always save the original plan as `.sqlplan` file
   - Document baseline metrics
   - Compare multiple plan versions

4. **After Making Changes:**
   - Capture new plan
   - Compare with original
   - Verify improvements with actual metrics

---

## Viewing Stored Procedure Definition

### Stored Procedure: SP_DBA_HELPtest

**Usage:**
```sql
SP_DBA_HELPtest master, (procedure name)
```

**Description:**
- Execute this stored procedure to view the actual SQL query definition of a stored procedure
- First parameter: Database name (e.g., `master`)
- Second parameter: Stored procedure name
- Returns the actual query text of the stored procedure

**Example:**
```sql
SP_DBA_HELPtest master, sp_helpdb
```

**Benefits:**
- Quick way to view stored procedure source code
- Useful for understanding procedure logic and troubleshooting
- Can be used to document or analyze existing procedures

---

## Statistics Investigation Task

### Task: Investigating Columns Without Statistics Information

**Objective:**
- Identify and analyze columns that lack statistics information
- This investigation will help improve query optimization and performance

**Status:** In Progress
- Detailed findings and methodology will be documented as the investigation progresses

---

### Stored Procedure: sp_dba_make_stats_for_null

**Purpose:**
- Identifies columns that do not have statistics information
- Generates DROP and CREATE STATISTICS statements for columns missing statistics
- Helps identify columns that need statistics for better query optimization

**Usage:**
```sql
EXEC sp_dba_make_stats_for_null 
    @I_DB_NAME = 'database_name',
    @I_TABLE_NAME = 'table_name'
```

**Parameters:**
- `@I_DB_NAME`: Database name to investigate
- `@I_TABLE_NAME`: Table name to check for missing statistics

**Procedure Definition:**
```sql
CREATE PROCEDURE [dbo].[sp_dba_make_stats_for_null]
( @I_DB_NAME VARCHAR(100)
, @I_TABLE_NAME VARCHAR(100))
AS
BEGIN
	DECLARE @V_SQL	VARCHAR(MAX);
	SET @V_SQL='USE '+@I_DB_NAME+';SELECT OBJECT_NAME(A.OBJECT_ID) AS TABLE_NAME
		, A.NAME COLUMN_NAME
		, B.STATS_ID
		, C.NAME AS STATS_NAME
		, ''DROP STATISTICS ''+OBJECT_NAME(A.OBJECT_ID)+''.''+C.NAME AS DROP_STMT
		, ''CREATE STATISTICS ''+A.NAME+'' ON ''+OBJECT_NAME(A.OBJECT_ID)+''(''+A.NAME+'')'' AS CREATE_STMT
		FROM SYS.ALL_COLUMNS A
		LEFT JOIN SYS.STATS_COLUMNS B
		ON A.OBJECT_ID = B.OBJECT_ID
		AND A.COLUMN_ID = B.COLUMN_ID
		LEFT JOIN SYS.STATS C
		ON B.OBJECT_ID = C.OBJECT_ID
		AND B.STATS_ID = C.STATS_ID
		WHERE 1=1
		AND B.stats_id IS NULL';

	SET @V_SQL = @V_SQL+' AND A.OBJECT_ID=OBJECT_ID('''+@I_TABLE_NAME+''')';
	EXEC (@V_SQL);
END
```

**How it works:**
- Joins `SYS.ALL_COLUMNS` with `SYS.STATS_COLUMNS` and `SYS.STATS` to find columns without statistics
- Filters for columns where `stats_id IS NULL` (no statistics exist)
- Returns:
  - `TABLE_NAME`: Name of the table
  - `COLUMN_NAME`: Name of the column without statistics
  - `STATS_ID`: NULL (indicating no statistics)
  - `STATS_NAME`: NULL (no statistics name)
  - `DROP_STMT`: DROP statement (if statistics exist)
  - `CREATE_STMT`: CREATE STATISTICS statement for the column

**Viewing the procedure definition:**
```sql
SP_DBA_HELPtest master, SP_DBA_MAKE_STATS_for_null
```

---

### Analysis of sp_dba_make_stats_for_null

**Procedure Overview:**
This stored procedure analyzes statistics information by joining system catalog views from the `sys` schema. It maps table, column, and statistics information to identify columns that lack statistics.

**Key Components:**

1. **System Catalog Views Used:**
   - `SYS.ALL_COLUMNS` (alias A): Contains all column information for user-defined and system objects
   - `SYS.STATS_COLUMNS` (alias B): Maps statistics to columns (contains `stats_id` and `column_id`)
   - `SYS.STATS` (alias C): Contains statistics metadata (statistics name, creation type, etc.)

2. **Join Logic:**
   ```sql
   FROM SYS.ALL_COLUMNS A
   LEFT JOIN SYS.STATS_COLUMNS B
       ON A.OBJECT_ID = B.OBJECT_ID
       AND A.COLUMN_ID = B.COLUMN_ID
   LEFT JOIN SYS.STATS C
       ON B.OBJECT_ID = C.OBJECT_ID
       AND B.STATS_ID = C.STATS_ID
   ```
   - **First LEFT JOIN**: Links columns to their statistics mapping
   - **Second LEFT JOIN**: Retrieves statistics metadata (name, type, etc.)
   - Uses `object_id` and `column_id` as join keys to match columns with statistics

3. **Filtering Logic:**
   - `WHERE B.stats_id IS NULL`: Identifies columns that have NO statistics
   - This is the core purpose - finding columns without statistics information

4. **Output Columns:**
   - `TABLE_NAME`: Table name (using `OBJECT_NAME(A.OBJECT_ID)`)
   - `COLUMN_NAME`: Column name (from `A.NAME`)
   - `STATS_ID`: NULL (indicating no statistics exist)
   - `STATS_NAME`: NULL (no statistics name available)
   - `DROP_STMT`: DROP statement (will be NULL since no statistics exist)
   - `CREATE_STMT`: Generated CREATE STATISTICS statement for the column

5. **Dynamic SQL Construction:**
   - Uses `USE @I_DB_NAME` to switch database context
   - Dynamically filters by table name using `OBJECT_ID(@I_TABLE_NAME)`
   - Allows execution across different databases

**Usage Example:**
```sql
EXEC sp_dba_make_stats_for_null 'ERP', 'ZZ_WM_IN_D'
```

**Analysis Summary:**
This procedure demonstrates how to query SQL Server system catalog views (`sys.all_columns`, `sys.stats_columns`, `sys.stats`) to map table, column, and statistics information. The LEFT JOIN approach ensures all columns are included in the result, even if they don't have statistics, which is essential for identifying missing statistics.

**Key Learning Points:**
- System catalog views in the `sys` schema can be joined to create comprehensive metadata queries
- LEFT JOINs are used to include columns without statistics (NULL values indicate missing statistics)
- The `object_id` and `column_id` combination uniquely identifies a column within a table
- Dynamic SQL allows the procedure to work across different databases

---

## Date Format

Last Updated: 2025-10-30

---

## Post‑Tuning Validation (Result Consistency Check)

After query tuning, always compare the original and tuned results.

Workflow:
- Run the pre‑tuning query and persist results to an origin table, e.g., `ZZ_<subject>_origin`.
- Run the post‑tuning query and persist results to a tuned table, e.g., `ZZ_<subject>_tune`.
- Validate equality by alternating EXCEPT checks in both directions. Both must return zero rows.

Example (SQL Server):
```sql
-- 1) Materialize results
SELECT /* pre-tuning */ *
INTO ZZ_sales_origin
FROM (
    -- original query here
) o;

SELECT /* post-tuning */ *
INTO ZZ_sales_tune
FROM (
    -- tuned query here
) t;

-- 2) Compare both directions (set equality)
-- origin - tuned should be empty
SELECT *
FROM ZZ_sales_origin
EXCEPT
SELECT *
FROM ZZ_sales_tune;

-- tuned - origin should be empty
SELECT *
FROM ZZ_sales_tune
EXCEPT
SELECT *
FROM ZZ_sales_origin;
```

Notes:
- Use the same projected columns and data types/order for fair comparison.
- If duplicates matter, compare with grouping keys and counts; otherwise set-based EXCEPT is sufficient.
- Consider normalizing time/precision or collation differences before comparison.

