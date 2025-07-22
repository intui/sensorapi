"""
Elementary tests for Sensor API.
These tests verify basic functionality and system health.
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthChecks:
    """API-001 to API-003: Basic health check tests."""
    
    def test_server_startup_and_health(self, client: TestClient):
        """API-001: Server startup and health endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Welcome to SensorAPI" == data["message"]
    
    def test_graphql_playground_accessibility(self, client: TestClient):
        """API-002: GraphQL playground accessibility."""
        response = client.get("/graphql")
        assert response.status_code == 200
        # GraphQL playground should return HTML
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_docs_endpoint(self, client: TestClient):
        """API-003: API documentation accessibility."""
        response = client.get("/docs")
        assert response.status_code == 200


class TestGraphQLSchema:
    """GQL-001 to GQL-004: Basic GraphQL schema tests."""
    
    def test_schema_introspection(self, client: TestClient):
        """GQL-001: Schema introspection."""
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                }
            }
        }
        """
        
        response = client.post("/graphql", json={"query": introspection_query})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "__schema" in data["data"]
        
        # Check that our custom types exist
        type_names = [t["name"] for t in data["data"]["__schema"]["types"]]
        assert "SensorType" in type_names
        assert "Location" in type_names
        assert "Sensor" in type_names
        assert "SensorReading" in type_names
    
    def test_query_structure_validation(self, client: TestClient):
        """GQL-002: Query structure validation."""
        # Valid query
        valid_query = """
        query {
            sensorTypes {
                id
                name
            }
        }
        """
        
        response = client.post("/graphql", json={"query": valid_query})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "sensorTypes" in data["data"]
    
    def test_mutation_structure_validation(self, client: TestClient, test_data_factory):
        """GQL-003: Mutation structure validation."""
        # Valid mutation
        mutation = """
        mutation CreateSensorType($input: CreateSensorTypeInput!) {
            createSensorType(input: $input) {
                id
                name
            }
        }
        """
        
        variables = {
            "input": test_data_factory.sensor_type_input(name="Test Type Schema Validation")
        }
        
        response = client.post("/graphql", json={"query": mutation, "variables": variables})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createSensorType" in data["data"]
        assert data["data"]["createSensorType"]["name"] == "Test Type Schema Validation"
    
    def test_invalid_query_error_handling(self, client: TestClient):
        """GQL-004: Invalid query error handling."""
        invalid_query = """
        query {
            nonExistentField {
                id
            }
        }
        """
        
        response = client.post("/graphql", json={"query": invalid_query})
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data


class TestBasicCRUDOperations:
    """CRUD-001 to CRUD-005: Basic CRUD smoke tests."""
    
    def test_create_sensor_type(self, client: TestClient, test_data_factory, graphql_queries):
        """CRUD-001: Create a sensor type."""
        variables = {
            "input": test_data_factory.sensor_type_input(name="CRUD Test Temperature")
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createSensorType" in data["data"]
        sensor_type = data["data"]["createSensorType"]
        assert sensor_type["name"] == "CRUD Test Temperature"
        assert sensor_type["isActive"] is True
    
    def test_read_sensor_types_list(self, client: TestClient, graphql_queries):
        """CRUD-002: Read sensor types list."""
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPES,
            "variables": {"activeOnly": True}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "sensorTypes" in data["data"]
        assert isinstance(data["data"]["sensorTypes"], list)
    
    def test_create_location(self, client: TestClient, test_data_factory, graphql_queries):
        """CRUD-003: Create a location."""
        variables = {
            "input": test_data_factory.location_input(name="CRUD Test Location")
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_LOCATION,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createLocation" in data["data"]
        location = data["data"]["createLocation"]
        assert location["name"] == "CRUD Test Location"
        assert location["isActive"] is True
    
    def test_create_sensor(self, client: TestClient, test_data_factory, graphql_queries, sample_sensor_type, sample_location):
        """CRUD-004: Create a sensor."""
        variables = {
            "input": test_data_factory.sensor_input(
                sensor_type_id=str(sample_sensor_type.id),
                location_id=str(sample_location.id),
                name="CRUD Test Sensor",
                deviceId="CRUD-TEST-001"
            )
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createSensor" in data["data"]
        sensor = data["data"]["createSensor"]
        assert sensor["name"] == "CRUD Test Sensor"
        assert sensor["deviceId"] == "CRUD-TEST-001"
        assert sensor["isActive"] is True
    
    def test_create_sensor_reading(self, client: TestClient, test_data_factory, graphql_queries, sample_sensor):
        """CRUD-005: Create a sensor reading."""
        variables = {
            "input": test_data_factory.sensor_reading_input(
                sensor_id=str(sample_sensor.id),
                value=22.5,
                rawValue=22.5
            )
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_READING,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createSensorReading" in data["data"]
        reading = data["data"]["createSensorReading"]
        assert reading["value"] == 22.5
        assert reading["rawValue"] == 22.5
        assert reading["sensorId"] == str(sample_sensor.id)


class TestErrorHandlingBasics:
    """Basic error handling tests."""
    
    def test_invalid_graphql_syntax(self, client: TestClient):
        """Test handling of invalid GraphQL syntax."""
        invalid_query = "query { invalid syntax }"
        
        response = client.post("/graphql", json={"query": invalid_query})
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
    
    def test_missing_required_fields(self, client: TestClient, graphql_queries):
        """Test handling of missing required fields."""
        # Try to create sensor type without required name field
        variables = {
            "input": {
                "description": "Missing name field"
            }
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
    
    def test_invalid_uuid_format(self, client: TestClient, graphql_queries):
        """Test handling of invalid UUID format."""
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPE,
            "variables": {"id": "invalid-uuid"}
        })
        
        assert response.status_code == 200
        data = response.json()
        # Should either return null or error depending on implementation
        assert "data" in data or "errors" in data
    
    def test_nonexistent_entity_access(self, client: TestClient, graphql_queries):
        """Test accessing non-existent entities."""
        # Try to get sensor readings for non-existent sensor
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_READINGS,
            "variables": {"sensorId": "00000000-0000-0000-0000-000000000000"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        # Should return empty list for non-existent sensor
        assert data["data"]["sensorReadings"] == []
