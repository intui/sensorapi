"""
Database models for sensor data.

This module defines the data structures for a generic sensor data system that can
handle various types of sensors and their readings.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from sqlalchemy import (
    Column, String, DateTime, Float, Integer, Text, Boolean,
    ForeignKey, JSON, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.core.config import settings


class SensorType(Base):
    """
    Represents a type of sensor (e.g., temperature, humidity, pressure).
    """
    __tablename__ = "api_sensor_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    unit = Column(String(20))
    
    # Validation settings
    min_value = Column(Float, doc="Minimum acceptable value for this sensor type")
    max_value = Column(Float, doc="Maximum acceptable value for this sensor type")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sensors = relationship("Sensor", back_populates="sensor_type")

    def __repr__(self):
        return f"<SensorType(id={self.id}, name='{self.name}', unit='{self.unit}')>"


class Location(Base):
    """
    Represents physical locations where sensors can be deployed.
    Supports hierarchical locations (e.g., Building > Floor > Room).
    """
    __tablename__ = "api_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    
    # Hierarchical structure
    parent_id = Column(UUID(as_uuid=True), ForeignKey("api_locations.id"))
    parent = relationship("Location", remote_side=[id], back_populates="children")
    children = relationship("Location", back_populates="parent")
    
    # Geographic coordinates (optional)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)  # meters above sea level
    
    # Address information
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Timezone information
    timezone = Column(String(50))  # e.g., "America/New_York", "UTC", "Europe/London"
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    sensors = relationship("Sensor", back_populates="location")


class Sensor(Base):
    """
    Represents individual sensor devices.
    Links sensor type with location and provides device-specific information.
    """
    __tablename__ = "api_sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(String(100), unique=True, nullable=False, index=True)  # Hardware device ID
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Foreign keys
    sensor_type_id = Column(UUID(as_uuid=True), ForeignKey("api_sensor_types.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("api_locations.id"), nullable=False)
    
    # Device information
    manufacturer = Column(String(100))
    model = Column(String(100))
    firmware_version = Column(String(50))
    hardware_version = Column(String(50))
    
    # Configuration
    sampling_interval = Column(Integer)  # seconds between readings
    calibration_date = Column(DateTime(timezone=True))
    calibration_offset = Column(Float, default=0.0)
    calibration_scale = Column(Float, default=1.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True))
    
    # Latest reading reference
    latest_reading_id = Column(UUID(as_uuid=True), ForeignKey("api_sensor_readings.id"))
    
    # Additional device metadata as JSON
    device_metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sensor_type = relationship("SensorType", back_populates="sensors")
    location = relationship("Location", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan", foreign_keys="SensorReading.sensor_id")
    latest_reading = relationship("SensorReading", foreign_keys=[latest_reading_id], post_update=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_api_sensor_device_location", "device_id", "location_id"),
        Index("idx_api_sensor_type_location", "sensor_type_id", "location_id"),
    )


class SensorReading(Base):
    """
    Stores individual sensor readings/measurements.
    Designed to handle high-volume time-series data efficiently.
    """
    __tablename__ = "api_sensor_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("api_sensors.id"), nullable=False)
    
    # Reading data
    value = Column(Float, nullable=False)  # The main sensor value
    raw_value = Column(Float)  # Uncalibrated raw value
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)  # When reading was taken
    received_at = Column(DateTime(timezone=True), server_default=func.now())  # When received by API
    
    # Relationships
    sensor = relationship("Sensor", back_populates="readings", foreign_keys=[sensor_id])
    
    # Indexes for time-series queries
    __table_args__ = (
        Index("idx_api_reading_sensor_timestamp", "sensor_id", "timestamp"),
        Index("idx_api_reading_timestamp", "timestamp"),
        Index("idx_api_reading_sensor_received", "sensor_id", "received_at"),
    )


class Alert(Base):
    """
    Stores alerts generated based on sensor readings.
    Supports various alert conditions and severity levels.
    """
    __tablename__ = "api_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("api_sensors.id"), nullable=False)
    reading_id = Column(UUID(as_uuid=True), ForeignKey("api_sensor_readings.id"))
    
    # Alert information
    alert_type = Column(String(50), nullable=False)  # threshold, anomaly, offline, etc.
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Alert condition
    condition_type = Column(String(50))  # greater_than, less_than, equals, range, etc.
    threshold_value = Column(Float)
    actual_value = Column(Float)
    
    # Status
    status = Column(String(20), default="active")  # active, acknowledged, resolved, suppressed
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(String(100))
    resolved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Additional alert data
    alert_metadata = Column(JSON)
    
    # Relationships
    sensor = relationship("Sensor")
    reading = relationship("SensorReading")
    
    # Indexes
    __table_args__ = (
        Index("idx_api_alert_sensor_status", "sensor_id", "status"),
        Index("idx_api_alert_triggered", "triggered_at"),
        Index("idx_api_alert_severity_status", "severity", "status"),
    )
