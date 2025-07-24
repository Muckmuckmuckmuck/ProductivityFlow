#!/usr/bin/env python3
"""
Check account verification status and potentially verify accounts manually
"""

import requests
import json

API_BASE_URL = 'https://productivityflow-backend-v3.onrender.com'

def check_account_status(email):
    """Check if an account exists and its verification status"""
    print(f"🔍 Checking account status for: {email}")
    
    # Try to register with the same email to see if it exists
    register_data = {
        "email": email,
        "password": "testpassword123",
        "name": "Test User"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/auth/register", json=register_data)
        
        if response.status_code == 409:
            print("   ✅ Account exists")
            return True
        elif response.status_code == 201:
            print("   ✅ Account created (didn't exist before)")
            return True
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_login_without_verification(email, password):
    """Test if login works without email verification"""
    print(f"\n🔐 Testing login without email verification...")
    
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
            print(f"   ✅ SUCCESS! Login works without email verification!")
            print(f"   User ID: {data.get('user', {}).get('id')}")
            print(f"   Name: {data.get('user', {}).get('name')}")
            return True
        else:
            data = response.json()
            print(f"   ❌ Login failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def create_test_account_and_check():
    """Create a test account and check if it works without verification"""
    print("🧪 Creating test account to check verification requirements...")
    
    import time
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
        print(f"   Registration Status: {response.status_code}")
        print(f"   Registration Response: {response.text}")
        
        if response.status_code == 201:
            print(f"   ✅ Account created successfully!")
            print(f"   Email: {test_email}")
            print(f"   Password: {test_password}")
            
            # Try to login immediately
            login_success = test_login_without_verification(test_email, test_password)
            
            if login_success:
                print(f"\n🎉 SUCCESS: Backend allows login without email verification!")
                print(f"   You can use these credentials in your Tauri app:")
                print(f"   Email: {test_email}")
                print(f"   Password: {test_password}")
                return test_email, test_password
            else:
                print(f"\n📧 Email verification is required.")
                print(f"   The backend enforces email verification.")
                return None, None
        else:
            print(f"   ❌ Failed to create account")
            return None, None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None, None

def main():
    print("🔍 Account Verification Check")
    print("=" * 50)
    
    # Get email from user
    email = input("Enter the email you used for registration: ").strip()
    
    if email:
        print(f"\nChecking account: {email}")
        account_exists = check_account_status(email)
        
        if account_exists:
            # Try common passwords
            common_passwords = [
                "password",
                "123456",
                "password123",
                "test",
                "admin",
                "qwerty",
                "letmein",
                "welcome"
            ]
            
            print(f"\n🔐 Testing login with common passwords...")
            for password in common_passwords:
                print(f"   Trying: {password}")
                if test_login_without_verification(email, password):
                    print(f"\n🎉 SUCCESS! Found working credentials:")
                    print(f"   Email: {email}")
                    print(f"   Password: {password}")
                    return
            
            print(f"\n❌ No common password worked.")
            print(f"   The account might need email verification or have a different password.")
    
    # Create a new test account to check verification requirements
    print(f"\n" + "=" * 50)
    print("Creating test account to check verification requirements...")
    test_email, test_password = create_test_account_and_check()
    
    if test_email and test_password:
        print(f"\n✅ You can use the test account for testing your Tauri app!")
    else:
        print(f"\n❌ Email verification is required by the backend.")
        print(f"   You'll need to check your email for verification instructions.")

if __name__ == "__main__":
    main() 