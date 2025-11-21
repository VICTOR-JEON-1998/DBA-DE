# ETL Work Notes

## November 21, 2025

### Common ETL Errors: Column Size Issues

ETL errors are often caused by column size issues.

When an issue suddenly occurs even though there were no changes to the source table, it's worth suspecting that the target table may be truncating the primary key (PK) when retrieving it from the source table.

For example, MSSQL and Vertica have different data type sizes. Vertica typically needs to be configured approximately 1.5 times larger than MSSQL.

**Example Scenario:**

**MSSQL Source Table:**
- Column A (PK): `VARCHAR(10)`
- Existing data: `abcdefgxxx`
- New data: `abcdefgyyy`

**Vertica Target Table:**
- Column A' (PK): `VARCHAR(10)` (same size as source)
- Existing loaded data: `abcdefg` (truncated from `abcdefgxxx`)
- New data to be inserted: `abcdefgyyy` → **Error occurs** (duplicate PK or truncation issue)

### Root Cause

When working with different database systems in ETL processes, data type sizes can differ between source and target databases. If the target table column size is not sufficiently large, data truncation can occur, leading to:

1. **Primary Key Violations**: Truncated PK values may create duplicates
2. **Data Loss**: Original data values are lost during truncation
3. **Unexpected Errors**: Issues may appear suddenly when new data exceeds the truncated length

### Best Practice

When designing ETL processes between different database systems:

1. **Compare Data Type Sizes**: Always compare data type sizes between source and target databases
2. **Set Generous Column Sizes**: Configure target table columns to be larger than source columns (e.g., 1.5x for MSSQL → Vertica)
3. **Validate Data Length**: Check actual data lengths in source tables before designing target schemas
4. **Test with Edge Cases**: Test ETL processes with maximum-length data to ensure no truncation occurs

This ensures that source data can be loaded correctly without duplicates or data loss.

