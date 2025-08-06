# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a full-stack sensor data management system with a Python GraphQL API backend and React frontend:

### Backend (Python)
- **FastAPI + Strawberry GraphQL**: Main API framework with GraphQL endpoint at `/graphql`
- **SQLAlchemy ORM**: Database abstraction with PostgreSQL support
- **Alembic**: Database migrations in `alembic/versions/`
- **Generic Sensor Model**: Flexible design supporting any sensor type via configurable SensorType entities

### Frontend (React + TypeScript)
- **React 19 + TypeScript**: Frontend in `frontend/` directory
- **Apollo Client**: GraphQL client for API communication
- **Vite**: Build tool and dev server
- **Chart.js**: Sensor data visualization

### Data Model
Core entities in `app/database/models.py`:
- **SensorType**: Configurable sensor definitions (temperature, humidity, etc.)
- **Location**: Hierarchical organization (buildings → floors → rooms)
- **Sensor**: Individual sensor devices with metadata
- **SensorReading**: Time-series measurements with quality indicators
- **Alert**: Monitoring system for threshold-based alerts

## Common Development Commands

### Backend Setup
```bash
# Setup virtual environment and dependencies
./setup.sh
source .venv/bin/activate

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Run development server
python main.py
# or via Docker
docker-compose up
```

### Testing
```bash
# Install test dependencies
python run_tests.py install

# Run different test suites
python run_tests.py elementary     # Basic functionality tests
python run_tests.py crud          # CRUD operation tests
python run_tests.py all           # All tests
python run_tests.py coverage      # Tests with coverage report

# Direct pytest usage
pytest                            # Run all tests
pytest tests/test_elementary.py   # Specific test file
pytest --cov=app --cov-report=html # Coverage report
```

### Code Quality
```bash
# Code formatting
black .
isort .

# Type checking
mypy .

# Available in requirements.txt - install before use
```

### Frontend Development
```bash
cd frontend/
npm install
npm run dev        # Development server
npm run build      # Production build
npm run lint       # ESLint
```

## Database Configuration

The application uses environment variables for database configuration:
- `DATABASE_URL`: PostgreSQL connection string
- `TEST_DATABASE_URL`: Test database (optional)

Set in `.env` file (copy from `.env.example`):
```env
DATABASE_URL=postgresql://username:password@hostname:port/database_name
```

## GraphQL API Structure

### Key Files
- `app/graphql/schema.py`: Main schema definition
- `app/graphql/types.py`: GraphQL type definitions
- `app/graphql/resolvers.py`: Query and mutation resolvers

### API Endpoints
- `/graphql`: GraphQL playground and API endpoint
- `/docs`: FastAPI auto-generated documentation
- `/health`: Health check endpoint

## Deployment

### Production Environment Variables
```env
DATABASE_URL=postgresql://...
SECRET_KEY=production-secret
ENVIRONMENT=production
DEBUG=false
```

### Available Deployment Configurations
- **Vercel**: Configured via `vercel.json`
- **Docker**: `docker-compose.yml` for containerized deployment
- **Scripts**: `deploy.sh`, `scripts/deploy-vercel.sh`, `scripts/deploy-azure.sh`

## Development Notes

### Generic Sensor Design
The system is designed to handle any type of sensor through configurable SensorType entities. When adding new sensor types, create appropriate SensorType records rather than modifying the data model.

### Time-Series Optimization
SensorReading table is optimized for time-series data with proper indexing on timestamp and sensor_id fields for efficient querying of historical data.

### Testing Strategy
- **Elementary tests**: Basic API connectivity and schema validation
- **CRUD tests**: Comprehensive entity operations testing
- **Integration tests**: Cross-entity workflows (planned)
- **Test runner**: `run_tests.py` provides convenient test execution

### Frontend Integration
The React frontend communicates with the GraphQL API via Apollo Client. GraphQL queries and mutations are centralized in `frontend/src/graphql/`.