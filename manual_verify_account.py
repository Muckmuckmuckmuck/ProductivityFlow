#!/usr/bin/env python3
"""
Manual Account Verification Script
This script helps verify user accounts when email verification is not working
"""

import requests
import json
import sys

# Configuration
BASE_URL = "https://productivityflow-backend-v3.onrender.com"
EMAIL = "infoproductivityflows@gmail.com"

def print_status(message, success=True):
    """Print formatted status message"""
    status = "✅" if success else "❌"
    print(f"{status} {message}")

def check_user_status():
    """Check if user exists and verification status"""
    try:
        # Try to login to see the current status
        login_data = {
            "email": EMAIL,
            "password": "testpassword123"  # Use the password you set
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print_status("User is already verified and can login!")
            return True
        elif response.status_code == 401:
            data = response.json()
            if "verification" in data.get("error", "").lower():
                print_status("User exists but needs verification", False)
                return False
            else:
                print_status(f"Login failed: {data.get('error')}", False)
                return False
        else:
            print_status(f"Unexpected response: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error checking user status: {e}", False)
        return False

def try_manual_verification():
    """Try the manual verification endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/auth/verify-manual/{EMAIL}")
        print(f"Manual verification response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print_status("Manual verification successful!")
            return True
        elif response.status_code == 403:
            print_status("Manual verification not available in production mode", False)
            return False
        elif response.status_code == 404:
            print_status("Manual verification endpoint not found (not deployed yet)", False)
            return False
        else:
            print_status(f"Manual verification failed: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error with manual verification: {e}", False)
        return False

def try_regular_verification():
    """Try to get verification token and verify normally"""
    try:
        # First, try to register again to get a new verification token
        register_data = {
            "email": EMAIL,
            "password": "testpassword123",
            "name": "Jay Reddy"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Registration response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 409:
            print_status("User already exists - checking if we can get verification info")
            # Try to get verification info from the response
            data = response.json()
            if "verification_token" in data:
                print_status("Found verification token in response")
                return verify_with_token(data["verification_token"])
            else:
                print_status("No verification token found in response", False)
                return False
        else:
            print_status(f"Unexpected registration response: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error with regular verification: {e}", False)
        return False

def verify_with_token(token):
    """Verify account with token"""
    try:
        verify_data = {"token": token}
        response = requests.post(f"{BASE_URL}/api/auth/verify", json=verify_data)
        print(f"Verification response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print_status("Account verified successfully!")
            return True
        else:
            print_status(f"Verification failed: {response.status_code}", False)
            return False
            
    except Exception as e:
        print_status(f"Error verifying with token: {e}", False)
        return False

def main():
    """Main verification process"""
    print("🔧 Manual Account Verification")
    print("=" * 40)
    print(f"Email: {EMAIL}")
    print(f"Backend: {BASE_URL}")
    print()
    
    # Step 1: Check current user status
    print("1. Checking user status...")
    if check_user_status():
        print_status("User is already verified and can login!")
        return
    
    # Step 2: Try manual verification
    print("\n2. Trying manual verification...")
    if try_manual_verification():
        print_status("Manual verification successful!")
        return
    
    # Step 3: Try regular verification
    print("\n3. Trying regular verification...")
    if try_regular_verification():
        print_status("Regular verification successful!")
        return
    
    # Step 4: Final check
    print("\n4. Final status check...")
    if check_user_status():
        print_status("User is now verified!")
    else:
        print_status("Verification failed - backend changes may not be deployed yet", False)
        print("\n🔧 Next Steps:")
        print("1. Wait for backend deployment to complete (5-10 minutes)")
        print("2. Check if email credentials are configured")
        print("3. Try the verification process again")

if __name__ == "__main__":
    main() 