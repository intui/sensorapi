# PostgreSQL Space Reclamation After Deletions

## Summary: Your Sensor Deletion (ID: 21927b67-a067-420c-a887-3edac2efd520)

When you deleted the "tibber power" sensor via the UI, here's what happened:

### ❌ **Space is NOT Released Immediately**

PostgreSQL uses a **Multi-Version Concurrency Control (MVCC)** system, which means:

1. **Deleted rows become "dead tuples"** - they're marked as deleted but not physically removed
2. **Disk space remains occupied** - the space is marked as reusable but not freed to the OS
3. **VACUUM process** is needed to reclaim the space

## What Actually Happened to Your Data

### 1. Sensor Deletion Process (from code)

```python
# In app/graphql/resolvers.py - delete_sensor mutation
def delete_sensor(self, info: Info, id: str) -> bool:
    # First: All sensor_readings for sensor ID 21927b67... were deleted
    db.query(SensorReadingModel).filter(SensorReadingModel.sensor_id == id).delete()
    
    # Second: The sensor itself was deleted
    db.delete(model)
    db.commit()
```

### 2. Database Operations

- ✅ Sensor record marked as deleted in `api_sensors` table
- ✅ All related sensor readings marked as deleted in `api_sensor_readings` table
- ⏳ Space marked as reusable (but not freed)
- ⏳ Waiting for VACUUM to physically reclaim space

## PostgreSQL Space Reclamation Methods

### Automatic: AUTOVACUUM (Default on Aiven)

Aiven PostgreSQL runs AUTOVACUUM automatically, which:

- **Triggers when**: ~20% of table rows are dead tuples
- **What it does**: Marks space as reusable for new data
- **Does NOT**: Shrink the physical file size immediately
- **Timing**: Usually runs within minutes to hours

### Manual: VACUUM Command

```sql
-- Basic VACUUM (non-blocking, marks space as reusable)
VACUUM api_sensor_readings;
VACUUM api_sensors;

-- VACUUM with statistics update
VACUUM ANALYZE api_sensor_readings;
VACUUM ANALYZE api_sensors;
```

### Aggressive: VACUUM FULL (Requires Table Lock)

```sql
-- VACUUM FULL (blocks all access, physically shrinks table)
-- ⚠️ WARNING: Locks table during operation!
VACUUM FULL api_sensor_readings;
VACUUM FULL api_sensors;
```

## Check Current Space Usage

### Query to Check Dead Tuples

```sql
SELECT 
    schemaname,
    relname as table_name,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    n_dead_tup::float / NULLIF(n_live_tup + n_dead_tup, 0) * 100 as dead_pct,
    pg_size_pretty(pg_relation_size(relid)) as table_size,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE relname IN ('api_sensors', 'api_sensor_readings', 'api_sensor_types')
ORDER BY n_dead_tup DESC;
```

### Query to Check Table Sizes

```sql
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE tablename LIKE 'api_sensor%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Database Size

```sql
SELECT pg_size_pretty(pg_database_size(current_database())) as total_db_size;
```

## When Will Space Actually Be Freed?

### Timeline for Your Deletion

| Time | What Happens | Space Status |
|------|-------------|--------------|
| **Immediate** (Now) | Rows marked as deleted | Space still occupied |
| **Minutes to Hours** | AUTOVACUUM runs | Space marked reusable (not freed) |
| **After VACUUM** | New data can use the space | File size unchanged |
| **After VACUUM FULL** | Physical file shrinks | Space returned to OS |

### Practical Impact

1. **For Your Database Growth**: Space can be reused for new sensor readings
2. **For Disk Usage**: File size stays the same until VACUUM FULL
3. **For Aiven Billing**: Still counted toward your storage limit
4. **For Performance**: VACUUM improves query performance by removing dead tuples

## How to Force Space Reclamation

### Option 1: Run Manual VACUUM (Recommended)

```sql
-- Non-blocking, fast
VACUUM (VERBOSE, ANALYZE) api_sensor_readings;
VACUUM (VERBOSE, ANALYZE) api_sensors;
```

### Option 2: Run VACUUM FULL (Use with Caution)

```sql
-- Blocks all access during operation!
-- Only run during maintenance windows
VACUUM FULL VERBOSE api_sensor_readings;
VACUUM FULL VERBOSE api_sensors;
```

### Option 3: Let AUTOVACUUM Handle It (Easiest)

Aiven's AUTOVACUUM will automatically clean up dead tuples. Just wait.

## Monitoring Recommendations

### 1. Check AUTOVACUUM Status

```sql
SELECT 
    relname,
    last_autovacuum,
    autovacuum_count,
    n_dead_tup
