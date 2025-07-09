# Sensor Data API - Project Overview

## 🎯 Project Summary

You now have a complete Python GraphQL API for generic sensor data management with PostgreSQL integration. The project includes:

### ✅ What's Been Created

1. **Complete Project Structure**
   - FastAPI + Strawberry GraphQL backend
   - SQLAlchemy ORM with PostgreSQL
   - Alembic database migrations
   - Virtual environment setup (.venv)

2. **Data Model** (Generic Sensor System)
   - **SensorType**: Configurable sensor types (temperature, humidity, etc.)
   - **Location**: Hierarchical location management (building → floor → room)
   - **Sensor**: Individual sensor devices with metadata
   - **SensorReading**: Time-series sensor measurements
   - **Alert**: Alert system for monitoring thresholds

3. **GraphQL API**
   - Complete CRUD operations for all entities
   - Time-series data queries
   - Real-time sensor status monitoring
   - Flexible filtering and pagination

4. **Development Tools**
   - Sample data creation script
   - Development helper script (dev.sh)
   - Code formatting and quality checks
   - Comprehensive documentation

## 🚀 Quick Start Guide

### 1. Configure Aiven PostgreSQL

1. Log into your Aiven console
2. Create a new PostgreSQL service
3. Copy the connection details
4. Edit `.env` file and replace the DATABASE_URL:

```env
DATABASE_URL=postgresql://avnadmin:your_password@your-host.aivencloud.com:port/defaultdb
```

### 2. Set Up and Run

```bash
# Activate virtual environment
source .venv/bin/activate

# Run full development setup (migrations + sample data + start server)
./dev.sh dev
```

### 3. Access the API

- **GraphQL Playground**: http://localhost:8000/graphql
- **API Documentation**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health

## 📊 Data Structure Overview

### Sensor Types
- Temperature (°C), Humidity (%RH), Pressure (hPa)
- Air Quality (AQI), Light Level (lux)
- Configurable units, ranges, and data types

### Location Hierarchy
```
Main Office Building
├── Floor 1
│   ├── Conference Room A
│   ├── Open Office
│   └── Server Room
├── Floor 2
│   └── ...
└── Floor 3
    └── ...
```

### Sensors
- Device ID, manufacturer, model, firmware version
- Calibration settings, sampling intervals
- Online status and last seen timestamps

### Time-Series Data
- Sensor readings with timestamps
- Quality indicators (good/uncertain/bad)
- Confidence scores
- Raw and calibrated values

## 🔧 Development Commands

```bash
# Start development environment
./dev.sh dev

# Just run migrations
./dev.sh migrate

# Create sample data
./dev.sh sample-data

# Start server only
./dev.sh start

# Run tests
./dev.sh test

# Format code
./dev.sh format

# Check code quality
./dev.sh check
```

## 📝 Example GraphQL Queries

### Get All Sensors with Latest Readings
```graphql
query {
  sensors {
    deviceId
    name
    sensorType { name, unit }
    location { name }
    latestReading { value, timestamp, quality }
  }
}
```

### Add New Sensor Reading
```graphql
mutation {
  createSensorReading(input: {
    sensorId: "sensor-uuid"
    value: 23.5
    quality: "good"
  }) {
    id
    value
    timestamp
  }
}
```

## 🌟 Key Features

### Generic Design
- Support any sensor type without code changes
- Configurable units, ranges, and data types
- Flexible metadata storage with JSON fields

### Scalable Architecture
- Time-series optimized database schema
- Efficient indexing for large datasets
- RESTful and GraphQL endpoints

### Real-time Monitoring
- Sensor online/offline status tracking
- Alert system for threshold monitoring
- Quality indicators for data reliability

### Location Management
- Hierarchical location structure
- Geographic coordinates support
- Multi-level organization (building/floor/room)

## 🔐 Security & Production

### Environment Variables
- Database credentials in .env file
- Configurable security settings
- Debug mode toggle

### Production Considerations
1. Set `DEBUG=False` in production
2. Use strong SECRET_KEY
3. Configure proper CORS origins
4. Set up SSL/TLS termination
5. Use connection pooling
6. Implement proper logging

## 📚 API Documentation

- **GraphQL Schema**: Auto-generated in playground
- **Query Examples**: See GRAPHQL_EXAMPLES.md
- **REST Docs**: Available at /docs endpoint
- **Data Models**: Defined in app/database/models.py

## 🔄 Database Migrations

The project uses Alembic for database migrations:

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📦 Project Structure

```
sensorapi/
├── app/
│   ├── core/          # Configuration
│   ├── database/      # Models and database setup
│   └── graphql/       # GraphQL schema and resolvers
├── alembic/           # Database migrations
├── scripts/           # Utility scripts
├── .venv/             # Virtual environment
├── main.py            # Application entry point
├── dev.sh             # Development helper script
└── requirements.txt   # Python dependencies
```

## 🧪 Testing

Add sensor readings, query time-series data, and test the alert system:

1. Use the sample data to explore the API
2. Try different GraphQL queries in the playground
3. Monitor sensor status and readings
4. Test location hierarchy and filtering

## 🎯 Next Steps

1. **Connect to Aiven**: Configure your PostgreSQL connection
2. **Run Migrations**: Set up the database schema
3. **Explore Data**: Use sample data to test queries
4. **Customize**: Add your specific sensor types and locations
5. **Deploy**: Set up production environment

The API is designed to be production-ready with proper error handling, data validation, and scalable architecture patterns.
