"""
Production API tests - runs against deployed Vercel instance.
These tests validate that the production API is working correctly.

Run with: pytest tests/test_production.py -v
"""
import pytest
import uuid
import time
from datetime import datetime


@pytest.mark.production
class TestProductionHealthChecks:
    """Test basic health and connectivity of production API."""
    
    def test_production_api_health(self, production_client):
        """Test that production API is responding."""
        response = production_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "SensorAPI"
    
    def test_production_api_root(self, production_client):
        """Test root endpoint provides correct API information."""
        response = production_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "graphql_endpoint" in data
        assert data["environment"] == "production"
    
    def test_production_docs_available(self, production_client):
        """Test that API documentation is available."""
        response = production_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.production
class TestProductionGraphQLSchema:
    """Test GraphQL schema and basic operations in production."""
    
    def test_graphql_introspection(self, production_client, graphql_queries):
        """Test GraphQL schema introspection works."""
        response = production_client.post("/graphql", json={
            "query": graphql_queries.INTROSPECTION
        })
        
        from conftest_production import assert_graphql_success
        data = assert_graphql_success(response, "__schema")
        
        # Verify expected types exist
        type_names = [t["name"] for t in data["__schema"]["types"]]
        expected_types = ["SensorType", "Location", "Sensor", "SensorReading"]
        
        for expected_type in expected_types:
            assert expected_type in type_names, f"Expected type {expected_type} not found in schema"
    
    def test_invalid_query_handling(self, production_client):
        """Test that invalid GraphQL queries are handled properly."""
        response = production_client.post("/graphql", json={
            "query": "query { invalidField }"
        })
        
        from conftest_production import assert_graphql_error
        errors = assert_graphql_error(response)
        assert len(errors) > 0


@pytest.mark.production
@pytest.mark.cleanup_required
class TestProductionSensorTypeCRUD:
    """Test sensor type CRUD operations in production."""
    
    def test_create_and_read_sensor_type(self, production_client, test_data_factory, graphql_queries, cleanup_test_data):
        """Test creating and reading a sensor type in production."""
        # Create sensor type
        sensor_type_input = test_data_factory.sensor_type_input(
            name=f"ProdTest_Temperature_{uuid.uuid4().hex[:8]}",
            description="Production test temperature sensor",
            unit="°C"
        )
        
        response = production_client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": {"input": sensor_type_input}
        })
        
        from conftest_production import assert_graphql_success
        data = assert_graphql_success(response, "createSensorType")
        
        created_sensor_type = data["createSensorType"]
        assert created_sensor_type["name"] == sensor_type_input["name"]
        assert created_sensor_type["unit"] == sensor_type_input["unit"]
        assert created_sensor_type["dataType"] == sensor_type_input["dataType"]
        
        # Register for cleanup
        cleanup_test_data("sensor_type", created_sensor_type["id"])
        
        # Test reading the created sensor type
        response = production_client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPE,
            "variables": {"id": created_sensor_type["id"]}
        })
        
        data = assert_graphql_success(response, "sensorType")
        fetched_sensor_type = data["sensorType"]
        
        assert fetched_sensor_type["id"] == created_sensor_type["id"]
        assert fetched_sensor_type["name"] == sensor_type_input["name"]
    
    def test_list_sensor_types(self, production_client, graphql_queries):
        """Test listing sensor types in production."""
        response = production_client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPES,
            "variables": {"activeOnly": True}
        })
        
        from conftest_production import assert_graphql_success
        data = assert_graphql_success(response, "sensorTypes")
        
        sensor_types = data["sensorTypes"]
        assert isinstance(sensor_types, list)
        
        # All returned sensor types should be active
        for sensor_type in sensor_types:
            assert sensor_type["isActive"] is True


@pytest.mark.production
@pytest.mark.cleanup_required
class TestProductionLocationCRUD:
    """Test location CRUD operations in production."""
    
    def test_create_and_read_location(self, production_client, test_data_factory, graphql_queries, cleanup_test_data):
        """Test creating and reading a location in production."""
        # Create location
        location_input = test_data_factory.location_input(
            name=f"ProdTest_Office_{uuid.uuid4().hex[:8]}",
            city="Production City",
            country="Test Country"
        )
        
        response = production_client.post("/graphql", json={
            "query": graphql_queries.CREATE_LOCATION,
            "variables": {"input": location_input}
        })
        
        from conftest_production import assert_graphql_success
        data = assert_graphql_success(response, "createLocation")
        
        created_location = data["createLocation"]
        assert created_location["name"] == location_input["name"]
        assert created_location["city"] == location_input["city"]
        assert created_location["country"] == location_input["country"]
        
        # Register for cleanup
        cleanup_test_data("location", created_location["id"])
        
        # Test listing locations includes our new location
        response = production_client.post("/graphql", json={
            "query": graphql_queries.GET_LOCATIONS
        })
        
        data = assert_graphql_success(response, "locations")
        locations = data["locations"]
        
        # Find our created location in the list
        found_location = next(
            (loc for loc in locations if loc["id"] == created_location["id"]), 
            None
        )
        assert found_location is not None
        assert found_location["name"] == location_input["name"]


