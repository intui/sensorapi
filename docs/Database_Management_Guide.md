# Database Management System

## Overview

The SensorAPI now supports easy switching between two database providers:
- **Aiven**: Original PostgreSQL database with limited TimescaleDB support
- **Tiger Cloud**: PostgreSQL service with TimescaleDB extension and time-series optimizations

## Quick Start

### Switch to Tiger Cloud (4.5M+ sensor readings)
```bash
python scripts/manage_database.py switch tiger_cloud
```

### Switch to Aiven (422K sensor readings)
```bash
python scripts/manage_database.py switch aiven
```

### Check current status
```bash
python scripts/manage_database.py status
```

### Test database connection
```bash
python scripts/manage_database.py test-connection
```

## Configuration

The system uses the `DATABASE_PROVIDER` environment variable to determine which database to use:

- `DATABASE_PROVIDER=aiven` → Uses `DATABASE_URL` (Aiven PostgreSQL)
- `DATABASE_PROVIDER=tiger_cloud` → Uses `TIGER_CLOUD_DATABASE_URL` (Tiger Cloud)

## API Endpoints

When the application is running, you can check database status via API:

- `GET /` - Root endpoint showing current database provider
- `GET /api/v1/health` - Health check
- `GET /api/v1/database/info` - Detailed database information
- `GET /api/v1/database/switch-guide` - Instructions for switching databases

## Database Comparison

| Feature | Aiven | Tiger Cloud |
|---------|-------|-------------|
| Database | PostgreSQL 16.9 | PostgreSQL 17.5 |
| TimescaleDB | v2.19.3 (limited) | v2.21.3 (PostgreSQL service) |
| Hypertables | ❌ Not supported | ❌ Service limitation |
| Time-series optimization | Basic indexes | Advanced PostgreSQL indexes |
| Data volume | ~422K sensor readings | ~4.5M sensor readings |
| Use case | Original development | Production time-series |

## Implementation Details

### Configuration (`app/core/config.py`)
- `DATABASE_PROVIDER` setting with validation
- `active_database_url` property that returns the correct URL
- `database_info` property with metadata
- Automatic postgres:// → postgresql:// URL conversion

### Database Connection (`app/database/database.py`)
- Uses `settings.active_database_url` instead of fixed URL
- Dynamic connection string based on provider
- Application name includes provider for database monitoring

### Management Script (`scripts/manage_database.py`)
- Switch between providers with validation
- Status checking with detailed information
- Connection testing with database statistics
- Environment file management

### API Endpoints (`app/api/endpoints/health.py`)
- Runtime database information
- Switch guide and instructions
- Database statistics and capabilities

## Usage Examples

### Development Workflow
```bash
# Start with Aiven for development
python scripts/manage_database.py switch aiven
python scripts/manage_database.py test-connection

# Switch to Tiger Cloud for production testing
python scripts/manage_database.py switch tiger_cloud
uvicorn main:app --reload

# Check API endpoints
curl http://localhost:8000/api/v1/database/info
```

### Production Deployment
Set `DATABASE_PROVIDER=tiger_cloud` in your production environment to use the Tiger Cloud database with optimized time-series performance.

## Files Modified

- `app/core/config.py` - Enhanced configuration with provider switching
- `app/database/database.py` - Dynamic database URL selection
- `main.py` - Added health endpoints
- `.env` - Added DATABASE_PROVIDER setting
- `scripts/manage_database.py` - Database management CLI
- `scripts/test_api.py` - API testing script
- `app/api/endpoints/health.py` - Health and database info endpoints

## Benefits

✅ **Easy switching** between databases without code changes
✅ **Runtime visibility** into active database configuration  
✅ **Automated testing** of database connections
✅ **Production ready** with Tiger Cloud's time-series optimizations
✅ **Development friendly** with Aiven for local/test scenarios
✅ **Transparent operation** - existing GraphQL API continues to work