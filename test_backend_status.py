#!/usr/bin/env python3
"""
Test Backend Status Script
"""

import requests
import json
import time

# Backend URL
API_URL = "https://my-home-backend-7m6d.onrender.com"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a specific endpoint"""
    try:
        url = f"{API_URL}{endpoint}"
        headers = {"Content-Type": "application/json"} if data else {}
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"✅ {method} {endpoint}: {response.status_code}")
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   Error: {response.text[:200]}...")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ {method} {endpoint}: {e}")
        return False

def main():
    print("🚀 Testing Backend Status")
    print("=" * 50)
    
    # Test basic endpoints
    test_endpoint("/health")
    print()
    
    # Test team endpoints
    test_endpoint("/api/teams/public")
    print()
    
    # Test team creation
    team_data = {
        "name": "Test Team",
        "user_name": "Test Manager", 
        "role": "manager"
    }
    test_endpoint("/api/teams", "POST", team_data)
    print()
    
    # Test login
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    test_endpoint("/api/auth/login", "POST", login_data)
    print()
    
    print("✅ Backend status test completed!")

if __name__ == '__main__':
    main() 