# Sensor Data Management System

A full-stack sensor data management system with Python GraphQL API backend and React frontend. Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap Environment and Dependencies
Always run these commands in sequence when working with a fresh clone:

```bash
# Setup Python virtual environment and core dependencies  
chmod +x setup.sh && ./setup.sh

# Activate the virtual environment (REQUIRED for all Python commands)
source .venv/bin/activate

# Setup environment configuration
cp .env.example .env
# Edit .env with your database credentials if needed

# Install frontend dependencies 
cd frontend && npm install && cd ..
```

**CRITICAL: Always activate the virtual environment with `source .venv/bin/activate` before running any Python commands.**

### Build and Run Commands

#### Frontend Build and Development
```bash
# Frontend development server
cd frontend && npm run dev
# Accessible at http://localhost:5173

# Frontend production build -- takes 8 seconds. NEVER CANCEL. Set timeout to 30+ seconds.
cd frontend && npm run build

# Frontend linting -- takes 2 seconds but will show TypeScript errors
cd frontend && npm run lint
```

#### Backend API Development  
```bash
# REQUIRED: Activate virtual environment first
source .venv/bin/activate

# Start API server (requires PostgreSQL database configured in .env)
python main.py
# GraphQL Playground: http://localhost:8000/graphql
# API Documentation: http://localhost:8000/docs  
# Health Check: http://localhost:8000/health

# Alternative: Use development helper script
chmod +x dev.sh && ./dev.sh start

# For production preview of built frontend
cd frontend && npm run preview
# Accessible at http://localhost:5173
```

**Database Requirement**: The API requires PostgreSQL. SQLite is not supported due to UUID column types in the database schema.

#### Database Operations (requires PostgreSQL setup)
```bash
# REQUIRED: Activate virtual environment first
source .venv/bin/activate

# Install database tools if not available (may fail due to network issues)
pip install alembic uvicorn

# Run database migrations
alembic upgrade head

# Create sample data
python scripts/create_sample_data.py

# All-in-one development setup
chmod +x dev.sh && ./dev.sh dev
```

### Testing

#### Testing Limitations
**IMPORTANT**: Due to network connectivity issues in some environments, test dependencies may fail to install via pip. The core application functionality is available, but comprehensive testing requires manual setup.

```bash
# REQUIRED: Activate virtual environment first  
source .venv/bin/activate

# Attempt to install test dependencies (may timeout)
python run_tests.py install

# If above fails, try manual installation
pip install pytest pytest-asyncio httpx

# Run available tests  
python run_tests.py elementary     # Basic functionality tests
python run_tests.py crud          # CRUD operation tests  
python run_tests.py all           # All tests
python run_tests.py coverage      # Tests with coverage report

# Direct pytest usage (if installed)
pytest                            # Run all tests
pytest tests/test_elementary.py   # Specific test file
```

### Code Quality and Linting

```bash
# REQUIRED: Activate virtual environment first
source .venv/bin/activate

# Install linting tools (may fail due to network issues)  
pip install black isort mypy flake8

# Format code (if tools are available)
black . && isort .

# Type checking (if mypy is available)
mypy app/ --ignore-missing-imports

# Using dev script helper
./dev.sh format    # Format code
./dev.sh check     # Check code quality
```

**Network Connectivity Note**: Due to PyPI timeout issues, some Python packages may fail to install. Use the dev.sh script or install packages individually with longer timeouts if needed.

## Validation Scenarios

Always test these scenarios after making changes:

### Basic API Functionality
1. **Health Check**: Visit http://localhost:8000/health and verify 200 response
2. **GraphQL Playground**: Access http://localhost:8000/graphql and verify UI loads
3. **API Documentation**: Check http://localhost:8000/docs loads properly

### Frontend Functionality  
1. **Development Server**: Run `npm run dev` and verify http://localhost:5173 loads
2. **Production Build**: Run `npm run build` and verify `dist/` folder is created
3. **Linting**: Run `npm run lint` to identify code quality issues

