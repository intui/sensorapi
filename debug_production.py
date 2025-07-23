#!/usr/bin/env python3
"""
Production Database Inspector - Debug tool for production API.
Allows you to inspect and debug the production database through the API.

Usage:
    python debug_production.py --list-all
    python debug_production.py --sensor-types
    python debug_production.py --locations
    python debug_production.py --sensors
    python debug_production.py --readings --sensor-id <id>
    python debug_production.py --create-test-data
    python debug_production.py --stats
"""

import httpx
import json
import uuid
import argparse
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


PRODUCTION_URL = "https://sensorapi-cpbpps2rw-widos-projects.vercel.app"


class ProductionDebugger:
    """Debug tool for production API."""
    
    def __init__(self, base_url: str = PRODUCTION_URL):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0)
    
    def graphql_query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a GraphQL query."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = self.client.post("/graphql", json=payload)
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        data = response.json()
        
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        
        return data["data"]
    
    def list_sensor_types(self) -> List[Dict]:
        """List all sensor types."""
        query = """
        query {
            sensorTypes {
                id
                name
                description
                unit
                dataType
                minValue
                maxValue
                isActive
                createdAt
            }
        }
        """
        
        data = self.graphql_query(query)
        return data["sensorTypes"]
    
    def list_locations(self) -> List[Dict]:
        """List all locations."""
        query = """
        query {
            locations {
                id
                name
                description
                city
                country
                latitude
                longitude
                isActive
                createdAt
            }
        }
        """
        
        data = self.graphql_query(query)
        return data["locations"]
    
    def list_sensors(self) -> List[Dict]:
        """List all sensors."""
        query = """
        query {
            sensors {
                id
                deviceId
                name
                description
                manufacturer
                model
                firmwareVersion
                hardwareVersion
                isActive
                isOnline
                lastSeen
                createdAt
            }
        }
        """
        
        data = self.graphql_query(query)
        return data["sensors"]
    
    def get_sensor_readings(self, sensor_id: str, limit: int = 50) -> List[Dict]:
        """Get readings for a specific sensor."""
        query = """
        query GetSensorReadings($sensorId: String!, $limit: Int) {
            sensorReadings(sensorId: $sensorId, limit: $limit) {
                id
                value
                rawValue
                timestamp
                receivedAt
            }
        }
        """
        
        data = self.graphql_query(query, {"sensorId": sensor_id, "limit": limit})
        return data["sensorReadings"]
    
    def create_test_sensor_type(self) -> Dict:
        """Create a test sensor type."""
        unique_id = uuid.uuid4().hex[:8]
        
        mutation = """
        mutation CreateSensorType($input: CreateSensorTypeInput!) {
            createSensorType(input: $input) {
                id
                name
                description
                unit
                dataType
                isActive
                createdAt
            }
        }
        """
        
        variables = {
            "input": {
                "name": f"Debug_TestSensor_{unique_id}",
                "description": "Debug test sensor created by production debugger",
                "unit": "debug_unit",
                "dataType": "float",
                "minValue": 0.0,
                "maxValue": 100.0
            }
        }
        
        data = self.graphql_query(mutation, variables)
        return data["createSensorType"]
    
    def create_test_location(self) -> Dict:
        """Create a test location."""
        unique_id = uuid.uuid4().hex[:8]
        
        mutation = """
        mutation CreateLocation($input: CreateLocationInput!) {
            createLocation(input: $input) {
                id
                name
                description
                city
                country
                latitude
                longitude
                isActive
                createdAt
            }
        }
        """
        
        variables = {
            "input": {
                "name": f"Debug_TestLocation_{unique_id}",
                "description": "Debug test location created by production debugger",
                "city": "Debug City",
                "country": "Debug Country",
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }
        
        data = self.graphql_query(mutation, variables)
        return data["createLocation"]
    
    def create_test_sensor(self, sensor_type_id: str, location_id: str) -> Dict:
        """Create a test sensor."""
        unique_id = uuid.uuid4().hex[:8]
        
        mutation = """
        mutation CreateSensor($input: CreateSensorInput!) {
            createSensor(input: $input) {
                id
                deviceId
                name
                description
                manufacturer
                model
                isActive
                createdAt
            }
        }
        """
        
        variables = {
            "input": {
                "sensorTypeId": sensor_type_id,
                "locationId": location_id,
                "deviceId": f"DEBUG_{unique_id}",
                "name": f"Debug_TestSensor_{unique_id}",
                "description": "Debug test sensor created by production debugger",
                "manufacturer": "Debug Manufacturer",
                "model": "Debug Model"
            }
        }
        
        data = self.graphql_query(mutation, variables)
        return data["createSensor"]
    
    def create_test_reading(self, sensor_id: str, value: float = 42.0) -> Dict:
        """Create a test sensor reading."""
        mutation = """
        mutation CreateSensorReading($input: CreateSensorReadingInput!) {
            createSensorReading(input: $input) {
                id
                value
                rawValue
                timestamp
                receivedAt
            }
        }
        """
        
        variables = {
            "input": {
                "sensorId": sensor_id,
                "value": value,
                "rawValue": str(value),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        data = self.graphql_query(mutation, variables)
        return data["createSensorReading"]
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        sensor_types = self.list_sensor_types()
        locations = self.list_locations()
        sensors = self.list_sensors()
        
        # Count readings for each sensor
        total_readings = 0
        for sensor in sensors:
            readings = self.get_sensor_readings(sensor["id"], limit=1000)
            total_readings += len(readings)
        
        return {
            "sensor_types": len(sensor_types),
            "locations": len(locations),
            "sensors": len(sensors),
            "sensor_readings": total_readings,
            "active_sensors": len([s for s in sensors if s["isActive"]]),
            "online_sensors": len([s for s in sensors if s["isOnline"]])
        }
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


def print_table(items: List[Dict], title: str, fields: List[str]):
    """Print a formatted table."""
    if not items:
        print(f"\n📋 {title}: No items found")
        return
    
    print(f"\n📋 {title} ({len(items)} items):")
    print("-" * 80)
    
    for i, item in enumerate(items, 1):
        print(f"{i}. {item.get('name', item.get('id', 'Unknown'))}")
        for field in fields:
            if field in item and item[field] is not None:
                print(f"   {field}: {item[field]}")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Debug production Sensor API database",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--url", default=PRODUCTION_URL, help="Production API URL")
    parser.add_argument("--list-all", action="store_true", help="List all entities")
    parser.add_argument("--sensor-types", action="store_true", help="List sensor types")
    parser.add_argument("--locations", action="store_true", help="List locations")
    parser.add_argument("--sensors", action="store_true", help="List sensors")
    parser.add_argument("--readings", action="store_true", help="List sensor readings")
    parser.add_argument("--sensor-id", help="Sensor ID for readings")
    parser.add_argument("--create-test-data", action="store_true", help="Create test data")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    
    args = parser.parse_args()
    
    if not any([args.list_all, args.sensor_types, args.locations, args.sensors, 
                args.readings, args.create_test_data, args.stats]):
        parser.print_help()
        return 1
    
    debugger = ProductionDebugger(args.url)
    
    try:
        print(f"🔍 Debugging production API: {args.url}")
        
        if args.stats or args.list_all:
            print("\n📊 Database Statistics:")
            stats = debugger.get_database_stats()
            for key, value in stats.items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
        
        if args.sensor_types or args.list_all:
            sensor_types = debugger.list_sensor_types()
            print_table(sensor_types, "Sensor Types", ["id", "unit", "dataType", "isActive"])
        
        if args.locations or args.list_all:
            locations = debugger.list_locations()
            print_table(locations, "Locations", ["id", "city", "country", "isActive"])
        
        if args.sensors or args.list_all:
            sensors = debugger.list_sensors()
            print_table(sensors, "Sensors", ["id", "deviceId", "manufacturer", "model", "isActive", "isOnline"])
        
        if args.readings:
            if not args.sensor_id:
                print("❌ --sensor-id required for readings")
                return 1
            
            readings = debugger.get_sensor_readings(args.sensor_id)
            print_table(readings, f"Sensor Readings for {args.sensor_id}", ["id", "value", "timestamp"])
        
        if args.create_test_data:
            print("\n🏗️  Creating test data...")
            
            # Create sensor type
            sensor_type = debugger.create_test_sensor_type()
            print(f"✅ Created sensor type: {sensor_type['name']} ({sensor_type['id']})")
            
            # Create location
            location = debugger.create_test_location()
            print(f"✅ Created location: {location['name']} ({location['id']})")
            
            # Create sensor
            sensor = debugger.create_test_sensor(sensor_type['id'], location['id'])
            print(f"✅ Created sensor: {sensor['name']} ({sensor['id']})")
            
            # Create some readings
            for i in range(3):
                reading = debugger.create_test_reading(sensor['id'], 20.0 + i * 5)
                print(f"✅ Created reading: {reading['value']} ({reading['id']})")
            
            print("\n🎉 Test data creation complete!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    finally:
        debugger.close()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
