# Query Tuning Statistics Guide (SQL Server)

## Purpose
Use these statements during tuning to measure elapsed time, CPU time, logical/physical reads, and operator-level behavior.

## Quick Start
```sql
-- Enable statistics for tuning
SET STATISTICS TIME ON;     -- CPU time and elapsed time
SET STATISTICS IO ON;       -- logical/physical reads per table/index
SET STATISTICS PROFILE ON;  -- execution profile as a result set

-- Run your test query here
-- SELECT * FROM dbo.YourTable WHERE YourColumn = 'value';

-- Disable after testing
SET STATISTICS TIME OFF;
SET STATISTICS IO OFF;
SET STATISTICS PROFILE OFF;
```

## What They Show
- TIME: CPU time and elapsed time per statement
- IO: Logical reads, physical reads, read-ahead reads per table/index
- PROFILE: Per-operator row counts with the actual plan shape

## Workflow
1. Turn ON the statistics.
2. Execute the query variants you want to compare.
3. Review Messages (TIME/IO) and the PROFILE result set.
4. Record key metrics (CPU ms, elapsed ms, logical reads) for comparison.
5. Turn the statistics OFF.

## Notes
- Session-scoped: only affects the current session.
- Prefer non-production environments when possible.

- For production-friendly insights, consider Query Store or `SET STATISTICS XML ON`.