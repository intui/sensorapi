"""
GraphQL resolvers for sensor data API.
Fixed to properly manage database connections and prevent connection leaks.
"""
from datetime import datetime
from typing import List, Optional

import strawberry
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.database.database import get_db_session
from app.database.models import Alert as AlertModel
from app.database.models import Location as LocationModel
from app.database.models import Sensor as SensorModel
from app.database.models import SensorReading as SensorReadingModel
from app.database.models import SensorType as SensorTypeModel
from app.graphql.types import (Alert, CreateLocationInput, CreateSensorInput,
                               CreateSensorReadingInput, CreateSensorTypeInput,
                               Location, Sensor, SensorReading, SensorType,
                               SensorDataStats, SensorDataRange, SensorReadingsAround,
                               UpdateAlertInput, UpdateLocationInput,
                               UpdateSensorInput, UpdateSensorReadingInput,
                               UpdateSensorStatusInput, UpdateSensorTypeInput,
                               WeatherForecastPoint, EnergyPredictionPointType,
                               ModelInfoType, PredictionResultType, TrainModelInput)


@strawberry.type
class Query:
    """GraphQL query operations."""

    @strawberry.field
    def sensor_types(self, info: Info, active_only: bool = True) -> List[SensorType]:
        """Get all sensor types."""
        with get_db_session() as db:
            query = db.query(SensorTypeModel)
            # Note: is_active field was removed from SensorType model
            # All sensor types are considered active
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
        online_only: bool = False,
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
    def sensor_data_stats(self, info: Info, sensor_id: str) -> Optional[SensorDataStats]:
        """Get comprehensive data statistics for a sensor."""
        from sqlalchemy import func
        
        with get_db_session() as db:
            # Get first and last readings
            first_reading = (
                db.query(SensorReadingModel)
                .filter(SensorReadingModel.sensor_id == sensor_id)
                .order_by(SensorReadingModel.timestamp.asc())
                .first()
            )
            
            last_reading = (
                db.query(SensorReadingModel)
                .filter(SensorReadingModel.sensor_id == sensor_id)
                .order_by(SensorReadingModel.timestamp.desc())
                .first()
            )
            
            # Get total count
            total_count = (
                db.query(func.count(SensorReadingModel.id))
                .filter(SensorReadingModel.sensor_id == sensor_id)
                .scalar() or 0
            )
            
            # Create date range
            date_range = SensorDataRange(
                start=first_reading.timestamp if first_reading else None,
                end=last_reading.timestamp if last_reading else None
            )
            
            return SensorDataStats(
                first_reading=SensorReading.from_model(first_reading) if first_reading else None,
                last_reading=SensorReading.from_model(last_reading) if last_reading else None,
                total_count=total_count,
                date_range=date_range
            )

    @strawberry.field
    def sensor_readings_around(
        self,
        info: Info,
        sensor_id: str,
        target_time: datetime,
        before: int = 1,
        after: int = 1
    ) -> SensorReadingsAround:
        """Get sensor readings before and after a target time."""
        
        with get_db_session() as db:
            # Get readings before target time
            before_readings = (
                db.query(SensorReadingModel)
                .filter(SensorReadingModel.sensor_id == sensor_id)
                .filter(SensorReadingModel.timestamp < target_time)
                .order_by(SensorReadingModel.timestamp.desc())
                .limit(before)
                .all()
            )
            
            # Get readings after target time
            after_readings = (
                db.query(SensorReadingModel)
                .filter(SensorReadingModel.sensor_id == sensor_id)
                .filter(SensorReadingModel.timestamp > target_time)
                .order_by(SensorReadingModel.timestamp.asc())
                .limit(after)
                .all()
            )
            
            return SensorReadingsAround(
                before=[SensorReading.from_model(model) for model in before_readings],
                after=[SensorReading.from_model(model) for model in after_readings]
            )

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

    @strawberry.field
    def weather_forecast(
        self,
        info: Info,
        location_id: str,
        hours: int = 96,
    ) -> List[WeatherForecastPoint]:
        """Get weather forecast for a location."""
        from app.services.weather import fetch_forecast

        with get_db_session() as db:
            location = db.query(LocationModel).filter(LocationModel.id == location_id).first()
            if not location:
                raise ValueError(f"Location not found: {location_id}")
            if location.latitude is None or location.longitude is None:
                raise ValueError(
                    f"Location '{location.name}' does not have coordinates configured. "
                    f"Please set latitude and longitude in the location settings."
                )

        hours = max(1, min(hours, 384))
        data = fetch_forecast(location.latitude, location.longitude, hours)
        return [
            WeatherForecastPoint(
                timestamp=p.timestamp,
                temperature=p.temperature,
                humidity=p.humidity,
                wind_speed=p.wind_speed,
                precipitation=p.precipitation,
                cloud_cover=p.cloud_cover,
            )
            for p in data
        ]

    @strawberry.field
    def energy_predictions(
        self,
        info: Info,
        electrical_sensor_id: str,
        thermal_sensor_id: str,
        location_id: str,
        hours: int = 96,
    ) -> PredictionResultType:
        """Get energy predictions based on weather forecast."""
        from app.services.weather import fetch_forecast
        from app.services.prediction import predict_energy

        with get_db_session() as db:
            location = db.query(LocationModel).filter(LocationModel.id == location_id).first()
            if not location:
                raise ValueError(f"Location not found: {location_id}")
            if location.latitude is None or location.longitude is None:
                raise ValueError(
                    f"Location '{location.name}' does not have coordinates. "
                    f"Please set latitude and longitude first."
                )

        hours = max(1, min(hours, 384))
        forecast = fetch_forecast(location.latitude, location.longitude, hours)
        result = predict_energy(forecast, electrical_sensor_id, thermal_sensor_id)

        return PredictionResultType(
            predictions=[
                EnergyPredictionPointType(
                    timestamp=p.timestamp,
                    temperature=p.temperature,
                    predicted_electrical_kwh=p.predicted_electrical_kwh,
                    predicted_thermal_kwh=p.predicted_thermal_kwh,
                    predicted_cop=p.predicted_cop,
                    confidence_low_electrical=p.confidence_low_electrical,
                    confidence_high_electrical=p.confidence_high_electrical,
                    confidence_low_thermal=p.confidence_low_thermal,
                    confidence_high_thermal=p.confidence_high_thermal,
                )
                for p in result.predictions
            ],
            total_electrical_kwh=result.total_electrical_kwh,
            total_thermal_kwh=result.total_thermal_kwh,
            average_cop=result.average_cop,
            model_info=ModelInfoType(
                r2_electrical=result.model_info.r2_electrical,
                r2_thermal=result.model_info.r2_thermal,
                training_samples=result.model_info.training_samples,
                trained_at=result.model_info.trained_at,
                feature_names=result.model_info.feature_names,
            ),
        )


