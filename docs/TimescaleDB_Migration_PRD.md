# TimescaleDB Migration Planning PRD

## Project Overview
**Project:** Migration to TimescaleDB on Tiger Cloud  
**Date:** September 1, 2025  
**Status:** Planning Phase  
**Priority:** High  

## Executive Summary
Migrate the sensor data management system from Aiven PostgreSQL to TimescaleDB on Tiger Cloud to leverage time-series optimizations for high-volume sensor data storage and querying.

## Objectives
1. **Database Migration**: Seamlessly migrate from Aiven PostgreSQL to TimescaleDB on Tiger Cloud
2. **Time-Series Optimization**: Implement TimescaleDB hypertables for optimal time-series data performance
3. **Data Import**: Import sample household energy data (153K+ records) from CSV
4. **Performance Enhancement**: Leverage TimescaleDB's time-series capabilities for sensor readings

## Current State Analysis

### Database Connection
- **Current**: Aiven PostgreSQL Cloud Database
- **Target**: Tiger Cloud TimescaleDB
- **Connection String**: Already configured in `.env` as `TIGER_CLOUD_DATABASE_URL`

### Data Volume
- **Sample Dataset**: `household_data_15min.csv` (59MB, 153,811 rows)
- **Data Frequency**: 15-minute intervals
- **Data Columns**: 69 sensor measurement columns for various industrial/residential devices
- **Time Range**: Starting from 2014-12-11 (historical energy consumption data)

### Current Schema Structure
```sql
-- Core Tables
api_sensor_types       -- Sensor type definitions
api_locations         -- Hierarchical location structure  
api_sensors           -- Sensor device instances
api_sensor_readings   -- Time-series sensor data (TARGET FOR HYPERTABLE)
api_alerts           -- Alert management
```

## Technical Requirements

### 1. Database Migration Steps
```mermaid
graph TD
    A[Configure Tiger Cloud Connection] --> B[Test Connection]
    B --> C[Run Schema Migration via Alembic]
    C --> D[Create TimescaleDB Extension]
    D --> E[Convert sensor_readings to Hypertable]
    E --> F[Import Sample Data]
    F --> G[Update Application Configuration]
    G --> H[Validate Data Integrity]
```

### 2. TimescaleDB Hypertable Configuration
**Target Table**: `api_sensor_readings`
**Partition Column**: `timestamp` (DateTime with timezone)
**Chunk Time Interval**: 1 day (recommended for 15-minute data)

### 3. Sample Data Schema Mapping
Map CSV columns to sensor_readings table:
- `utc_timestamp` → `timestamp`
- Device columns (69 sensors) → Multiple sensor_reading records
- Values → `value` field

## Implementation Plan

### Phase 1: Database Setup (Day 1)
1. **Environment Configuration**
   - [ ] Switch `DATABASE_URL` to Tiger Cloud connection
   - [ ] Test database connectivity
   - [ ] Verify TimescaleDB extension availability

2. **Schema Migration**
   - [ ] Run Alembic migrations on Tiger Cloud database
   - [ ] Create all necessary tables
   - [ ] Verify foreign key relationships

### Phase 2: TimescaleDB Configuration (Day 1)
1. **Hypertable Creation**
   ```sql
   -- Enable TimescaleDB extension
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   
   -- Convert sensor_readings table to hypertable
   SELECT create_hypertable('api_sensor_readings', 'timestamp', 
                           chunk_time_interval => INTERVAL '1 day');
   ```

2. **Index Optimization**
   - [ ] Create time-based indexes
   - [ ] Optimize sensor_id + timestamp composite indexes
   - [ ] Add TimescaleDB-specific performance indexes

### Phase 3: Data Import Strategy (Day 2)
1. **Sensor Type Setup**
   ```python
   # Create sensor types for all 69 household data columns
   sensor_types = [
       "grid_import", "pv_generation", "storage_charge", 
       "heat_pump", "dishwasher", "washing_machine", etc.
   ]
   ```

2. **Location Hierarchy**
   ```python
   # Create location structure
   locations = {
       "DE_KN_industrial1": "Industrial Building 1",
       "DE_KN_residential1": "Residential Building 1", 
       etc.
   }
   ```

3. **CSV Data Import Process**
   ```python
   # Bulk insert strategy for 153K+ records
   # Process in chunks of 1000 records
   # Transform wide CSV format to normalized sensor_readings
   ```

