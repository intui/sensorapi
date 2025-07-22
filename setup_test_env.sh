#!/bin/bash

# Test Environment Setup Script
# Sets up Docker test database and runs tests

set -e

echo "🐳 Setting up Docker test environment for Sensor API"
echo "=" * 60

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker daemon."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Start test database
start_test_db() {
    print_status "Starting test database container..."
    
    # Stop and remove existing container if it exists
    if docker ps -a --format 'table {{.Names}}' | grep -q sensor-test-db; then
        print_warning "Existing test database container found. Removing..."
        docker stop sensor-test-db || true
        docker rm sensor-test-db || true
    fi
    
    # Start the test database
    docker-compose -f docker-compose.test.yml up -d test-db
    
    print_status "Waiting for database to be ready..."
    
    # Wait for database to be healthy
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec sensor-test-db pg_isready -U test_user -d sensor_test_db &> /dev/null; then
            print_success "Test database is ready!"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Database failed to start after $max_attempts attempts"
            docker logs sensor-test-db
            exit 1
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    echo
}

# Install test dependencies
install_dependencies() {
    print_status "Installing test dependencies..."
    
    if [ -f "requirements-test.txt" ]; then
        /usr/bin/python3 -m pip install -r requirements-test.txt --user
        print_success "Test dependencies installed"
    else
        print_warning "requirements-test.txt not found, installing basic dependencies..."
        /usr/bin/python3 -m pip install pytest pytest-asyncio httpx pytest-cov fastapi[all] --user
    fi
}

# Set environment variables
set_environment() {
    print_status "Setting up environment variables..."
    
    export DATABASE_URL="postgresql://test_user:test_pass@localhost:5433/sensor_test_db"
    export TEST_DATABASE_URL="postgresql://test_user:test_pass@localhost:5433/sensor_test_db"
    export SECRET_KEY="test-secret-key-for-docker-setup"
    export ENVIRONMENT="test"
    export DEBUG="True"
    export PYTHONPATH="$PWD:$PYTHONPATH"
    
    print_success "Environment variables configured"
    echo "  DATABASE_URL: $DATABASE_URL"
    echo "  PYTHONPATH: $PYTHONPATH"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if [ -f "alembic.ini" ]; then
        /usr/bin/python3 -m alembic upgrade head
        print_success "Database migrations completed"
    else
        print_warning "alembic.ini not found, skipping migrations"
    fi
}

# Run tests
run_tests() {
    local test_type=${1:-"elementary"}
    
    print_status "Running $test_type tests..."
    
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
        print_success "$test_type tests completed successfully!"
    else
        print_error "$test_type tests failed!"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    docker-compose -f docker-compose.test.yml down
    print_success "Cleanup completed"
}

# Show usage
show_usage() {
    echo "Usage: $0 [command] [test_type]"
    echo ""
    echo "Commands:"
    echo "  setup     - Setup Docker test environment"
    echo "  test      - Run tests (requires test_type)"
    echo "  cleanup   - Stop and remove test containers"
    echo "  full      - Complete setup and run tests"
    echo ""
    echo "Test types (for 'test' and 'full' commands):"
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
            check_docker
            start_test_db
            install_dependencies
            set_environment
            run_migrations
            print_success "🎉 Test environment setup completed!"
            print_status "You can now run tests with: $0 test $test_type"
            ;;
        "test")
            check_docker
            start_test_db
            install_dependencies
            set_environment
            run_tests $test_type
            ;;
        "cleanup")
            cleanup
            ;;
        "full")
            check_docker
            start_test_db
            install_dependencies
            set_environment
            run_migrations
            run_tests $test_type
            print_success "🎉 Full test cycle completed!"
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Trap cleanup on script exit
trap cleanup EXIT

# Run main function with all arguments
case ${1:-"help"} in
    "test"|"full")
        # For test commands, don't auto-cleanup to allow database to stay running
        trap - EXIT
        main "$@"
        cleanup
        ;;
    *)
        main "$@"
        ;;
esac
