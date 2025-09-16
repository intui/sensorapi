"""
Tests for sensor datapoint access functionality.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient


class TestSensorDatapoint:
    """Tests for the sensor_datapoint GraphQL resolver."""

    def test_sensor_datapoint_before(self, client: TestClient, sample_sensor_with_readings):
        """Test getting the last datapoint before a given time."""
        sensor_id, readings = sample_sensor_with_readings
        
        # Get a target time that's after the first reading but before the last
        target_time = readings[1].timestamp + timedelta(minutes=1)
        
        query = """
        query TestSensorDatapointBefore($sensorId: String!, $targetTime: DateTime!) {
            sensorDatapoint(sensorId: $sensorId, targetTime: $targetTime, direction: "before") {
                value
                timestamp
                isInterpolated
                sourceReadings {
                    timestamp
                    value
                }
            }
        }
        """
        
        response = client.post("/graphql", json={
            "query": query,
            "variables": {
                "sensorId": sensor_id,
                "targetTime": target_time.isoformat()
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        datapoint = data["data"]["sensorDatapoint"]
        assert datapoint is not None
        assert datapoint["isInterpolated"] is False
        assert len(datapoint["sourceReadings"]) == 1
        # Should return the reading at index 1 (the last one before target_time)
        assert datapoint["value"] == readings[1].value

    def test_sensor_datapoint_after(self, client: TestClient, sample_sensor_with_readings):
        """Test getting the first datapoint after a given time."""
        sensor_id, readings = sample_sensor_with_readings
        
        # Get a target time that's after the first reading but before the second
        target_time = readings[0].timestamp + timedelta(minutes=1)
        
        query = """
        query TestSensorDatapointAfter($sensorId: String!, $targetTime: DateTime!) {
            sensorDatapoint(sensorId: $sensorId, targetTime: $targetTime, direction: "after") {
                value
                timestamp
                isInterpolated
                sourceReadings {
                    timestamp
                    value
                }
            }
        }
        """
        
        response = client.post("/graphql", json={
            "query": query,
            "variables": {
                "sensorId": sensor_id,
                "targetTime": target_time.isoformat()
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        datapoint = data["data"]["sensorDatapoint"]
        assert datapoint is not None
        assert datapoint["isInterpolated"] is False
        assert len(datapoint["sourceReadings"]) == 1
        # Should return the reading at index 1 (the first one after target_time)
        assert datapoint["value"] == readings[1].value

    def test_sensor_datapoint_interpolate(self, client: TestClient, sample_sensor_with_readings):
        """Test linear interpolation between two datapoints."""
        sensor_id, readings = sample_sensor_with_readings
        
        # Get a target time exactly in the middle between first and second reading
        time_diff = readings[1].timestamp - readings[0].timestamp
        target_time = readings[0].timestamp + time_diff / 2
        
        query = """
        query TestSensorDatapointInterpolate($sensorId: String!, $targetTime: DateTime!) {
            sensorDatapoint(sensorId: $sensorId, targetTime: $targetTime, direction: "interpolate") {
                value
                timestamp
                isInterpolated
                sourceReadings {
                    timestamp
                    value
                }
            }
        }
        """
        
        response = client.post("/graphql", json={
            "query": query,
            "variables": {
                "sensorId": sensor_id,
                "targetTime": target_time.isoformat()
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        datapoint = data["data"]["sensorDatapoint"]
        assert datapoint is not None
        assert datapoint["isInterpolated"] is True
        assert len(datapoint["sourceReadings"]) == 2
        
        # The interpolated value should be the average of the two readings
        # since we're targeting the exact middle timestamp
        expected_value = (readings[0].value + readings[1].value) / 2
        assert abs(datapoint["value"] - expected_value) < 0.001

    def test_sensor_datapoint_no_data(self, client: TestClient, sample_sensor):
        """Test behavior when no readings are available."""
        sensor_id = sample_sensor
        target_time = datetime.now()
        
        query = """
        query TestSensorDatapointNoData($sensorId: String!, $targetTime: DateTime!) {
            sensorDatapoint(sensorId: $sensorId, targetTime: $targetTime, direction: "before") {
                value
                timestamp
                isInterpolated
            }
        }
        """
        
        response = client.post("/graphql", json={
            "query": query,
            "variables": {
                "sensorId": sensor_id,
                "targetTime": target_time.isoformat()
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["sensorDatapoint"] is None

    def test_sensor_datapoint_invalid_direction(self, client: TestClient, sample_sensor_with_readings):
        """Test behavior with invalid direction parameter."""
        sensor_id, readings = sample_sensor_with_readings
        target_time = readings[0].timestamp + timedelta(minutes=1)
        
        query = """
        query TestSensorDatapointInvalid($sensorId: String!, $targetTime: DateTime!) {
            sensorDatapoint(sensorId: $sensorId, targetTime: $targetTime, direction: "invalid") {
                value
                timestamp
                isInterpolated
            }
        }
        """
        
        response = client.post("/graphql", json={
            "query": query,
            "variables": {
                "sensorId": sensor_id,
                "targetTime": target_time.isoformat()
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        # Should return None for invalid direction
        assert data["data"]["sensorDatapoint"] is None