### Phase 4: Application Updates (Day 2)
1. **Configuration Changes**
   - [ ] Update database connection in production
   - [ ] Modify environment variables
   - [ ] Update deployment scripts

2. **Performance Optimization**
   - [ ] Leverage TimescaleDB time-series functions
   - [ ] Implement compressed chunks for historical data
   - [ ] Add continuous aggregates for common queries

## Technical Implementation Details

### Database Connection Update
```python
# .env file change
DATABASE_URL=postgres://tsdbadmin:pro9zdeicmhxn0ax@at3hy6aafv.ebrvvpbww1.tsdb.cloud.timescale.com:35598/tsdb?sslmode=require
```

### Hypertable Creation Script
```sql
-- Create hypertable after schema migration
SELECT create_hypertable(
    'api_sensor_readings',
    'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Create indexes for optimal performance
CREATE INDEX IF NOT EXISTS idx_readings_sensor_time 
    ON api_sensor_readings (sensor_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_readings_time_value 
    ON api_sensor_readings (timestamp DESC, value);
```

### Data Import Script Structure
```python
import pandas as pd
from sqlalchemy.orm import sessionmaker
from app.database.models import SensorType, Location, Sensor, SensorReading

def import_household_data():
    # 1. Read CSV file
    df = pd.read_csv('import_data/household_data_15min.csv')
    
    # 2. Create sensor types and locations
    create_sensor_infrastructure(df.columns)
    
    # 3. Transform wide format to long format
    readings_data = transform_to_readings(df)
    
    # 4. Bulk insert in chunks
    bulk_insert_readings(readings_data, chunk_size=1000)
```

## Risk Assessment

### High Risk
- **Data Loss**: Migration failure could result in data loss
- **Downtime**: Application unavailable during migration
- **Performance Degradation**: Incorrect hypertable configuration

### Mitigation Strategies
- **Backup Strategy**: Full database backup before migration
- **Blue-Green Deployment**: Maintain parallel environments
- **Rollback Plan**: Keep Aiven database as fallback
- **Testing**: Comprehensive testing on staging environment

## Success Criteria

### Functional Requirements
- [ ] All existing sensor data preserved
- [ ] Sample household data successfully imported
- [ ] All GraphQL queries working correctly
- [ ] Real-time sensor reading ingestion functional

### Performance Requirements
- [ ] Query performance improved by 50%+ for time-series data
- [ ] Sub-second response for sensor reading ranges
- [ ] Efficient storage with TimescaleDB compression
- [ ] Scalable to millions of sensor readings

### Operational Requirements
- [ ] Zero data loss during migration
- [ ] Maximum 4-hour downtime window
- [ ] Automated backup and recovery procedures
- [ ] Monitoring and alerting in place

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1** | 4 hours | Database setup, connection testing, schema migration |
| **Phase 2** | 2 hours | Hypertable creation, index optimization |
| **Phase 3** | 6 hours | Data import script development and execution |
| **Phase 4** | 2 hours | Application updates, deployment |
| **Testing** | 2 hours | End-to-end validation, performance testing |
| **Total** | **16 hours** | Complete migration over 2 days |

## Scripts and Tools Required

### 1. Migration Scripts
- `scripts/migrate_to_timescaledb.py` - Main migration orchestrator
- `scripts/create_hypertable.sql` - TimescaleDB configuration
- `scripts/import_household_data.py` - CSV data import utility

### 2. Validation Scripts  
- `scripts/validate_migration.py` - Data integrity verification
- `scripts/performance_test.py` - Query performance validation

### 3. Rollback Procedures
- `scripts/rollback_to_aiven.py` - Emergency rollback utility
- `scripts/backup_tiger_cloud.py` - Backup creation utility

## Next Steps

1. **Create Migration Scripts** (Next 2 hours)
2. **Setup Staging Environment** (Next 4 hours)  
3. **Execute Migration Plan** (Following day)
4. **Production Deployment** (Day 2)

## Stakeholder Sign-off

- [ ] **Development Team Lead** - Technical approach approved
- [ ] **DevOps Engineer** - Infrastructure changes approved  
- [ ] **Data Engineering** - Data import strategy approved
- [ ] **Product Owner** - Timeline and success criteria approved

---

**Document Version**: 1.0  
**Last Updated**: September 1, 2025  
**Next Review**: Post-migration (September 3, 2025)