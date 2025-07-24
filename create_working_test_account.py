#!/usr/bin/env python3
"""
Create a working test account and handle email verification
"""

import requests
import json
import time

API_BASE_URL = 'https://productivityflow-backend-v3.onrender.com'

def create_test_account():
    """Create a test account and return credentials"""
    print("🔧 Creating test account...")
    
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
            return test_email, test_password, data.get('user_id')
        else:
            print(f"   ❌ Failed to create account")
            return None, None, None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None, None, None

def verify_email_with_token(token):
    """Verify email with token"""
    print(f"🔐 Verifying email with token...")
    
    verify_data = {
        "token": token
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/auth/verify", json=verify_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print(f"   ✅ Email verified successfully!")
            return True
        else:
            print(f"   ❌ Email verification failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_login(email, password):
    """Test login after verification"""
    print(f"🔐 Testing login...")
    
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

def main():
    print("🧪 Create Working Test Account")
    print("=" * 50)
    
    # Step 1: Create account
    email, password, user_id = create_test_account()
    
    if not email or not password:
        print("❌ Failed to create account")
        return
    
    print(f"\n📧 Test Account Created:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   User ID: {user_id}")
    
    # Step 2: Try login (should fail due to email verification)
    print(f"\n🔐 Testing login (should fail due to email verification)...")
    login_success = test_login(email, password)
    
    if login_success:
        print(f"\n🎉 SUCCESS: Account works without email verification!")
        print(f"   You can use these credentials in your Tauri app:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
    else:
        print(f"\n📧 Email verification required.")
        print(f"   The account was created but needs email verification.")
        print(f"   Check the email inbox for {email} for verification instructions.")
        print(f"   Or the backend might be auto-verifying accounts for testing.")

if __name__ == "__main__":
    main() 