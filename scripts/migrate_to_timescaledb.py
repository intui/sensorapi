#!/usr/bin/env python3
"""
TimescaleDB Migration Script

This script migrates the sensor API from Aiven PostgreSQL to TimescaleDB on Tiger Cloud.

IMPORTANT: For full TimescaleDB hypertable support, you need a Tiger Cloud service 
with "time-series and analytics" enabled. PostgreSQL services have limited TimescaleDB
functionality - this script will fall back to PostgreSQL time-series optimizations.

It handles:
1. Database connection testing
2. Schema migration via Alembic  
3. TimescaleDB hypertable creation (with Tiger Cloud and traditional approaches)
4. PostgreSQL time-series optimization fallback
5. Data validation

Tiger Cloud Hypertable Creation:
- For Time-series services: Uses CREATE TABLE ... WITH (tsdb.hypertable, tsdb.partition_column='time')
- For PostgreSQL services: Uses traditional create_hypertable() function
- Fallback: PostgreSQL time-series optimized indexes

Usage:
    python scripts/migrate_to_timescaledb.py
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from app.database.models import Base
from app.core.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TimescaleDBMigrator:
    def __init__(self):
        # Use Tiger Cloud database URL from settings
        from app.core.config import settings
        self.tiger_db_url = settings.TIGER_CLOUD_DATABASE_URL
        if not self.tiger_db_url:
            raise ValueError("TIGER_CLOUD_DATABASE_URL not configured in settings")
        
        self.engine = None
        self.session = None
        
    def test_connection(self):
        """Test connection to TimescaleDB"""
        logger.info("Testing connection to TimescaleDB...")
        try:
            # Convert postgres:// to postgresql:// if needed
            db_url = self.tiger_db_url
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            
            self.engine = create_engine(db_url)
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                logger.info(f"Connected successfully. Database version: {version}")
                
                # Check if TimescaleDB extension is available
                result = conn.execute(text("""
                    SELECT EXISTS(
                        SELECT 1 FROM pg_available_extensions 
                        WHERE name = 'timescaledb'
                    );
                """))
                has_timescaledb = result.fetchone()[0]
                logger.info(f"TimescaleDB extension available: {has_timescaledb}")
                
                return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def run_alembic_migration(self):
        """Run Alembic migrations on TimescaleDB"""
        logger.info("Running Alembic migrations...")
        try:
            # Convert postgres:// to postgresql:// if needed
            db_url = self.tiger_db_url
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            
            # Create Alembic config
            alembic_cfg = Config("alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", db_url)
            
            # Check current revision
            from alembic.script import ScriptDirectory
            from alembic.runtime.environment import EnvironmentContext
            from alembic.runtime.migration import MigrationContext
            
            script = ScriptDirectory.from_config(alembic_cfg)
            
            with self.engine.connect() as conn:
                context = MigrationContext.configure(conn)
                current_rev = context.get_current_revision()
                head_rev = script.get_current_head()
                
                logger.info(f"Current database revision: {current_rev}")
                logger.info(f"Latest migration revision: {head_rev}")
                
                if current_rev == head_rev:
                    logger.info("Database is already at the latest migration")
                    return True
                
                # Run migrations
                command.upgrade(alembic_cfg, "head")
                logger.info("Alembic migrations completed successfully")
                return True
        except Exception as e:
            logger.error(f"Alembic migration failed: {e}")
            return False
    
    def enable_timescaledb(self):
        """Enable TimescaleDB extension"""
        logger.info("Enabling TimescaleDB extension...")
        try:
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
                conn.commit()
                logger.info("TimescaleDB extension enabled")
                return True
        except Exception as e:
            logger.error(f"Failed to enable TimescaleDB: {e}")
            return False
    
    def create_hypertable(self):
        """Convert sensor_readings table to hypertable or optimize for time-series"""
        logger.info("Creating hypertable for sensor readings...")
        try:
            with self.engine.connect() as conn:
                # Check if table exists
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'api_sensor_readings'
                    );
                """))
                table_exists = result.fetchone()[0]
                
                if not table_exists:
                    logger.error("api_sensor_readings table does not exist")
                    return False
                
                # Check data before conversion
                result = conn.execute(text("SELECT COUNT(*) FROM api_sensor_readings;"))
                row_count = result.fetchone()[0]
                logger.info(f"Table api_sensor_readings has {row_count} rows")
                
                # First try Tiger Cloud syntax (for Time-series and analytics services)
                try:
                    logger.info("Testing Tiger Cloud hypertable capability...")
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS test_tiger_hypertable (
                            time TIMESTAMPTZ NOT NULL,
                            value DOUBLE PRECISION
                        ) WITH (
                            tsdb.hypertable,
                            tsdb.partition_column='time'
                        );
                    """))
                    conn.execute(text("DROP TABLE IF EXISTS test_tiger_hypertable;"))
                    conn.commit()
                    
                    logger.info("Tiger Cloud hypertable syntax is supported!")
                    logger.info("To convert existing table, you would need to recreate it with WITH clause")
                    logger.info("For now, trying traditional TimescaleDB approach...")
                    
                except Exception as tiger_error:
                    logger.info(f"Tiger Cloud syntax not available: {tiger_error}")
                
                # Try traditional TimescaleDB hypertable creation
                try:
                    conn.execute(text("""
                        SELECT create_hypertable(
                            'api_sensor_readings',
                            'timestamp',
                            chunk_time_interval => INTERVAL '1 day',
                            if_not_exists => TRUE
                        );
                    """))
                    conn.commit()
                    logger.info("Hypertable created successfully using traditional TimescaleDB")
                    
                    # Create optimized indexes
                    self.create_optimized_indexes(conn)
                    return True
                    
                except Exception as hypertable_error:
                    logger.warning(f"Cannot create hypertable: {hypertable_error}")
                    logger.info("This appears to be a PostgreSQL service without full TimescaleDB capabilities")
                    logger.info("Falling back to PostgreSQL time-series optimizations...")
                    
                    # Create time-series optimized indexes for regular PostgreSQL
                    self.create_postgresql_time_series_indexes(conn)
                    logger.info("PostgreSQL time-series optimizations applied")
                    return True
                
        except Exception as e:
            logger.error(f"Failed to optimize table: {e}")
            return False
    
    def create_postgresql_time_series_indexes(self, conn):
        """Create PostgreSQL optimized indexes for time-series data"""
        logger.info("Creating PostgreSQL time-series optimized indexes...")
        
        # Rollback any failed transaction first
        try:
            conn.rollback()
        except:
            pass
        
        indexes = [
            # Primary time-series index
            """
            CREATE INDEX IF NOT EXISTS idx_readings_timestamp_sensor 
            ON api_sensor_readings (timestamp DESC, sensor_id);
            """,
            # Sensor-specific time-series queries
            """
            CREATE INDEX IF NOT EXISTS idx_readings_sensor_timestamp_desc 
            ON api_sensor_readings (sensor_id, timestamp DESC);
            """,
            # Value-based queries with time filtering
            """
            CREATE INDEX IF NOT EXISTS idx_readings_timestamp_value 
            ON api_sensor_readings (timestamp, value) 
            WHERE value IS NOT NULL;
            """,
            # Recent data queries
            """
            CREATE INDEX IF NOT EXISTS idx_readings_received_at 
            ON api_sensor_readings (received_at DESC);
            """,
            # Composite index for aggregations (using immutable function)
            """
            CREATE INDEX IF NOT EXISTS idx_readings_timestamp_hour_sensor 
            ON api_sensor_readings (
                EXTRACT(HOUR FROM timestamp), 
                DATE_TRUNC('day', timestamp), 
                sensor_id
            );
            """,
            # Partial index for non-null values
            """
            CREATE INDEX IF NOT EXISTS idx_readings_sensor_value_timestamp 
            ON api_sensor_readings (sensor_id, value, timestamp) 
            WHERE value IS NOT NULL;
            """
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                conn.commit()
                logger.info("PostgreSQL time-series index created successfully")
            except Exception as e:
                logger.warning(f"Index creation failed (may already exist): {e}")
                try:
                    conn.rollback()
                except:
                    pass
        
        logger.info("All PostgreSQL time-series indexes created/verified")
    
    def create_optimized_indexes(self, conn):
        """Create TimescaleDB optimized indexes"""
        logger.info("Creating optimized indexes...")
        
        indexes = [
            """
            CREATE INDEX IF NOT EXISTS idx_readings_sensor_time_desc 
            ON api_sensor_readings (sensor_id, timestamp DESC);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_readings_time_value 
            ON api_sensor_readings (timestamp DESC, value) 
            WHERE value IS NOT NULL;
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_readings_sensor_received 
            ON api_sensor_readings (sensor_id, received_at DESC);
            """
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                logger.info("Index created successfully")
            except Exception as e:
                logger.warning(f"Index creation failed (may already exist): {e}")
        
        conn.commit()
    
    def validate_migration(self):
        """Validate the migration was successful"""
        logger.info("Validating migration...")
        try:
            with self.engine.begin() as conn:
                # Check tables exist
                result = conn.execute(text("""
                    SELECT table_name FROM information_schema.tables 
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
                
                logger.info(f"All tables present: {tables}")
                
            # Check hypertable separately to avoid transaction issues
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(text("""
                        SELECT hypertable_name, chunk_time_interval 
                        FROM timescaledb_information.hypertables 
                        WHERE hypertable_name = 'api_sensor_readings';
                    """))
                    hypertable_info = result.fetchone()
                    
                    if hypertable_info:
                        table_name, interval = hypertable_info
                        logger.info(f"Hypertable confirmed: {table_name} with interval {interval}")
                    else:
                        logger.info("No hypertable found - using regular PostgreSQL optimizations")
                        
            except Exception as e:
                logger.info(f"Hypertable check failed (expected for PostgreSQL service): {e}")
                logger.info("Database is optimized for time-series with PostgreSQL indexes")
            
            # Check indexes separately
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(text("""
                        SELECT indexname FROM pg_indexes 
                        WHERE tablename = 'api_sensor_readings' 
                        AND indexname LIKE 'idx_readings_%'
                        ORDER BY indexname;
                    """))
                    indexes = [row[0] for row in result.fetchall()]
                    logger.info(f"Time-series indexes: {len(indexes)} created")
                    for idx in indexes:
                        logger.info(f"  {idx}")
            except Exception as e:
                logger.warning(f"Index check failed: {e}")
                
            return True
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False
    
    def run_migration(self):
        """Execute the complete migration process"""
        logger.info("=" * 60)
        logger.info("STARTING TIMESCALEDB MIGRATION")
        logger.info("=" * 60)
        
        steps = [
            ("Testing connection", self.test_connection),
            ("Running Alembic migrations", self.run_alembic_migration),
            ("Enabling TimescaleDB", self.enable_timescaledb),
            ("Creating hypertable", self.create_hypertable),
            ("Validating migration", self.validate_migration)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n--- {step_name} ---")
            success = step_func()
            if not success:
                logger.error(f"Migration failed at step: {step_name}")
                return False
            logger.info(f"✅ {step_name} completed successfully")
        
        logger.info("=" * 60)
        logger.info("MIGRATION COMPLETED SUCCESSFULLY! 🎉")
        logger.info("=" * 60)
        logger.info("Next steps:")
        logger.info("1. Update DATABASE_URL to use TIGER_CLOUD_DATABASE_URL")
        logger.info("2. Run data import script for household data")
        logger.info("3. Test application with new database")
        
        return True

def main():
    """Main migration entry point"""
    try:
        migrator = TimescaleDBMigrator()
        success = migrator.run_migration()
        
        if success:
            print("\n🎉 Migration completed successfully!")
            print("Check migration.log for detailed logs.")
            sys.exit(0)
        else:
            print("\n❌ Migration failed!")
            print("Check migration.log for error details.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Migration script failed: {e}")
        print(f"\n❌ Migration script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()