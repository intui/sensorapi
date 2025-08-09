#!/usr/bin/env python3
"""
Test script for new sensor status update features.
This script tests the automatic sensor status updates when creating readings.
"""

import asyncio
from datetime import datetime
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.database import get_db_session
from app.database.models import Sensor as SensorModel, SensorReading as SensorReadingModel
from app.graphql.resolvers import Mutation
from app.graphql.types import CreateSensorReadingInput


async def test_sensor_status_updates():
    """Test automatic sensor status updates when creating readings."""
    
    print("Testing automatic sensor status updates...")
    
    # Create mutation instance
    mutation = Mutation()
    
    # Find a sensor to test with
    with get_db_session() as db:
        sensor = db.query(SensorModel).first()
        if not sensor:
            print("No sensors found in database. Please create a sensor first.")
            return
        
        print(f"Testing with sensor: {sensor.name} (ID: {sensor.id})")
        print(f"Initial status - Active: {sensor.is_active}, Online: {sensor.is_online}, Last Seen: {sensor.last_seen}")
        
        # Set sensor to inactive and offline for testing
        sensor.is_active = False
        sensor.is_online = False
        sensor.last_seen = None
        sensor.latest_reading_id = None
        db.commit()
        print("Set sensor to inactive/offline for testing")
    
    # Create a new sensor reading using the mutation
    reading_input = CreateSensorReadingInput(
        sensor_id=str(sensor.id),
        value=25.5,
        raw_value=25.3,
        timestamp=datetime.utcnow()
    )
    
    try:
        # This should automatically update sensor status
        new_reading = mutation.create_sensor_reading(None, reading_input)
        print(f"Created new reading with value: {new_reading.value}")
        
        # Check updated sensor status
        with get_db_session() as db:
            updated_sensor = db.query(SensorModel).filter(SensorModel.id == sensor.id).first()
            print(f"Updated status - Active: {updated_sensor.is_active}, Online: {updated_sensor.is_online}")
            print(f"Last Seen: {updated_sensor.last_seen}")
            print(f"Latest Reading ID: {updated_sensor.latest_reading_id}")
            
            # Verify the status was updated correctly
            assert updated_sensor.is_active == True, "Sensor should be activated after receiving reading"
            assert updated_sensor.is_online == True, "Sensor should be online after receiving reading"
            assert updated_sensor.last_seen is not None, "Last seen should be set"
            assert updated_sensor.latest_reading_id is not None, "Latest reading ID should be set"
            
            print("✅ All status updates working correctly!")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_sensor_status_updates())
