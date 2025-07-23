"""
Production test configuration for testing against deployed Vercel API.
This runs tests against the live API without requiring database access.
"""
import os
import pytest
import httpx
from datetime import datetime, timedelta
import uuid

# Production API URL - update this with your actual Vercel deployment URL
PRODUCTION_API_URL = "https://sensorapi-i89wpp801-widos-projects.vercel.app"


class ProductionClient:
    """HTTP client wrapper for testing production API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0)
    
    def post(self, path: str, **kwargs):
        """Make a POST request to the production API."""
        response = self.client.post(path, **kwargs)
        return response
    
    def get(self, path: str, **kwargs):
        """Make a GET request to the production API."""
        response = self.client.get(path, **kwargs)
        return response
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


@pytest.fixture(scope="session")
def production_client():
    """Create HTTP client for production API testing."""
    client = ProductionClient(PRODUCTION_API_URL)
    yield client
    client.close()


@pytest.fixture
def test_data_factory():
    """Factory for creating test data with unique identifiers."""
    
    class TestDataFactory:
        @staticmethod
        def sensor_type_input(name=None, **kwargs):
            """Create sensor type input data."""
            unique_suffix = str(uuid.uuid4())[:8]
            return {
                "name": name or f"TestSensorType_{unique_suffix}",
                "description": kwargs.get("description", "Test sensor type"),
                "unit": kwargs.get("unit", "°C"),
                "dataType": kwargs.get("dataType", "float"),
                "minValue": kwargs.get("minValue", -50.0),
                "maxValue": kwargs.get("maxValue", 100.0),
                **kwargs
            }
        
        @staticmethod
        def location_input(name=None, **kwargs):
            """Create location input data."""
            unique_suffix = str(uuid.uuid4())[:8]
            return {
                "name": name or f"TestLocation_{unique_suffix}",
                "description": kwargs.get("description", "Test location"),
                "city": kwargs.get("city", "Test City"),
                "country": kwargs.get("country", "Test Country"),
                "latitude": kwargs.get("latitude", 40.7128),
                "longitude": kwargs.get("longitude", -74.0060),
                **kwargs
            }
        
        @staticmethod
        def sensor_input(sensor_type_id, location_id, name=None, **kwargs):
            """Create sensor input data."""
            unique_suffix = str(uuid.uuid4())[:8]
            return {
                "sensorTypeId": sensor_type_id,
                "locationId": location_id,
                "deviceId": kwargs.get("deviceId", f"TEST_{unique_suffix}"),
                "name": name or f"TestSensor_{unique_suffix}",
                "description": kwargs.get("description", "Test sensor"),
                "manufacturer": kwargs.get("manufacturer", "TestManufacturer"),
                "model": kwargs.get("model", "TestModel"),
                "firmwareVersion": kwargs.get("firmwareVersion", "1.0.0"),
                "hardwareVersion": kwargs.get("hardwareVersion", "1.0.0"),
                "samplingInterval": kwargs.get("samplingInterval", 60),
                **kwargs
            }
        
        @staticmethod
        def sensor_reading_input(sensor_id, **kwargs):
            """Create sensor reading input data."""
            return {
                "sensorId": sensor_id,
                "value": kwargs.get("value", 25.5),
                "rawValue": kwargs.get("rawValue", 25.5),
                "timestamp": kwargs.get("timestamp", datetime.utcnow().isoformat() + "Z"),
                **kwargs
            }
    
    return TestDataFactory


@pytest.fixture
def graphql_queries():
    """GraphQL query templates for testing."""
    
    class GraphQLQueries:
        # Schema introspection
        INTROSPECTION = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    kind
                }
            }
        }
        """
        
        # Sensor Type queries
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
                createdAt
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
                createdAt
            }
        }
        """
        
        # Location queries
        CREATE_LOCATION = """
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
        
        GET_LOCATIONS = """
        query GetLocations {
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
        
        # Sensor queries
        CREATE_SENSOR = """
        mutation CreateSensor($input: CreateSensorInput!) {
            createSensor(input: $input) {
                id
                deviceId
                name
                description
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
        query GetSensors {
            sensors {
                id
                deviceId
                name
                description
                manufacturer
                model
                isActive
                isOnline
                createdAt
            }
        }
        """
        
        GET_SENSOR = """
        query GetSensor($id: String!) {
            sensor(id: $id) {
                id
                deviceId
                name
                description
                manufacturer
                model
                isActive
                isOnline
                createdAt
            }
        }
        """
        
        # Sensor Reading queries
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
                value
                rawValue
                timestamp
                receivedAt
            }
        }
        """
    
    return GraphQLQueries


@pytest.fixture
def cleanup_test_data():
    """
    Fixture to help with cleanup of test data.
    Since we're testing against production, we should be careful about cleanup.
    """
    created_entities = []
    
    def register_for_cleanup(entity_type, entity_id):
        """Register an entity for cleanup after test."""
        created_entities.append((entity_type, entity_id))
    
    yield register_for_cleanup
    
    # Note: In production testing, we might want to leave some test data
    # or implement a specific cleanup strategy. For now, we'll just log
    # what was created for manual cleanup if needed.
    if created_entities:
        print(f"\nTest created {len(created_entities)} entities:")
        for entity_type, entity_id in created_entities:
            print(f"  - {entity_type}: {entity_id}")


# Helper functions for production testing
def assert_graphql_success(response, expected_operation=None):
    """Assert that a GraphQL response was successful."""
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert "data" in data, f"No 'data' field in response: {data}"
    
    if "errors" in data:
        pytest.fail(f"GraphQL errors: {data['errors']}")
    
    if expected_operation:
        assert expected_operation in data["data"], f"Expected operation '{expected_operation}' not in response"
    
    return data["data"]


def assert_graphql_error(response, expected_error_message=None):
    """Assert that a GraphQL response contains expected errors."""
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert "errors" in data, f"Expected errors in response: {data}"
    
    if expected_error_message:
        error_messages = [error.get("message", "") for error in data["errors"]]
        assert any(expected_error_message in msg for msg in error_messages), \
            f"Expected error message '{expected_error_message}' not found in: {error_messages}"
    
    return data.get("errors", [])


# Production-specific test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "production: mark test as requiring production environment"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "cleanup_required: mark test as creating data that needs cleanup"
    )
