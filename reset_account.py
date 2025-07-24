#!/usr/bin/env python3
"""
Account Reset/Creation Script
This script helps create a new account or reset existing one
"""

import requests
import json
import sys

# Configuration
BASE_URL = "https://productivityflow-backend-v3.onrender.com"
EMAIL = "infoproductivityflows@gmail.com"
PASSWORD = "testpassword123"  # Simple password for testing
NAME = "Jay Reddy"

def print_status(message, success=True):
    """Print formatted status message"""
    status = "✅" if success else "❌"
    print(f"{status} {message}")

def create_new_account():
    """Create a new account with the specified credentials"""
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
        elif response.status_code == 409:
            print_status("User already exists - will try to login")
            return False
        else:
            print_status(f"Registration failed: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error creating account: {e}", False)
        return False

def test_login():
    """Test login with the specified credentials"""
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

def try_different_passwords():
    """Try common passwords that might have been used"""
    common_passwords = [
        "testpassword123",
        "password123",
        "123456789",
        "jayreddy123",
        "productivityflow",
        "test123",
        "password",
        "jay",
        "reddy"
    ]
    
    print("Trying common passwords...")
    for password in common_passwords:
        try:
            login_data = {
                "email": EMAIL,
                "password": password
            }
            
            response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            if response.status_code == 200:
                print_status(f"Found working password: {password}")
                return password
            elif response.status_code == 401:
                data = response.json()
                if "verification" in data.get("error", "").lower():
                    print_status(f"Password works but verification required: {password}")
                    return password
                    
        except Exception as e:
            continue
    
    print_status("No working password found", False)
    return None

def main():
    """Main account setup process"""
    print("🔧 Account Setup/Reset")
    print("=" * 30)
    print(f"Email: {EMAIL}")
    print(f"Password: {PASSWORD}")
    print(f"Backend: {BASE_URL}")
    print()
    
    # Step 1: Try to create new account
    print("1. Creating new account...")
    if create_new_account():
        print_status("Account created successfully!")
    else:
        print_status("Account already exists or creation failed")
    
    # Step 2: Test login with specified password
    print("\n2. Testing login...")
    if test_login():
        print_status("Login successful with specified password!")
        return
    
    # Step 3: Try different passwords
    print("\n3. Trying different passwords...")
    working_password = try_different_passwords()
    if working_password:
        print_status(f"Found working password: {working_password}")
        print(f"\n🔧 Use this password in the debug page: {working_password}")
        return
    
    # Step 4: Final attempt with new account
    print("\n4. Final attempt - creating fresh account...")
    if create_new_account():
        print_status("Fresh account created!")
        if test_login():
            print_status("Login successful with fresh account!")
            print(f"\n🔧 Use these credentials:")
            print(f"Email: {EMAIL}")
            print(f"Password: {PASSWORD}")
        else:
            print_status("Login failed even with fresh account", False)
    else:
        print_status("Failed to create fresh account", False)
        print("\n🔧 Manual Steps:")
        print("1. Wait for backend deployment to complete")
        print("2. Try creating account with different email")
        print("3. Check if backend is responding correctly")

if __name__ == "__main__":
    main() 