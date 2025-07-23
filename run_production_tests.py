#!/usr/bin/env python3
"""
Production Test Runner

This script runs tests against the production Vercel deployment.
It uses HTTP requests to test the API endpoints without requiring database access.

Usage:
    python run_production_tests.py [options]

Options:
    --url URL       Production API URL (default: auto-detect from vercel)
    --verbose       Verbose test output
    --fast          Run only fast tests (skip slow/cleanup tests)
    --health-only   Run only health check tests
    --cleanup       Run cleanup tests (creates temporary data)
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def get_production_url():
    """Get the production URL from Vercel."""
    try:
        result = subprocess.run(
            ["vercel", "ls", "--json"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            import json
            deployments = json.loads(result.stdout)
            
            # Find the most recent production deployment
            for deployment in deployments:
                if deployment.get("target") == "production":
                    return f"https://{deployment['url']}"
        
        # Fallback to default
        return "https://sensorapi-cpbpps2rw-widos-projects.vercel.app"
        
    except Exception as e:
        print(f"Warning: Could not get Vercel URL automatically: {e}")
        return "https://sensorapi-cpbpps2rw-widos-projects.vercel.app"


def run_production_tests(args):
    """Run production tests with specified options."""
    
    # Set up test environment
    test_env = os.environ.copy()
    
    # Build pytest command
    pytest_args = [
        sys.executable, "-m", "pytest",
        "tests/test_production.py",
        "--tb=short"
    ]
    
    # Add verbosity
    if args.verbose:
        pytest_args.append("-v")
    else:
        pytest_args.append("-q")
    
    # Test filtering
    if args.health_only:
        pytest_args.extend(["-k", "health"])
    elif args.fast:
        pytest_args.extend(["-m", "not slow and not cleanup_required"])
    elif not args.cleanup:
        pytest_args.extend(["-m", "not cleanup_required"])
    
    # Set production URL in environment
    if args.url:
        # Update the conftest file with the custom URL
        conftest_path = Path("tests/conftest_production.py")
        if conftest_path.exists():
            with open(conftest_path, 'r') as f:
                content = f.read()
            
            # Replace the URL
            updated_content = content.replace(
                'PRODUCTION_API_URL = "https://sensorapi-cpbpps2rw-widos-projects.vercel.app"',
                f'PRODUCTION_API_URL = "{args.url}"'
            )
            
            with open(conftest_path, 'w') as f:
                f.write(updated_content)
    
    print(f"🚀 Running production tests against: {args.url or get_production_url()}")
    print(f"📋 Test command: {' '.join(pytest_args)}")
    print("-" * 60)
    
    # Run tests
    result = subprocess.run(pytest_args, env=test_env)
    
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run tests against production Sensor API deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_production_tests.py --health-only
    python run_production_tests.py --verbose --fast
    python run_production_tests.py --url https://my-custom-api.vercel.app
    python run_production_tests.py --cleanup  # Creates test data
        """
    )
    
    parser.add_argument(
        "--url",
        help="Production API URL to test against"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose test output"
    )
    
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run only fast tests (exclude slow/cleanup tests)"
    )
    
    parser.add_argument(
        "--health-only",
        action="store_true",
        help="Run only health check tests"
    )
    
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Include tests that create temporary data (requires cleanup)"
    )
    
    args = parser.parse_args()
    
    # Set default URL if not provided
    if not args.url:
        args.url = get_production_url()
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    try:
        return run_production_tests(args)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
