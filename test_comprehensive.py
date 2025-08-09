#!/usr/bin/env python3
"""
Simple test script to verify sensor status tracking functionality.
"""
import sys
import os
from datetime import datetime
from uuid import UUID

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.database import get_db_session
from app.database.models import Sensor, SensorReading
from app.graphql.types import CreateSensorReadingInput

def test_basic_functionality():
    """Test basic sensor status functionality."""
    
    print("🔍 Testing basic sensor status functionality...")
    
    with get_db_session() as db:
        # Get a sensor
        sensor = db.query(Sensor).first()
        if not sensor:
            print("❌ No sensors found. Please run setup_test_data.py first.")
            return False
        
        print(f"📍 Testing with sensor: {sensor.name}")
        print(f"   Device ID: {sensor.device_id}")
        print(f"   Initial status: Active={sensor.is_active}, Online={sensor.is_online}")
        print(f"   Latest reading ID: {sensor.latest_reading_id}")
        
        # Reset sensor status for testing
        sensor.is_active = False
        sensor.is_online = False
        sensor.last_seen = None
        sensor.latest_reading_id = None
        db.commit()
        
        print(f"   Reset status: Active={sensor.is_active}, Online={sensor.is_online}")
        
        # Create a sensor reading manually
        print("\n📊 Creating sensor reading manually...")
        
        new_reading = SensorReading(
            sensor_id=sensor.id,
            value=24.5,
            raw_value=24.3,
            timestamp=datetime.utcnow()
        )
        db.add(new_reading)
        db.flush()  # Get the ID
        
        print(f"✅ Created reading: ID={new_reading.id}, Value={new_reading.value}")
        
        # Now manually update sensor status (simulating what our GraphQL resolver should do)
        print("\n🔄 Updating sensor status...")
        
        sensor.is_active = True
        sensor.is_online = True
        sensor.last_seen = new_reading.timestamp
        sensor.latest_reading_id = new_reading.id
        db.commit()
        
        print(f"✅ Updated sensor status:")
        print(f"   Active: {sensor.is_active}")
        print(f"   Online: {sensor.is_online}")
        print(f"   Last seen: {sensor.last_seen}")
        print(f"   Latest reading ID: {sensor.latest_reading_id}")
        
        # Test the relationship
        print("\n🔗 Testing latest reading relationship...")
        try:
            db.refresh(sensor)
            if sensor.latest_reading:
                print(f"✅ Latest reading accessible: Value={sensor.latest_reading.value}")
            else:
                print("❌ Latest reading relationship not working")
                return False
        except Exception as e:
            print(f"❌ Error accessing latest reading: {e}")
            return False
        
        print("\n🎉 Basic functionality test passed!")
        return True

def test_graphql_resolver():
    """Test the GraphQL resolver functionality."""
    
    print("\n🚀 Testing GraphQL resolver...")
    
    try:
        from app.graphql.resolvers import Mutation
        from app.graphql.types import CreateSensorReadingInput
        
        with get_db_session() as db:
            sensor = db.query(Sensor).first()
            if not sensor:
                print("❌ No sensors found.")
                return False
            
            # Reset sensor for test
            sensor.is_active = False
            sensor.is_online = False
            sensor.last_seen = None
            db.commit()
            
            print(f"📍 Using sensor: {sensor.name} (ID: {sensor.id})")
            print(f"   Reset status: Active={sensor.is_active}, Online={sensor.is_online}")
            
            # Create input
            reading_input = CreateSensorReadingInput(
                sensor_id=str(sensor.id),
                value=26.7,
                raw_value=26.5,
                timestamp=datetime.utcnow()
            )
            
            print(f"📊 Creating reading via GraphQL resolver...")
            print(f"   Input: sensor_id={reading_input.sensor_id}, value={reading_input.value}")
            
            # Call the resolver through Mutation class
            mutation = Mutation()
            new_reading = mutation.create_sensor_reading(None, reading_input)
            
            print(f"✅ Reading created: ID={new_reading.id}")
            
            # Check if sensor was updated (get fresh instance)
            with get_db_session() as db2:
                updated_sensor = db2.query(Sensor).filter(Sensor.id == sensor.id).first()
                print(f"📋 Sensor status after GraphQL resolver:")
                print(f"   Active: {updated_sensor.is_active}")
                print(f"   Online: {updated_sensor.is_online}")
                print(f"   Last seen: {updated_sensor.last_seen}")
                print(f"   Latest reading ID: {updated_sensor.latest_reading_id}")
                
                # Verify updates
                if (updated_sensor.is_active and updated_sensor.is_online and 
                    updated_sensor.last_seen is not None and 
                    str(updated_sensor.latest_reading_id) == new_reading.id):
                    print("✅ GraphQL resolver working correctly!")
                    return True
                else:
                    print("❌ GraphQL resolver not updating sensor status properly")
                    print(f"   Expected latest_reading_id: {new_reading.id}")
                    print(f"   Actual latest_reading_id: {updated_sensor.latest_reading_id}")
                    return False
                
    except Exception as e:
        print(f"❌ Error testing GraphQL resolver: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Sensor Status Tracking Test Suite")
    print("=" * 50)
    
    success1 = test_basic_functionality()
    success2 = test_graphql_resolver()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! Sensor status tracking is working.")
    else:
        print("❌ Some tests failed. Check the output above.")