@pytest.mark.production
@pytest.mark.cleanup_required
@pytest.mark.slow
class TestProductionCompleteWorkflow:
    """Test complete end-to-end workflows in production."""
    
    def test_complete_sensor_setup_workflow(self, production_client, test_data_factory, graphql_queries, cleanup_test_data):
        """Test complete workflow: create sensor type -> location -> sensor -> reading."""
        
        # Step 1: Create sensor type
        sensor_type_input = test_data_factory.sensor_type_input(
            name=f"ProdWorkflow_Humidity_{uuid.uuid4().hex[:8]}",
            unit="%",
            dataType="float"
        )
        
        response = production_client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": {"input": sensor_type_input}
        })
        
        from conftest_production import assert_graphql_success
        data = assert_graphql_success(response, "createSensorType")
        sensor_type = data["createSensorType"]
        cleanup_test_data("sensor_type", sensor_type["id"])
        
        # Step 2: Create location
        location_input = test_data_factory.location_input(
            name=f"ProdWorkflow_Lab_{uuid.uuid4().hex[:8]}",
            city="Production Lab City"
        )
        
        response = production_client.post("/graphql", json={
            "query": graphql_queries.CREATE_LOCATION,
            "variables": {"input": location_input}
        })
        
        data = assert_graphql_success(response, "createLocation")
        location = data["createLocation"]
        cleanup_test_data("location", location["id"])
        
        # Step 3: Create sensor
        sensor_input = test_data_factory.sensor_input(
            sensor_type_id=sensor_type["id"],
            location_id=location["id"],
            name=f"ProdWorkflow_Sensor_{uuid.uuid4().hex[:8]}"
        )
        
        response = production_client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR,
            "variables": {"input": sensor_input}
        })
        
        data = assert_graphql_success(response, "createSensor")
        sensor = data["createSensor"]
        cleanup_test_data("sensor", sensor["id"])
        
        # Verify relationships
        assert sensor["deviceId"] == sensor_input["deviceId"]
        assert sensor["name"] == sensor_input["name"]
        
        # Step 4: Create sensor reading
        reading_input = test_data_factory.sensor_reading_input(
            sensor_id=sensor["id"],
            value=65.5  # Humidity percentage
        )
        
        response = production_client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_READING,
            "variables": {"input": reading_input}
        })
        
        data = assert_graphql_success(response, "createSensorReading")
        reading = data["createSensorReading"]
        cleanup_test_data("sensor_reading", reading["id"])
        
        assert reading["value"] == 65.5
        assert reading["sensorId"] == sensor["id"]  # Verify relationship
        
        # Step 5: Read back sensor readings
        response = production_client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_READINGS,
            "variables": {"sensorId": sensor["id"], "limit": 10}
        })
        
        data = assert_graphql_success(response, "sensorReadings")
        readings = data["sensorReadings"]
        
        assert len(readings) >= 1
        assert any(r["id"] == reading["id"] for r in readings)


@pytest.mark.production
class TestProductionPerformance:
    """Test production API performance and reliability."""
    
    def test_api_response_time(self, production_client):
        """Test that API responds within reasonable time."""
        start_time = time.time()
        
        response = production_client.get("/health")
        
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0, f"API response time {response_time:.2f}s is too slow"
    
    def test_graphql_query_performance(self, production_client, graphql_queries):
        """Test GraphQL query performance."""
        start_time = time.time()
        
        response = production_client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPES,
            "variables": {"activeOnly": True}
        })
        
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 10.0, f"GraphQL query time {response_time:.2f}s is too slow"
        
        from conftest_production import assert_graphql_success
        data = assert_graphql_success(response, "sensorTypes")
        assert isinstance(data["sensorTypes"], list)


@pytest.mark.production
class TestProductionErrorHandling:
    """Test error handling in production environment."""
    
    def test_invalid_sensor_type_creation(self, production_client, graphql_queries):
        """Test error handling for invalid sensor type data."""
        # Test with missing required field
        response = production_client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": {"input": {"description": "Missing name field"}}
        })
        
        from conftest_production import assert_graphql_error
        errors = assert_graphql_error(response)
        assert len(errors) > 0
    
    def test_nonexistent_entity_access(self, production_client, graphql_queries):
        """Test accessing non-existent entities."""
        fake_id = str(uuid.uuid4())
        
        response = production_client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPE,
            "variables": {"id": fake_id}
        })
        
        # Should return success with null data for non-existent entity
        from conftest_production import assert_graphql_success
        data = assert_graphql_success(response, "sensorType")
        assert data["sensorType"] is None
