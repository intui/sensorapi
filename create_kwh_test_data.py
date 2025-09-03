"""
Quick script to create kWh sensor types and sensors for heat pump testing
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import SensorType, Sensor, Location, SensorReading
from datetime import datetime, timedelta
import random

async def create_kwh_test_data():
    db = SessionLocal()
    try:
        # Create or get kWh sensor types
        electrical_sensor_type = db.query(SensorType).filter(
            SensorType.name == "Electrical Energy Meter"
        ).first()
        
        if not electrical_sensor_type:
            electrical_sensor_type = SensorType(
                name="Electrical Energy Meter",
                description="Measures electrical energy consumption in kWh",
                unit="kWh",
                min_value=0.0,
                max_value=10000.0
            )
            db.add(electrical_sensor_type)
            db.commit()
            db.refresh(electrical_sensor_type)
        
        thermal_sensor_type = db.query(SensorType).filter(
            SensorType.name == "Thermal Energy Meter"
        ).first()
        
        if not thermal_sensor_type:
            thermal_sensor_type = SensorType(
                name="Thermal Energy Meter", 
                description="Measures thermal energy production in kWh",
                unit="kWh",
                min_value=0.0,
                max_value=15000.0
            )
            db.add(thermal_sensor_type)
            db.commit()
            db.refresh(thermal_sensor_type)
        
        # Create or get test location
        test_location = db.query(Location).filter(
            Location.name == "Heat Pump Test House"
        ).first()
        
        if not test_location:
            test_location = Location(
                name="Heat Pump Test House",
                description="Test location for heat pump monitoring",
                city="Demo City",
                country="Demo Country",
                is_active=True
            )
            db.add(test_location)
            db.commit()
            db.refresh(test_location)
        
        # Create electrical energy sensor
        electrical_sensor = db.query(Sensor).filter(
            Sensor.device_id == "HE_ELEC_001"
        ).first()
        
        if not electrical_sensor:
            electrical_sensor = Sensor(
                device_id="HE_ELEC_001",
                name="Heat Pump Electrical Meter",
                description="Measures electrical energy consumed by heat pump",
                sensor_type_id=electrical_sensor_type.id,
                location_id=test_location.id,
                manufacturer="Demo Meters Inc",
                model="DM-E100",
                is_active=True,
                is_online=True
            )
            db.add(electrical_sensor)
            db.commit()
            db.refresh(electrical_sensor)
        
        # Create thermal energy sensor
        thermal_sensor = db.query(Sensor).filter(
            Sensor.device_id == "HE_THERM_001"
        ).first()
        
        if not thermal_sensor:
            thermal_sensor = Sensor(
                device_id="HE_THERM_001",
                name="Heat Pump Thermal Meter",
                description="Measures thermal energy produced by heat pump",
                sensor_type_id=thermal_sensor_type.id,
                location_id=test_location.id,
                manufacturer="Demo Meters Inc",
                model="DM-T100", 
                is_active=True,
                is_online=True
            )
            db.add(thermal_sensor)
            db.commit()
            db.refresh(thermal_sensor)
        
        # Create sample readings for the last 30 days
        print("Creating sample energy readings...")
        
        # Generate sample data for last 30 days
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        # Clear existing readings for these sensors
        db.query(SensorReading).filter(
            SensorReading.sensor_id.in_([electrical_sensor.id, thermal_sensor.id])
        ).delete()
        db.commit()
        
        # Generate hourly readings
        current_electrical = 1000.0  # Starting meter reading
        current_thermal = 2500.0     # Starting meter reading
        
        current_time = start_time
        while current_time <= end_time:
            # Simulate daily pattern - higher usage during day, lower at night
            hour = current_time.hour
            if 6 <= hour <= 22:  # Day time
                electrical_increment = random.uniform(0.8, 1.5)  # kWh per hour
                cop = random.uniform(2.5, 4.0)  # Good COP during day
            else:  # Night time
                electrical_increment = random.uniform(0.3, 0.8)  # kWh per hour  
                cop = random.uniform(2.0, 3.5)  # Lower COP at night
            
            thermal_increment = electrical_increment * cop
            
            current_electrical += electrical_increment
            current_thermal += thermal_increment
            
            # Add some randomness
            current_electrical += random.uniform(-0.1, 0.1)
            current_thermal += random.uniform(-0.2, 0.2)
            
            # Create electrical reading
            electrical_reading = SensorReading(
                sensor_id=electrical_sensor.id,
                value=round(current_electrical, 2),
                timestamp=current_time,
                received_at=current_time
            )
            db.add(electrical_reading)
            
            # Create thermal reading
            thermal_reading = SensorReading(
                sensor_id=thermal_sensor.id,
                value=round(current_thermal, 2),
                timestamp=current_time,
                received_at=current_time
            )
            db.add(thermal_reading)
            
            current_time += timedelta(hours=1)
        
        db.commit()
        
        print(f"✓ Created kWh sensor types")
        print(f"✓ Created electrical sensor: {electrical_sensor.name}")
        print(f"✓ Created thermal sensor: {thermal_sensor.name}")
        print(f"✓ Created sample readings from {start_time} to {end_time}")
        print(f"✓ Total electrical energy: {current_electrical - 1000:.2f} kWh")
        print(f"✓ Total thermal energy: {current_thermal - 2500:.2f} kWh")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_kwh_test_data())