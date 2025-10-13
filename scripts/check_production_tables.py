#!/usr/bin/env python3
"""
Script to check if production database has all required tables.
Run this before deploying to Vercel to ensure migrations are applied.

Usage:
    # Set your production database URL
    export DATABASE_URL="postgresql://user:pass@host:port/database"
    
    # Run the script
    python scripts/check_production_tables.py
"""

import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import NullPool

# Required tables for the sensor API
REQUIRED_TABLES = [
    'sensor_types',
    'locations',
    'sensors',
    'sensor_readings',
    'alerts',
    'alembic_version',  # Migration tracking table
]

def check_database_tables():
    """Check if all required tables exist in the production database."""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("\nSet it like this:")
        print('export DATABASE_URL="postgresql://user:pass@host:port/database"')
        return False
    
    print(f"🔍 Checking database: {database_url.split('@')[1] if '@' in database_url else 'unknown'}")
    print("-" * 70)
    
    try:
        # Create engine with NullPool for one-time connection
        engine = create_engine(database_url, poolclass=NullPool)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful")
            print(f"   PostgreSQL version: {version.split(',')[0]}")
            print()
        
        # Get inspector to check schema
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"📊 Found {len(existing_tables)} tables in database:")
        for table in sorted(existing_tables):
            print(f"   - {table}")
        print()
        
        # Check for required tables
        missing_tables = set(REQUIRED_TABLES) - set(existing_tables)
        
        if missing_tables:
            print("❌ MISSING REQUIRED TABLES:")
            for table in sorted(missing_tables):
                print(f"   - {table}")
            print()
            print("⚠️  You need to run migrations:")
            print("   alembic upgrade head")
            return False
        
        print("✅ All required tables exist!")
        print()
        
        # Check alembic version
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()
            if version:
                print(f"📌 Current migration version: {version[0]}")
            else:
                print("⚠️  No migration version found (alembic_version table is empty)")
        
        # Check table row counts
        print()
        print("📈 Table row counts:")
        with engine.connect() as conn:
            for table in sorted(existing_tables):
                if table != 'alembic_version':
                    try:
                        result = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                        count = result.fetchone()[0]
                        print(f"   {table:20} {count:>8} rows")
                    except Exception as e:
                        print(f"   {table:20} ERROR: {str(e)}")
        
        print()
        print("=" * 70)
        print("✅ DATABASE IS READY FOR VERCEL DEPLOYMENT")
        print("=" * 70)
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("Possible issues:")
        print("  - Database connection string is incorrect")
        print("  - Database server is not accessible")
        print("  - Firewall is blocking the connection")
        print("  - Database credentials are invalid")
        return False


if __name__ == "__main__":
    success = check_database_tables()
    sys.exit(0 if success else 1)
