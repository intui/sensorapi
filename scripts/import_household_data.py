#!/usr/bin/env python3
"""
Household Data Import Script

This script imports the household_data_15min.csv file into TimescaleDB.
It transforms the wide CSV format into normalized sensor readings.

Usage:
    python scripts/import_household_data.py
"""

import os
import sys
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import SensorType, Location, Sensor, SensorReading
from app.database.database import get_db

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_household_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HouseholdDataImporter:
    def __init__(self):
        # Use Tiger Cloud database URL
        self.db_url = os.getenv('TIGER_CLOUD_DATABASE_URL')
        if not self.db_url:
            raise ValueError("TIGER_CLOUD_DATABASE_URL not found in environment")
        
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Data file path
        self.csv_path = project_root / "import_data" / "household_data_15min.csv"
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        # Mapping dictionaries
        self.sensor_types = {}
        self.locations = {}
        self.sensors = {}
    
    def analyze_csv_structure(self):
        """Analyze the CSV file structure"""
        logger.info("Analyzing CSV file structure...")
        
        # Read just the header
        df_sample = pd.read_csv(self.csv_path, nrows=5)
        
        logger.info(f"CSV file: {self.csv_path}")
        logger.info(f"Columns: {len(df_sample.columns)}")
        logger.info(f"Sample columns: {list(df_sample.columns[:10])}")
        
        # Analyze sensor naming patterns
        sensor_columns = [col for col in df_sample.columns if col not in ['utc_timestamp', 'cet_cest_timestamp']]
        
        # Extract unique location patterns
        locations = set()
        sensor_types = set()
        
        for col in sensor_columns:
            if col.startswith('DE_KN_'):
                parts = col.split('_')
                if len(parts) >= 3:
                    # Extract location (e.g., DE_KN_industrial1)
                    location = '_'.join(parts[:3])
                    locations.add(location)
                    
                    # Extract sensor type (everything after location)
                    sensor_type = '_'.join(parts[3:])
                    if sensor_type:
                        sensor_types.add(sensor_type)
        
        logger.info(f"Unique locations found: {len(locations)}")
        logger.info(f"Unique sensor types found: {len(sensor_types)}")
        logger.info(f"Sample locations: {sorted(list(locations))[:5]}")
        logger.info(f"Sample sensor types: {sorted(list(sensor_types))[:10]}")
        
        return locations, sensor_types, sensor_columns
    
    def create_sensor_types(self, sensor_types: set) -> Dict[str, uuid.UUID]:
        """Create sensor type records"""
        logger.info(f"Creating {len(sensor_types)} sensor types...")
        
        # Define sensor type mappings with proper units and descriptions
        type_definitions = {
            'grid_import': {'unit': 'kW', 'description': 'Grid electricity import'},
            'grid_export': {'unit': 'kW', 'description': 'Grid electricity export'},
            'pv': {'unit': 'kW', 'description': 'Photovoltaic generation'},
            'pv_1': {'unit': 'kW', 'description': 'Photovoltaic generation (Array 1)'},
            'pv_2': {'unit': 'kW', 'description': 'Photovoltaic generation (Array 2)'},
            'pv_roof': {'unit': 'kW', 'description': 'Roof photovoltaic generation'},
            'pv_facade': {'unit': 'kW', 'description': 'Facade photovoltaic generation'},
            'storage_charge': {'unit': 'kW', 'description': 'Battery storage charging'},
            'storage_decharge': {'unit': 'kW', 'description': 'Battery storage discharging'},
            'heat_pump': {'unit': 'kW', 'description': 'Heat pump consumption'},
            'dishwasher': {'unit': 'kW', 'description': 'Dishwasher consumption'},
            'washing_machine': {'unit': 'kW', 'description': 'Washing machine consumption'},
            'freezer': {'unit': 'kW', 'description': 'Freezer consumption'},
            'refrigerator': {'unit': 'kW', 'description': 'Refrigerator consumption'},
            'ev': {'unit': 'kW', 'description': 'Electric vehicle charging'},
            'circulation_pump': {'unit': 'kW', 'description': 'Circulation pump consumption'},
            'compressor': {'unit': 'kW', 'description': 'Compressor consumption'},
            'cooling_aggregate': {'unit': 'kW', 'description': 'Cooling aggregate consumption'},
            'cooling_pumps': {'unit': 'kW', 'description': 'Cooling pumps consumption'},
            'ventilation': {'unit': 'kW', 'description': 'Ventilation system consumption'},
            'machine_1': {'unit': 'kW', 'description': 'Industrial machine 1 consumption'},
            'machine_2': {'unit': 'kW', 'description': 'Industrial machine 2 consumption'},
            'machine_3': {'unit': 'kW', 'description': 'Industrial machine 3 consumption'},
            'machine_4': {'unit': 'kW', 'description': 'Industrial machine 4 consumption'},
            'machine_5': {'unit': 'kW', 'description': 'Industrial machine 5 consumption'},
            'area_offices': {'unit': 'kW', 'description': 'Office area consumption'},
            'area_room_1': {'unit': 'kW', 'description': 'Room 1 consumption'},
            'area_room_2': {'unit': 'kW', 'description': 'Room 2 consumption'},
            'area_room_3': {'unit': 'kW', 'description': 'Room 3 consumption'},
            'area_room_4': {'unit': 'kW', 'description': 'Room 4 consumption'},
        }
        
        created_types = {}
        
        with self.SessionLocal() as session:
            for sensor_type in sensor_types:
                if sensor_type in type_definitions:
                    definition = type_definitions[sensor_type]
                else:
                    # Generic definition for unknown types
                    definition = {'unit': 'kW', 'description': f'Energy consumption/generation: {sensor_type}'}
                
                # Check if sensor type already exists
                existing = session.query(SensorType).filter(SensorType.name == sensor_type).first()
                if existing:
                    created_types[sensor_type] = existing.id
                    continue
                
                sensor_type_record = SensorType(
                    name=sensor_type,
                    description=definition['description'],
                    unit=definition['unit'],
                    min_value=0.0,  # Energy values are typically non-negative
                    max_value=None  # No upper limit defined
                )
                
                session.add(sensor_type_record)
                session.flush()
                created_types[sensor_type] = sensor_type_record.id
            
            session.commit()
        
        logger.info(f"Created/found {len(created_types)} sensor types")
        return created_types
    
    def create_locations(self, locations: set) -> Dict[str, uuid.UUID]:
        """Create location records with hierarchy"""
        logger.info(f"Creating {len(locations)} locations...")
        
        created_locations = {}
        
        with self.SessionLocal() as session:
            # Create root location (Germany)
            root_location = session.query(Location).filter(Location.name == "Germany").first()
            if not root_location:
                root_location = Location(
                    name="Germany",
                    description="Country: Germany",
                    country="Germany"
                )
                session.add(root_location)
                session.flush()
            
            # Create region location (Baden-Württemberg, Konstanz)
            region_location = session.query(Location).filter(Location.name == "DE_KN").first()
            if not region_location:
                region_location = Location(
                    name="DE_KN",
                    description="Konstanz, Baden-Württemberg, Germany",
                    parent_id=root_location.id,
                    city="Konstanz",
                    country="Germany"
                )
                session.add(region_location)
                session.flush()
            
            # Create building locations
            for location in locations:
                existing = session.query(Location).filter(Location.name == location).first()
                if existing:
                    created_locations[location] = existing.id
                    continue
                
                # Parse location name for type
                if 'industrial' in location:
                    building_type = "Industrial Building"
                elif 'residential' in location:
                    building_type = "Residential Building"
                elif 'public' in location:
                    building_type = "Public Building"
                else:
                    building_type = "Building"
                
                location_record = Location(
                    name=location,
                    description=f"{building_type} - {location}",
                    parent_id=region_location.id,
                    city="Konstanz",
                    country="Germany"
                )
                
                session.add(location_record)
                session.flush()
                created_locations[location] = location_record.id
            
            session.commit()
        
        logger.info(f"Created/found {len(created_locations)} locations")
        return created_locations
    
    def create_sensors(self, sensor_columns: List[str]) -> Dict[str, uuid.UUID]:
        """Create sensor records"""
        logger.info(f"Creating sensors for {len(sensor_columns)} data columns...")
        
        created_sensors = {}
        
        with self.SessionLocal() as session:
            for col in sensor_columns:
                if col.startswith('DE_KN_'):
                    parts = col.split('_')
                    if len(parts) >= 4:
                        # Extract location and sensor type
                        location_name = '_'.join(parts[:3])
                        sensor_type_name = '_'.join(parts[3:])
                        
                        if location_name in self.locations and sensor_type_name in self.sensor_types:
                            # Check if sensor already exists
                            existing = session.query(Sensor).filter(Sensor.device_id == col).first()
                            if existing:
                                created_sensors[col] = existing.id
                                continue
                            
                            sensor_record = Sensor(
                                device_id=col,
                                name=f"{sensor_type_name.title()} - {location_name}",
                                description=f"Energy measurement for {sensor_type_name} at {location_name}",
                                sensor_type_id=self.sensor_types[sensor_type_name],
                                location_id=self.locations[location_name],
                                manufacturer="Smart Meter",
                                sampling_interval=900,  # 15 minutes = 900 seconds
                                is_active=True
                            )
                            
                            session.add(sensor_record)
                            session.flush()
                            created_sensors[col] = sensor_record.id
            
            session.commit()
        
        logger.info(f"Created/found {len(created_sensors)} sensors")
        return created_sensors
    
    def import_readings_batch(self, df_chunk: pd.DataFrame, chunk_index: int):
        """Import a batch of sensor readings"""
        logger.info(f"Importing chunk {chunk_index} with {len(df_chunk)} rows...")
        
        readings_to_insert = []
        
        for _, row in df_chunk.iterrows():
            timestamp = pd.to_datetime(row['utc_timestamp'])
            
            # Skip invalid timestamps
            if pd.isna(timestamp):
                continue
            
            # Process each sensor column
            for col in df_chunk.columns:
                if col.startswith('DE_KN_') and col in self.sensors:
                    value = row[col]
                    
                    # Skip empty/invalid values
                    if pd.isna(value) or value == '':
                        continue
                    
                    try:
                        value = float(value)
                        
                        # Create sensor reading
                        reading = SensorReading(
                            sensor_id=self.sensors[col],
                            value=value,
                            raw_value=value,
                            timestamp=timestamp
                        )
                        readings_to_insert.append(reading)
                        
                    except (ValueError, TypeError):
                        # Skip invalid numeric values
                        continue
        
        # Batch insert readings
        if readings_to_insert:
            with self.SessionLocal() as session:
                session.bulk_save_objects(readings_to_insert)
                session.commit()
            
            logger.info(f"Imported {len(readings_to_insert)} readings from chunk {chunk_index}")
        
        return len(readings_to_insert)
    
    def import_data(self, chunk_size: int = 1000):
        """Import the complete household dataset"""
        logger.info("Starting household data import...")
        
        # Analyze CSV structure
        locations, sensor_types, sensor_columns = self.analyze_csv_structure()
        
        # Create infrastructure
        self.sensor_types = self.create_sensor_types(sensor_types)
        self.locations = self.create_locations(locations)
        self.sensors = self.create_sensors(sensor_columns)
        
        logger.info(f"Infrastructure created. Starting data import with chunk size {chunk_size}...")
        
        # Import data in chunks
        total_readings = 0
        chunk_index = 0
        
        for chunk in pd.read_csv(self.csv_path, chunksize=chunk_size):
            readings_count = self.import_readings_batch(chunk, chunk_index)
            total_readings += readings_count
            chunk_index += 1
            
            if chunk_index % 10 == 0:
                logger.info(f"Processed {chunk_index} chunks, {total_readings} total readings")
        
        logger.info(f"Data import completed! Total readings imported: {total_readings}")
        return total_readings

def main():
    """Main import entry point"""
    try:
        importer = HouseholdDataImporter()
        
        logger.info("=" * 60)
        logger.info("STARTING HOUSEHOLD DATA IMPORT")
        logger.info("=" * 60)
        
        total_readings = importer.import_data(chunk_size=1000)
        
        logger.info("=" * 60)
        logger.info(f"IMPORT COMPLETED! 🎉")
        logger.info(f"Total readings imported: {total_readings:,}")
        logger.info("=" * 60)
        
        print(f"\n🎉 Import completed successfully!")
        print(f"Total readings imported: {total_readings:,}")
        print("Check import_household_data.log for detailed logs.")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        print(f"\n❌ Import failed: {e}")
        print("Check import_household_data.log for error details.")
        sys.exit(1)

if __name__ == "__main__":
    main()