# Nested field resolvers
@strawberry.field
def resolve_sensor_type(sensor: Sensor, info: Info) -> Optional[SensorType]:
    """Resolve the sensor_type field for a Sensor."""
    with get_db_session() as db:
        model = (
            db.query(SensorTypeModel)
            .filter(SensorTypeModel.id == sensor.sensor_type_id)
            .first()
        )
        return SensorType.from_model(model) if model else None


@strawberry.field
def resolve_location(sensor: Sensor, info: Info) -> Optional[Location]:
    """Resolve the location field for a Sensor."""
    with get_db_session() as db:
        model = (
            db.query(LocationModel)
            .filter(LocationModel.id == sensor.location_id)
            .first()
        )
        return Location.from_model(model) if model else None


@strawberry.field
def resolve_sensor_for_reading(reading: SensorReading, info: Info) -> Optional[Sensor]:
    """Resolve the sensor field for a SensorReading."""
    with get_db_session() as db:
        model = (
            db.query(SensorModel).filter(SensorModel.id == reading.sensor_id).first()
        )
        return Sensor.from_model(model) if model else None


# Add the resolvers to the respective types
Sensor.sensor_type = resolve_sensor_type
Sensor.location = resolve_location
SensorReading.sensor = resolve_sensor_for_reading


@strawberry.type
class Mutation:
    """GraphQL mutation operations."""

    @strawberry.mutation
    def create_sensor_type(
        self, info: Info, input: CreateSensorTypeInput
    ) -> SensorType:
        """Create a new sensor type."""
        with get_db_session() as db:
            model = SensorTypeModel(
                name=input.name,
                description=input.description,
                unit=input.unit,
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
    def create_sensor_reading(
        self, info: Info, input: CreateSensorReadingInput
    ) -> SensorReading:
        """Create a new sensor reading and update sensor status."""
        with get_db_session() as db:
            # Create the sensor reading
            reading_model = SensorReadingModel(
                sensor_id=input.sensor_id,
                value=input.value,
                raw_value=input.raw_value,
                timestamp=input.timestamp or datetime.utcnow(),
            )
            db.add(reading_model)
            db.flush()  # Get the ID without committing
            
            # Update sensor status
            sensor_model = db.query(SensorModel).filter(SensorModel.id == input.sensor_id).first()
            if sensor_model:
                # Update sensor status fields
                sensor_model.is_active = True  # Auto-activate on receiving reading
                sensor_model.is_online = True  # Mark as online
                sensor_model.last_seen = reading_model.timestamp
                sensor_model.latest_reading_id = reading_model.id
                sensor_model.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(reading_model)
            return SensorReading.from_model(reading_model)

    @strawberry.mutation
    def delete_sensor_readings(self, info: Info, sensor_id: str) -> int:
        """Delete all sensor readings for a given sensor. Returns count of deleted readings."""
        with get_db_session() as db:
            deleted_count = (
                db.query(SensorReadingModel)
                .filter(SensorReadingModel.sensor_id == sensor_id)
                .delete()
            )
            db.commit()
            return deleted_count

    # Update mutations
    @strawberry.mutation
    def update_sensor_type(
        self, info: Info, id: str, input: UpdateSensorTypeInput
    ) -> Optional[SensorType]:
        """Update a sensor type."""
        with get_db_session() as db:
            model = db.query(SensorTypeModel).filter(SensorTypeModel.id == id).first()
            if not model:
                return None

            if input.name is not None:
                model.name = input.name
            if input.description is not None:
                model.description = input.description
            if input.unit is not None:
                model.unit = input.unit
            if input.min_value is not None:
                model.min_value = input.min_value
            if input.max_value is not None:
                model.max_value = input.max_value

            db.commit()
            db.refresh(model)
            return SensorType.from_model(model)

    @strawberry.mutation
    def update_location(
        self, info: Info, id: str, input: UpdateLocationInput
    ) -> Optional[Location]:
        """Update a location."""
        with get_db_session() as db:
            model = db.query(LocationModel).filter(LocationModel.id == id).first()
            if not model:
                return None

            if input.name is not None:
                model.name = input.name
            if input.description is not None:
                model.description = input.description
            if input.parent_id is not None:
                model.parent_id = input.parent_id
            if input.latitude is not None:
                model.latitude = input.latitude
            if input.longitude is not None:
                model.longitude = input.longitude
            if input.altitude is not None:
                model.altitude = input.altitude
            if input.address is not None:
                model.address = input.address
            if input.city is not None:
                model.city = input.city
            if input.country is not None:
                model.country = input.country
            if input.postal_code is not None:
                model.postal_code = input.postal_code
            if input.is_active is not None:
                model.is_active = input.is_active

            db.commit()
            db.refresh(model)
            return Location.from_model(model)

    @strawberry.mutation
    def update_sensor(
        self, info: Info, id: str, input: UpdateSensorInput
    ) -> Optional[Sensor]:
        """Update a sensor."""
        with get_db_session() as db:
            model = db.query(SensorModel).filter(SensorModel.id == id).first()
            if not model:
                return None

            if input.device_id is not None:
                model.device_id = input.device_id
            if input.name is not None:
                model.name = input.name
            if input.description is not None:
                model.description = input.description
            if input.sensor_type_id is not None:
                model.sensor_type_id = input.sensor_type_id
            if input.location_id is not None:
                model.location_id = input.location_id
            if input.manufacturer is not None:
                model.manufacturer = input.manufacturer
            if input.model is not None:
                model.model = input.model
            if input.firmware_version is not None:
                model.firmware_version = input.firmware_version
            if input.hardware_version is not None:
                model.hardware_version = input.hardware_version
            if input.sampling_interval is not None:
                model.sampling_interval = input.sampling_interval
            if input.calibration_date is not None:
                model.calibration_date = input.calibration_date
            if input.calibration_offset is not None:
                model.calibration_offset = input.calibration_offset
            if input.calibration_scale is not None:
                model.calibration_scale = input.calibration_scale
            if input.is_active is not None:
                model.is_active = input.is_active
            if input.is_online is not None:
                model.is_online = input.is_online

            db.commit()
            db.refresh(model)
            return Sensor.from_model(model)

    @strawberry.mutation
    def update_sensor_status(
        self, info: Info, id: str, input: UpdateSensorStatusInput
    ) -> Optional[Sensor]:
        """Update sensor status (active/online state)."""
        with get_db_session() as db:
            model = db.query(SensorModel).filter(SensorModel.id == id).first()
            if not model:
                return None

            if input.is_active is not None:
                model.is_active = input.is_active
            if input.is_online is not None:
                model.is_online = input.is_online
                
            # Update timestamp when status changes
            model.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(model)
            return Sensor.from_model(model)

    @strawberry.mutation
    def update_sensor_reading(
        self, info: Info, id: str, input: UpdateSensorReadingInput
    ) -> Optional[SensorReading]:
        """Update a sensor reading."""
        with get_db_session() as db:
            model = (
                db.query(SensorReadingModel).filter(SensorReadingModel.id == id).first()
            )
            if not model:
                return None

            if input.value is not None:
                model.value = input.value
            if input.raw_value is not None:
                model.raw_value = input.raw_value
            if input.timestamp is not None:
                model.timestamp = input.timestamp

            db.commit()
            db.refresh(model)
            return SensorReading.from_model(model)

    @strawberry.mutation
    def update_alert(
        self, info: Info, id: str, input: UpdateAlertInput
    ) -> Optional[Alert]:
        """Update an alert."""
        with get_db_session() as db:
            model = db.query(AlertModel).filter(AlertModel.id == id).first()
            if not model:
                return None

            if input.status is not None:
                model.status = input.status
                if input.status == "acknowledged":
                    model.acknowledged_at = datetime.utcnow()
                elif input.status == "resolved":
                    model.resolved_at = datetime.utcnow()
            if input.acknowledged_by is not None:
                model.acknowledged_by = input.acknowledged_by

            db.commit()
            db.refresh(model)
            return Alert.from_model(model)

    # Delete mutations
    @strawberry.mutation
    def delete_sensor_type(self, info: Info, id: str) -> bool:
        """Delete a sensor type. Returns True if deleted, False if not found."""
        with get_db_session() as db:
            model = db.query(SensorTypeModel).filter(SensorTypeModel.id == id).first()
            if not model:
                return False
            db.delete(model)
            db.commit()
            return True

    @strawberry.mutation
    def delete_location(self, info: Info, id: str) -> bool:
        """Delete a location. Returns True if deleted, False if not found."""
        with get_db_session() as db:
            model = db.query(LocationModel).filter(LocationModel.id == id).first()
            if not model:
                return False
            db.delete(model)
            db.commit()
            return True

    @strawberry.mutation
    def delete_sensor(self, info: Info, id: str) -> bool:
        """Delete a sensor. Returns True if deleted, False if not found."""
        with get_db_session() as db:
            model = db.query(SensorModel).filter(SensorModel.id == id).first()
            if not model:
                return False
            
            # Clear latest_reading_id FK before deleting readings to avoid constraint violation
            model.latest_reading_id = None
            db.flush()

            # Delete all sensor readings for this sensor
            db.query(SensorReadingModel).filter(SensorReadingModel.sensor_id == id).delete()

            # Then delete the sensor itself
            db.delete(model)
            db.commit()
            return True

    @strawberry.mutation
    def delete_sensor_reading(self, info: Info, id: str) -> bool:
        """Delete a sensor reading. Returns True if deleted, False if not found."""
        with get_db_session() as db:
            model = (
                db.query(SensorReadingModel).filter(SensorReadingModel.id == id).first()
            )
            if not model:
                return False
            db.delete(model)
            db.commit()
            return True

    @strawberry.mutation
    def delete_alert(self, info: Info, id: str) -> bool:
        """Delete an alert. Returns True if deleted, False if not found."""
        with get_db_session() as db:
            model = db.query(AlertModel).filter(AlertModel.id == id).first()
            if not model:
                return False
            db.delete(model)
            db.commit()
            return True

    @strawberry.mutation
    def train_prediction_model(self, info: Info, input: TrainModelInput) -> ModelInfoType:
        """Train (or retrain) a prediction model from historical data."""
        from app.services.prediction import train_model

        with get_db_session() as db:
            # Validate location
            location = db.query(LocationModel).filter(LocationModel.id == input.location_id).first()
            if not location:
                raise ValueError(f"Location not found: {input.location_id}")
            if location.latitude is None or location.longitude is None:
                raise ValueError(
                    f"Location '{location.name}' does not have coordinates configured."
                )

            # Fetch historical readings
            elec_readings = (
                db.query(SensorReadingModel)
                .filter(SensorReadingModel.sensor_id == input.electrical_sensor_id)
                .order_by(SensorReadingModel.timestamp.asc())
                .all()
            )
            therm_readings = (
                db.query(SensorReadingModel)
                .filter(SensorReadingModel.sensor_id == input.thermal_sensor_id)
                .order_by(SensorReadingModel.timestamp.asc())
                .all()
            )

            readings_e = [{"timestamp": r.timestamp.isoformat(), "value": r.value} for r in elec_readings]
            readings_t = [{"timestamp": r.timestamp.isoformat(), "value": r.value} for r in therm_readings]

        result = train_model(
            readings_electrical=readings_e,
            readings_thermal=readings_t,
            latitude=location.latitude,
            longitude=location.longitude,
            electrical_sensor_id=input.electrical_sensor_id,
            thermal_sensor_id=input.thermal_sensor_id,
            lookback_days=input.lookback_days,
        )

        return ModelInfoType(
            r2_electrical=result.r2_electrical,
            r2_thermal=result.r2_thermal,
            training_samples=result.training_samples,
            trained_at=result.trained_at,
            feature_names=result.feature_names,
        )


# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
