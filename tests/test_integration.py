"""
Integration tests for Sensor API workflows.
Tests complete end-to-end scenarios and cross-entity operations.
"""
import pytest
from datetime import datetime, timedelta


class TestCompleteWorkflows:
    """Integration tests for complete sensor data workflows."""
    
    def test_complete_sensor_setup_workflow(self, client, test_data_factory, graphql_queries):
        """INT-001: Create complete sensor setup (type → location → sensor → readings)."""
        
        # Step 1: Create sensor type
        sensor_type_vars = {
            "input": test_data_factory.sensor_type_input(
                name="Integration Test Temperature",
                unit="°C",
                dataType="float",
                minValue=-40.0,
                maxValue=80.0
            )
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": sensor_type_vars
        })
        
        assert response.status_code == 200
        sensor_type_data = response.json()["data"]["createSensorType"]
        sensor_type_id = sensor_type_data["id"]
        
        # Step 2: Create location
        location_vars = {
            "input": test_data_factory.location_input(
                name="Integration Test Building",
                city="Test City",
                country="Test Country"
            )
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_LOCATION,
            "variables": location_vars
        })
        
        assert response.status_code == 200
        location_data = response.json()["data"]["createLocation"]
        location_id = location_data["id"]
        
        # Step 3: Create sensor
        sensor_vars = {
            "input": test_data_factory.sensor_input(
                sensor_type_id=sensor_type_id,
                location_id=location_id,
                name="Integration Test Sensor",
                deviceId="INTEGRATION-001"
            )
        }
        
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR,
            "variables": sensor_vars
        })
        
        assert response.status_code == 200
        sensor_data = response.json()["data"]["createSensor"]
        sensor_id = sensor_data["id"]
        
        # Step 4: Create multiple sensor readings
        reading_values = [20.5, 21.0, 20.8, 21.2, 20.9]
        reading_ids = []
        
        for value in reading_values:
            reading_vars = {
                "input": test_data_factory.sensor_reading_input(
                    sensor_id=sensor_id,
                    value=value,
                    rawValue=value
                )
            }
            
            response = client.post("/graphql", json={
                "query": graphql_queries.CREATE_SENSOR_READING,
                "variables": reading_vars
            })
            
            assert response.status_code == 200
            reading_data = response.json()["data"]["createSensorReading"]
            reading_ids.append(reading_data["id"])
        
        # Step 5: Verify complete setup by querying readings
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_READINGS,
            "variables": {"sensorId": sensor_id, "limit": 10}
        })
        
        assert response.status_code == 200
        readings_data = response.json()["data"]["sensorReadings"]
        assert len(readings_data) == 5
        
        # Verify all readings have correct sensor ID
        for reading in readings_data:
            assert reading["sensorId"] == sensor_id
            assert reading["value"] in reading_values
    
    def test_sensor_with_multiple_types_and_locations(self, client, test_data_factory, graphql_queries):
        """INT-002: Test sensors across multiple types and locations."""
        
        # Create multiple sensor types
        sensor_types = []
        for type_name in ["Temperature", "Humidity", "Pressure"]:
            vars = {
                "input": test_data_factory.sensor_type_input(
                    name=f"Multi-{type_name}",
                    dataType="float"
                )
            }
            
            response = client.post("/graphql", json={
                "query": graphql_queries.CREATE_SENSOR_TYPE,
                "variables": vars
            })
            
            assert response.status_code == 200
            sensor_types.append(response.json()["data"]["createSensorType"])
        
        # Create multiple locations
        locations = []
        for location_name in ["Building A", "Building B", "Building C"]:
            vars = {
                "input": test_data_factory.location_input(
                    name=f"Multi-{location_name}",
                    city="Multi City"
                )
            }
            
            response = client.post("/graphql", json={
                "query": graphql_queries.CREATE_LOCATION,
                "variables": vars
            })
            
            assert response.status_code == 200
            locations.append(response.json()["data"]["createLocation"])
        
        # Create sensors for each type/location combination
        sensors = []
        for i, sensor_type in enumerate(sensor_types):
            for j, location in enumerate(locations):
                vars = {
                    "input": test_data_factory.sensor_input(
                        sensor_type_id=sensor_type["id"],
                        location_id=location["id"],
                        name=f"Multi-Sensor-{i}-{j}",
                        deviceId=f"MULTI-{i}-{j}"
                    )
                }
                
                response = client.post("/graphql", json={
                    "query": graphql_queries.CREATE_SENSOR,
                    "variables": vars
                })
                
                assert response.status_code == 200
                sensors.append(response.json()["data"]["createSensor"])
        
        # Verify we created 9 sensors (3 types × 3 locations)
        assert len(sensors) == 9
        
        # Test filtering by sensor type
        for sensor_type in sensor_types:
            response = client.post("/graphql", json={
                "query": graphql_queries.GET_SENSORS,
                "variables": {"sensorTypeId": sensor_type["id"]}
            })
            
            assert response.status_code == 200
            filtered_sensors = response.json()["data"]["sensors"]
            # Should have 3 sensors (one in each location)
            type_sensors = [s for s in filtered_sensors if s["sensorTypeId"] == sensor_type["id"]]
            assert len(type_sensors) == 3
        
        # Test filtering by location
        for location in locations:
            response = client.post("/graphql", json={
                "query": graphql_queries.GET_SENSORS,
                "variables": {"locationId": location["id"]}
            })
            
            assert response.status_code == 200
            filtered_sensors = response.json()["data"]["sensors"]
            # Should have 3 sensors (one of each type)
            location_sensors = [s for s in filtered_sensors if s["locationId"] == location["id"]]
            assert len(location_sensors) == 3
    
    def test_data_consistency_with_concurrent_operations(self, client, test_data_factory, graphql_queries, sample_sensor):
        """INT-003: Test data consistency with multiple operations."""
        
        # Create multiple readings rapidly
        reading_values = [i * 0.1 for i in range(1, 21)]  # 20 readings
        created_readings = []
        
        for value in reading_values:
            vars = {
                "input": test_data_factory.sensor_reading_input(
                    sensor_id=str(sample_sensor.id),
                    value=value,
                    rawValue=value
                )
            }
            
            response = client.post("/graphql", json={
                "query": graphql_queries.CREATE_SENSOR_READING,
                "variables": vars
            })
            
            assert response.status_code == 200
            created_readings.append(response.json()["data"]["createSensorReading"])
        
        # Verify all readings were created
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_READINGS,
            "variables": {"sensorId": str(sample_sensor.id), "limit": 50}
        })
        
        assert response.status_code == 200
        all_readings = response.json()["data"]["sensorReadings"]
        
        # Should have at least our 20 new readings plus any existing ones
        new_readings = [r for r in all_readings if r["value"] in reading_values]
        assert len(new_readings) == 20
        
        # Verify readings are ordered by timestamp (most recent first)
        timestamps = [datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")) for r in all_readings]
        assert timestamps == sorted(timestamps, reverse=True)
    
    def test_delete_cascade_behavior(self, client, test_data_factory, graphql_queries):
        """INT-004: Test cascade delete behavior."""
        
        # Create complete setup
        sensor_type_vars = {
            "input": test_data_factory.sensor_type_input(name="Cascade Test Type")
        }
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR_TYPE,
            "variables": sensor_type_vars
        })
        sensor_type_id = response.json()["data"]["createSensorType"]["id"]
        
        location_vars = {
            "input": test_data_factory.location_input(name="Cascade Test Location")
        }
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_LOCATION,
            "variables": location_vars
        })
        location_id = response.json()["data"]["createLocation"]["id"]
        
        sensor_vars = {
            "input": test_data_factory.sensor_input(
                sensor_type_id=sensor_type_id,
                location_id=location_id,
                name="Cascade Test Sensor",
                deviceId="CASCADE-001"
            )
        }
        response = client.post("/graphql", json={
            "query": graphql_queries.CREATE_SENSOR,
            "variables": sensor_vars
        })
        sensor_id = response.json()["data"]["createSensor"]["id"]
        
        # Create readings
        for i in range(5):
            reading_vars = {
                "input": test_data_factory.sensor_reading_input(
                    sensor_id=sensor_id,
                    value=float(i),
                    rawValue=float(i)
                )
            }
            response = client.post("/graphql", json={
                "query": graphql_queries.CREATE_SENSOR_READING,
                "variables": reading_vars
            })
            assert response.status_code == 200
        
        # Verify readings exist
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_READINGS,
            "variables": {"sensorId": sensor_id}
        })
        readings = response.json()["data"]["sensorReadings"]
        assert len(readings) == 5
        
        # Delete all readings for the sensor
        response = client.post("/graphql", json={
            "query": graphql_queries.DELETE_SENSOR_READINGS,
            "variables": {"sensorId": sensor_id}
        })
        
        assert response.status_code == 200
        delete_result = response.json()["data"]["deleteSensorReadings"]
        assert delete_result is True
        
        # Verify readings are deleted
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSOR_READINGS,
            "variables": {"sensorId": sensor_id}
        })
        readings = response.json()["data"]["sensorReadings"]
        assert len(readings) == 0


