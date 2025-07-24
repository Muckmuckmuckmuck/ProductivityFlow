#!/usr/bin/env python3
"""
Test script to check password verification and user account status
"""

import requests
import json

API_BASE_URL = 'https://productivityflow-backend-v3.onrender.com'

def test_user_status():
    """Test the status of the jaymreddy12@gmail.com account"""
    print("🔍 Testing user account status...")
    
    # Test 1: Try to register with the same email (should fail with 409)
    print("\n1️⃣ Testing registration with existing email...")
    register_data = {
        "email": "jaymreddy12@gmail.com",
        "password": "testpassword123",
        "name": "Jay Reddy"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/auth/register", json=register_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 409:
            print("   ✅ User account exists (as expected)")
        else:
            print("   ❌ Unexpected response")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_login_with_different_passwords():
    """Test login with different passwords to see what happens"""
    print("\n2️⃣ Testing login with different passwords...")
    
    test_passwords = [
        "testpassword123",  # The password we used in registration test
        "password123",      # Common password
        "jaymreddy12",      # Email-based password
        "12345678",         # Simple password
        "wrongpassword"     # Obviously wrong
    ]
    
    for password in test_passwords:
        print(f"\n   Testing password: {password}")
        login_data = {
            "email": "jaymreddy12@gmail.com",
            "password": password
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS! Password works: {password}")
                data = response.json()
                print(f"   User ID: {data.get('user', {}).get('id')}")
                print(f"   Name: {data.get('user', {}).get('name')}")
                return password
            else:
                data = response.json()
                print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def test_backend_health():
    """Test if backend is responding"""
    print("\n3️⃣ Testing backend health...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
        else:
            print("   ❌ Backend health check failed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("🧪 Password Verification Test")
    print("=" * 50)
    
    test_backend_health()
    test_user_status()
    working_password = test_login_with_different_passwords()
    
    print("\n" + "=" * 50)
    if working_password:
        print(f"🎉 SUCCESS: Found working password: {working_password}")
        print("The issue was likely that you were using a different password than expected.")
    else:
        print("❌ No working password found. The account might have a different password than expected.")
        print("💡 Try creating a new account with a different email to test the flow.")

if __name__ == "__main__":
    main() 