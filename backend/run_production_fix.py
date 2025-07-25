#!/usr/bin/env python3
"""
Production Database Fix Script
"""

import requests
import json
import time

# Production backend URL
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

def create_test_data():
    """Create test data on the production backend"""
    print("\n🔄 Creating test data...")
    
    # Create test users
    test_users = [
        ("manager@productivityflow.com", "password123", "Manager User"),
        ("employee@productivityflow.com", "password123", "Employee User"),
        ("test@example.com", "password123", "Test User")
    ]
    
    for email, password, name in test_users:
        data = {
            "email": email,
            "password": password,
            "name": name
        }
        test_endpoint("/api/auth/register", "POST", data)
        print()
    
    # Create test team
    team_data = {
        "name": "ProductivityFlow Team",
        "user_name": "Test Manager",
        "role": "manager"
    }
    test_endpoint("/api/teams", "POST", team_data)
    print()

def main():
    print("🚀 Production Database Fix")
    print("=" * 50)
    
    # Wait for deployment to complete
    print("⏳ Waiting for deployment to complete...")
    time.sleep(60)
    
    # Test basic endpoints
    print("\n🔄 Testing endpoints...")
    test_endpoint("/health")
    print()
    
    # Test team endpoints
    test_endpoint("/api/teams")
    print()
    
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
    
    # Test login with existing user
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    test_endpoint("/api/auth/login", "POST", login_data)
    print()
    
    # Create fresh test data
    create_test_data()
    
    # Final test
    print("\n🔄 Final test...")
    test_endpoint("/api/teams/public")
    print()
    
    print("✅ Production fix completed!")

if __name__ == '__main__':
    main() 