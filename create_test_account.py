#!/usr/bin/env python3
"""
Create Test Account Script
This script creates a fresh test account with known credentials
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://productivityflow-backend-v3.onrender.com"
EMAIL = f"test{int(datetime.now().timestamp())}@example.com"  # Unique email
PASSWORD = "testpassword123"
NAME = "Test User"

def print_status(message, success=True):
    """Print formatted status message"""
    status = "✅" if success else "❌"
    print(f"{status} {message}")

def create_account():
    """Create a new account"""
    try:
        register_data = {
            "email": EMAIL,
            "password": PASSWORD,
            "name": NAME
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Registration response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            print_status("Account created successfully!")
            print(f"User ID: {data.get('user_id')}")
            print(f"Verified: {data.get('user', {}).get('is_verified')}")
            print(f"Dev mode: {data.get('dev_mode')}")
            return True
        else:
            print_status(f"Registration failed: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error creating account: {e}", False)
        return False

def test_login():
    """Test login with the new account"""
    try:
        login_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print_status("Login successful!")
            print(f"Token received: {bool(data.get('token'))}")
            print(f"User: {data.get('user', {}).get('name')}")
            return True
        elif response.status_code == 401:
            data = response.json()
            if "verification" in data.get("error", "").lower():
                print_status("Login blocked - verification required", False)
                return False
            else:
                print_status(f"Login failed: {data.get('error')}", False)
                return False
        else:
            print_status(f"Unexpected login response: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error testing login: {e}", False)
        return False

def main():
    """Main account creation process"""
    print("🔧 Create Test Account")
    print("=" * 25)
    print(f"Email: {EMAIL}")
    print(f"Password: {PASSWORD}")
    print(f"Name: {NAME}")
    print(f"Backend: {BASE_URL}")
    print()
    
    # Step 1: Create account
    print("1. Creating new account...")
    if create_account():
        print_status("Account created successfully!")
    else:
        print_status("Account creation failed", False)
        return
    
    # Step 2: Test login
    print("\n2. Testing login...")
    if test_login():
        print_status("Login successful!")
        print(f"\n🎉 SUCCESS! Use these credentials in the debug page:")
        print(f"Email: {EMAIL}")
        print(f"Password: {PASSWORD}")
        print(f"Name: {NAME}")
        print(f"\n🔧 These credentials should work immediately!")
    else:
        print_status("Login failed", False)
        print(f"\n🔧 Account created but login failed. Try manually with:")
        print(f"Email: {EMAIL}")
        print(f"Password: {PASSWORD}")

if __name__ == "__main__":
    main() 