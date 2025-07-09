#!/bin/bash

# Development helper script for Sensor API

set -e  # Exit on any error

echo "🚀 Sensor API Development Setup"
echo "================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if DATABASE_URL is configured
if grep -q "replace_with_your" .env; then
    echo "❌ Please configure your Aiven PostgreSQL connection in .env file"
    echo "   Edit .env and replace the DATABASE_URL with your actual connection string"
    exit 1
fi

echo "✓ Environment setup complete"

# Function to run database migrations
run_migrations() {
    echo "📦 Running database migrations..."
    
    # Initialize Alembic if not already done
    if [ ! -d "alembic/versions" ]; then
        mkdir -p alembic/versions
    fi
    
    # Create initial migration if no migrations exist
    if [ -z "$(ls -A alembic/versions 2>/dev/null)" ]; then
        echo "  Creating initial migration..."
        alembic revision --autogenerate -m "Initial migration - sensor data schema"
    fi
    
    # Apply migrations
    echo "  Applying migrations..."
    alembic upgrade head
    
    echo "✓ Database migrations completed"
}

# Function to create sample data
create_sample_data() {
    echo "🌱 Creating sample data..."
    python scripts/create_sample_data.py
    echo "✓ Sample data created"
}

# Function to start the API server
start_server() {
    echo "🚀 Starting Sensor API server..."
    echo "   GraphQL Playground: http://localhost:8000/graphql"
    echo "   API Documentation: http://localhost:8000/docs"
    echo "   Health Check: http://localhost:8000/health"
    echo ""
    echo "Press Ctrl+C to stop the server"
    python main.py
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    pytest -v
    echo "✓ Tests completed"
}

# Function to format code
format_code() {
    echo "🎨 Formatting code..."
    black .
    isort .
    echo "✓ Code formatted"
}

# Function to check code quality
check_code() {
    echo "🔍 Checking code quality..."
    black --check .
    isort --check-only .
    mypy .
    echo "✓ Code quality check completed"
}

# Main menu
case "${1:-help}" in
    "migrate")
        run_migrations
        ;;
    "sample-data")
        run_migrations
        create_sample_data
        ;;
    "start"|"server")
        run_migrations
        start_server
        ;;
    "test")
        run_tests
        ;;
    "format")
        format_code
        ;;
    "check")
        check_code
        ;;
    "dev")
        # Full development setup
        run_migrations
        create_sample_data
        start_server
        ;;
    "help"|*)
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "  migrate      - Run database migrations"
        echo "  sample-data  - Create sample data (includes migrate)"
        echo "  start|server - Start the API server (includes migrate)"
        echo "  test         - Run tests"
        echo "  format       - Format code with black and isort"
        echo "  check        - Check code quality"
        echo "  dev          - Full setup: migrate + sample-data + start server"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./dev.sh dev         # Set up everything and start server"
        echo "  ./dev.sh migrate     # Just run migrations"
        echo "  ./dev.sh start       # Start server (with migrations)"
        echo "  ./dev.sh sample-data # Create sample data"
        ;;
esac
