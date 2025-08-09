#!/usr/bin/env python3
"""
Test the GraphQL field resolvers, particularly the latestReading field.
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.database import get_db_session
from app.database.models import Sensor, SensorReading
from app.graphql.types import Sensor as SensorType

def test_latest_reading_resolver():
    """Test the latestReading field resolver."""
    
    print("🔍 Testing latestReading GraphQL field resolver...")
    
    with get_db_session() as db:
        # Get a sensor with readings
        sensor = db.query(Sensor).first()
        if not sensor:
            print("❌ No sensors found.")
            return False
        
        print(f"📍 Testing with sensor: {sensor.name}")
        print(f"   Latest reading ID in DB: {sensor.latest_reading_id}")
        
        # Convert to GraphQL type
        sensor_gql = SensorType.from_model(sensor)
        
        print(f"📊 GraphQL Sensor object created")
        print(f"   ID: {sensor_gql.id}")
        print(f"   Name: {sensor_gql.name}")
        print(f"   Active: {sensor_gql.is_active}")
        print(f"   Online: {sensor_gql.is_online}")
        print(f"   Last Seen: {sensor_gql.last_seen}")
        
        # Test the latest_reading resolver
        print("\n🔗 Testing latest_reading field resolver...")
        try:
            # This should call the resolver we implemented
            latest_reading_gql = sensor_gql.latest_reading
            
            if latest_reading_gql:
                print(f"✅ Latest reading resolver working:")
                print(f"   Reading ID: {latest_reading_gql.id}")
                print(f"   Value: {latest_reading_gql.value}")
                print(f"   Timestamp: {latest_reading_gql.timestamp}")
                return True
            else:
                print("❌ Latest reading resolver returned None")
                return False
                
        except Exception as e:
            print(f"❌ Error in latest reading resolver: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_sensors_query():
    """Test the sensors query with all filters."""
    
    print("\n🔍 Testing sensors GraphQL query...")
    
    try:
        from app.graphql.resolvers import Query
        
        query = Query()
        
        # Test basic sensors query
        print("📊 Testing sensors query with no filters...")
        sensors = query.sensors(None)
        
        print(f"✅ Found {len(sensors)} sensors")
        for sensor in sensors:
            print(f"   - {sensor.name}: Active={sensor.is_active}, Online={sensor.is_online}")
        
        # Test with filters
        print("\n📊 Testing sensors query with activeOnly=True...")
        active_sensors = query.sensors(None, active_only=True)
        print(f"✅ Found {len(active_sensors)} active sensors")
        
        print("\n📊 Testing sensors query with onlineOnly=True...")
        online_sensors = query.sensors(None, online_only=True)
        print(f"✅ Found {len(online_sensors)} online sensors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing sensors query: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 GraphQL Field Resolver Test Suite")
    print("=" * 50)
    
    success1 = test_latest_reading_resolver()
    success2 = test_sensors_query()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All GraphQL resolver tests passed!")
    else:
        print("❌ Some GraphQL resolver tests failed.")
