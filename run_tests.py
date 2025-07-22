"""
Test runner script for Sensor API.
Provides easy commands for running different test suites.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=Path(__file__).parent)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def install_test_dependencies():
    """Install testing dependencies."""
    dependencies = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.20.0",
        "httpx>=0.24.0",
        "pytest-cov>=4.0.0",
        "pytest-xdist>=3.0.0",
        "factory-boy>=3.2.0",
        "faker>=18.0.0",
        "pytest-mock>=3.10.0"
    ]
    
    cmd = f"{sys.executable} -m pip install {' '.join(dependencies)}"
    return run_command(cmd, "Installing test dependencies")


def run_elementary_tests():
    """Run elementary/smoke tests."""
    cmd = "python -m pytest tests/test_elementary.py -v"
    return run_command(cmd, "Running elementary tests")


def run_crud_tests():
    """Run CRUD tests."""
    cmd = "python -m pytest tests/test_*_crud.py -v"
    return run_command(cmd, "Running CRUD tests")


def run_all_tests():
    """Run all tests."""
    cmd = "python -m pytest tests/ -v"
    return run_command(cmd, "Running all tests")


def run_tests_with_coverage():
    """Run tests with coverage report."""
    cmd = "python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v"
    return run_command(cmd, "Running tests with coverage")


def run_performance_tests():
    """Run performance tests."""
    cmd = "python -m pytest tests/test_performance/ -v --timeout=300"
    return run_command(cmd, "Running performance tests")


def run_parallel_tests():
    """Run tests in parallel."""
    cmd = "python -m pytest tests/ -n auto -v"
    return run_command(cmd, "Running tests in parallel")


def setup_test_database():
    """Setup test database."""
    print("\n🗄️  Setting up test database...")
    print("Please ensure you have a test PostgreSQL database running.")
    print("Update the TEST_DATABASE_URL in tests/conftest.py if needed.")
    print("Default: postgresql://test_user:test_pass@localhost:5432/sensor_test_db")
    
    # You might want to add actual database setup commands here
    return True


def main():
    """Main test runner interface."""
    print("🧪 Sensor API Test Runner")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("""
Usage: python run_tests.py <command>

Available commands:
  install     - Install test dependencies
  setup-db    - Setup test database
  elementary  - Run elementary/smoke tests
  crud        - Run CRUD tests
  all         - Run all tests
  coverage    - Run tests with coverage report
  performance - Run performance tests
  parallel    - Run tests in parallel
  
Examples:
  python run_tests.py install
  python run_tests.py elementary
  python run_tests.py coverage
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        install_test_dependencies()
    elif command == "setup-db":
        setup_test_database()
    elif command == "elementary":
        run_elementary_tests()
    elif command == "crud":
        run_crud_tests()
    elif command == "all":
        run_all_tests()
    elif command == "coverage":
        run_tests_with_coverage()
    elif command == "performance":
        run_performance_tests()
    elif command == "parallel":
        run_parallel_tests()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python run_tests.py' without arguments to see available commands.")


if __name__ == "__main__":
    main()
