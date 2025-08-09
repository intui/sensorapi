#!/usr/bin/env python3
"""
Setup test data for sensor status tracking testing.
"""
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import SensorType, Location, Sensor
from app.core.config import settings

def setup_test_data():
    """Create basic test data for testing sensor functionality."""
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Create sensor type
        sensor_type = SensorType(
            name="Temperature",
            description="Temperature sensor",
            unit="°C",
            min_value=-50.0,
            max_value=100.0
        )
        db.add(sensor_type)
        db.flush()
        
        # Create location
        location = Location(
            name="Test Building",
            description="Main test building",
            latitude=40.7128,
            longitude=-74.0060
        )
        db.add(location)
        db.flush()
        
        # Create sensor
        sensor = Sensor(
            device_id="TEST-SENSOR-001",
            name="Test Temperature Sensor",
            description="Temperature sensor for testing",
            sensor_type_id=sensor_type.id,
            location_id=location.id,
            manufacturer="TestCorp",
            model="TempSens-100",
            firmware_version="1.0.0",
            is_active=True,
            is_online=False  # Start as offline
        )
        db.add(sensor)
        db.commit()
        
        print(f"✅ Created test data:")
        print(f"   - Sensor Type: {sensor_type.name} (ID: {sensor_type.id})")
        print(f"   - Location: {location.name} (ID: {location.id})")
        print(f"   - Sensor: {sensor.name} (ID: {sensor.id})")
        print(f"   - Device ID: {sensor.device_id}")
        print(f"   - Initial status: is_active={sensor.is_active}, is_online={sensor.is_online}")
        
        return sensor.id
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    sensor_id = setup_test_data()
    print(f"\n🚀 Test data ready! Sensor ID: {sensor_id}")