class TestGraphQLAdvanced:
    """Advanced GraphQL operation tests."""
    
    def test_complex_nested_query(self, client, sample_sensor):
        """GQL-ADV-001: Complex nested queries."""
        complex_query = """
        query ComplexSensorQuery($sensorId: String!) {
            sensor(id: $sensorId) {
                id
                deviceId
                name
                isActive
                isOnline
                sensorType {
                    id
                    name
                    unit
                    dataType
                    minValue
                    maxValue
                }
                location {
                    id
                    name
                    city
                    country
                    latitude
                    longitude
                }
            }
            sensorReadings(sensorId: $sensorId, limit: 3) {
                id
                value
                rawValue
                timestamp
                receivedAt
            }
        }
        """
        
        response = client.post("/graphql", json={
            "query": complex_query,
            "variables": {"sensorId": str(sample_sensor.id)}
        })
        
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Verify nested sensor data
        sensor_data = data["sensor"]
        assert sensor_data["id"] == str(sample_sensor.id)
        assert "sensorType" in sensor_data
        assert "location" in sensor_data
        assert sensor_data["sensorType"]["name"] is not None
        assert sensor_data["location"]["name"] is not None
        
        # Verify readings data
        readings_data = data["sensorReadings"]
        assert isinstance(readings_data, list)
    
    def test_batch_mutations(self, client, test_data_factory, graphql_queries, sample_sensor_type, sample_location):
        """GQL-ADV-005: Batch mutations (multiple sensors)."""
        
        # Create multiple sensors in sequence (simulating batch operations)
        sensor_names = ["Batch Sensor 1", "Batch Sensor 2", "Batch Sensor 3"]
        created_sensors = []
        
        for i, name in enumerate(sensor_names):
            vars = {
                "input": test_data_factory.sensor_input(
                    sensor_type_id=str(sample_sensor_type.id),
                    location_id=str(sample_location.id),
                    name=name,
                    deviceId=f"BATCH-{i+1:03d}"
                )
            }
            
            response = client.post("/graphql", json={
                "query": graphql_queries.CREATE_SENSOR,
                "variables": vars
            })
            
            assert response.status_code == 200
            created_sensors.append(response.json()["data"]["createSensor"])
        
        # Verify all sensors were created
        assert len(created_sensors) == 3
        for i, sensor in enumerate(created_sensors):
            assert sensor["name"] == sensor_names[i]
            assert sensor["deviceId"] == f"BATCH-{i+1:03d}"
        
        # Verify we can query all sensors by location
        response = client.post("/graphql", json={
            "query": graphql_queries.GET_SENSORS,
            "variables": {"locationId": str(sample_location.id)}
        })
        
        assert response.status_code == 200
        location_sensors = response.json()["data"]["sensors"]
        
        # Should include our batch sensors plus any existing ones
        batch_sensor_ids = [s["id"] for s in created_sensors]
        found_batch_sensors = [s for s in location_sensors if s["id"] in batch_sensor_ids]
        assert len(found_batch_sensors) == 3
