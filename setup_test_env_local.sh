#!/bin/bash

# Alternative Test Setup Script (without Docker)
# Sets up test environment using SQLite or local PostgreSQL

set -e

echo "🧪 Setting up Test Environment for Sensor API (No Docker)"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Install test dependencies
install_dependencies() {
    print_status "Installing test dependencies..."
    
    # First, ensure we have the basic packages
    /usr/bin/python3 -m pip install --user fastapi uvicorn sqlalchemy psycopg2-binary alembic python-multipart
    
    if [ -f "requirements-test.txt" ]; then
        /usr/bin/python3 -m pip install --user -r requirements-test.txt
        print_success "Test dependencies installed"
    else
        print_warning "requirements-test.txt not found, installing basic dependencies..."
        /usr/bin/python3 -m pip install --user pytest pytest-asyncio httpx pytest-cov fastapi[all]
    fi
}

# Setup SQLite test database (fallback option)
setup_sqlite() {
    print_status "Setting up SQLite test database..."
    
    export DATABASE_URL="sqlite:///./test_sensor_api.db"
    export TEST_DATABASE_URL="sqlite:///./test_sensor_api.db"
    export SECRET_KEY="test-secret-key-sqlite"
    export ENVIRONMENT="test"
    export DEBUG="True"
    
    print_success "SQLite test database configured"
    echo "  DATABASE_URL: $DATABASE_URL"
}

# Setup local PostgreSQL (if available)
setup_local_postgres() {
    print_status "Checking for local PostgreSQL..."
    
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL found, attempting to create test database..."
        
        # Try to create test database
        if createdb sensor_test_db 2>/dev/null; then
            print_success "Test database 'sensor_test_db' created"
        else
            print_warning "Database might already exist or insufficient permissions"
        fi
        
        # Load environment variables from .env if it exists
        if [ -f ".env" ]; then
            export $(grep -v '^#' .env | xargs)
        fi
        
        # Use the DATABASE_URL from .env if it exists, otherwise construct one
        if [ -n "$DATABASE_URL" ] && [[ $DATABASE_URL == postgresql* ]]; then
            export TEST_DATABASE_URL="$DATABASE_URL"
            print_success "Using DATABASE_URL from .env"
            echo "  DATABASE_URL: $DATABASE_URL"
            
            # Test the connection
            if psql "$DATABASE_URL" -c "SELECT 1;" >/dev/null 2>&1; then
                print_success "PostgreSQL connection test successful"
                return 0
            else
                print_warning "PostgreSQL connection test failed, falling back to SQLite"
                return 1
            fi
        else
            export DATABASE_URL="postgresql://$(whoami)@localhost:5432/sensor_test_db"
            export TEST_DATABASE_URL="postgresql://$(whoami)@localhost:5432/sensor_test_db"
            export SECRET_KEY="test-secret-key-postgres"
            export ENVIRONMENT="test"
            export DEBUG="True"
            
            print_success "PostgreSQL test database configured"
            echo "  DATABASE_URL: $DATABASE_URL"
            return 0
        fi
    else
        print_warning "PostgreSQL not found, falling back to SQLite"
        return 1
    fi
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if command -v alembic &> /dev/null; then
        # Remove existing database file if using SQLite
        if [[ $DATABASE_URL == sqlite* ]]; then
            rm -f ./test_sensor_api.db
            print_status "Removed existing SQLite test database"
        fi
        
        /usr/bin/python3 -m alembic upgrade head
        print_success "Database migrations completed"
    else
        print_error "Alembic not found. Installing..."
        /usr/bin/python3 -m pip install --user alembic
        /usr/bin/python3 -m alembic upgrade head
        print_success "Database migrations completed"
    fi
}

# Create sample data for testing
create_sample_data() {
    print_status "Creating sample data for testing..."
    
    if [ -f "scripts/create_sample_data.py" ]; then
        python scripts/create_sample_data.py
        print_success "Sample data created"
    else
        print_warning "Sample data script not found, skipping..."
    fi
}

# Run tests
run_tests() {
    local test_type=${1:-"elementary"}
    
    print_status "Running $test_type tests..."
    
    # Ensure we're in the right directory and Python path is set
    export PYTHONPATH="$PWD:$PYTHONPATH"
    
    case $test_type in
        "elementary")
            /usr/bin/python3 -m pytest tests/test_elementary.py -v
            ;;
        "crud")
            /usr/bin/python3 -m pytest tests/test_*_crud.py -v
            ;;
        "integration")
            /usr/bin/python3 -m pytest tests/test_integration.py -v
            ;;
        "all")
            /usr/bin/python3 -m pytest tests/ -v
            ;;
        "coverage")
            /usr/bin/python3 -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v
            ;;
        *)
            print_error "Unknown test type: $test_type"
            print_status "Available types: elementary, crud, integration, all, coverage"
            exit 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_success "$test_type tests completed successfully! 🎉"
    else
        print_error "$test_type tests failed!"
        exit 1
    fi
}

# Show test results summary
show_results() {
    print_status "Test Results Summary:"
    echo "====================="
    
    if [ -f "htmlcov/index.html" ]; then
        print_success "Coverage report generated: htmlcov/index.html"
    fi
    
    if [[ $DATABASE_URL == sqlite* ]]; then
        print_status "Test database: ./test_sensor_api.db (SQLite)"
    else
        print_status "Test database: $DATABASE_URL"
    fi
}

# Cleanup
cleanup() {
    print_status "Cleaning up test environment..."
    
    if [[ $DATABASE_URL == sqlite* ]]; then
        if [ -f "./test_sensor_api.db" ]; then
            rm -f ./test_sensor_api.db
            print_success "SQLite test database removed"
        fi
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [command] [test_type]"
    echo ""
    echo "Commands:"
    echo "  setup     - Setup test environment (PostgreSQL or SQLite)"
    echo "  test      - Run tests (requires test_type)"
    echo "  cleanup   - Clean up test files"
    echo "  full      - Complete setup and run tests"
    echo ""
    echo "Test types:"
    echo "  elementary  - Basic functionality tests"
    echo "  crud       - CRUD operation tests"
    echo "  integration - Integration workflow tests"
    echo "  all        - All tests"
    echo "  coverage   - All tests with coverage report"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 test elementary"
    echo "  $0 full coverage"
    echo "  $0 cleanup"
}

# Main execution
main() {
    local command=${1:-"help"}
    local test_type=${2:-"elementary"}
    
    case $command in
        "setup")
            install_dependencies
            if ! setup_local_postgres; then
                setup_sqlite
            fi
            run_migrations
            print_success "🎉 Test environment setup completed!"
            print_status "You can now run tests with: $0 test $test_type"
            ;;
        "test")
            if [ -z "$DATABASE_URL" ]; then
                print_warning "Environment not set up. Running setup first..."
                install_dependencies
                if ! setup_local_postgres; then
                    setup_sqlite
                fi
                run_migrations
            fi
            run_tests $test_type
            show_results
            ;;
        "cleanup")
            cleanup
            ;;
        "full")
            install_dependencies
            if ! setup_local_postgres; then
                setup_sqlite
            fi
            run_migrations
            run_tests $test_type
            show_results
            print_success "🎉 Full test cycle completed!"
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Run main function with all arguments
main "$@"
