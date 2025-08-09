#!/usr/bin/env python3
"""
Test GraphQL functionality by running actual GraphQL queries.
"""
import sys
import os
import asyncio
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import strawberry
from strawberry.fastapi import GraphQLRouter

from app.graphql.resolvers import Query, Mutation
from app.database.database import get_db_session
from app.database.models import Sensor
from app.graphql.types import CreateSensorReadingInput

def test_graphql_schema():
    """Test GraphQL queries using the actual schema."""
    
    print("🔍 Testing GraphQL schema functionality...")
    
    # Create the schema
    schema = strawberry.Schema(query=Query, mutation=Mutation)
    
    # Test query: get sensors with latestReading
    sensors_query = """
    query GetSensors {
        sensors {
            id
            name
            deviceId
            isActive
            isOnline
            lastSeen
            latestReading {
                id
                value
                timestamp
            }
        }
    }
    """
    
    print("📊 Executing sensors query with latestReading field...")
    try:
        result = schema.execute_sync(sensors_query)
        
        if result.errors:
            print("❌ GraphQL errors:", result.errors)
            return False
        
        sensors = result.data['sensors']
        print(f"✅ Found {len(sensors)} sensors")
        
        for sensor in sensors:
            print(f"   📍 Sensor: {sensor['name']} (ID: {sensor['id']})")
            print(f"      Active: {sensor['isActive']}, Online: {sensor['isOnline']}")
            print(f"      Last Seen: {sensor['lastSeen']}")
            
            if sensor['latestReading']:
                latest = sensor['latestReading']
                print(f"      ✅ Latest Reading: ID={latest['id']}, Value={latest['value']}, Time={latest['timestamp']}")
            else:
                print(f"      ⚠️  No latest reading found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error executing GraphQL query: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_create_sensor_reading_mutation():
    """Test the createSensorReading mutation."""
    
    print("\n🔄 Testing createSensorReading mutation...")
    
    # Get a sensor ID
    with get_db_session() as db:
        sensor = db.query(Sensor).first()
        if not sensor:
            print("❌ No sensors found for testing")
            return False
        
        sensor_id = str(sensor.id)
        print(f"📍 Using sensor: {sensor.name} (ID: {sensor_id})")
        
        # Reset sensor status for clean test
        sensor.is_active = False
        sensor.is_online = False
        sensor.last_seen = None
        db.commit()
        print("   Reset sensor to inactive/offline")
    
    # Create the schema
    schema = strawberry.Schema(query=Query, mutation=Mutation)
    
    # Test mutation
    mutation_query = f"""
    mutation CreateReading {{
        createSensorReading(input: {{
            sensorId: "{sensor_id}"
            value: 28.5
            rawValue: 28.3
            timestamp: "{datetime.utcnow().isoformat()}Z"
        }}) {{
            id
            value
            timestamp
            sensorId
        }}
    }}
    """
    
    print("📊 Executing createSensorReading mutation...")
    try:
        result = schema.execute_sync(mutation_query)
        
        if result.errors:
            print("❌ GraphQL mutation errors:", result.errors)
            return False
        
        reading = result.data['createSensorReading']
        print(f"✅ Created reading: ID={reading['id']}, Value={reading['value']}")
        
        # Check if sensor status was updated
        with get_db_session() as db:
            updated_sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
            print(f"📋 Sensor status after mutation:")
            print(f"   Active: {updated_sensor.is_active}")
            print(f"   Online: {updated_sensor.is_online}")
            print(f"   Last Seen: {updated_sensor.last_seen}")
            print(f"   Latest Reading ID: {updated_sensor.latest_reading_id}")
            
            if (updated_sensor.is_active and updated_sensor.is_online and 
                updated_sensor.last_seen is not None and 
                str(updated_sensor.latest_reading_id) == reading['id']):
                print("✅ Sensor status correctly updated by mutation!")
                return True
            else:
                print("❌ Sensor status not properly updated")
                return False
        
    except Exception as e:
        print(f"❌ Error executing GraphQL mutation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 GraphQL Schema Integration Test")
    print("=" * 50)
    
    success1 = test_graphql_schema()
    success2 = test_create_sensor_reading_mutation()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All GraphQL schema tests passed!")
        print("✅ PRD features are working correctly through GraphQL!")
    else:
        print("❌ Some GraphQL schema tests failed.")
