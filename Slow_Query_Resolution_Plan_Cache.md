# Slow Query Resolution: Plan Cache Clearing Strategy

## Overview
When monitoring tools detect slow queries in database systems, one effective resolution method is clearing the plan cache. This document outlines the process and considerations for using plan cache clearing as a troubleshooting technique.

## What is Plan Cache?
The plan cache (also known as query plan cache or execution plan cache) stores compiled query execution plans to improve performance by avoiding recompilation overhead. However, cached plans can sometimes become suboptimal due to:
- Data distribution changes
- Statistics updates
- Schema modifications
- Resource constraints

## When to Clear Plan Cache

### Indications for Plan Cache Clearing
- Monitoring tools show sudden performance degradation
- Queries that previously performed well are now slow
- After significant data changes or statistics updates
- When query plans appear suboptimal in execution plans
- Resource contention issues persist despite other optimizations

### Warning Signs
- CPU usage spikes without apparent cause
- Increased logical reads in query execution plans
- Memory pressure in plan cache
- Inconsistent query performance across similar workloads

## Implementation Methods

### SQL Server
```sql
-- Clear entire plan cache
DBCC FREEPROCCACHE;

-- Clear plan cache for specific database
DBCC FREEPROCCACHE(DB_ID('DatabaseName'));

-- Clear plan cache for specific query
DBCC FREEPROCCACHE(plan_handle);
```

### Oracle
```sql
-- Clear shared pool (includes plan cache)
ALTER SYSTEM FLUSH SHARED_POOL;

-- Clear specific cursor
EXEC DBMS_SHARED_POOL.PURGE('schema.object_name', 'C');
```

### PostgreSQL
```sql
-- Clear all cached plans
DISCARD PLANS;

-- Clear specific prepared statement
DEALLOCATE statement_name;
```

### MySQL
```sql
-- Clear query cache
RESET QUERY CACHE;

-- Clear prepared statements
DEALLOCATE PREPARE statement_name;
```

## Step-by-Step Process

### 1. Identify the Problem
- Use monitoring tools to identify slow queries
- Analyze query execution plans
- Check resource utilization patterns
- Document baseline performance metrics

### 2. Analyze Plan Cache Impact
- Review plan cache hit ratios
- Identify frequently executed queries
- Check for plan cache bloat
- Analyze memory usage patterns

### 3. Execute Plan Cache Clearing
- Choose appropriate clearing method based on database system
- Execute during low-traffic periods if possible
- Monitor system performance during execution
- Document the clearing operation

### 4. Monitor Results
- Track query performance post-clearing
- Monitor plan cache regeneration
- Verify performance improvements
- Document any side effects

## Best Practices

### Timing Considerations
- Execute during maintenance windows when possible
- Avoid peak business hours
- Consider impact on application performance
- Plan for temporary performance degradation

### Monitoring Requirements
- Set up alerts for plan cache clearing operations
- Monitor query compilation overhead
- Track plan cache hit ratios
- Document performance baselines

### Risk Mitigation
- Test in non-production environments first
- Have rollback procedures ready
- Monitor application connectivity
- Prepare for temporary performance impact

## Alternative Approaches

### Before Clearing Plan Cache
1. **Statistics Updates**
   ```sql
   UPDATE STATISTICS table_name;
   ```

2. **Index Maintenance**
   ```sql
   REBUILD INDEX index_name ON table_name;
   ```

3. **Query Optimization**
   - Review and optimize query logic
   - Add appropriate indexes
   - Consider query hints

### After Clearing Plan Cache
1. **Monitor Regeneration**
   - Track plan cache rebuild time
   - Monitor compilation overhead
   - Verify optimal plan selection

2. **Performance Validation**
   - Compare before/after metrics
   - Validate query performance improvements
   - Document lessons learned

## Monitoring and Alerting

### Key Metrics to Monitor
- Plan cache hit ratio
- Query compilation time
- Memory usage in plan cache
- Query execution time trends
- Resource utilization patterns

### Recommended Alerts
- Plan cache hit ratio below threshold
- Excessive compilation overhead
- Memory pressure in plan cache
- Query performance degradation
- Failed plan cache operations

## Documentation Requirements

### What to Document
- Date and time of plan cache clearing
- Reason for clearing (monitoring tool alerts)
- Method used for clearing
- Performance impact observed
- Results and effectiveness
- Follow-up actions required

### Sample Documentation Template
```
Date: [Date]
Time: [Time]
Database: [Database Name]
Reason: [Monitoring tool alert description]
Method: [Clearing method used]
Impact: [Performance impact observed]
Results: [Effectiveness of the action]
Follow-up: [Next steps required]
```

## Conclusion

Clearing plan cache is a valuable troubleshooting technique when monitoring tools detect slow queries. However, it should be used judiciously as part of a comprehensive performance optimization strategy. Always consider alternative approaches first and ensure proper monitoring and documentation throughout the process.

## Related Topics
- Query Performance Optimization
- Database Monitoring Strategies
- Execution Plan Analysis
- Statistics Management
- Index Optimization


# Real Example

### Clearing DB Plan Cache with Monitoring

Identify outliers in the transaction distribution chart.

<img width="1120" height="646" alt="image" src="https://github.com/user-attachments/assets/6bfc815e-d9c1-443a-ba4d-7229e5442019" />

<img width="885" height="733" alt="image" src="https://github.com/user-attachments/assets/ea315273-8c65-479f-9d61-f2452cfcda4a" />

<img width="2048" height="1038" alt="image" src="https://github.com/user-attachments/assets/3021598c-d28d-45fa-8123-b55ad74d5a4b" />


Copy the parameter values together with the SQL query and paste them into a text editor.

- Declare @bn VARCHAR(100)
- SET @b1 = 'variable';
- Use Ctrl+H to search for " : " and replace with @b (the original code maps variables like ":1").

Then execute the code and check whether the result returns quickly.

If it runs fast, it indicates the plan cache is pinned to an old (suboptimal) plan.

If it runs fast, proceed with the following. If it remains slow, further tuning is required.

<img width="1583" height="662" alt="image" src="https://github.com/user-attachments/assets/00e0d2f3-999c-417f-83b0-34db5f7b5a0d" />


``` sql
SELECT * FROM MONITOR.dbo.DBA_SESSIONS_DETAIL
WHERE 1=1
AND	SQL LIKE '%shopOutAskIfDataFixService%getMainList%MainList%' -- adjust the keyword accordingly
AND COLLECTION_DATE >= '20251028 17:00:00'
ORDER BY COLLECTION_DATE
```
Compare the ELAPSED_SEC between slow and fast executions.

<img width="2048" height="567" alt="image" src="https://github.com/user-attachments/assets/1413f946-4fac-47e5-af48-d9d7d8b8e82b" />

<img width="1453" height="586" alt="image" src="https://github.com/user-attachments/assets/b5c2d2b0-92c3-4cc5-a960-43e9c721a289" />


The slow and fast executions will likely have different plan handle values.

You can confirm by comparing the query plans.

Copy one query plan from the slow execution and one from the fast execution (total two plans), search for an XML formatter in Google, and convert both to XML.

In Notepad, press Alt+L to switch to XML mode for easier comparison.

At the very end, the ParameterList values will be set differently.

After confirming the differences, clear the plan cache for the query that ran slowly.

<img width="1665" height="1053" alt="image" src="https://github.com/user-attachments/assets/e56be2a9-35a2-47ce-948e-011cc62e6510" />


DBCC FREEPROCCACHE (plan_handle) will remove the incorrectly fixed plan cache entry.
