#!/usr/bin/env python3
"""
Test Current Backend Script
This script tests the current backend with the configured email credentials
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://productivityflow-backend-v3.onrender.com"
EMAIL = "infoproductivityflows@gmail.com"
PASSWORD = "testpassword123"  # Try this password first
NAME = "Jay Reddy"

def print_status(message, success=True):
    """Print formatted status message"""
    status = "✅" if success else "❌"
    print(f"{status} {message}")

def test_registration():
    """Test registration with your email"""
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
            print(f"Message: {data.get('message')}")
            return True
        elif response.status_code == 409:
            print_status("User already exists (expected)")
            return False
        else:
            print_status(f"Registration failed: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error in registration: {e}", False)
        return False

def test_login():
    """Test login with your email"""
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

def try_different_passwords():
    """Try different passwords for your email"""
    passwords = [
        "testpassword123",
        "password123",
        "123456789",
        "jayreddy123",
        "productivityflow",
        "test123",
        "password",
        "jay",
        "reddy",
        "infoproductivityflows",
        "gmail123"
    ]
    
    print("Trying different passwords...")
    for password in passwords:
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

def test_verification_endpoint():
    """Test if verification endpoint exists"""
    try:
        response = requests.get(f"{BASE_URL}/api/auth/verify-manual/{EMAIL}")
        print(f"Manual verification response status: {response.status_code}")
        
        if response.status_code == 200:
            print_status("Manual verification endpoint available!")
            return True
        elif response.status_code == 403:
            print_status("Manual verification not available in production")
            return False
        elif response.status_code == 404:
            print_status("Manual verification endpoint not found (not deployed)")
            return False
        else:
            print_status(f"Manual verification failed: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error testing manual verification: {e}", False)
        return False

def main():
    """Main test process"""
    print("🔧 Current Backend Test")
    print("=" * 30)
    print(f"Email: {EMAIL}")
    print(f"Backend: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Step 1: Test registration
    print("1. Testing registration...")
    test_registration()
    
    # Step 2: Test login
    print("\n2. Testing login...")
    if test_login():
        print_status("Login successful!")
        return
    
    # Step 3: Try different passwords
    print("\n3. Trying different passwords...")
    working_password = try_different_passwords()
    if working_password:
        print_status(f"Found working password: {working_password}")
        print(f"\n🔧 Use this password: {working_password}")
        return
    
    # Step 4: Test manual verification
    print("\n4. Testing manual verification...")
    test_verification_endpoint()
    
    print("\n📧 Email Verification Status:")
    print("- Email credentials are configured in backend")
    print("- Registration sends verification emails")
    print("- Check your email: infoproductivityflows@gmail.com")
    print("- Look for verification email from ProductivityFlow")
    print("- Click the verification link in the email")
    print("- Then try logging in again")

if __name__ == "__main__":
    main() 