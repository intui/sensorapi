"""
Sample data creation script for the Sensor API.
This script creates some basic sensor types, locations, sensors, and sample readings.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine, Base
from app.database.models import SensorType, Location, Sensor, SensorReading
from app.core.config import settings

def create_sample_data():
    """Create sample data for testing the API."""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create sensor types
        sensor_types = [
            SensorType(
                name="Temperature",
                description="Temperature sensor measuring in Celsius",
                unit="°C",
                data_type="float",
                min_value=-40.0,
                max_value=85.0
            ),
            SensorType(
                name="Humidity",
                description="Relative humidity sensor",
                unit="%RH",
                data_type="float",
                min_value=0.0,
                max_value=100.0
            ),
            SensorType(
                name="Pressure",
                description="Atmospheric pressure sensor",
                unit="hPa",
                data_type="float",
                min_value=800.0,
                max_value=1100.0
            ),
            SensorType(
                name="Air Quality",
                description="Air quality index sensor",
                unit="AQI",
                data_type="integer",
                min_value=0,
                max_value=500
            ),
            SensorType(
                name="Light Level",
                description="Ambient light sensor",
                unit="lux",
                data_type="float",
                min_value=0.0,
                max_value=100000.0
            )
        ]
        
        for sensor_type in sensor_types:
            db.add(sensor_type)
        
        db.commit()
        print("✓ Created sensor types")
        
        # Create locations
        building = Location(
            name="Main Office Building",
            description="Primary office building",
            address="123 Technology Street",
            city="Helsinki",
            country="Finland",
            postal_code="00100",
            latitude=60.1699,
            longitude=24.9384
        )
        db.add(building)
        db.commit()
        
        # Create floors
        floors = []
        for i in range(1, 4):  # 3 floors
            floor = Location(
                name=f"Floor {i}",
                description=f"Floor {i} of the main building",
                parent_id=building.id
            )
            db.add(floor)
            floors.append(floor)
        
        db.commit()
        
        # Create rooms
        rooms = []
        room_names = ["Conference Room A", "Open Office", "Server Room", "Break Room", "Reception"]
        
        for floor in floors:
            for room_name in room_names:
                room = Location(
                    name=f"{room_name} - {floor.name}",
                    description=f"{room_name} located on {floor.name}",
                    parent_id=floor.id
                )
                db.add(room)
                rooms.append(room)
        
        db.commit()
        print("✓ Created locations (building, floors, rooms)")
        
        # Create sensors
        sensors = []
        manufacturers = ["SensorTech", "IoT Solutions", "SmartSense", "TechCorp"]
        models = ["ST-100", "IOT-200", "SS-300", "TC-400"]
        
        # Get sensor types from database
        temp_type = db.query(SensorType).filter(SensorType.name == "Temperature").first()
        humidity_type = db.query(SensorType).filter(SensorType.name == "Humidity").first()
        pressure_type = db.query(SensorType).filter(SensorType.name == "Pressure").first()
        air_quality_type = db.query(SensorType).filter(SensorType.name == "Air Quality").first()
        light_type = db.query(SensorType).filter(SensorType.name == "Light Level").first()
        
        sensor_configs = [
            (temp_type, "TEMP", "Temperature"),
            (humidity_type, "HUM", "Humidity"),
            (pressure_type, "PRES", "Pressure"),
            (air_quality_type, "AQ", "Air Quality"),
            (light_type, "LIGHT", "Light")
        ]
        
        device_counter = 1
        for room in rooms[:10]:  # Create sensors for first 10 rooms
            for sensor_type, prefix, name in sensor_configs:
                sensor = Sensor(
                    device_id=f"{prefix}{device_counter:03d}",
                    name=f"{name} Sensor - {room.name}",
                    description=f"{name} monitoring for {room.name}",
                    sensor_type_id=sensor_type.id,
                    location_id=room.id,
                    manufacturer=random.choice(manufacturers),
                    model=random.choice(models),
                    firmware_version=f"v{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}",
                    sampling_interval=300,  # 5 minutes
                    is_active=True,
                    is_online=True,
                    last_seen=datetime.utcnow()
                )
                db.add(sensor)
                sensors.append(sensor)
                device_counter += 1
        
        db.commit()
        print(f"✓ Created {len(sensors)} sensors")
        
        # Create sample readings for the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        readings_count = 0
        for sensor in sensors:
            current_time = start_time
            
            # Base values for different sensor types
            base_values = {
                "Temperature": 22.0,  # °C
                "Humidity": 45.0,     # %RH
                "Pressure": 1013.25,  # hPa
                "Air Quality": 50,    # AQI
                "Light Level": 300.0  # lux
            }
            
            # Variation ranges
            variations = {
                "Temperature": 5.0,
                "Humidity": 15.0,
                "Pressure": 20.0,
                "Air Quality": 30,
                "Light Level": 200.0
            }
            
            sensor_type_name = sensor.sensor_type.name
            base_value = base_values.get(sensor_type_name, 0.0)
            variation = variations.get(sensor_type_name, 1.0)
            
            # Generate readings every 5 minutes
            while current_time <= end_time:
                # Add some random variation and daily patterns
                hour = current_time.hour
                
                # Daily patterns
                if sensor_type_name == "Temperature":
                    # Temperature varies throughout the day
                    daily_factor = 2 * (0.5 - abs(hour - 12) / 24)
                    value = base_value + daily_factor + random.uniform(-variation/2, variation/2)
                elif sensor_type_name == "Light Level":
                    # Light is higher during work hours
                    if 8 <= hour <= 18:
                        daily_factor = 400 + random.uniform(-100, 200)
                    else:
                        daily_factor = 50 + random.uniform(-30, 50)
                    value = daily_factor
                else:
                    # Other sensors have minor random variations
                    value = base_value + random.uniform(-variation/2, variation/2)
                
                # Ensure values are within bounds
                if sensor.sensor_type.min_value is not None:
                    value = max(value, sensor.sensor_type.min_value)
                if sensor.sensor_type.max_value is not None:
                    value = min(value, sensor.sensor_type.max_value)
                
                reading = SensorReading(
                    sensor_id=sensor.id,
                    value=round(value, 2),
                    raw_value=round(value + random.uniform(-0.1, 0.1), 3),
                    timestamp=current_time
                )
                
                db.add(reading)
                readings_count += 1
                
                current_time += timedelta(minutes=5)
        
        db.commit()
        print(f"✓ Created {readings_count} sensor readings")
        
        print("\n🎉 Sample data creation completed successfully!")
        print("\nYou can now start the API and explore the data using GraphQL queries.")
        print("Run: python main.py")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating sample data for Sensor API...")
    create_sample_data()
