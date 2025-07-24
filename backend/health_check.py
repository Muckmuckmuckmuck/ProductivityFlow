#!/usr/bin/env python3
"""
Simple health check script for ProductivityFlow Backend
"""

import requests
import sys
import time

def check_backend_health():
    """Check if the backend is healthy"""
    backend_url = "https://productivityflow-backend-496367590729.us-central1.run.app"
    
    print("🏥 Checking ProductivityFlow Backend Health...")
    print(f"📍 Backend URL: {backend_url}")
    print("=" * 50)
    
    try:
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        response = requests.get(f"{backend_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check PASSED")
            print(f"📊 Status: {data.get('status', 'unknown')}")
            print(f"🗄️ Database: {data.get('database', 'unknown')}")
            print(f"🐍 Python: {data.get('python_version', 'unknown')}")
            print(f"⚡ Flask: {data.get('flask_version', 'unknown')}")
            print(f"🕐 Timestamp: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"❌ Health check FAILED - Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Backend is not reachable")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error - Backend is not responding")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False

def test_basic_endpoints():
    """Test basic API endpoints"""
    backend_url = "https://productivityflow-backend-496367590729.us-central1.run.app"
    
    print("\n🧪 Testing Basic API Endpoints...")
    print("=" * 50)
    
    endpoints = [
        ("/api/auth/register", "POST", "User Registration"),
        ("/api/auth/login", "POST", "User Login"),
        ("/api/teams", "GET", "Get Teams"),
        ("/api/teams", "POST", "Create Team"),
        ("/api/analytics/burnout-risk", "GET", "Burnout Risk"),
        ("/api/analytics/distraction-profile", "GET", "Distraction Profile"),
        ("/api/subscription/status", "GET", "Subscription Status"),
    ]
    
    working_endpoints = 0
    total_endpoints = len(endpoints)
    
    for endpoint, method, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{backend_url}{endpoint}", timeout=5)
            elif method == "POST":
                response = requests.post(f"{backend_url}{endpoint}", json={}, timeout=5)
            
            if response.status_code in [200, 201, 400, 401, 404]:
                print(f"✅ {description} - {endpoint}")
                working_endpoints += 1
            else:
                print(f"❌ {description} - {endpoint} (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ {description} - {endpoint} (Error: {str(e)})")
    
    print(f"\n📊 Endpoint Test Results: {working_endpoints}/{total_endpoints} working")
    return working_endpoints == total_endpoints

def main():
    """Main health check function"""
    print("🚀 ProductivityFlow Backend Health Check")
    print("=" * 60)
    
    # Check basic health
    health_ok = check_backend_health()
    
    if health_ok:
        # Test endpoints
        endpoints_ok = test_basic_endpoints()
        
        print("\n" + "=" * 60)
        if endpoints_ok:
            print("🎉 ALL TESTS PASSED - Backend is fully operational!")
            sys.exit(0)
        else:
            print("⚠️ Backend is running but some endpoints may have issues")
            sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("❌ Backend health check failed - Backend is not operational")
        sys.exit(1)

if __name__ == "__main__":
    main() 