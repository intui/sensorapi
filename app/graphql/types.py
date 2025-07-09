"""
GraphQL types and schema definitions for sensor data API.
"""
from datetime import datetime
from typing import List, Optional
import strawberry
from strawberry.types import Info

from app.database.models import (
    SensorType as SensorTypeModel,
    Location as LocationModel,
    Sensor as SensorModel,
    SensorReading as SensorReadingModel,
    Alert as AlertModel,
)


@strawberry.type
class SensorType:
    """GraphQL type for sensor types."""
    id: str
    name: str
    description: Optional[str]
    unit: Optional[str]
    data_type: str
    min_value: Optional[float]
    max_value: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    @classmethod
    def from_model(cls, model: SensorTypeModel) -> "SensorType":
        return cls(
            id=str(model.id),
            name=model.name,
            description=model.description,
            unit=model.unit,
            data_type=model.data_type,
            min_value=model.min_value,
            max_value=model.max_value,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active,
        )


@strawberry.type
class Location:
    """GraphQL type for sensor locations."""
    id: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]
    address: Optional[str]
    city: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    @classmethod
    def from_model(cls, model: LocationModel) -> "Location":
        return cls(
            id=str(model.id),
            name=model.name,
            description=model.description,
            parent_id=str(model.parent_id) if model.parent_id else None,
            latitude=model.latitude,
            longitude=model.longitude,
            altitude=model.altitude,
            address=model.address,
            city=model.city,
            country=model.country,
            postal_code=model.postal_code,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active,
        )


@strawberry.type
class Sensor:
    """GraphQL type for sensors."""
    id: str
    device_id: str
    name: str
    description: Optional[str]
    sensor_type_id: str
    location_id: str
    manufacturer: Optional[str]
    model: Optional[str]
    firmware_version: Optional[str]
    hardware_version: Optional[str]
    sampling_interval: Optional[int]
    calibration_date: Optional[datetime]
    calibration_offset: float
    calibration_scale: float
    is_active: bool
    is_online: bool
    last_seen: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    @strawberry.field
    def sensor_type(self, info: Info) -> Optional[SensorType]:
        """Get the sensor type for this sensor."""
        # This will be resolved by the resolver
        return None

    @strawberry.field
    def location(self, info: Info) -> Optional[Location]:
        """Get the location for this sensor."""
        # This will be resolved by the resolver
        return None

    @strawberry.field
    def latest_reading(self, info: Info) -> Optional["SensorReading"]:
        """Get the latest reading for this sensor."""
        # This will be resolved by the resolver
        return None

    @classmethod
    def from_model(cls, model: SensorModel) -> "Sensor":
        return cls(
            id=str(model.id),
            device_id=model.device_id,
            name=model.name,
            description=model.description,
            sensor_type_id=str(model.sensor_type_id),
            location_id=str(model.location_id),
            manufacturer=model.manufacturer,
            model=model.model,
            firmware_version=model.firmware_version,
            hardware_version=model.hardware_version,
            sampling_interval=model.sampling_interval,
            calibration_date=model.calibration_date,
            calibration_offset=model.calibration_offset,
            calibration_scale=model.calibration_scale,
            is_active=model.is_active,
            is_online=model.is_online,
            last_seen=model.last_seen,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


@strawberry.type
class SensorReading:
    """GraphQL type for sensor readings."""
    id: str
    sensor_id: str
    value: float
    raw_value: Optional[float]
    timestamp: datetime
    received_at: datetime

    @strawberry.field
    def sensor(self, info: Info) -> Optional[Sensor]:
        """Get the sensor for this reading."""
        # This will be resolved by the resolver
        return None

    @classmethod
    def from_model(cls, model: SensorReadingModel) -> "SensorReading":
        return cls(
            id=str(model.id),
            sensor_id=str(model.sensor_id),
            value=model.value,
            raw_value=model.raw_value,
            timestamp=model.timestamp,
            received_at=model.received_at,
        )


@strawberry.type
class Alert:
    """GraphQL type for alerts."""
    id: str
    sensor_id: str
    reading_id: Optional[str]
    alert_type: str
    severity: str
    title: str
    message: str
    condition_type: Optional[str]
    threshold_value: Optional[float]
    actual_value: Optional[float]
    status: str
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[str]
    resolved_at: Optional[datetime]
    triggered_at: datetime

    @strawberry.field
    def sensor(self, info: Info) -> Optional[Sensor]:
        """Get the sensor for this alert."""
        # This will be resolved by the resolver
        return None

    @strawberry.field
    def reading(self, info: Info) -> Optional[SensorReading]:
        """Get the reading that triggered this alert."""
        # This will be resolved by the resolver
        return None

    @classmethod
    def from_model(cls, model: AlertModel) -> "Alert":
        return cls(
            id=str(model.id),
            sensor_id=str(model.sensor_id),
            reading_id=str(model.reading_id) if model.reading_id else None,
            alert_type=model.alert_type,
            severity=model.severity,
            title=model.title,
            message=model.message,
            condition_type=model.condition_type,
            threshold_value=model.threshold_value,
            actual_value=model.actual_value,
            status=model.status,
            acknowledged_at=model.acknowledged_at,
            acknowledged_by=model.acknowledged_by,
            resolved_at=model.resolved_at,
            triggered_at=model.triggered_at,
        )


# Input types for mutations
@strawberry.input
class CreateSensorTypeInput:
    """Input for creating a new sensor type."""
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    data_type: str = "float"
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@strawberry.input
class CreateLocationInput:
    """Input for creating a new location."""
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


@strawberry.input
class CreateSensorInput:
    """Input for creating a new sensor."""
    device_id: str
    name: str
    description: Optional[str] = None
    sensor_type_id: str
    location_id: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None
    sampling_interval: Optional[int] = None


@strawberry.input
class CreateSensorReadingInput:
    """Input for creating a new sensor reading."""
    sensor_id: str
    value: float
    raw_value: Optional[float] = None
    timestamp: Optional[datetime] = None
