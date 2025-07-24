#!/usr/bin/env python3
"""
Quick Authentication Test for ProductivityFlow Backend
Tests sign-up and sign-in functionality
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "testpassword123"
TEST_NAME = "Test User"

def print_test(test_name, status, message=""):
    """Print test result with formatting"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {test_name}: {'PASS' if status else 'FAIL'}")
    if message:
        print(f"   {message}")

def test_authentication():
    """Test the authentication system"""
    print("🔐 Testing ProductivityFlow Authentication System")
    print("=" * 50)
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_test("Health Check", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Health Check", False, f"Error: {e}")
        return False
    
    # Test 2: User Registration
    try:
        register_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        success = response.status_code == 201
        print_test("User Registration", success, f"Status: {response.status_code}")
        
        if success:
            register_response = response.json()
            print(f"   User ID: {register_response.get('user_id', 'N/A')}")
            print(f"   Message: {register_response.get('message', 'N/A')}")
        else:
            print(f"   Error: {response.json().get('error', 'Unknown error')}")
            
    except Exception as e:
        print_test("User Registration", False, f"Error: {e}")
        return False
    
    # Test 3: User Login
    try:
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        success = response.status_code == 200
        print_test("User Login", success, f"Status: {response.status_code}")
        
        if success:
            login_response = response.json()
            token = login_response.get('token')
            user_id = login_response.get('user_id')
            print(f"   User ID: {user_id}")
            print(f"   Token: {token[:20]}..." if token else "No token")
        else:
            print(f"   Error: {response.json().get('error', 'Unknown error')}")
            
    except Exception as e:
        print_test("User Login", False, f"Error: {e}")
        return False
    
    # Test 4: Team Creation (if login successful)
    if success and token:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            team_data = {
                "name": "Test Team",
                "employee_code": "TEST123"
            }
            response = requests.post(f"{BASE_URL}/api/teams", json=team_data, headers=headers)
            success = response.status_code == 201
            print_test("Team Creation", success, f"Status: {response.status_code}")
            
            if success:
                team_response = response.json()
                team_id = team_response.get('team_id')
                print(f"   Team ID: {team_id}")
            else:
                print(f"   Error: {response.json().get('error', 'Unknown error')}")
                
        except Exception as e:
            print_test("Team Creation", False, f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Authentication Test Complete!")
    return True

if __name__ == "__main__":
    test_authentication() 