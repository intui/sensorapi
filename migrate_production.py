#!/usr/bin/env python3
"""
Production database migration script.
This script connects to the production database and runs Alembic migrations.
"""

import os
import sys
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text

def run_production_migration():
    """Run Alembic migration on production database."""
    
    # Get the production database URL
    # This should be set via Vercel environment variables
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not found.")
        print("Make sure you have the production database URL set.")
        sys.exit(1)
    
    print(f"🔍 Production database URL: {database_url[:50]}...")
    
    try:
        # Test database connection first
        print("🔗 Testing database connection...")
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Check current migration status
        print("\n📋 Checking current migration status...")
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        try:
            # Show current revision
            command.current(alembic_cfg, verbose=True)
        except Exception as e:
            print(f"⚠️ Could not get current revision: {e}")
            print("This might be the first time running migrations on this database.")
        
        # Run migrations
        print("\n🚀 Running Alembic migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully!")
        
        # Verify the column exists now
        print("\n🔍 Verifying latest_reading_id column...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'api_sensors' 
                AND column_name = 'latest_reading_id'
            """))
            
            if result.fetchone():
                print("✅ latest_reading_id column exists in production database!")
            else:
                print("❌ latest_reading_id column still not found!")
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("🏭 Production Database Migration")
    print("=" * 50)
    run_production_migration()
