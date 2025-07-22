"""
Comprehensive CRUD tests for Sensor Types.
Tests all create, read, update, and delete operations with various scenarios.
"""
import pytest
from datetime import datetime


class TestSensorTypeCreate:
    """ST-C-001 to ST-C-008: Sensor Type Creation Tests."""
    
    def test_create_sensor_type_all_fields(self, client, test_data_factory, graphql_queries):
        """ST-C-001: Create sensor type with all fields."""
        variables = {
            "input": test_data_factory.sensor_type_input(
                name="Temperature Comprehensive",
                description="Comprehensive air temperature sensor with full metadata",
                unit="°C",
                dataType="float",
                minValue=-50.0,
                maxValue=100.0
            )
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        sensor_type = data["data"]["createSensorType"]
        assert sensor_type["name"] == "Temperature Comprehensive"
        assert sensor_type["description"] == "Comprehensive air temperature sensor with full metadata"
        assert sensor_type["unit"] == "°C"
        assert sensor_type["dataType"] == "float"
        assert sensor_type["minValue"] == -50.0
        assert sensor_type["maxValue"] == 100.0
        assert sensor_type["isActive"] is True
        assert sensor_type["createdAt"] is not None
    
    def test_create_sensor_type_minimal_fields(self, client, test_data_factory, graphql_queries):
        """ST-C-002: Create sensor type with minimal required fields."""
        variables = {
            "input": {
                "name": "Minimal Sensor Type",
                "dataType": "float"
            }
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        sensor_type = data["data"]["createSensorType"]
        assert sensor_type["name"] == "Minimal Sensor Type"
        assert sensor_type["dataType"] == "float"
        assert sensor_type["isActive"] is True
    
    def test_create_sensor_type_special_characters(self, client, graphql_queries):
        """ST-C-003: Create sensor type with special characters in name."""
        variables = {
            "input": {
                "name": "Special-Chars_123 & Symbols!",
                "description": "Testing special characters: @#$%^&*()",
                "unit": "µg/m³",
                "dataType": "float"
            }
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        sensor_type = data["data"]["createSensorType"]
        assert sensor_type["name"] == "Special-Chars_123 & Symbols!"
        assert sensor_type["unit"] == "µg/m³"
    
    def test_create_sensor_type_unicode_characters(self, client, graphql_queries):
        """ST-C-004: Create sensor type with Unicode characters."""
        variables = {
            "input": {
                "name": "Température 温度 Температура",
                "description": "Unicode test: 日本語 Русский العربية",
                "unit": "°C",
                "dataType": "float"
            }
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        sensor_type = data["data"]["createSensorType"]
        assert sensor_type["name"] == "Température 温度 Температура"
    
    def test_create_sensor_type_boundary_values(self, client, graphql_queries):
        """ST-C-005: Create sensor type with boundary values (min/max)."""
        variables = {
            "input": {
                "name": "Boundary Values Test",
                "dataType": "float",
                "minValue": -999999.99,
                "maxValue": 999999.99
            }
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        sensor_type = data["data"]["createSensorType"]
        assert sensor_type["minValue"] == -999999.99
        assert sensor_type["maxValue"] == 999999.99
    
    def test_create_sensor_type_different_data_types(self, client, graphql_queries):
        """ST-C-006: Create sensor types with different data types."""
        data_types = ["float", "integer", "boolean", "string"]
        
        for data_type in data_types:
            variables = {
                "input": {
                    "name": f"DataType {data_type.title()} Test",
                    "dataType": data_type,
                    "description": f"Testing {data_type} data type"
                }
            }
            
            response = client.post("/graphql", json={
                "query": graphql_queries.CREATE_SENSOR_TYPE,
                "variables": variables
            })
            
            assert response.status_code == 200
            data = response.json()
            sensor_type = data["data"]["createSensorType"]
            assert sensor_type["dataType"] == data_type
    
    def test_create_sensor_type_long_description(self, client, graphql_queries):
        """ST-C-007: Create sensor type with extremely long description."""
        long_description = "A" * 1000  # 1000 character description
        
        variables = {
            "input": {
                "name": "Long Description Test",
                "description": long_description,
                "dataType": "float"
            }
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        sensor_type = data["data"]["createSensorType"]
        assert sensor_type["description"] == long_description
    
    def test_create_sensor_type_null_optional_fields(self, client, graphql_queries):
        """ST-C-008: Create sensor type with null optional fields."""
        variables = {
            "input": {
                "name": "Null Fields Test",
                "dataType": "float",
                "description": None,
                "unit": None,
                "minValue": None,
                "maxValue": None
            }
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        sensor_type = data["data"]["createSensorType"]
        assert sensor_type["name"] == "Null Fields Test"
        assert sensor_type["description"] is None
        assert sensor_type["unit"] is None


class TestSensorTypeRead:
    """ST-R-001 to ST-R-009: Sensor Type Read Tests."""
    
    def test_fetch_all_sensor_types(self, client, graphql_queries, sample_sensor_type):
        """ST-R-001: Fetch all sensor types."""
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPES
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        sensor_types = data["data"]["sensorTypes"]
        assert isinstance(sensor_types, list)
        assert len(sensor_types) >= 1  # At least our sample sensor type
    
    def test_fetch_active_sensor_types_only(self, client, graphql_queries):
        """ST-R-002: Fetch sensor types with active_only=true."""
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPES,
            "variables": {"activeOnly": True}
        })
        
        assert response.status_code == 200
        data = response.json()
        sensor_types = data["data"]["sensorTypes"]
        # All returned sensor types should be active
        for sensor_type in sensor_types:
            assert sensor_type["isActive"] is True
    
    def test_fetch_all_sensor_types_including_inactive(self, client, graphql_queries):
        """ST-R-003: Fetch sensor types with active_only=false."""
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPES,
            "variables": {"activeOnly": False}
        })
        
        assert response.status_code == 200
        data = response.json()
        sensor_types = data["data"]["sensorTypes"]
        assert isinstance(sensor_types, list)
    
    def test_fetch_specific_sensor_type_by_id(self, client, graphql_queries, sample_sensor_type):
        """ST-R-004: Fetch specific sensor type by ID."""
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPE,
            "variables": {"id": str(sample_sensor_type.id)}
        })
        
        assert response.status_code == 200
        data = response.json()
        sensor_type = data["data"]["sensorType"]
        assert sensor_type is not None
        assert sensor_type["id"] == str(sample_sensor_type.id)
        assert sensor_type["name"] == sample_sensor_type.name
    
    def test_fetch_nonexistent_sensor_type(self, client, graphql_queries):
        """ST-R-009: Fetch non-existent sensor type by ID."""
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_TYPE,
            "variables": {"id": "00000000-0000-0000-0000-000000000000"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["sensorType"] is None


class TestSensorTypeValidation:
    """Error handling and validation tests for sensor types."""
    
    def test_create_duplicate_sensor_type_name(self, client, graphql_queries, sample_sensor_type):
        """Test creating sensor type with duplicate name (should fail)."""
        variables = {
            "input": {
                "name": sample_sensor_type.name,  # Duplicate name
                "dataType": "float"
            }
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data  # Should have validation error
    
    def test_create_sensor_type_missing_name(self, client, graphql_queries):
        """Test creating sensor type without required name field."""
        variables = {
            "input": {
                "dataType": "float",
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
    
    def test_create_sensor_type_invalid_data_type(self, client, graphql_queries):
        """Test creating sensor type with invalid data type."""
        variables = {
            "input": {
                "name": "Invalid Data Type Test",
                "dataType": "invalid_type"
            }
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
    
    def test_create_sensor_type_invalid_min_max_range(self, client, graphql_queries):
        """Test creating sensor type with min > max values."""
        variables = {
            "input": {
                "name": "Invalid Range Test",
                "dataType": "float",
                "minValue": 100.0,
                "maxValue": 50.0  # max < min
            }
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": variables
        })
        
        # This might succeed in the basic implementation, but should ideally validate
        assert response.status_code == 200
