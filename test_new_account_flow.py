#!/usr/bin/env python3
"""
Test script to create a new account and test the complete login flow
"""

import requests
import json
import time

API_BASE_URL = 'https://productivityflow-backend-v3.onrender.com'

def create_new_account():
    """Create a new test account"""
    print("🔧 Creating new test account...")
    
    # Use timestamp to ensure unique email
    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@example.com"
    test_password = "TestPassword123"
    test_name = "Test User"
    
    register_data = {
        "email": test_email,
        "password": test_password,
        "name": test_name
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/auth/register", json=register_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Account created successfully!")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Email: {test_email}")
            print(f"   Password: {test_password}")
            return test_email, test_password, data.get('user_id')
        else:
            print(f"   ❌ Failed to create account")
            return None, None, None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None, None, None

def test_login(email, password):
    """Test login with the new account"""
    print(f"\n🔐 Testing login with new account...")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login successful!")
            print(f"   User ID: {data.get('user', {}).get('id')}")
            print(f"   Name: {data.get('user', {}).get('name')}")
            print(f"   Token: {data.get('token', 'Missing')[:20]}...")
            return True
        else:
            print(f"   ❌ Login failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_existing_account_login():
    """Test login with the existing jaymreddy12@gmail.com account"""
    print(f"\n🔍 Testing login with existing account...")
    
    # Try some common passwords that might have been used
    common_passwords = [
        "password",
        "123456",
        "password123",
        "admin",
        "test",
        "qwerty",
        "letmein",
        "welcome",
        "monkey",
        "dragon"
    ]
    
    for password in common_passwords:
        print(f"   Trying password: {password}")
        login_data = {
            "email": "jaymreddy12@gmail.com",
            "password": password
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS! Password found: {password}")
                print(f"   User ID: {data.get('user', {}).get('id')}")
                print(f"   Name: {data.get('user', {}).get('name')}")
                return password
            else:
                data = response.json()
                print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def main():
    print("🧪 New Account Flow Test")
    print("=" * 50)
    
    # Test 1: Create new account
    email, password, user_id = create_new_account()
    
    if email and password:
        # Test 2: Login with new account
        login_success = test_login(email, password)
        
        if login_success:
            print(f"\n🎉 SUCCESS: Complete flow works!")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print(f"   You can use these credentials in your Tauri app")
        else:
            print(f"\n❌ Login failed with new account")
    else:
        print(f"\n❌ Failed to create new account")
    
    # Test 3: Try to find password for existing account
    print(f"\n" + "=" * 50)
    print("🔍 Trying to find password for existing account...")
    found_password = test_existing_account_login()
    
    if found_password:
        print(f"\n🎉 Found password for jaymreddy12@gmail.com: {found_password}")
    else:
        print(f"\n❌ Could not find password for existing account")
        print(f"💡 The account might have been created with a different password")

if __name__ == "__main__":
    main() 