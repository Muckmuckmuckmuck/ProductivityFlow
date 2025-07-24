#!/usr/bin/env python3
"""
Test script for employee authentication
"""

import requests
import json

def test_employee_login():
    """Test employee login functionality"""
    
    print("🧪 Testing Employee Authentication...")
    print("=" * 50)
    
    # Test employee login
    login_data = {
        "email": "Jaymreddy12@gmail.com",
        "password": "password123"
    }
    
    print(f"📧 Testing login with: {login_data['email']}")
    
    try:
        # Test through CORS proxy
        response = requests.post(
            "http://localhost:3002/api/auth/employee-login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Employee login successful!")
            print(f"👤 User: {data['user']['name']}")
            print(f"🏢 Team: {data['user']['team_name']}")
            print(f"🔑 Token: {data['token'][:50]}...")
            print("\n🎉 Employee authentication is working perfectly!")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_employee_login()
    if success:
        print("\n✅ All tests passed! Employee tracker is ready to use.")
    else:
        print("\n❌ Tests failed. Please check the backend and CORS proxy.") 