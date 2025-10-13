#!/usr/bin/env python3
"""
Manual script to delete a sensor and all its readings.
This bypasses the GraphQL layer and works directly with the database.

Usage:
    source .venv/bin/activate
    python scripts/delete_sensor_manual.py
"""

import sys
from sqlalchemy import text
from app.database.database import engine, get_db_session
from app.database.models import Sensor as SensorModel, SensorReading as SensorReadingModel

# The sensor ID to delete
SENSOR_ID = "21927b67-a067-420c-a887-3edac2efd520"
SENSOR_NAME = "tibber power"

def delete_sensor_and_readings():
    """Delete the sensor and all its readings."""
    
    print(f"🗑️  Attempting to delete sensor: {SENSOR_NAME}")
    print(f"   ID: {SENSOR_ID}")
    print("-" * 70)
    
    try:
        with get_db_session() as db:
            # Step 1: Check if sensor exists
            sensor = db.query(SensorModel).filter(SensorModel.id == SENSOR_ID).first()
            
            if not sensor:
                print(f"❌ Sensor with ID {SENSOR_ID} not found!")
                return False
            
            print(f"✅ Found sensor: {sensor.name}")
            print(f"   Type: {sensor.sensor_type.name if sensor.sensor_type else 'Unknown'}")
            print(f"   Location: {sensor.location.name if sensor.location else 'Unknown'}")
            print()
            
            # Step 2: Count readings before deletion
            readings_count = db.query(SensorReadingModel).filter(
                SensorReadingModel.sensor_id == SENSOR_ID
            ).count()
            
            print(f"📊 Found {readings_count:,} readings associated with this sensor")
            print()
            
            # Step 3: Clear latest_reading_id FIRST to avoid foreign key constraint
            print("� Clearing latest_reading_id reference on the sensor...")
            db.execute(
                text("UPDATE api_sensors SET latest_reading_id = NULL WHERE id = :sensor_id"),
                {"sensor_id": SENSOR_ID}
            )
            print("✅ Cleared sensor's latest_reading_id reference")
            print()
            
            # Step 4: Delete all sensor readings
            print("�️  Deleting sensor readings...")
            deleted_readings = db.query(SensorReadingModel).filter(
                SensorReadingModel.sensor_id == SENSOR_ID
            ).delete(synchronize_session=False)
            
            print(f"✅ Deleted {deleted_readings:,} sensor readings")
            print()
            
            # Step 5: Delete the sensor itself
            print("🗑️  Deleting sensor...")
            db.delete(sensor)
            
            # Step 6: Commit all changes
            db.commit()
            
            print("✅ Successfully deleted sensor and all associated readings!")
            print()
            print("=" * 70)
            print("DELETION SUMMARY:")
            print(f"  Sensor ID: {SENSOR_ID}")
            print(f"  Sensor Name: {SENSOR_NAME}")
            print(f"  Readings Deleted: {deleted_readings:,}")
            print("=" * 70)
            print()
            print("💡 Note: Space will be reclaimed by PostgreSQL AUTOVACUUM")
            print("   Run 'VACUUM ANALYZE api_sensor_readings;' to speed up reclamation")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("Possible issues:")
        print("  - Database connection failed")
        print("  - Foreign key constraints")
        print("  - Insufficient permissions")
        import traceback
        traceback.print_exc()
        return False


def vacuum_tables():
    """Run VACUUM ANALYZE to reclaim space."""
    print()
    print("🧹 Running VACUUM ANALYZE to reclaim space...")
    
    try:
        # Need to use autocommit for VACUUM
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text("VACUUM ANALYZE api_sensor_readings"))
            conn.execute(text("VACUUM ANALYZE api_sensors"))
        
        print("✅ VACUUM completed successfully!")
        print("   Dead tuples have been marked for reuse")
        
    except Exception as e:
        print(f"⚠️  VACUUM failed (non-critical): {str(e)}")
        print("   AUTOVACUUM will handle it automatically")


if __name__ == "__main__":
    print()
    print("=" * 70)
    print("MANUAL SENSOR DELETION SCRIPT")
    print("=" * 70)
    print()
    
    success = delete_sensor_and_readings()
    
    if success:
        # Try to vacuum, but don't fail if it doesn't work
        try:
            vacuum_tables()
        except:
            pass
        
        print()
        print("✨ Done!")
        sys.exit(0)
    else:
        print()
        print("❌ Deletion failed!")
        sys.exit(1)
