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

https://www.notion.so/image/attachment%3Ad8124fb4-050a-4125-8873-8dcf34c302d3%3Aimage.png?table=block&id=29a53698-6d16-8035-90bb-c9f7ff72ed64&spaceId=0af99f2e-8fd6-4b1d-b06a-d80ab9501941&width=2000&userId=708820b9-e2a0-43be-8e24-39679e79f0ff&cache=v2

https://www.notion.so/image/attachment%3A1f4d750c-d27c-43be-805e-ef9cea7ef898%3Aimage.png?table=block&id=29a53698-6d16-8024-95ea-f4b6ba27ceef&spaceId=0af99f2e-8fd6-4b1d-b06a-d80ab9501941&width=2000&userId=708820b9-e2a0-43be-8e24-39679e79f0ff&cache=v2

https://www.notion.so/image/attachment%3Aa053c2a3-cc02-4c97-a434-8744397ef58e%3Aimage.png?table=block&id=29a53698-6d16-8062-b757-fcf917c28e22&spaceId=0af99f2e-8fd6-4b1d-b06a-d80ab9501941&width=2000&userId=708820b9-e2a0-43be-8e24-39679e79f0ff&cache=v2

Copy the parameter values together with the SQL query and paste them into a text editor.

- Declare @bn VARCHAR(100)
- SET @b1 = 'variable';
- Use Ctrl+H to search for " : " and replace with @b (the original code maps variables like ":1").

Then execute the code and check whether the result returns quickly.

If it runs fast, it indicates the plan cache is pinned to an old (suboptimal) plan.

If it runs fast, proceed with the following. If it remains slow, further tuning is required.

https://www.notion.so/image/attachment%3A3539fa9c-f430-4b2a-ac72-ccb6fdd54824%3Aimage.png?table=block&id=29a53698-6d16-8009-9a89-cc64df4b9eef&spaceId=0af99f2e-8fd6-4b1d-b06a-d80ab9501941&width=2000&userId=708820b9-e2a0-43be-8e24-39679e79f0ff&cache=v2

``` sql
SELECT * FROM MONITOR.dbo.DBA_SESSIONS_DETAIL
WHERE 1=1
AND	SQL LIKE '%shopOutAskIfDataFixService%getMainList%MainList%' -- adjust the keyword accordingly
AND COLLECTION_DATE >= '20251028 17:00:00'
ORDER BY COLLECTION_DATE
```
Compare the ELAPSED_SEC between slow and fast executions.

https://www.notion.so/image/attachment%3A8ec6b3b8-fbbc-457c-810d-6861e726be1a%3Aimage.png?table=block&id=29a53698-6d16-800d-bcd3-cd75cb5c624e&spaceId=0af99f2e-8fd6-4b1d-b06a-d80ab9501941&width=2000&userId=708820b9-e2a0-43be-8e24-39679e79f0ff&cache=v2

https://www.notion.so/image/attachment%3A4b3f2b79-814a-4689-a89d-03af5e02011f%3Aimage.png?table=block&id=29a53698-6d16-807c-a907-c29af60ce694&spaceId=0af99f2e-8fd6-4b1d-b06a-d80ab9501941&width=2000&userId=708820b9-e2a0-43be-8e24-39679e79f0ff&cache=v2


The slow and fast executions will likely have different plan handle values.

You can confirm by comparing the query plans.

Copy one query plan from the slow execution and one from the fast execution (total two plans), search for an XML formatter in Google, and convert both to XML.

In Notepad, press Alt+L to switch to XML mode for easier comparison.

At the very end, the ParameterList values will be set differently.

After confirming the differences, clear the plan cache for the query that ran slowly.


https://www.notion.so/image/attachment%3A1339c99f-6302-4c03-b775-ea6696436c6f%3Aimage.png?table=block&id=29a53698-6d16-8095-a71c-c9ce7bd2b2d4&spaceId=0af99f2e-8fd6-4b1d-b06a-d80ab9501941&width=2000&userId=708820b9-e2a0-43be-8e24-39679e79f0ff&cache=v2

DBCC FREEPROCCACHE (plan_handle) will remove the incorrectly fixed plan cache entry.