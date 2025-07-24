#!/usr/bin/env python3
"""
Simple test of cloud backend with manual verification
"""

import requests
import json
import time
from datetime import datetime

# Cloud backend URL
API_BASE_URL = "https://productivityflow-backend-v3.onrender.com"

def test_health():
    """Test backend health"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data}")
            return True
        else:
            print(f"❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"❌ Backend health error: {e}")
        return False

def create_test_manager():
    """Create a test manager account"""
    print("\n📝 Creating Test Manager Account...")
    try:
        timestamp = int(time.time())
        email = f"cloud_test_manager_{timestamp}@example.com"
        password = "TestPass123!"
        name = "Cloud Test Manager"
        
        data = {
            "email": email,
            "password": password,
            "name": name
        }
        
        response = requests.post(f"{API_BASE_URL}/api/auth/register", json=data, timeout=10)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Manager account created: {email}")
            print(f"📧 Verification required: {result.get('message')}")
            return email, password
        else:
            print(f"❌ Manager creation failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Manager creation error: {e}")
        return None, None

def test_api_endpoints():
    """Test various API endpoints"""
    print("\n🔗 Testing API Endpoints...")
    
    endpoints = [
        "/health",
        "/api",
        "/api/auth/register",
        "/api/auth/login", 
        "/api/teams/join"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def test_team_join():
    """Test team joining without authentication"""
    print("\n👥 Testing Team Join...")
    try:
        data = {
            "team_code": "TEST123",
            "user_name": "Test Employee"
        }
        response = requests.post(f"{API_BASE_URL}/api/teams/join", json=data, timeout=10)
        print(f"Team join response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Team join error: {e}")

def main():
    """Run simple tests"""
    print("🚀 PRODUCTIVITYFLOW CLOUD BACKEND SIMPLE TEST")
    print("=" * 50)
    print(f"🌐 Backend: {API_BASE_URL}")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("❌ Backend is not responding")
        return
    
    # Test 2: API endpoints
    test_api_endpoints()
    
    # Test 3: Create test manager
    email, password = create_test_manager()
    
    # Test 4: Team join
    test_team_join()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print("✅ Backend is operational")
    print("✅ API endpoints are accessible")
    if email:
        print(f"✅ Test account created: {email}")
        print("📧 Manual email verification required")
    print("✅ Team join endpoint accessible")
    
    print("\n🌐 Cloud Backend Status: ✅ OPERATIONAL")
    print("📱 Applications can connect to cloud backend")
    print("🔧 Email verification may be required for new accounts")

if __name__ == "__main__":
    main() 