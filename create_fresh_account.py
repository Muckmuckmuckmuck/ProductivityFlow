#!/usr/bin/env python3
"""
Create Fresh Account Script
This script creates a fresh account with the user's email and a known password
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://productivityflow-backend-v3.onrender.com"
EMAIL = "infoproductivityflows@gmail.com"
PASSWORD = "jayreddy123"  # Simple password we know
NAME = "Jay Reddy"

def print_status(message, success=True):
    """Print formatted status message"""
    status = "✅" if success else "❌"
    print(f"{status} {message}")

def create_fresh_account():
    """Create a fresh account with known password"""
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
            print_status("Fresh account created successfully!")
            print(f"User ID: {data.get('user_id')}")
            print(f"Message: {data.get('message')}")
            return True
        elif response.status_code == 409:
            print_status("User already exists - cannot create fresh account")
            return False
        else:
            print_status(f"Registration failed: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error creating account: {e}", False)
        return False

def test_login():
    """Test login with the new password"""
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
                print_status("Login blocked - verification required (check email)")
                return False
            else:
                print_status(f"Login failed: {data.get('error')}", False)
                return False
        else:
            print_status(f"Unexpected login response: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error in login: {e}", False)
        return False

def main():
    """Main account creation process"""
    print("🔧 Create Fresh Account")
    print("=" * 25)
    print(f"Email: {EMAIL}")
    print(f"Password: {PASSWORD}")
    print(f"Name: {NAME}")
    print(f"Backend: {BASE_URL}")
    print()
    
    # Step 1: Create fresh account
    print("1. Creating fresh account...")
    if create_fresh_account():
        print_status("Fresh account created!")
        
        # Step 2: Test login
        print("\n2. Testing login...")
        if test_login():
            print_status("Login successful!")
            print(f"\n🎉 SUCCESS! Use these credentials:")
            print(f"Email: {EMAIL}")
            print(f"Password: {PASSWORD}")
            print(f"\n🔧 These credentials should work!")
        else:
            print_status("Login failed - check email for verification")
            print(f"\n📧 Check your email: {EMAIL}")
            print("Look for verification email from ProductivityFlow")
            print("Click the verification link, then try logging in again")
    else:
        print_status("Cannot create fresh account - user already exists")
        print(f"\n🔧 Try logging in with:")
        print(f"Email: {EMAIL}")
        print(f"Password: {PASSWORD}")
        print("\n📧 Or check your email for verification link")

if __name__ == "__main__":
    main() 