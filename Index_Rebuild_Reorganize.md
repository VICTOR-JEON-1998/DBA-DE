# SQL Server Index Rebuild and Reorganize

## Why Perform Index Rebuild/Reorganize?

Index rebuild and reorganize operations are performed to resolve index fragmentation and improve slow query performance.

### How Indexes Work
- Indexes are like books on a bookshelf - they perform best when physically ordered sequentially
- When `INSERT`, `UPDATE`, or `DELETE` operations occur, the physical order can become disrupted
- Fragmentation causes the query optimizer to jump around the index pages instead of reading sequentially
- This increases disk head movement, resulting in higher I/O overhead

## Query Optimizer Decision Making

The query optimizer decides whether to use an index or perform a table scan:
- **Table Scan**: The optimizer may choose a table scan if:
  - The table is too small
  - Too much data is requested (large result set)

## Index Page Structure

SQL Server indexes use a B-tree structure with three main page types:
- **Root Page**: Top-level page of the index
- **Branch Page**: Intermediate pages that point to leaf pages
- **Leaf Page**: Bottom-level pages containing the actual data or pointers to data

## Fragmentation Analysis Query

The following query analyzes index fragmentation and recommends the appropriate maintenance action:

```sql
SELECT * 
INTO #REBUILD_OR_REORG
FROM (
    SELECT
        OBJECT_SCHEMA_NAME(ips.object_id) AS SchemaName,
        OBJECT_NAME(ips.object_id) AS TableName,
        i.name AS IndexName,
        ips.avg_fragmentation_in_percent AS [Fragmentation (%)],
        ips.page_count,
        -- Generate recommended action based on fragmentation rate and index size
        CASE
            WHEN ips.avg_fragmentation_in_percent > 30 THEN 'REBUILD'
            WHEN ips.avg_fragmentation_in_percent > 10 THEN 'REORGANIZE'
            ELSE 'NONE'
        END AS Recommended_Action
    FROM
        sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'SAMPLED') AS ips
    JOIN
        sys.indexes AS i ON ips.object_id = i.object_id 
                       AND ips.index_id = i.index_id
    WHERE
        ips.avg_fragmentation_in_percent > 0  -- Filter only fragmented indexes
        AND ips.page_count > 100              -- Filter indexes with meaningful size (100+ pages)
) T
```

### Fragmentation Thresholds
- **> 30%**: `REBUILD` recommended (more intensive operation, rebuilds the entire index)
- **> 10%**: `REORGANIZE` recommended (less intensive, reorganizes existing pages)
- **≤ 10%**: No action needed

## SQL Server Index Limits

### How Many Indexes Can a Table Have?
The number of indexes depends on the index type:
- **Clustered Index**: 1 per table (defines the physical order of data)
- **Non-Clustered Index**: Up to 999 per table

**Total**: SQL Server allows up to 1,000 indexes per table (1 clustered + 999 non-clustered)

## Best Practices

1. **Regular Monitoring**: Run fragmentation analysis queries regularly to identify indexes that need maintenance
2. **Maintenance Windows**: Perform `REBUILD` operations during maintenance windows as they require more resources and can lock tables
3. **Page Count Filter**: Only maintain indexes with significant size (e.g., > 100 pages) to avoid unnecessary overhead
4. **Fragmentation Threshold**: Use appropriate thresholds (10% for REORGANIZE, 30% for REBUILD) based on your environment's requirements