FROM pg_stat_user_tables
WHERE relname LIKE 'api_sensor%'
ORDER BY last_autovacuum DESC NULLS LAST;
```

### 2. Check for Bloat

```sql
SELECT 
    schemaname || '.' || tablename as table,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_dead_tup,
    n_live_tup,
    ROUND(100 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### 3. Set Up Alerts (in Aiven Console)

- Alert when dead tuple ratio > 20%
- Alert when table size grows unexpectedly
- Monitor AUTOVACUUM frequency

## Best Practices for Space Management

### 1. Regular Bulk Deletions?

If you frequently delete large amounts of data:

```python
# After bulk deletions, trigger VACUUM manually
from sqlalchemy import text

with get_db_session() as db:
    # Perform deletions
    db.query(SensorReadingModel).filter(...).delete()
    db.commit()
    
    # Trigger VACUUM
    db.execute(text("VACUUM ANALYZE api_sensor_readings"))
```

### 2. Scheduled Maintenance

- Run `VACUUM ANALYZE` during low-traffic periods
- Consider `VACUUM FULL` monthly if you have high deletion rates
- Monitor Aiven's automatic maintenance windows

### 3. Table Partitioning (Future Consideration)

For `api_sensor_readings`, consider time-based partitioning:

- Old partitions can be dropped entirely (instant space reclamation)
- Better for time-series data with retention policies

## Aiven-Specific Considerations

### AUTOVACUUM Configuration (Default)

Aiven enables AUTOVACUUM with these defaults:

- `autovacuum = on`
- `autovacuum_vacuum_threshold = 50`
- `autovacuum_vacuum_scale_factor = 0.2` (20% dead tuples)
- `autovacuum_analyze_threshold = 50`

### Connection Limits Impact

Remember your Aiven plan connection limits:

- VACUUM operations use connections
- AUTOVACUUM runs in background (doesn't count toward user limit)
- Manual VACUUM uses a user connection

### Monitoring in Aiven Console

1. Go to Aiven Console → Your Database
2. Check "Metrics" tab for:
   - Database size over time
   - Dead tuples count
   - VACUUM activity
3. Set up alerts for space usage thresholds

## Summary: Your Specific Case

**Sensor Deleted**: `tibber power` (ID: 21927b67-a067-420c-a887-3edac2efd520)

**What Was Deleted**:

- 1 sensor record in `api_sensors`
- All associated readings in `api_sensor_readings` (could be thousands)
- Related alerts (if any)

**Space Reclamation Timeline**:

1. ✅ Immediate: Rows marked as deleted (logical deletion)
2. ⏳ 10-60 minutes: AUTOVACUUM will likely run
3. ⏳ After AUTOVACUUM: Space reusable for new data
4. ❌ File size: Unchanged (unless you run VACUUM FULL)

**Recommendation**:

- **Do nothing** - let AUTOVACUUM handle it automatically
- **If urgent**: Run `VACUUM ANALYZE api_sensor_readings;` manually
- **For space return**: Only use `VACUUM FULL` if absolutely necessary

**To check status now**:

```bash
# Connect to your Aiven database and run:
SELECT 
    relname,
    n_dead_tup as dead_rows,
    n_live_tup as live_rows,
    last_autovacuum
FROM pg_stat_user_tables
WHERE relname IN ('api_sensors', 'api_sensor_readings');
```

---

**Date**: October 13, 2025  
**Context**: Sensor deletion via UI - Space reclamation question  
**Recommendation**: Trust AUTOVACUUM, monitor via Aiven console
