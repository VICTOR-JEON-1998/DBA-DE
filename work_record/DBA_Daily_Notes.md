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

