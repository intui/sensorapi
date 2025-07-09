# Sensor Data GraphQL API

A Python-based GraphQL API for managing generic sensor data with PostgreSQL database integration.

## Features

- **GraphQL API** with Strawberry GraphQL
- **Generic Sensor Data Model** supporting various sensor types
- **PostgreSQL Integration** with SQLAlchemy ORM
- **Time-series Data Storage** optimized for sensor readings
- **Location Hierarchy** support for organizing sensors
- **Alert System** for monitoring sensor values
- **Database Migrations** with Alembic
- **FastAPI Backend** with automatic OpenAPI documentation

## Data Model

The API supports a flexible data model for sensor management:

### Core Entities

1. **SensorType**: Defines types of sensors (temperature, humidity, pressure, etc.)
2. **Location**: Hierarchical location management (buildings, floors, rooms)
3. **Sensor**: Individual sensor devices with metadata
4. **SensorReading**: Time-series sensor measurements
5. **Alert**: Automated alerts based on sensor conditions

### Key Features

- **Generic Design**: Support any type of sensor with configurable data types
- **Hierarchical Locations**: Organize sensors in a tree structure
- **Time-series Optimization**: Efficient storage and querying of sensor readings
- **Alert Management**: Configurable thresholds and alert conditions

## Quick Start

### 1. Setup Environment

```bash
# Make setup script executable and run it
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source .venv/bin/activate
```

### 2. Configure Database

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` file with your Aiven PostgreSQL connection details:
```env
DATABASE_URL=postgresql://username:password@hostname:port/database_name
```

### 3. Initialize Database

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 4. Run the API

```bash
python main.py
```

The API will be available at:
- GraphQL Playground: http://localhost:8000/graphql
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Usage

### GraphQL Queries

#### Create a Sensor Type
```graphql
mutation {
  createSensorType(input: {
    name: "Temperature"
    description: "Temperature sensor in Celsius"
    unit: "°C"
    dataType: "float"
    minValue: -40.0
    maxValue: 85.0
  }) {
    id
    name
    unit
  }
}
```

#### Create a Location
```graphql
mutation {
  createLocation(input: {
    name: "Building A"
    description: "Main office building"
    address: "123 Main St"
    city: "Helsinki"
    country: "Finland"
  }) {
    id
    name
  }
}
```

#### Create a Sensor
```graphql
mutation {
  createSensor(input: {
    deviceId: "TEMP001"
    name: "Office Temperature Sensor"
    sensorTypeId: "sensor-type-id"
    locationId: "location-id"
    manufacturer: "SensorCorp"
    model: "TC-100"
  }) {
    id
    deviceId
    name
  }
}
```

#### Add Sensor Reading
```graphql
mutation {
  createSensorReading(input: {
    sensorId: "sensor-id"
    value: 22.5
  }) {
    id
    value
    timestamp
  }
}
```

#### Query Sensor Data
```graphql
query {
  sensors(locationId: "location-id") {
    id
    name
    deviceId
    sensorType {
      name
      unit
    }
    location {
      name
    }
    latestReading {
      value
      timestamp
      quality
    }
  }
}
```

#### Get Time Series Data
```graphql
query {
  sensorReadings(
    sensorId: "sensor-id"
    limit: 100
    startTime: "2024-01-01T00:00:00Z"
    endTime: "2024-01-02T00:00:00Z"
  ) {
    value
    timestamp
    quality
  }
}
```

## Project Structure

```
sensorapi/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Application configuration
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py        # Database connection
│   │   └── models.py          # SQLAlchemy models
│   ├── graphql/
│   │   ├── __init__.py
│   │   ├── types.py           # GraphQL types
│   │   ├── resolvers.py       # GraphQL resolvers
│   │   └── schema.py          # Main GraphQL schema
│   └── __init__.py
├── alembic/                   # Database migrations
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── setup.sh                   # Environment setup script
├── .env.example               # Environment template
├── .gitignore
└── README.md
```

## Database Schema

The database schema is designed for efficient time-series data storage:

- **Indexed columns** for fast time-based queries
- **UUID primary keys** for distributed systems
- **JSON columns** for flexible metadata storage
- **Hierarchical locations** with parent-child relationships
- **Quality indicators** for data reliability tracking

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy .
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in environment variables
2. Configure proper CORS origins
3. Use a production WSGI server like Gunicorn
4. Set up proper logging and monitoring
5. Configure database connection pooling
6. Set up SSL/TLS termination

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
