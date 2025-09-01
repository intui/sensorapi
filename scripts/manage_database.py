#!/usr/bin/env python3
"""
Database Management Script

This script provides easy commands to switch between databases and manage configurations.

Usage:
    python scripts/manage_database.py switch aiven|tiger_cloud
    python scripts/manage_database.py status
    python scripts/manage_database.py test-connection
    python scripts/manage_database.py info
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv, set_key, get_key

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

from sqlalchemy import create_engine, text
from app.core.config import settings

class DatabaseManager:
    def __init__(self):
        self.env_file = project_root / ".env"
        
    def switch_database(self, provider: str):
        """Switch the active database provider."""
        if provider not in ["aiven", "tiger_cloud"]:
            print(f"❌ Invalid provider: {provider}. Use 'aiven' or 'tiger_cloud'")
            return False
            
        # Update the .env file
        set_key(self.env_file, "DATABASE_PROVIDER", provider)
        print(f"✅ Switched DATABASE_PROVIDER to: {provider}")
        
        # Reload settings
        os.environ["DATABASE_PROVIDER"] = provider
        
        return True
    
    def get_status(self):
        """Get current database configuration status."""
        current_provider = get_key(self.env_file, "DATABASE_PROVIDER") or "aiven"
        
        print("=" * 60)
        print("DATABASE CONFIGURATION STATUS")
        print("=" * 60)
        print(f"Current Provider: {current_provider}")
        
        # Check Aiven database configuration
        aiven_url = get_key(self.env_file, "DATABASE_URL")
        print(f"Aiven DATABASE_URL: {'✅ Configured' if aiven_url else '❌ Not configured'}")
        
        # Check Tiger Cloud configuration  
        tiger_url = get_key(self.env_file, "TIGER_CLOUD_DATABASE_URL")
        print(f"Tiger Cloud URL: {'✅ Configured' if tiger_url else '❌ Not configured'}")
        
        print("\nActive Configuration:")
        try:
            # Import fresh settings
            from importlib import reload
            from app.core import config
            reload(config)
            active_settings = config.Settings()
            
            print(f"  Provider: {active_settings.DATABASE_PROVIDER}")
            print(f"  Active URL: {active_settings.active_database_url[:50]}...")
            print(f"  Is Tiger Cloud: {active_settings.database_info['is_tiger_cloud']}")
            print(f"  Supports TimescaleDB: {active_settings.database_info['supports_timescaledb']}")
            
        except Exception as e:
            print(f"  ❌ Error loading settings: {e}")
    
    def test_connection(self):
        """Test connection to the currently active database."""
        try:
            # Import fresh settings
            from importlib import reload
            from app.core import config
            reload(config)
            active_settings = config.Settings()
            
            print(f"Testing connection to: {active_settings.DATABASE_PROVIDER}")
            print(f"URL: {active_settings.active_database_url[:50]}...")
            
            engine = create_engine(active_settings.active_database_url)
            
            with engine.connect() as conn:
                # Test basic connectivity
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"✅ Connection successful!")
                print(f"Database version: {version}")
                
                # Check for TimescaleDB extension
                try:
                    result = conn.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';"))
                    timescale_version = result.fetchone()
                    if timescale_version:
                        print(f"🚀 TimescaleDB extension: v{timescale_version[0]}")
                    else:
                        print("📊 No TimescaleDB extension found")
                except:
                    print("📊 TimescaleDB check not applicable")
                
                # Check table count
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name LIKE 'api_%'
                """))
                table_count = result.fetchone()[0]
                print(f"📋 API tables found: {table_count}")
                
                # Check sensor readings count
                try:
                    result = conn.execute(text("SELECT COUNT(*) FROM api_sensor_readings;"))
                    reading_count = result.fetchone()[0]
                    print(f"📈 Sensor readings: {reading_count:,}")
                except:
                    print("📈 Sensor readings table not accessible")
                    
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
            
        return True
    
    def show_info(self):
        """Show detailed database information."""
        print("=" * 60)
        print("DATABASE CONFIGURATION GUIDE")
        print("=" * 60)
        print()
        print("Available Commands:")
        print("  switch aiven       - Use Aiven database (DATABASE_URL)")
        print("  switch tiger_cloud - Use Tiger Cloud database (TIGER_CLOUD_DATABASE_URL)")
        print("  status            - Show current configuration")
        print("  test-connection   - Test connection to active database")
        print("  info              - Show this help")
        print()
        print("Environment Variables:")
        print("  DATABASE_PROVIDER      - 'aiven' or 'tiger_cloud'")
        print("  DATABASE_URL           - Aiven PostgreSQL connection string")
        print("  TIGER_CLOUD_DATABASE_URL - Tiger Cloud connection string")
        print()
        print("Examples:")
        print("  # Switch to Tiger Cloud")
        print("  python scripts/manage_database.py switch tiger_cloud")
        print()
        print("  # Switch back to Aiven")
        print("  python scripts/manage_database.py switch aiven")
        print()
        print("  # Check current status")
        print("  python scripts/manage_database.py status")

def main():
    parser = argparse.ArgumentParser(description="Database Management Tool")
    parser.add_argument("command", choices=["switch", "status", "test-connection", "info"],
                       help="Command to execute")
    parser.add_argument("provider", nargs="?", choices=["aiven", "tiger_cloud"],
                       help="Database provider (required for 'switch' command)")
    
    args = parser.parse_args()
    
    manager = DatabaseManager()
    
    if args.command == "switch":
        if not args.provider:
            print("❌ Provider required for 'switch' command. Use 'aiven' or 'tiger_cloud'")
            sys.exit(1)
        success = manager.switch_database(args.provider)
        if success:
            print("\n🔄 Restart your application to use the new database configuration.")
    
    elif args.command == "status":
        manager.get_status()
    
    elif args.command == "test-connection":
        success = manager.test_connection()
        if not success:
            sys.exit(1)
    
    elif args.command == "info":
        manager.show_info()

if __name__ == "__main__":
    main()