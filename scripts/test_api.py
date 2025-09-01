#!/usr/bin/env python3
"""
Test script to verify database switching functionality.
"""

import sys
import requests
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_api_endpoints():
    """Test the API endpoints to verify database functionality."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing API endpoints...")
    print("=" * 50)
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint:")
            print(f"   Provider: {data.get('database_provider', 'Unknown')}")
            print(f"   Environment: {data.get('environment', 'Unknown')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test health endpoint
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint:")
            print(f"   Status: {data.get('status', 'Unknown')}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
        
        # Test database info endpoint
        response = requests.get(f"{base_url}/api/v1/database/info")
        if response.status_code == 200:
            data = response.json()
            print("✅ Database info endpoint:")
            db_info = data.get('database', {})
            stats = data.get('statistics', {})
            
            print(f"   Provider: {db_info.get('provider', 'Unknown')}")
            print(f"   Version: {db_info.get('version', 'Unknown')[:50]}...")
            print(f"   TimescaleDB: {db_info.get('timescaledb_version', 'Not available')}")
            print(f"   API Tables: {stats.get('api_tables', 0)}")
            print(f"   Sensor Readings: {stats.get('sensor_readings', 0):,}")
            print(f"   Is Tiger Cloud: {db_info.get('is_tiger_cloud', False)}")
        else:
            print(f"❌ Database info endpoint failed: {response.status_code}")
        
        # Test switch guide endpoint
        response = requests.get(f"{base_url}/api/v1/database/switch-guide")
        if response.status_code == 200:
            data = response.json()
            print("✅ Switch guide endpoint:")
            print(f"   Current: {data.get('current_provider', 'Unknown')}")
            print(f"   Available: {data.get('available_providers', [])}")
        else:
            print(f"❌ Switch guide endpoint failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the API server running?")
        print("💡 Start the server with: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
        return False

if __name__ == "__main__":
    print("📊 Database Management System Test")
    print("=" * 50)
    
    success = test_api_endpoints()
    
    if success:
        print("\n🎉 All tests passed!")
        print("\n💡 Try switching databases:")
        print("   python scripts/manage_database.py switch tiger_cloud")
        print("   python scripts/test_api.py")
        print("   python scripts/manage_database.py switch aiven")
        print("   python scripts/test_api.py")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)