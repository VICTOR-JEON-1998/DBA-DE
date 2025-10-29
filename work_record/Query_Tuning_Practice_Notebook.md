# Query Tuning Practice Notebook

## Purpose
This notebook serves as a practice record for query tuning sessions. Use it to document tuning experiments, compare performance metrics, and track improvements.

## Temporary Table Management

### Drop Temporary Table
```sql
-- Drop temporary table if it exists
DROP TABLE IF EXISTS #SHOP;
```

**Explanation:**
- `DROP TABLE IF EXISTS` safely removes a temporary table only if it exists
- The `#` prefix indicates a local temporary table in SQL Server
- This pattern prevents errors when the table doesn't exist, making scripts more robust
- Useful for cleaning up between tuning iterations or at the start of a fresh testing session
- Alternative syntax: `IF OBJECT_ID('tempdb..#SHOP') IS NOT NULL DROP TABLE #SHOP;`

### Create Temporary Table Template
```sql
-- Create temporary table for testing
CREATE TABLE #SHOP (
    ID INT PRIMARY KEY,
    ShopName VARCHAR(100),
    Category VARCHAR(50),
    CreatedDate DATETIME
);

-- Or using SELECT INTO
SELECT 
    ID,
    ShopName,
    Category,
    CreatedDate
INTO #SHOP
FROM dbo.ShopTable
WHERE Condition = 'Value';
```

## Tuning Session Template

### Session Setup
```sql
-- Clean up any previous temporary objects
DROP TABLE IF EXISTS #SHOP;
DROP TABLE IF EXISTS #Results;

-- Enable performance statistics
SET STATISTICS TIME ON;
SET STATISTICS IO ON;
SET STATISTICS PROFILE ON;
```

### Query Under Test
```sql
-- Your query here
SELECT 
    -- Columns
FROM 
    -- Tables
WHERE 
    -- Conditions
```

### Performance Metrics Recording

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| CPU Time (ms) | | | |
| Elapsed Time (ms) | | | |
| Logical Reads | | | |
| Physical Reads | | | |

### Session Cleanup
```sql
-- Disable statistics
SET STATISTICS TIME OFF;
SET STATISTICS IO OFF;
SET STATISTICS PROFILE OFF;

-- Clean up temporary objects
DROP TABLE IF EXISTS #SHOP;
DROP TABLE IF EXISTS #Results;
```

## Practice Scenarios

### Scenario 1: Index Optimization
**Date:** _____________  
**Objective:** Improve query performance using indexes

**Query:**
```sql
-- Original query
```

**Optimization Applied:**
- [ ] Added index on: `_______________`
- [ ] Modified query structure
- [ ] Updated statistics

**Results:**
- Before: _______ ms
- After: _______ ms
- Improvement: _______%

---

### Scenario 2: Plan Cache Investigation
**Date:** _____________  
**Objective:** Compare fast vs slow query plans

**Query:**
```sql
-- Query with performance issue
```

**Investigation Steps:**
1. [ ] Identified slow query in monitoring
2. [ ] Extracted parameters and SQL
3. [ ] Executed query directly for validation
4. [ ] Compared plan handles
5. [ ] Analyzed ParameterList differences
6. [ ] Cleared problematic plan cache

**Results:**
- Plan Handle (Slow): `_______________`
- Plan Handle (Fast): `_______________`
- Action Taken: `_______________`

---

### Scenario 3: Statistics Update
**Date:** _____________  
**Objective:** Refresh statistics to improve query plans

**Tables Updated:**
```sql
UPDATE STATISTICS dbo.TableName;
```

**Results:**
- Before: _______ ms
- After: _______ ms
- Improvement: _______%

---

## Useful Tuning Commands

### Check Current Query Plans
```sql
-- View cached plans for a specific query
SELECT 
    plan_handle,
    statement_start_offset,
    statement_end_offset,
    execution_count,
    total_elapsed_time,
    total_logical_reads,
    query_plan
FROM sys.dm_exec_query_stats
CROSS APPLY sys.dm_exec_query_plan(plan_handle)
WHERE query_plan.exist('//RelOp') = 1
ORDER BY total_elapsed_time DESC;
```

### Find Missing Indexes
```sql
-- Review index suggestions
SELECT 
    d.database_id,
    d.object_id,
    d.equality_columns,
    d.inequality_columns,
    d.included_columns,
    s.user_seeks,
    s.user_scans,
    s.avg_total_user_cost,
    s.avg_user_impact
FROM sys.dm_db_missing_index_details d
INNER JOIN sys.dm_db_missing_index_groups g
    ON d.index_handle = g.index_handle
INNER JOIN sys.dm_db_missing_index_group_stats s
    ON g.index_group_handle = s.group_handle
ORDER BY s.avg_total_user_cost * s.avg_user_impact * (s.user_seeks + s.user_scans) DESC;
```

### Clear Plan Cache for Testing
```sql
-- Clear entire plan cache (use with caution)
DBCC FREEPROCCACHE;

-- Clear plan cache for specific database
DBCC FREEPROCCACHE(DB_ID('DatabaseName'));

-- Clear plan cache for specific plan handle
DBCC FREEPROCCACHE(plan_handle);
```

## Notes and Observations

### Date: _____________
**Topic:** _____________  
**Key Learnings:**
- 
- 
- 

---

## Best Practices Checklist

- [ ] Always test in non-production first
- [ ] Document baseline metrics before changes
- [ ] Use temporary tables when appropriate
- [ ] Clean up temporary objects after use
- [ ] Disable statistics after tuning sessions
- [ ] Compare multiple iterations
- [ ] Document all changes made
- [ ] Consider production impact before applying changes

