# Sensor API Testing Guide

This directory contains comprehensive tests for the Sensor API, covering elementary functionality, CRUD operations, integration tests, and performance testing.

## Quick Start

### 1. Install Test Dependencies

```bash
# Install testing dependencies
pip install -r requirements-test.txt

# Or use the test runner
python run_tests.py install
```

### 2. Setup Test Database

Create a PostgreSQL test database:

```bash
# Create test database (adjust credentials as needed)
createdb -U postgres sensor_test_db

# Or use Docker
docker run --name sensor-test-db -e POSTGRES_USER=test_user -e POSTGRES_PASSWORD=test_pass -e POSTGRES_DB=sensor_test_db -p 5432:5432 -d postgres:14
```

Update the database URL in `tests/conftest.py` if needed:
```python
TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/sensor_test_db"
```

### 3. Run Migrations

```bash
# Set the test database URL
export DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/sensor_test_db

# Run migrations
alembic upgrade head
```

### 4. Run Tests

```bash
# Run elementary tests (basic functionality)
python run_tests.py elementary

# Run CRUD tests
python run_tests.py crud

# Run all tests
python run_tests.py all

# Run tests with coverage
python run_tests.py coverage
```

## Test Structure

```
tests/
├── conftest.py                 # Test configuration and fixtures
├── test_elementary.py          # Elementary/smoke tests
├── test_sensor_types_crud.py   # Sensor Types CRUD tests
├── test_locations_crud.py      # Locations CRUD tests (to be created)
├── test_sensors_crud.py        # Sensors CRUD tests (to be created)
├── test_sensor_readings_crud.py # Sensor Readings CRUD tests (to be created)
└── ...
```

## Test Categories

### Elementary Tests (`test_elementary.py`)
- **API-001 to API-003**: Health checks and basic connectivity
- **GQL-001 to GQL-004**: GraphQL schema validation
- **CRUD-001 to CRUD-005**: Basic CRUD smoke tests
- **Error handling**: Basic error scenarios

### CRUD Tests (`test_*_crud.py`)
Comprehensive testing for each entity:
- **Create**: All field combinations, validation, edge cases
- **Read**: Filtering, sorting, pagination, relationships
- **Update**: Field updates, validation, constraints
- **Delete**: Soft/hard delete, cascading, constraints

### Integration Tests (planned)
- Cross-entity operations
- Complex workflows
- Data consistency
- Transaction handling

### Performance Tests (planned)
- Load testing
- Concurrent operations
- Large dataset handling
- Response time validation

## Test Execution Options

### Using Test Runner

```bash
# Install dependencies
python run_tests.py install

# Run specific test suites
python run_tests.py elementary
python run_tests.py crud
python run_tests.py all

# Performance and advanced options
python run_tests.py coverage
python run_tests.py parallel
python run_tests.py performance
```

### Using pytest Directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_elementary.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run in parallel
pytest -n auto

# Run with specific markers (when implemented)
pytest -m "not slow"
```

## Environment Variables

Set these environment variables for testing:

```bash
export DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/sensor_test_db
export TEST_DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/sensor_test_db
export SECRET_KEY=test-secret-key
export ENVIRONMENT=test
export DEBUG=True
```

## Test Fixtures

The test suite provides several fixtures for common test data:

- `test_db`: Database session for tests
- `client`: FastAPI test client
- `sample_sensor_type`: Pre-created sensor type
- `sample_location`: Pre-created location
- `sample_sensor`: Pre-created sensor
- `sample_sensor_reading`: Pre-created sensor reading
- `graphql_queries`: GraphQL query templates
- `test_data_factory`: Factory for creating test data

## Writing New Tests

### Basic Test Structure

```python
def test_my_feature(client, test_data_factory, graphql_queries):
    """Test description with test ID (e.g., ST-C-009)."""
    # Arrange
    variables = {
        "input": test_data_factory.sensor_type_input(name="Test Feature")
    }
    
    # Act
    response = client.post("/graphql", json={
        "query": graphql_queries.CREATE_SENSOR_TYPE,
        "variables": variables
    })
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["createSensorType"]["name"] == "Test Feature"
```

### Test Naming Convention

- Test IDs: `{ENTITY}-{OPERATION}-{NUMBER}` (e.g., ST-C-001, LOC-R-005)
- Test functions: `test_{operation}_{entity}_{scenario}`
- Test classes: `Test{Entity}{Operation}` (e.g., TestSensorTypeCreate)

## Continuous Integration

Tests run automatically on GitHub Actions for:
- Python 3.8, 3.9, 3.10, 3.11
- PostgreSQL 14
- Coverage reporting
- Code linting (black, isort, flake8, mypy)

## Test Coverage Goals

- **Elementary Tests**: 100% pass rate
- **CRUD Tests**: 95%+ pass rate  
- **Integration Tests**: 90%+ pass rate
- **Code Coverage**: 85%+ overall coverage

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   pg_isready -h localhost -p 5432
   
   # Verify database exists
   psql -h localhost -U test_user -d sensor_test_db -c "SELECT 1;"
   ```

2. **Migration Issues**
   ```bash
   # Reset database
   alembic downgrade base
   alembic upgrade head
   ```

3. **Import Errors**
   ```bash
   # Install in development mode
   pip install -e .
   ```

4. **GraphQL Schema Errors**
   ```bash
   # Verify schema compilation
   python -c "from app.graphql.schema import schema; print('Schema OK')"
   ```

### Debug Mode

Run tests with debug output:

```bash
# Verbose pytest output
pytest -v -s

# Print database queries
export SQLALCHEMY_ECHO=True
pytest tests/test_elementary.py::test_create_sensor_type -s
```

## Next Steps

1. **Complete CRUD Test Suite**: Implement remaining CRUD test files
2. **Integration Tests**: Add cross-entity operation tests
3. **Performance Tests**: Add load and stress testing
4. **Security Tests**: Add authentication and authorization tests
5. **End-to-End Tests**: Add full workflow testing

For detailed test specifications, see [TESTING_PLAN.md](../TESTING_PLAN.md).
