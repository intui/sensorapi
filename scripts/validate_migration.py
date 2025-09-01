#!/usr/bin/env python3
"""
Validation Script for TimescaleDB Migration

This script validates that the migration to TimescaleDB was successful by:
1. Checking database connectivity
2. Verifying table structure
3. Validating hypertable configuration
4. Testing data integrity
5. Performance benchmarking

Usage:
    python scripts/validate_migration.py
"""

import os
import sys
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database.models import SensorType, Location, Sensor, SensorReading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MigrationValidator:
    def __init__(self):
        self.db_url = os.getenv('TIGER_CLOUD_DATABASE_URL')
        if not self.db_url:
            raise ValueError("TIGER_CLOUD_DATABASE_URL not found in environment")
        
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def test_connectivity(self):
        """Test database connectivity"""
        logger.info("Testing database connectivity...")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT current_database(), version();"))
                db_name, version = result.fetchone()
                logger.info(f"Connected to database: {db_name}")
                logger.info(f"Database version: {version}")
                return True
        except Exception as e:
            logger.error(f"Connectivity test failed: {e}")
            return False
    
    def validate_schema(self):
        """Validate database schema"""
        logger.info("Validating database schema...")
        try:
            with self.engine.connect() as conn:
                # Check all required tables exist
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name LIKE 'api_%'
                    ORDER BY table_name;
                """))
                tables = [row[0] for row in result.fetchall()]
                
                expected_tables = [
                    'api_alerts', 'api_locations', 'api_sensor_readings', 
                    'api_sensor_types', 'api_sensors'
                ]
                
                missing_tables = set(expected_tables) - set(tables)
                if missing_tables:
                    logger.error(f"Missing tables: {missing_tables}")
                    return False
                
                logger.info(f"All required tables present: {tables}")
                
                # Check table row counts
                for table in expected_tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
                    count = result.fetchone()[0]
                    logger.info(f"Table {table}: {count:,} rows")
                
                return True
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    def validate_hypertable(self):
        """Validate TimescaleDB hypertable configuration"""
        logger.info("Validating hypertable configuration...")
        try:
            with self.engine.connect() as conn:
                # Check TimescaleDB extension
                result = conn.execute(text("""
                    SELECT extname FROM pg_extension WHERE extname = 'timescaledb';
                """))
                extension = result.fetchone()
                if not extension:
                    logger.error("TimescaleDB extension not installed")
                    return False
                
                logger.info("TimescaleDB extension is installed")
                
                # Check hypertable status
                result = conn.execute(text("""
                    SELECT 
                        table_name, 
                        chunk_time_interval,
                        num_chunks
                    FROM timescaledb_information.hypertables 
                    WHERE table_name = 'api_sensor_readings';
                """))
                hypertable_info = result.fetchone()
                
                if not hypertable_info:
                    logger.error("api_sensor_readings is not a hypertable")
                    return False
                
                table_name, interval, num_chunks = hypertable_info
                logger.info(f"Hypertable: {table_name}")
                logger.info(f"Chunk interval: {interval}")
                logger.info(f"Number of chunks: {num_chunks}")
                
                # Check chunk information
                result = conn.execute(text("""
                    SELECT 
                        chunk_name,
                        range_start,
                        range_end
                    FROM timescaledb_information.chunks 
                    WHERE hypertable_name = 'api_sensor_readings'
                    ORDER BY range_start
                    LIMIT 5;
                """))
                chunks = result.fetchall()
                
                if chunks:
                    logger.info("Sample chunks:")
                    for chunk_name, start, end in chunks:
                        logger.info(f"  {chunk_name}: {start} to {end}")
                else:
                    logger.info("No chunks found (table may be empty)")
                
                return True
        except Exception as e:
            logger.error(f"Hypertable validation failed: {e}")
            return False
    
    def validate_data_integrity(self):
        """Validate data integrity"""
        logger.info("Validating data integrity...")
        try:
            with self.SessionLocal() as session:
                # Check foreign key relationships
                sensor_types_count = session.query(SensorType).count()
                locations_count = session.query(Location).count()
                sensors_count = session.query(Sensor).count()
                readings_count = session.query(SensorReading).count()
                
                logger.info(f"Data counts:")
                logger.info(f"  Sensor types: {sensor_types_count:,}")
                logger.info(f"  Locations: {locations_count:,}")
                logger.info(f"  Sensors: {sensors_count:,}")
                logger.info(f"  Readings: {readings_count:,}")
                
                # Check for orphaned records
                with self.engine.connect() as conn:
                    # Sensors without valid sensor_type_id
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM api_sensors s
                        LEFT JOIN api_sensor_types st ON s.sensor_type_id = st.id
                        WHERE st.id IS NULL;
                    """))
                    orphaned_sensors = result.fetchone()[0]
                    
                    # Readings without valid sensor_id
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM api_sensor_readings sr
                        LEFT JOIN api_sensors s ON sr.sensor_id = s.id
                        WHERE s.id IS NULL;
                    """))
                    orphaned_readings = result.fetchone()[0]
                    
                    if orphaned_sensors > 0:
                        logger.warning(f"Found {orphaned_sensors} orphaned sensors")
                    if orphaned_readings > 0:
                        logger.warning(f"Found {orphaned_readings} orphaned readings")
                    
                    if orphaned_sensors == 0 and orphaned_readings == 0:
                        logger.info("✅ No orphaned records found")
                
                return True
        except Exception as e:
            logger.error(f"Data integrity validation failed: {e}")
            return False
    
    def benchmark_performance(self):
        """Benchmark query performance"""
        logger.info("Running performance benchmarks...")
        try:
            with self.engine.connect() as conn:
                # Test queries with timing
                test_queries = [
                    ("Count all readings", "SELECT COUNT(*) FROM api_sensor_readings;"),
                    ("Recent readings (last hour)", """
                        SELECT COUNT(*) FROM api_sensor_readings 
                        WHERE timestamp > NOW() - INTERVAL '1 hour';
                    """),
                    ("Sensor with most readings", """
                        SELECT s.name, COUNT(sr.id) as reading_count
                        FROM api_sensors s
                        JOIN api_sensor_readings sr ON s.id = sr.sensor_id
                        GROUP BY s.id, s.name
                        ORDER BY reading_count DESC
                        LIMIT 1;
                    """),
                    ("Average value by sensor type", """
                        SELECT st.name, AVG(sr.value) as avg_value, COUNT(sr.id) as count
                        FROM api_sensor_types st
                        JOIN api_sensors s ON st.id = s.sensor_type_id
                        JOIN api_sensor_readings sr ON s.id = sr.sensor_id
                        GROUP BY st.id, st.name
                        ORDER BY count DESC
                        LIMIT 5;
                    """),
                    ("Time range query with aggregation", """
                        SELECT 
                            DATE_TRUNC('hour', timestamp) as hour,
                            AVG(value) as avg_value,
                            COUNT(*) as reading_count
                        FROM api_sensor_readings 
                        WHERE timestamp >= NOW() - INTERVAL '24 hours'
                        GROUP BY hour
                        ORDER BY hour DESC
                        LIMIT 10;
                    """)
                ]
                
                for query_name, query_sql in test_queries:
                    start_time = time.time()
                    result = conn.execute(text(query_sql))
                    rows = result.fetchall()
                    end_time = time.time()
                    
                    duration = (end_time - start_time) * 1000  # Convert to milliseconds
                    logger.info(f"Query: {query_name}")
                    logger.info(f"  Duration: {duration:.2f}ms")
                    logger.info(f"  Results: {len(rows)} rows")
                    
                    # Log first few results for validation
                    if rows and len(rows) <= 5:
                        for row in rows:
                            logger.info(f"    {row}")
                    elif rows:
                        logger.info(f"    Sample: {rows[0]}")
                
                return True
        except Exception as e:
            logger.error(f"Performance benchmark failed: {e}")
            return False
    
    def validate_timescaledb_features(self):
        """Test TimescaleDB specific features"""
        logger.info("Testing TimescaleDB features...")
        try:
            with self.engine.connect() as conn:
                # Test time_bucket function
                result = conn.execute(text("""
                    SELECT 
                        time_bucket('1 hour', timestamp) as bucket,
                        COUNT(*) as reading_count,
                        AVG(value) as avg_value
                    FROM api_sensor_readings 
                    GROUP BY bucket
                    ORDER BY bucket DESC
                    LIMIT 5;
                """))
                buckets = result.fetchall()
                
                if buckets:
                    logger.info("Time bucket aggregation working:")
                    for bucket, count, avg_val in buckets:
                        logger.info(f"  {bucket}: {count} readings, avg={avg_val:.3f}")
                else:
                    logger.info("No data for time bucket test")
                
                # Test TimescaleDB statistics
                result = conn.execute(text("""
                    SELECT 
                        schemaname,
                        tablename,
                        num_chunks,
                        compression_status,
                        uncompressed_heap_size,
                        compressed_heap_size
                    FROM timescaledb_information.hypertable_stats
                    WHERE tablename = 'api_sensor_readings';
                """))
                stats = result.fetchone()
                
                if stats:
                    schema, table, chunks, compression, uncompressed, compressed = stats
                    logger.info(f"Hypertable statistics:")
                    logger.info(f"  Chunks: {chunks}")
                    logger.info(f"  Compression: {compression}")
                    logger.info(f"  Uncompressed size: {uncompressed}")
                    logger.info(f"  Compressed size: {compressed}")
                
                return True
        except Exception as e:
            logger.error(f"TimescaleDB features test failed: {e}")
            return False
    
    def run_validation(self):
        """Run complete validation suite"""
        logger.info("=" * 60)
        logger.info("STARTING MIGRATION VALIDATION")
        logger.info("=" * 60)
        
        tests = [
            ("Database connectivity", self.test_connectivity),
            ("Schema validation", self.validate_schema),
            ("Hypertable configuration", self.validate_hypertable),
            ("Data integrity", self.validate_data_integrity),
            ("Performance benchmarks", self.benchmark_performance),
            ("TimescaleDB features", self.validate_timescaledb_features)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} ---")
            try:
                success = test_func()
                results[test_name] = success
                if success:
                    logger.info(f"✅ {test_name} passed")
                else:
                    logger.error(f"❌ {test_name} failed")
            except Exception as e:
                logger.error(f"❌ {test_name} failed with exception: {e}")
                results[test_name] = False
        
        # Summary
        logger.info("=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} - {test_name}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All validation tests passed!")
            return True
        else:
            logger.error(f"❌ {total - passed} tests failed")
            return False

def main():
    """Main validation entry point"""
    try:
        validator = MigrationValidator()
        success = validator.run_validation()
        
        if success:
            print("\n🎉 Validation completed successfully!")
            print("All tests passed. Migration is validated.")
            sys.exit(0)
        else:
            print("\n❌ Validation failed!")
            print("Some tests failed. Check validation.log for details.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation script failed: {e}")
        print(f"\n❌ Validation script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()