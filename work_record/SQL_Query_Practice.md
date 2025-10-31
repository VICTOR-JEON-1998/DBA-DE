# SQL Query Practice Notes

## Quiz: Find Queries with Multiple Execution Plans

### Problem Statement

Find queries from the `MONITOR.dbo.DBA_SESSIONS_DETAIL` table where a single combination of `SQL_HANDLE` and `STATEMENT_SQL_HANDLE` has **3 or more distinct execution plans** (`PLAN_HANDLE`) within the last 7 days.

**Requirements:**
- Time range: Last 7 days (from collection date)
- Group by: `SQL_HANDLE` and `STATEMENT_SQL_HANDLE` pair
- Condition: Must have 3 or more distinct `PLAN_HANDLE` values

---

## Learning Process and Attempts

### Attempt 1: Initial Exploration

```sql
-- Understanding the table structure
SELECT TOP 100 * FROM MONITOR.dbo.DBA_SESSIONS_DETAIL
```

**Purpose:** Get familiar with the table structure and available columns.

---

### Attempt 2: Grouping with COUNT - Wrong Approach

```sql
WITH A AS (
    SELECT 
        SQL_HANDLE,
        COUNT(SQL_HANDLE) AS CNT_SQL_HANDLE, 
        STATEMENT_SQL_HANDLE, 
        COUNT(STATEMENT_SQL_HANDLE) AS CNT_STATEMENT_SQL_HANDLE, 
        PLAN_HANDLE
    FROM MONITOR.dbo.DBA_SESSIONS_DETAIL
    GROUP BY (SQL_HANDLE), (STATEMENT_SQL_HANDLE), PLAN_HANDLE
)
SELECT COUNT(DISTINCT(*)) FROM A
```

**Issue:**
- Grouping by `PLAN_HANDLE` as well defeats the purpose - we want to count distinct plans per SQL/STATEMENT pair
- Syntax error: `COUNT(DISTINCT(*))` is invalid

**Learning Point:** We need to group by `SQL_HANDLE` and `STATEMENT_SQL_HANDLE` only, then count distinct `PLAN_HANDLE` values within each group.

---

### Attempt 3: Simple COUNT Check

```sql
SELECT COUNT(*)
FROM MONITOR.dbo.DBA_SESSIONS_DETAIL
WHERE SQL_HANDLE = 0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
```

**Purpose:** Verify data exists and test specific handle value.

---

### Attempt 4: Basic Grouping Without Distinct Count

```sql
SELECT 
    SQL_HANDLE,
    COUNT(SQL_HANDLE) AS CNT_SQL_HANDLE
FROM MONITOR.dbo.DBA_SESSIONS_DETAIL
GROUP BY (SQL_HANDLE)
```

**Issue:** This only counts total rows per `SQL_HANDLE`, not distinct `PLAN_HANDLE` values.

---

### Attempt 5: Grouping with Plan Handle (Incorrect Logic)

```sql
SELECT 
    SQL_HANDLE, 
    STATEMENT_SQL_HANDLE, 
    PLAN_HANDLE, 
    COUNT(PLAN_HANDLE) AS CNT_PLAN_HANDLE
FROM MONITOR.dbo.DBA_SESSIONS_DETAIL
GROUP BY (SQL_HANDLE), (STATEMENT_SQL_HANDLE), (PLAN_HANDLE)
```

**Issue:** Grouping by `PLAN_HANDLE` creates a row for each unique plan, so `COUNT(PLAN_HANDLE)` will always be 1. We need to count **distinct** plans per SQL/STATEMENT pair.

**Learning Point:** Use `COUNT(DISTINCT PLAN_HANDLE)` when grouping by `SQL_HANDLE` and `STATEMENT_SQL_HANDLE` only.

---

### Attempt 6: Complex Join Approach

```sql
SELECT 
    B.*,
    A.CNT_PLAN_HANDLE
FROM (
    SELECT 
        SQL_HANDLE, 
        STATEMENT_SQL_HANDLE, 
        PLAN_HANDLE, 
        COUNT(PLAN_HANDLE) AS CNT_PLAN_HANDLE
    FROM MONITOR.dbo.DBA_SESSIONS_DETAIL
    GROUP BY (SQL_HANDLE), (STATEMENT_SQL_HANDLE), (PLAN_HANDLE)
) A
JOIN MONITOR.dbo.DBA_SESSIONS_DETAIL B 
    ON A.PLAN_HANDLE = B.PLAN_HANDLE
WHERE B.COLLECTION_DATE > '20251025 00:00:00'
  AND A.CNT_PLAN_HANDLE >= 3
```

**Issue:** Same fundamental problem - grouping by `PLAN_HANDLE` means we're counting rows, not distinct plans.

---

### Attempt 7: Pair Grouping with CTE (Getting Closer)

```sql
-- SQL_HANDLE, STATEMENT_SQL_HANDLE pair grouping
WITH T AS (
    SELECT 
        SQL_HANDLE, 
        STATEMENT_SQL_HANDLE 
    FROM MONITOR.dbo.DBA_SESSIONS_DETAIL
    GROUP BY (SQL_HANDLE), (STATEMENT_SQL_HANDLE)
)
SELECT A.* 
FROM MONITOR.dbo.DBA_SESSIONS_DETAIL A
JOIN T ON (
    A.SQL_HANDLE = T.SQL_HANDLE 
    AND A.STATEMENT_SQL_HANDLE = T.STATEMENT_SQL_HANDLE
)
WHERE A.COLLECTION_DATE > '20251025 00:00:00'
-- For this pair, count how many PLAN_HANDLE values exist
```