### Full Stack Integration (requires database)
1. **Database Connection**: Verify API starts without errors when DATABASE_URL is configured
2. **GraphQL Queries**: Test basic queries in GraphQL playground
3. **Frontend-Backend Communication**: Verify frontend can communicate with API

## Project Architecture

### Backend (Python)
- **Location**: `/app/` directory
- **Framework**: FastAPI + Strawberry GraphQL + SQLAlchemy ORM
- **Database**: PostgreSQL with Alembic migrations
- **Key Files**:
  - `main.py` - Application entry point
  - `app/core/config.py` - Configuration management  
  - `app/graphql/schema.py` - GraphQL schema definition
  - `app/database/models.py` - Database models
  - `alembic/versions/` - Database migrations

### Frontend (React + TypeScript)
- **Location**: `/frontend/` directory
- **Framework**: React 19 + TypeScript + Vite + Apollo Client
- **Key Files**:
  - `src/` - React application source
  - `package.json` - Dependencies and build scripts
  - `vite.config.ts` - Build configuration

### Database Schema
**Generic Sensor Design**: The system supports any sensor type through configurable SensorType entities:
- **SensorType**: Defines sensor types (temperature, humidity, etc.)
- **Location**: Hierarchical organization (buildings → floors → rooms)  
- **Sensor**: Individual sensor devices with metadata
- **SensorReading**: Time-series measurements with quality indicators
- **Alert**: Monitoring system for threshold-based alerts

## Common Tasks and File Locations

### Development Scripts
- `setup.sh` - Environment setup
- `dev.sh` - Development helper (migrate, start, test, format, check)
- `run_tests.py` - Test runner with multiple suites

### Configuration Files
- `.env` - Environment variables (copy from `.env.example`)
- `alembic.ini` - Database migration configuration
- `requirements.txt` - Python dependencies
- `frontend/package.json` - Frontend dependencies

### Documentation
- `README.md` - General project information
- `CLAUDE.md` - AI assistant specific guidance
- `CONTRIBUTING.md` - Development guidelines
- `DEPLOYMENT.md` - Deployment instructions

### Testing
- `tests/` - Python test suites
- `tests/test_elementary.py` - Basic functionality tests
- `tests/conftest.py` - Test configuration

## Troubleshooting

### Common Issues

**PyPI Connectivity**: If `pip install` commands timeout, this is a known network limitation. Try:
- Installing packages individually 
- Using the existing installed packages
- Using system-level package manager alternatives

**Database Connection**: If the API fails to start:
- **CRITICAL**: The API requires PostgreSQL - SQLite is not supported due to UUID types in database schema
- Verify `.env` file has correct PostgreSQL DATABASE_URL  
- Check if PostgreSQL is running and accessible
- For testing without database: Use Docker Compose setup: `docker-compose up db`

**Frontend Build Issues**: If npm commands fail:
- Verify Node.js version compatibility (needs Node 18+)
- Clear npm cache: `npm cache clean --force`
- Remove node_modules and reinstall: `rm -rf node_modules && npm install`

### Build Time Expectations
- **Frontend Build**: ~8 seconds (set timeout to 30+ seconds)
- **Frontend Lint**: ~2 seconds (will show TypeScript errors)
- **Python Package Installation**: May timeout due to network issues
- **Test Suite**: Depends on database connectivity and test dependency availability

**NEVER CANCEL** long-running builds or installs - they may be working despite appearing stuck.

## Quick Reference Commands

```bash
# Full environment setup
chmod +x setup.sh && ./setup.sh && source .venv/bin/activate && cp .env.example .env

# Frontend development  
cd frontend && npm install && npm run dev

# Backend development (basic)
source .venv/bin/activate && python main.py

# All-in-one development (requires database)
source .venv/bin/activate && chmod +x dev.sh && ./dev.sh dev

# Build everything
source .venv/bin/activate && cd frontend && npm run build && cd .. && python -c "import app"
```

Always ensure you're in the correct directory and have activated the virtual environment before running Python commands.