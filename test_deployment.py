#!/usr/bin/env python3
"""
Test Deployment Script
Monitors backend deployment and tests new endpoints
"""

import requests
import time
import json
from datetime import datetime

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a specific endpoint"""
    url = f"https://my-home-backend-7m6d.onrender.com{endpoint}"
    headers = {"Content-Type": "application/json"} if data else {}
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"🔍 {description}")
        print(f"   {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                if "success" in result:
                    print(f"   ✅ Success: {result['success']}")
                if "message" in result:
                    print(f"   📝 Message: {result['message']}")
                if "team" in result:
                    print(f"   🏢 Team: {result['team']['name']} (Code: {result['team']['employee_code']})")
                return True
            except:
                print(f"   📄 Response: {response.text[:100]}...")
                return True
        else:
            if response.status_code == 404:
                print(f"   ❌ Endpoint not found (deployment in progress)")
            else:
                print(f"   ⚠️ Error: {response.status_code}")
                try:
                    error = response.json()
                    print(f"   📝 Error: {error.get('message', 'Unknown error')}")
                except:
                    print(f"   📄 Response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 ProductivityFlow Backend Deployment Test")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test existing endpoints first
    print("\n📋 Testing Existing Endpoints:")
    test_endpoint("GET", "/health", description="Health Check")
    test_endpoint("POST", "/api/teams", {"name": "Test Team", "user_name": "Test Manager"}, "Team Creation")
    
    # Test new endpoints (these should work after deployment)
    print("\n🆕 Testing New Endpoints (deployment pending):")
    
    endpoints_to_test = [
        ("POST", "/api/auth/register", {
            "name": "Test Manager", 
            "email": "test@example.com", 
            "password": "TestPassword123", 
            "organization": "Test Organization"
        }, "Manager Registration"),
        
        ("POST", "/api/auth/login", {
            "email": "test@example.com", 
            "password": "TestPassword123"
        }, "Manager Login"),
        
        ("POST", "/api/auth/employee-login", {
            "team_code": "VK95I2",
            "user_name": "Test Employee"
        }, "Employee Login"),
        
        ("POST", "/api/teams/join", {
            "employee_code": "VK95I2",
            "user_name": "New Employee"
        }, "Team Join"),
        
        ("GET", "/api/analytics/burnout-risk", None, "Burnout Risk Analysis"),
        ("GET", "/api/analytics/distraction-profile", None, "Distraction Profile"),
    ]
    
    for method, endpoint, data, description in endpoints_to_test:
        test_endpoint(method, endpoint, data, description)
        time.sleep(1)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT STATUS SUMMARY")
    print("=" * 50)
    
    # Check health again
    try:
        response = requests.get("https://my-home-backend-7m6d.onrender.com/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Status: {data.get('status', 'unknown')}")
            print(f"📊 Version: {data.get('version', 'unknown')}")
            print(f"🌍 Environment: {data.get('environment', 'unknown')}")
            print(f"🗄️ Database: {data.get('database', 'unknown')}")
        else:
            print(f"⚠️ Backend Status: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Backend Status: {e}")
    
    print("\n📋 NEXT STEPS:")
    print("1. If new endpoints return 404, the deployment is still in progress")
    print("2. Wait 2-5 minutes for Render to deploy the updated backend")
    print("3. Run this script again to test the new endpoints")
    print("4. Monitor deployment at: https://dashboard.render.com")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 