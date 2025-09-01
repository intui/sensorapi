#!/usr/bin/env python3
"""
TimescaleDB Migration Script

This script migrates the sensor API from Aiven PostgreSQL to TimescaleDB on Tiger Cloud.
It handles:
1. Database connection testing
2. Schema migration via Alembic
3. TimescaleDB hypertable creation
4. Data validation

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
        # Use Tiger Cloud database URL
        self.tiger_db_url = os.getenv('TIGER_CLOUD_DATABASE_URL')
        if not self.tiger_db_url:
            raise ValueError("TIGER_CLOUD_DATABASE_URL not found in environment")
        
        self.engine = None
        self.session = None
        
    def test_connection(self):
        """Test connection to TimescaleDB"""
        logger.info("Testing connection to TimescaleDB...")
        try:
            self.engine = create_engine(self.tiger_db_url)
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
            # Create Alembic config
            alembic_cfg = Config("alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", self.tiger_db_url)
            
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
        """Convert sensor_readings table to hypertable"""
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
                
                # Check if already a hypertable
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT 1 FROM timescaledb_information.hypertables 
                        WHERE table_name = 'api_sensor_readings'
                    );
                """))
                is_hypertable = result.fetchone()[0]
                
                if is_hypertable:
                    logger.info("Table is already a hypertable")
                    return True
                
                # Create hypertable
                conn.execute(text("""
                    SELECT create_hypertable(
                        'api_sensor_readings',
                        'timestamp',
                        chunk_time_interval => INTERVAL '1 day',
                        if_not_exists => TRUE
                    );
                """))
                conn.commit()
                logger.info("Hypertable created successfully")
                
                # Create optimized indexes
                self.create_optimized_indexes(conn)
                
                return True
        except Exception as e:
            logger.error(f"Failed to create hypertable: {e}")
            return False
    
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
            with self.engine.connect() as conn:
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
                
                # Check hypertable status
                result = conn.execute(text("""
                    SELECT table_name, chunk_time_interval 
                    FROM timescaledb_information.hypertables 
                    WHERE table_name = 'api_sensor_readings';
                """))
                hypertable_info = result.fetchone()
                
                if hypertable_info:
                    logger.info(f"Hypertable confirmed: {hypertable_info[0]} with interval {hypertable_info[1]}")
                else:
                    logger.error("Hypertable not found")
                    return False
                
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