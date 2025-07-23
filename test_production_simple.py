#!/usr/bin/env python3
"""
Simple production API test - self-contained test without external dependencies.
Tests the deployed Vercel API endpoints directly.

Usage: python test_production_simple.py
"""

import httpx
import json
import uuid
import time
from datetime import datetime


PRODUCTION_URL = "https://sensorapi-cpbpps2rw-widos-projects.vercel.app"


def test_api_health():
    """Test production API health endpoint."""
    print("🔍 Testing API health...")
    
    with httpx.Client(timeout=30.0) as client:
        response = client.get(f"{PRODUCTION_URL}/health")
        
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        
        data = response.json()
        assert data["status"] == "healthy", f"API not healthy: {data}"
        assert data["service"] == "SensorAPI", f"Wrong service name: {data}"
        
        print(f"✅ Health check passed: {data}")


def test_api_root():
    """Test production API root endpoint."""
    print("🔍 Testing API root...")
    
    with httpx.Client(timeout=30.0) as client:
        response = client.get(f"{PRODUCTION_URL}/")
        
        assert response.status_code == 200, f"Root endpoint failed: {response.status_code}"
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["environment"] == "production"
        
        print(f"✅ Root endpoint passed: {data}")


def test_graphql_schema():
    """Test GraphQL schema introspection."""
    print("🔍 Testing GraphQL schema...")
    
    introspection_query = """
    query {
        __schema {
            types {
                name
                kind
            }
        }
    }
    """
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(f"{PRODUCTION_URL}/graphql", json={
            "query": introspection_query
        })
        
        assert response.status_code == 200, f"GraphQL introspection failed: {response.status_code}"
        
        data = response.json()
        assert "data" in data, f"No data in GraphQL response: {data}"
        assert "__schema" in data["data"], f"No schema in response: {data}"
        
        # Check for expected types
        type_names = [t["name"] for t in data["data"]["__schema"]["types"]]
        expected_types = ["SensorType", "Location", "Sensor", "SensorReading"]
        
        for expected_type in expected_types:
            assert expected_type in type_names, f"Type {expected_type} not found in schema"
        
        print(f"✅ GraphQL schema introspection passed, found {len(type_names)} types")


def test_sensor_type_operations():
    """Test basic sensor type CRUD operations."""
    print("🔍 Testing sensor type operations...")
    
    # Create a unique sensor type
    unique_id = uuid.uuid4().hex[:8]
    sensor_type_name = f"ProdTest_Temperature_{unique_id}"
    
    create_mutation = """
    mutation CreateSensorType($input: CreateSensorTypeInput!) {
        createSensorType(input: $input) {
            id
            name
            description
            unit
            dataType
            isActive
            createdAt
        }
    }
    """
    
    variables = {
        "input": {
            "name": sensor_type_name,
            "description": "Production test temperature sensor",
            "unit": "°C",
            "dataType": "float",
            "minValue": -50.0,
            "maxValue": 100.0
        }
    }
    
    with httpx.Client(timeout=30.0) as client:
        # Create sensor type
        response = client.post(f"{PRODUCTION_URL}/graphql", json={
            "query": create_mutation,
            "variables": variables
        })
        
        assert response.status_code == 200, f"Create sensor type failed: {response.status_code}"
        
        data = response.json()
        assert "data" in data, f"No data in response: {data}"
        assert "createSensorType" in data["data"], f"No createSensorType in response: {data}"
        
        created_sensor_type = data["data"]["createSensorType"]
        assert created_sensor_type["name"] == sensor_type_name
        assert created_sensor_type["unit"] == "°C"
        
        print(f"✅ Created sensor type: {created_sensor_type['id']}")
        
        # List sensor types
        list_query = """
        query {
            sensorTypes(activeOnly: true) {
                id
                name
                unit
                isActive
            }
        }
        """
        
        response = client.post(f"{PRODUCTION_URL}/graphql", json={
            "query": list_query
        })
        
        assert response.status_code == 200, f"List sensor types failed: {response.status_code}"
        
        data = response.json()
        assert "data" in data
        assert "sensorTypes" in data["data"]
        
        sensor_types = data["data"]["sensorTypes"]
        assert isinstance(sensor_types, list)
        
        # Find our created sensor type
        found_sensor_type = next(
            (st for st in sensor_types if st["id"] == created_sensor_type["id"]), 
            None
        )
        assert found_sensor_type is not None, "Created sensor type not found in list"
        
        print(f"✅ Found created sensor type in list of {len(sensor_types)} sensor types")


def test_api_performance():
    """Test API response times."""
    print("🔍 Testing API performance...")
    
    with httpx.Client(timeout=30.0) as client:
        # Test health endpoint performance
        start_time = time.time()
        response = client.get(f"{PRODUCTION_URL}/health")
        health_time = time.time() - start_time
        
        assert response.status_code == 200
        assert health_time < 5.0, f"Health endpoint too slow: {health_time:.2f}s"
        
        # Test GraphQL performance
        start_time = time.time()
        response = client.post(f"{PRODUCTION_URL}/graphql", json={
            "query": "query { sensorTypes(activeOnly: true) { id name } }"
        })
        graphql_time = time.time() - start_time
        
        assert response.status_code == 200
        assert graphql_time < 10.0, f"GraphQL query too slow: {graphql_time:.2f}s"
        
        print(f"✅ Performance test passed - Health: {health_time:.2f}s, GraphQL: {graphql_time:.2f}s")


def test_error_handling():
    """Test API error handling."""
    print("🔍 Testing error handling...")
    
    with httpx.Client(timeout=30.0) as client:
        # Test invalid GraphQL query
        response = client.post(f"{PRODUCTION_URL}/graphql", json={
            "query": "query { invalidField }"
        })
        
        assert response.status_code == 200  # GraphQL returns 200 even for errors
        
        data = response.json()
        assert "errors" in data, "Expected errors for invalid query"
        
        print(f"✅ Error handling test passed - Got {len(data['errors'])} errors as expected")


def main():
    """Run all production tests."""
    print(f"🚀 Running production tests against: {PRODUCTION_URL}")
    print("=" * 60)
    
    tests = [
        test_api_health,
        test_api_root,
        test_graphql_schema,
        test_sensor_type_operations,
        test_api_performance,
        test_error_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All production tests passed!")
        return 0
    else:
        print(f"⚠️  {failed} tests failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