**Progress:** Correctly identified the need to group by the pair, but didn't complete the distinct count logic.

---

### Attempt 8: Still Grouping by PLAN_HANDLE

```sql
SELECT 
    SQL_HANDLE, 
    STATEMENT_SQL_HANDLE, 
    COUNT(SQL_HANDLE) AS CNT
FROM MONITOR.dbo.DBA_SESSIONS_DETAIL
GROUP BY (SQL_HANDLE), (STATEMENT_SQL_HANDLE), PLAN_HANDLE
ORDER BY CNT DESC
```

**Issue:** Still including `PLAN_HANDLE` in GROUP BY, which creates separate groups for each plan instead of counting distinct plans.

---

### Practice: Understanding GROUP BY with Test Data

```sql
DROP TABLE IF EXISTS TEST;

CREATE TABLE TEST(COLA VARCHAR(100), COLB VARCHAR(100), COLC VARCHAR(100));

INSERT INTO TEST VALUES('A','1','AA');
INSERT INTO TEST VALUES('A','1','AB');
INSERT INTO TEST VALUES('A','1','AC');
INSERT INTO TEST VALUES('A','1','AD');
INSERT INTO TEST VALUES('A','2','AA');
INSERT INTO TEST VALUES('A','2','AA');
INSERT INTO TEST VALUES('A','2','AB');

SELECT * FROM TEST;
```

**Test Query:**
```sql
SELECT COLA, COLB, COUNT(DISTINCT COLC) AS CNT_DISTINCT
FROM TEST
GROUP BY COLA, COLB;
```

**Result:**
- (A, 1): 4 distinct COLC values (AA, AB, AC, AD)
- (A, 2): 2 distinct COLC values (AA, AB) - note AA appears twice but counted once

**Key Learning:**
> **GROUP BY fixes the conditions you want, then you can aggregate/count within those groups.**

When you `GROUP BY COLA, COLB`, you create groups for each unique (COLA, COLB) combination. Then `COUNT(DISTINCT COLC)` counts how many distinct COLC values exist within each group.

---

## Final Solution

### Correct Answer

```sql
WITH T AS (
    SELECT 
        SQL_HANDLE, 
        STATEMENT_SQL_HANDLE, 
        COUNT(DISTINCT PLAN_HANDLE) AS CNT
    FROM MONITOR.DBO.DBA_SESSIONS_DETAIL
    WHERE COLLECTION_DATE > DATEADD(DAY, -7, GETDATE())  -- Last 7 days
    GROUP BY SQL_HANDLE, STATEMENT_SQL_HANDLE
    HAVING COUNT(DISTINCT PLAN_HANDLE) >= 3  -- 3 or more distinct plans
)
SELECT 
    A.*, 
    T.CNT 
FROM MONITOR.DBO.DBA_SESSIONS_DETAIL A
JOIN T ON (
    T.SQL_HANDLE = A.SQL_HANDLE 
    AND T.STATEMENT_SQL_HANDLE = A.STATEMENT_SQL_HANDLE
)
WHERE A.COLLECTION_DATE > DATEADD(DAY, -7, GETDATE())
ORDER BY T.CNT DESC, A.COLLECTION_DATE DESC;
```

### Explanation

1. **CTE (Common Table Expression) `T`:**
   - Groups rows by `SQL_HANDLE` and `STATEMENT_SQL_HANDLE` pair
   - Counts **distinct** `PLAN_HANDLE` values within each group using `COUNT(DISTINCT PLAN_HANDLE)`
   - Filters to only pairs with 3 or more distinct plans using `HAVING`

2. **Main Query:**
   - Joins back to the original table to get all detail rows
   - Filters by date range again for the detail rows
   - Includes the count in the result for reference

### Key Concepts Learned

1. **GROUP BY Logic:**
   - Groups rows by specified columns
   - Aggregate functions (COUNT, SUM, etc.) operate within each group
   - Columns in GROUP BY determine the grouping level

2. **COUNT(DISTINCT column):**
   - Counts unique values within a group
   - Essential when you want to know "how many different X values exist" per group

3. **HAVING vs WHERE:**
   - `WHERE`: Filters rows before grouping
   - `HAVING`: Filters groups after aggregation (must use with GROUP BY)

4. **CTE Pattern:**
   - Identify qualifying groups in CTE
   - Join back to original table to get full detail rows

### Improvements to Original Solution

- Used `DATEADD(DAY, -7, GETDATE())` instead of hardcoded date for last 7 days
- Added `ORDER BY` for better result organization
- Added date filter in main query for consistency

---

## Takeaways

### Common Mistakes to Avoid

1. ❌ **Grouping by the column you want to count distinct values of**
   ```sql
   -- WRONG: This creates separate groups for each PLAN_HANDLE
   GROUP BY SQL_HANDLE, STATEMENT_SQL_HANDLE, PLAN_HANDLE
   ```

2. ❌ **Using COUNT() instead of COUNT(DISTINCT)**
   ```sql
   -- WRONG: Counts total rows, not distinct values
   COUNT(PLAN_HANDLE)
   ```

3. ✅ **Correct approach: Group by identifying columns, count distinct target column**
   ```sql
   -- CORRECT: Groups by pair, counts distinct plans
   GROUP BY SQL_HANDLE, STATEMENT_SQL_HANDLE
   COUNT(DISTINCT PLAN_HANDLE)
   ```

### When to Use This Pattern

This pattern is useful when you need to:
- Find groups with multiple distinct values of a particular column
- Identify queries with plan instability (multiple execution plans)
- Detect data quality issues (e.g., multiple versions of same entity)
- Analyze variability within groups

---

## Date Format

Last Updated: 2025-10-30

