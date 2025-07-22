# Sensor API Testing Plan

## Overview

This document outlines a comprehensive testing strategy for the Sensor API, covering both elementary tests and in-depth CRUD operations across all entities and scenarios.

## Table of Contents

1. [Test Environment Setup](#test-environment-setup)
2. [Elementary Tests](#elementary-tests)
3. [Comprehensive CRUD Tests](#comprehensive-crud-tests)
4. [Integration Tests](#integration-tests)
5. [Performance Tests](#performance-tests)
6. [Error Handling Tests](#error-handling-tests)
7. [Security Tests](#security-tests)
8. [Data Consistency Tests](#data-consistency-tests)
9. [Test Implementation Guide](#test-implementation-guide)

---

## Test Environment Setup

### Prerequisites
- Python 3.8+
- PostgreSQL test database
- pytest and testing dependencies
- GraphQL client for API testing

### Test Dependencies
```bash
pip install pytest pytest-asyncio httpx strawberry-graphql[debug-server] factory-boy faker
```

### Environment Configuration
```bash
# .env.test
DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/sensor_test_db
APP_NAME=SensorAPI_Test
DEBUG=True
ENVIRONMENT=test
```

---

## Elementary Tests

### 1. Health Check Tests
- **API-001**: Server startup and health endpoint
- **API-002**: GraphQL playground accessibility
- **API-003**: Database connection verification

### 2. Basic GraphQL Schema Tests
- **GQL-001**: Schema introspection
- **GQL-002**: Query structure validation
- **GQL-003**: Mutation structure validation
- **GQL-004**: Type definitions verification

### 3. Database Connection Tests
- **DB-001**: Database connectivity
- **DB-002**: Migration verification
- **DB-003**: Table structure validation
- **DB-004**: Index verification

### 4. Basic CRUD Smoke Tests
- **CRUD-001**: Create a sensor type
- **CRUD-002**: Read sensor types list
- **CRUD-003**: Create a location
- **CRUD-004**: Create a sensor
- **CRUD-005**: Create a sensor reading

---

## Comprehensive CRUD Tests

### Sensor Types (`api_sensor_types`)

#### Create Operations
- **ST-C-001**: Create sensor type with all fields
- **ST-C-002**: Create sensor type with minimal required fields
- **ST-C-003**: Create sensor type with special characters in name
- **ST-C-004**: Create sensor type with Unicode characters
- **ST-C-005**: Create sensor type with boundary values (min/max)
- **ST-C-006**: Create sensor type with different data types (float, integer, boolean, string)
- **ST-C-007**: Create sensor type with extremely long description
- **ST-C-008**: Create sensor type with null optional fields

#### Read Operations
- **ST-R-001**: Fetch all sensor types
- **ST-R-002**: Fetch sensor types with active_only=true
- **ST-R-003**: Fetch sensor types with active_only=false
- **ST-R-004**: Fetch specific sensor type by ID
- **ST-R-005**: Fetch sensor type with related sensors
- **ST-R-006**: Fetch sensor types ordered by name
- **ST-R-007**: Fetch sensor types ordered by created_at
- **ST-R-008**: Fetch sensor types with pagination
- **ST-R-009**: Fetch non-existent sensor type by ID

#### Update Operations
- **ST-U-001**: Update sensor type name
- **ST-U-002**: Update sensor type description
- **ST-U-003**: Update sensor type unit
- **ST-U-004**: Update sensor type min/max values
- **ST-U-005**: Update sensor type data_type
- **ST-U-006**: Update sensor type is_active status
- **ST-U-007**: Update multiple fields simultaneously
- **ST-U-008**: Update with null values for optional fields
- **ST-U-009**: Update non-existent sensor type

#### Delete Operations
- **ST-D-001**: Soft delete sensor type (set is_active=false)
- **ST-D-002**: Hard delete sensor type without dependencies
- **ST-D-003**: Attempt to delete sensor type with dependent sensors
- **ST-D-004**: Delete non-existent sensor type
- **ST-D-005**: Cascade delete validation

### Locations (`api_locations`)

#### Create Operations
- **LOC-C-001**: Create root location (no parent)
- **LOC-C-002**: Create child location with parent
- **LOC-C-003**: Create location with full address details
- **LOC-C-004**: Create location with GPS coordinates
- **LOC-C-005**: Create location with boundary coordinates (poles, equator)
- **LOC-C-006**: Create location with invalid coordinates
- **LOC-C-007**: Create location with duplicate name in same parent
- **LOC-C-008**: Create location with duplicate name in different parent
- **LOC-C-009**: Create deeply nested location hierarchy (5+ levels)

#### Read Operations
- **LOC-R-001**: Fetch all locations
- **LOC-R-002**: Fetch locations with hierarchical structure
- **LOC-R-003**: Fetch locations by parent_id
- **LOC-R-004**: Fetch root locations (parent_id is null)
- **LOC-R-005**: Fetch location with all child locations
- **LOC-R-006**: Fetch location path (from root to specific location)
- **LOC-R-007**: Fetch locations within geographic bounds
- **LOC-R-008**: Fetch locations by city/country
- **LOC-R-009**: Fetch locations with sensor count

#### Update Operations
- **LOC-U-001**: Update location name
- **LOC-U-002**: Update location parent (move in hierarchy)
- **LOC-U-003**: Update GPS coordinates
- **LOC-U-004**: Update address details
- **LOC-U-005**: Update location to root (remove parent)
- **LOC-U-006**: Create circular reference (location as its own ancestor)
- **LOC-U-007**: Update location description
- **LOC-U-008**: Update location activity status

#### Delete Operations
- **LOC-D-001**: Delete leaf location (no children, no sensors)
- **LOC-D-002**: Delete location with child locations
- **LOC-D-003**: Delete location with associated sensors
- **LOC-D-004**: Delete location with both children and sensors
- **LOC-D-005**: Soft delete vs hard delete behavior

### Sensors (`api_sensors`)

#### Create Operations
- **SEN-C-001**: Create sensor with all fields
- **SEN-C-002**: Create sensor with minimal required fields
- **SEN-C-003**: Create sensor with duplicate device_id (should fail)
- **SEN-C-004**: Create sensor with invalid sensor_type_id
- **SEN-C-005**: Create sensor with invalid location_id
- **SEN-C-006**: Create sensor with future calibration_date
- **SEN-C-007**: Create sensor with past calibration_date
- **SEN-C-008**: Create sensor with extreme sampling_interval values
- **SEN-C-009**: Create multiple sensors in same location
- **SEN-C-010**: Create sensor with version strings containing special chars

#### Read Operations
- **SEN-R-001**: Fetch all sensors
- **SEN-R-002**: Fetch sensors by location_id
- **SEN-R-003**: Fetch sensors by sensor_type_id
- **SEN-R-004**: Fetch sensors with both location and type filters
- **SEN-R-005**: Fetch active sensors only
- **SEN-R-006**: Fetch online sensors only
- **SEN-R-007**: Fetch sensor by device_id
- **SEN-R-008**: Fetch sensor with related data (type, location)
- **SEN-R-009**: Fetch sensors with reading count
- **SEN-R-010**: Fetch sensors ordered by last_seen
- **SEN-R-011**: Fetch sensors by calibration status

#### Update Operations
- **SEN-U-001**: Update sensor name
- **SEN-U-002**: Update sensor location
- **SEN-U-003**: Update sensor type
- **SEN-U-004**: Update sensor online status
- **SEN-U-005**: Update sensor calibration date
- **SEN-U-006**: Update sensor firmware version
- **SEN-U-007**: Update sensor sampling interval
- **SEN-U-008**: Update sensor last_seen timestamp
- **SEN-U-009**: Update sensor with invalid references
- **SEN-U-010**: Bulk update multiple sensors

#### Delete Operations
- **SEN-D-001**: Delete sensor without readings
- **SEN-D-002**: Delete sensor with readings
- **SEN-D-003**: Soft delete sensor (set is_active=false)
- **SEN-D-004**: Delete sensor and verify reading cleanup
- **SEN-D-005**: Delete sensor referenced by alerts

### Sensor Readings (`api_sensor_readings`)

#### Create Operations
- **SR-C-001**: Create reading with current timestamp
- **SR-C-002**: Create reading with custom timestamp
- **SR-C-003**: Create reading with future timestamp
- **SR-C-004**: Create reading with past timestamp
- **SR-C-005**: Create reading with null raw_value
- **SR-C-006**: Create reading with same value and raw_value
- **SR-C-007**: Create reading with different value and raw_value
- **SR-C-008**: Create reading with boundary values (min/max from sensor type)
- **SR-C-009**: Create reading outside sensor type range
- **SR-C-010**: Create reading with invalid sensor_id
- **SR-C-011**: Bulk create multiple readings
- **SR-C-012**: Create reading with extremely precise values
- **SR-C-013**: Create reading with negative values
- **SR-C-014**: Create reading with zero value

#### Read Operations
- **SR-R-001**: Fetch readings for specific sensor
- **SR-R-002**: Fetch readings with time range filter
- **SR-R-003**: Fetch readings with limit
- **SR-R-004**: Fetch readings ordered by timestamp (desc)
- **SR-R-005**: Fetch readings ordered by timestamp (asc)
- **SR-R-006**: Fetch latest reading for sensor
- **SR-R-007**: Fetch oldest reading for sensor
- **SR-R-008**: Fetch readings with sensor details
- **SR-R-009**: Fetch readings by value range
- **SR-R-010**: Fetch readings for multiple sensors
- **SR-R-011**: Fetch readings with aggregation (avg, min, max)
- **SR-R-012**: Fetch readings with time-based grouping

#### Update Operations
- **SR-U-001**: Update reading value
- **SR-U-002**: Update reading timestamp
- **SR-U-003**: Update reading raw_value
- **SR-U-004**: Update reading with validation against sensor type
- **SR-U-005**: Bulk update readings
- **SR-U-006**: Update non-existent reading

#### Delete Operations
- **SR-D-001**: Delete specific reading by ID
- **SR-D-002**: Delete all readings for sensor (implemented mutation)
- **SR-D-003**: Delete readings by time range
- **SR-D-004**: Delete readings by value range
- **SR-D-005**: Bulk delete multiple readings
- **SR-D-006**: Delete readings and verify data integrity

### Alerts (`api_alerts`)

#### Create Operations
- **AL-C-001**: Create threshold alert
- **AL-C-002**: Create anomaly alert
- **AL-C-003**: Create communication alert
- **AL-C-004**: Create alert with all severity levels
- **AL-C-005**: Create alert with custom message
- **AL-C-006**: Create alert with metadata
- **AL-C-007**: Create alert for non-existent sensor

#### Read Operations
- **AL-R-001**: Fetch all alerts
- **AL-R-002**: Fetch alerts by sensor
- **AL-R-003**: Fetch alerts by severity
- **AL-R-004**: Fetch alerts by type
- **AL-R-005**: Fetch active alerts only
- **AL-R-006**: Fetch resolved alerts only
- **AL-R-007**: Fetch alerts by time range

#### Update Operations
- **AL-U-001**: Resolve alert
- **AL-U-002**: Update alert severity
- **AL-U-003**: Update alert message
- **AL-U-004**: Add alert metadata

#### Delete Operations
- **AL-D-001**: Delete resolved alerts
- **AL-D-002**: Delete old alerts
- **AL-D-003**: Delete alerts by sensor

---

## Integration Tests

### Cross-Entity Operations
- **INT-001**: Create complete sensor setup (type → location → sensor → readings)
- **INT-002**: Verify cascade operations
- **INT-003**: Test referential integrity
- **INT-004**: Test transaction rollback scenarios
- **INT-005**: Test concurrent operations

### GraphQL Advanced Queries
- **GQL-ADV-001**: Complex nested queries
- **GQL-ADV-002**: Query with multiple filters
- **GQL-ADV-003**: Query with aliases
- **GQL-ADV-004**: Query with fragments
- **GQL-ADV-005**: Batch mutations
- **GQL-ADV-006**: Query depth limitations

### Data Relationships
- **REL-001**: Sensor type with multiple sensors
- **REL-002**: Location hierarchy navigation
- **REL-003**: Sensor with multiple readings
- **REL-004**: Location with nested sensors
- **REL-005**: Cross-reference data integrity

---

## Performance Tests

### Load Testing
- **PERF-001**: 1000 concurrent sensor reading insertions
- **PERF-002**: Large dataset queries (10k+ readings)
- **PERF-003**: Complex aggregation queries
- **PERF-004**: Concurrent user simulation
- **PERF-005**: Database connection pooling

### Scalability Testing
- **SCALE-001**: 100k sensor readings query performance
- **SCALE-002**: 1M readings data integrity
- **SCALE-003**: 1000 sensors management
- **SCALE-004**: Deep location hierarchy (20+ levels)
- **SCALE-005**: Memory usage under load

### Response Time Testing
- **RT-001**: Query response times under load
- **RT-002**: Mutation response times
- **RT-003**: Complex query optimization
- **RT-004**: Database index effectiveness

---

## Error Handling Tests

### Input Validation
- **ERR-001**: Invalid UUID formats
- **ERR-002**: Required field omissions
- **ERR-003**: Data type mismatches
- **ERR-004**: Field length violations
- **ERR-005**: Invalid enum values
- **ERR-006**: Malformed timestamps
- **ERR-007**: Invalid coordinate ranges
- **ERR-008**: SQL injection attempts

### Business Logic Errors
- **BL-001**: Circular location references
- **BL-002**: Orphaned entity references
- **BL-003**: Constraint violations
- **BL-004**: Invalid state transitions
- **BL-005**: Data consistency violations

### System Errors
- **SYS-001**: Database connection failures
- **SYS-002**: Network timeout handling
- **SYS-003**: Memory exhaustion scenarios
- **SYS-004**: Concurrent access conflicts

---

## Security Tests

### Authentication & Authorization
- **SEC-001**: Unauthenticated access attempts
- **SEC-002**: Token validation
- **SEC-003**: Role-based access control
- **SEC-004**: API rate limiting

### Data Security
- **SEC-005**: Input sanitization
- **SEC-006**: SQL injection prevention
- **SEC-007**: GraphQL query depth limits
- **SEC-008**: Data exposure in error messages

### Infrastructure Security
- **SEC-009**: HTTPS enforcement
- **SEC-010**: CORS configuration
- **SEC-011**: Security headers validation

---

## Data Consistency Tests

### ACID Properties
- **ACID-001**: Transaction atomicity
- **ACID-002**: Data consistency rules
- **ACID-003**: Isolation levels
- **ACID-004**: Durability verification

### Concurrent Operations
- **CONC-001**: Race condition handling
- **CONC-002**: Dead lock prevention
- **CONC-003**: Lost update scenarios
- **CONC-004**: Phantom read prevention

### Data Integrity
- **DI-001**: Foreign key constraints
- **DI-002**: Unique constraints
- **DI-003**: Check constraints
- **DI-004**: Trigger operations

---

## Test Implementation Guide

### Test Structure
```
tests/
├── conftest.py                 # Test configuration and fixtures
├── test_elementary/           # Elementary tests
│   ├── test_health.py
│   ├── test_schema.py
│   └── test_database.py
├── test_crud/                 # CRUD tests
│   ├── test_sensor_types.py
│   ├── test_locations.py
│   ├── test_sensors.py
│   ├── test_sensor_readings.py
│   └── test_alerts.py
├── test_integration/          # Integration tests
│   ├── test_workflows.py
│   ├── test_relationships.py
│   └── test_graphql_advanced.py
├── test_performance/          # Performance tests
│   ├── test_load.py
│   ├── test_scalability.py
│   └── test_response_times.py
├── test_errors/              # Error handling tests
│   ├── test_validation.py
│   ├── test_business_logic.py
│   └── test_system_errors.py
├── test_security/            # Security tests
│   ├── test_authentication.py
│   ├── test_authorization.py
│   └── test_data_security.py
└── test_consistency/         # Data consistency tests
    ├── test_acid.py
    ├── test_concurrency.py
    └── test_integrity.py
```

### Test Fixtures
```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base, get_db
from app.database.models import *

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine("postgresql://test_user:test_pass@localhost:5432/sensor_test_db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_db(test_engine):
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def client(test_db):
    from app.main import app
    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as client:
        yield client
```

### Sample Test Implementation
```python
# test_sensor_types.py
def test_create_sensor_type_all_fields(client):
    """ST-C-001: Create sensor type with all fields"""
    mutation = """
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
        }
    }
    """
    
    variables = {
        "input": {
            "name": "Temperature",
            "description": "Air temperature sensor",
            "unit": "°C",
            "dataType": "float",
            "minValue": -50.0,
            "maxValue": 100.0
        }
    }
    
    response = client.post("/graphql", json={"query": mutation, "variables": variables})
    assert response.status_code == 200
    data = response.json()["data"]["createSensorType"]
    assert data["name"] == "Temperature"
    assert data["unit"] == "°C"
    assert data["dataType"] == "float"
    assert data["minValue"] == -50.0
    assert data["maxValue"] == 100.0
    assert data["isActive"] is True
```

### Test Execution Commands
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_elementary/
pytest tests/test_crud/
pytest tests/test_performance/

# Run with coverage
pytest --cov=app --cov-report=html

# Run performance tests
pytest tests/test_performance/ --timeout=300

# Run tests in parallel
pytest -n auto
```

### Test Reporting
- Generate HTML coverage reports
- Performance benchmarking results
- Test execution time analysis
- Failed test debugging information
- Test data cleanup verification

---

## Test Success Criteria

### Elementary Tests: 100% pass rate
- All basic functionality working
- No critical errors in core operations

### CRUD Tests: 95%+ pass rate
- All primary CRUD operations working
- Edge cases handled appropriately
- Data validation functioning

### Integration Tests: 90%+ pass rate
- Cross-entity operations working
- Complex scenarios handled
- Data consistency maintained

### Performance Tests: Meet SLA requirements
- Response times < 200ms for simple queries
- Response times < 2s for complex queries
- Support 100+ concurrent users

### Error Handling: 100% coverage
- All error scenarios identified
- Appropriate error messages
- Graceful degradation

This comprehensive testing plan ensures the Sensor API is robust, reliable, and ready for production deployment.
