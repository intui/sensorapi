"""
GraphQL resolvers for sensor data API.
Fixed to properly manage database connections and prevent connection leaks.
"""
from datetime import datetime
from typing import List, Optional
import strawberry
from strawberry.types import Info
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.database.database import get_db_session
from app.database.models import (
    SensorType as SensorTypeModel,
    Location as LocationModel,
    Sensor as SensorModel,
    SensorReading as SensorReadingModel,
    Alert as AlertModel,
)
from app.graphql.types import (
    SensorType, Location, Sensor, SensorReading, Alert,
    CreateSensorTypeInput, CreateLocationInput, CreateSensorInput, CreateSensorReadingInput,
)


@strawberry.type
class Query:
    """GraphQL query operations."""
    
    @strawberry.field
    def sensor_types(self, info: Info, active_only: bool = True) -> List[SensorType]:
        """Get all sensor types."""
        with get_db_session() as db:
            query = db.query(SensorTypeModel)
            if active_only:
                query = query.filter(SensorTypeModel.is_active == True)
            models = query.all()
            return [SensorType.from_model(model) for model in models]
    
    @strawberry.field
    def sensor_type(self, info: Info, id: str) -> Optional[SensorType]:
        """Get a sensor type by ID."""
        with get_db_session() as db:
            model = db.query(SensorTypeModel).filter(SensorTypeModel.id == id).first()
            return SensorType.from_model(model) if model else None
    
    @strawberry.field
    def locations(self, info: Info, active_only: bool = True) -> List[Location]:
        """Get all locations."""
        with get_db_session() as db:
            query = db.query(LocationModel)
            if active_only:
                query = query.filter(LocationModel.is_active == True)
            models = query.all()
            return [Location.from_model(model) for model in models]
    
    @strawberry.field
    def location(self, info: Info, id: str) -> Optional[Location]:
        """Get a location by ID."""
        with get_db_session() as db:
            model = db.query(LocationModel).filter(LocationModel.id == id).first()
            return Location.from_model(model) if model else None
    
    @strawberry.field
    def sensors(
        self, 
        info: Info, 
        location_id: Optional[str] = None,
        sensor_type_id: Optional[str] = None,
        active_only: bool = True,
        online_only: bool = False
    ) -> List[Sensor]:
        """Get sensors with optional filtering."""
        with get_db_session() as db:
            query = db.query(SensorModel)
            
            if location_id:
                query = query.filter(SensorModel.location_id == location_id)
            if sensor_type_id:
                query = query.filter(SensorModel.sensor_type_id == sensor_type_id)
            if active_only:
                query = query.filter(SensorModel.is_active == True)
            if online_only:
                query = query.filter(SensorModel.is_online == True)
            
            models = query.all()
            return [Sensor.from_model(model) for model in models]
    
    @strawberry.field
    def sensor(self, info: Info, id: str) -> Optional[Sensor]:
        """Get a sensor by ID."""
        with get_db_session() as db:
            model = db.query(SensorModel).filter(SensorModel.id == id).first()
            return Sensor.from_model(model) if model else None
    
    @strawberry.field
    def sensor_readings(
        self,
        info: Info,
        sensor_id: str,
        limit: int = 100,
        offset: int = 0,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[SensorReading]:
        """Get sensor readings with optional filtering."""
        with get_db_session() as db:
            query = db.query(SensorReadingModel).filter(
                SensorReadingModel.sensor_id == sensor_id
            )
            
            if start_time:
                query = query.filter(SensorReadingModel.timestamp >= start_time)
            if end_time:
                query = query.filter(SensorReadingModel.timestamp <= end_time)
            
            query = query.order_by(desc(SensorReadingModel.timestamp))
            query = query.offset(offset).limit(limit)
            
            models = query.all()
            return [SensorReading.from_model(model) for model in models]
    
    @strawberry.field
    def alerts(
        self,
        info: Info,
        sensor_id: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
    ) -> List[Alert]:
        """Get alerts with optional filtering."""
        with get_db_session() as db:
            query = db.query(AlertModel)
            
            if sensor_id:
                query = query.filter(AlertModel.sensor_id == sensor_id)
            if active_only:
                query = query.filter(AlertModel.is_active == True)
            
            query = query.order_by(desc(AlertModel.created_at))
            query = query.limit(limit)
            
            models = query.all()
            return [Alert.from_model(model) for model in models]


@strawberry.type
class Mutation:
    """GraphQL mutation operations."""
    
    @strawberry.mutation
    def create_sensor_type(self, info: Info, input: CreateSensorTypeInput) -> SensorType:
        """Create a new sensor type."""
        with get_db_session() as db:
            model = SensorTypeModel(
                name=input.name,
                description=input.description,
                unit=input.unit,
                data_type=input.data_type,
                min_value=input.min_value,
                max_value=input.max_value,
            )
            db.add(model)
            db.commit()
            db.refresh(model)
            return SensorType.from_model(model)
    
    @strawberry.mutation
    def create_location(self, info: Info, input: CreateLocationInput) -> Location:
        """Create a new location."""
        with get_db_session() as db:
            model = LocationModel(
                name=input.name,
                description=input.description,
                city=input.city,
                country=input.country,
                postal_code=input.postal_code,
                address=input.address,
                latitude=input.latitude,
                longitude=input.longitude,
                altitude=input.altitude,
                parent_id=input.parent_id,
            )
            db.add(model)
            db.commit()
            db.refresh(model)
            return Location.from_model(model)
    
    @strawberry.mutation
    def create_sensor(self, info: Info, input: CreateSensorInput) -> Sensor:
        """Create a new sensor."""
        with get_db_session() as db:
            model = SensorModel(
                device_id=input.device_id,
                name=input.name,
                description=input.description,
                sensor_type_id=input.sensor_type_id,
                location_id=input.location_id,
                manufacturer=input.manufacturer,
                model=input.model,
                firmware_version=input.firmware_version,
                hardware_version=input.hardware_version,
                sampling_interval=input.sampling_interval,
            )
            db.add(model)
            db.commit()
            db.refresh(model)
            return Sensor.from_model(model)
    
    @strawberry.mutation
    def create_sensor_reading(self, info: Info, input: CreateSensorReadingInput) -> SensorReading:
        """Create a new sensor reading."""
        with get_db_session() as db:
            model = SensorReadingModel(
                sensor_id=input.sensor_id,
                value=input.value,
                raw_value=input.raw_value,
                timestamp=input.timestamp or datetime.utcnow(),
            )
            db.add(model)
            db.commit()
            db.refresh(model)
            return SensorReading.from_model(model)


# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
