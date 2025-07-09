# GitHub Repository Setup Guide

## Project: Sensor API with GraphQL and PostgreSQL

This guide will help you upload your sensor API project to GitHub as a private repository.

## Repository Information
- **Project Name**: `sensorapi` or `sensor-graphql-api`
- **Description**: Python GraphQL API for generic sensor data with PostgreSQL backend
- **Visibility**: Private
- **Technologies**: Python, FastAPI, Strawberry GraphQL, SQLAlchemy, PostgreSQL, Alembic

## Option 1: Using GitHub Web Interface (Recommended)

1. **Go to GitHub**: Open https://github.com in your browser
2. **Sign in** to your GitHub account
3. **Create New Repository**:
   - Click the "+" icon in the top right corner
   - Select "New repository"
   - Repository name: `sensorapi` or `sensor-graphql-api`
   - Description: `Python GraphQL API for generic sensor data with PostgreSQL backend`
   - Select "Private" repository
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

4. **Add Remote and Push**:
   ```bash
   # Copy the repository URL from GitHub (should look like):
   # https://github.com/YOUR_USERNAME/sensorapi.git
   
   git remote add origin https://github.com/YOUR_USERNAME/sensorapi.git
   git push -u origin main
   ```

## Option 2: Using GitHub CLI (if available)

1. **Install GitHub CLI** (if not already installed):
   ```bash
   # On Ubuntu/Debian
   sudo apt update && sudo apt install gh
   
   # On macOS
   brew install gh
   
   # On Windows
   # Download from https://cli.github.com/
   ```

2. **Authenticate with GitHub**:
   ```bash
   gh auth login
   ```

3. **Create and Push Repository**:
   ```bash
   gh repo create sensorapi --private --source=. --remote=origin --push
   ```

## Repository Structure

Your repository will include:

```
sensorapi/
├── app/                        # Main application package
│   ├── core/                   # Core configuration
│   ├── database/               # Database models and connection
│   └── graphql/                # GraphQL schema and resolvers
├── alembic/                    # Database migrations
├── scripts/                    # Utility scripts
├── requirements.txt            # Python dependencies
├── requirements-vercel.txt     # Vercel-specific requirements
├── main.py                     # FastAPI application entry point
├── README.md                   # Project documentation
├── DEPLOYMENT.md               # Deployment instructions
├── GRAPHQL_EXAMPLES.md         # GraphQL query examples
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── vercel.json                 # Vercel deployment config
├── .env.example                # Environment variables template
├── .env.production.example     # Production environment template
└── .gitignore                  # Git ignore rules
```

## Features Included

- ✅ **FastAPI + Strawberry GraphQL** backend
- ✅ **PostgreSQL** database with SQLAlchemy ORM
- ✅ **Alembic** database migrations
- ✅ **Generic sensor data model** (SensorType, Location, Sensor, SensorReading, Alert)
- ✅ **Sample data creation** script
- ✅ **Deployment configurations** for Vercel and Azure
- ✅ **Docker support** with multi-stage builds
- ✅ **Comprehensive documentation** and examples
- ✅ **Environment management** with .venv support

## Next Steps After Upload

1. **Set up GitHub Secrets** (for CI/CD):
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: Your application secret key
   - Add other environment variables as needed

2. **Enable GitHub Actions** (optional):
   - Create `.github/workflows/` directory
   - Add CI/CD workflows for testing and deployment

3. **Configure Branch Protection** (recommended):
   - Go to Settings > Branches
   - Add protection rules for `main` branch
   - Require pull request reviews
   - Require status checks

4. **Add Collaborators** (if needed):
   - Go to Settings > Collaborators
   - Add team members with appropriate permissions

## Quick Start Commands

After uploading to GitHub, others can get started with:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/sensorapi.git
cd sensorapi

# Set up environment
chmod +x setup.sh && ./setup.sh

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
source .venv/bin/activate
alembic upgrade head

# Create sample data
python scripts/create_sample_data.py

# Start development server
chmod +x dev.sh && ./dev.sh
```

## Support

For questions about this project structure or deployment, refer to:
- `README.md` - General project information
- `DEPLOYMENT.md` - Deployment instructions
- `GRAPHQL_EXAMPLES.md` - API usage examples
