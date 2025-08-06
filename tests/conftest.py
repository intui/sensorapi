"""
Test configuration and fixtures for Sensor API tests.
"""
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.database import Base, get_db
from app.database.models import SensorType, Location, Sensor, SensorReading, Alert
from main import app


# Test database URL (using port 5433 for Docker to avoid conflicts)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql://test_user:test_pass@localhost:5433/sensor_test_db"
)


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine and tables."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def test_db(test_engine):
    """Create test database session with proper cleanup."""
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        
        # Clean up all tables after each test
        with test_engine.connect() as conn:
            # Use raw SQL to clear tables in correct order (handle foreign keys)
            conn.execute(text("DELETE FROM api_alerts"))
            conn.execute(text("DELETE FROM api_sensor_readings"))
            conn.execute(text("DELETE FROM api_sensors"))
            conn.execute(text("DELETE FROM api_locations"))
            conn.execute(text("DELETE FROM api_sensor_types"))
            conn.commit()


@pytest.fixture
def client(test_db):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_sensor_type(test_db):
    """Create a sample sensor type for testing."""
    sensor_type = SensorType(
        name="Temperature",
        description="Air temperature sensor",
        unit="°C",
        data_type="float",
        min_value=-50.0,
        max_value=100.0
    )
    test_db.add(sensor_type)
    test_db.commit()
    test_db.refresh(sensor_type)
    return sensor_type


@pytest.fixture
def sample_location(test_db):
    """Create a sample location for testing."""
    location = Location(
        name="Test Building",
        description="Main test facility",
        city="Test City",
        country="Test Country",
        latitude=40.7128,
        longitude=-74.0060
    )
    test_db.add(location)
    test_db.commit()
    test_db.refresh(location)
    return location


@pytest.fixture
def sample_sensor(test_db, sample_sensor_type, sample_location):
    """Create a sample sensor for testing."""
    sensor = Sensor(
        device_id="TEST-SENSOR-001",
        name="Test Temperature Sensor",
        description="Primary temperature sensor for testing",
        sensor_type_id=sample_sensor_type.id,
        location_id=sample_location.id,
        manufacturer="TestCorp",
        model="TempSens-2000",
        firmware_version="1.0.0",
        hardware_version="1.0.0",
        sampling_interval=60
    )
    test_db.add(sensor)
    test_db.commit()
    test_db.refresh(sensor)
    return sensor


@pytest.fixture
def sample_sensor_reading(test_db, sample_sensor):
    """Create a sample sensor reading for testing."""
    reading = SensorReading(
        sensor_id=sample_sensor.id,
        value=23.5,
        raw_value=23.5
    )
    test_db.add(reading)
    test_db.commit()
    test_db.refresh(reading)
    return reading


# GraphQL Query Templates
class GraphQLQueries:
    """Common GraphQL queries for testing."""
    
    CREATE_SENSOR_TYPE = """
    mutation CreateSensorType($input: CreateSensorTypeInput!) {
        createSensorType(input: $input) {
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
    
    GET_SENSOR_TYPES = """
    query GetSensorTypes($activeOnly: Boolean) {
        sensorTypes(activeOnly: $activeOnly) {
            id
            name
            description
            unit
            dataType
            minValue
            maxValue
            isActive
        }
    }
    """
    
    GET_SENSOR_TYPE = """
    query GetSensorType($id: String!) {
        sensorType(id: $id) {
            id
            name
            description
            unit
            dataType
            minValue
            maxValue
            isActive
        }
    }
    """
    
    CREATE_LOCATION = """
    mutation CreateLocation($input: CreateLocationInput!) {
        createLocation(input: $input) {
            id
            name
            description
            parentId
            latitude
            longitude
            altitude
            address
            city
            country
            postalCode
            isActive
            createdAt
        }
    }
    """
    
    GET_LOCATIONS = """
    query GetLocations($activeOnly: Boolean) {
        locations(activeOnly: $activeOnly) {
            id
            name
            description
            parentId
            latitude
            longitude
            city
            country
            isActive
        }
    }
    """
    
    CREATE_SENSOR = """
    mutation CreateSensor($input: CreateSensorInput!) {
        createSensor(input: $input) {
            id
            deviceId
            name
            description
            sensorTypeId
            locationId
            manufacturer
            model
            firmwareVersion
            hardwareVersion
            samplingInterval
            isActive
            isOnline
            createdAt
        }
    }
    """
    
    GET_SENSORS = """
    query GetSensors($locationId: String, $sensorTypeId: String, $activeOnly: Boolean, $onlineOnly: Boolean) {
        sensors(locationId: $locationId, sensorTypeId: $sensorTypeId, activeOnly: $activeOnly, onlineOnly: $onlineOnly) {
            id
            deviceId
            name
            description
            sensorTypeId
            locationId
            manufacturer
            model
            isActive
            isOnline
        }
    }
    """
    
    CREATE_SENSOR_READING = """
    mutation CreateSensorReading($input: CreateSensorReadingInput!) {
        createSensorReading(input: $input) {
            id
            sensorId
            value
            rawValue
            timestamp
            receivedAt
        }
    }
    """
    
    GET_SENSOR_READINGS = """
    query GetSensorReadings($sensorId: String!, $limit: Int, $startTime: DateTime, $endTime: DateTime) {
        sensorReadings(sensorId: $sensorId, limit: $limit, startTime: $startTime, endTime: $endTime) {
            id
            sensorId
            value
            rawValue
            timestamp
            receivedAt
        }
    }
    """
    
    DELETE_SENSOR_READINGS = """
    mutation DeleteSensorReadings($sensorId: String!) {
        deleteSensorReadings(sensorId: $sensorId)
    }
    """


@pytest.fixture
def graphql_queries():
    """Provide GraphQL queries for testing."""
    return GraphQLQueries


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def sensor_type_input(**kwargs):
        """Create sensor type input with defaults."""
        defaults = {
            "name": "Test Sensor Type",
            "description": "A test sensor type",
            "unit": "unit",
            "dataType": "float",
            "minValue": 0.0,
            "maxValue": 100.0
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def location_input(**kwargs):
        """Create location input with defaults."""
        defaults = {
            "name": "Test Location",
            "description": "A test location",
            "city": "Test City",
            "country": "Test Country",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def sensor_input(sensor_type_id, location_id, **kwargs):
        """Create sensor input with defaults."""
        defaults = {
            "deviceId": "TEST-DEVICE-001",
            "name": "Test Sensor",
            "description": "A test sensor",
            "sensorTypeId": sensor_type_id,
            "locationId": location_id,
            "manufacturer": "TestCorp",
            "model": "TestModel",
            "firmwareVersion": "1.0.0",
            "hardwareVersion": "1.0.0",
            "samplingInterval": 60
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def sensor_reading_input(sensor_id, **kwargs):
        """Create sensor reading input with defaults."""
        defaults = {
            "sensorId": sensor_id,
            "value": 25.0,
            "rawValue": 25.0
        }
        defaults.update(kwargs)
        return defaults


@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory
