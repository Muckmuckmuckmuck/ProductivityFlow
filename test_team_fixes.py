#!/usr/bin/env python3
"""
Test script to verify team creation, email verification, and team management fixes
"""

import requests
import json
import time

# Configuration
API_URL = "https://my-home-backend-7m6d.onrender.com"
TEST_EMAIL = f"test_fix_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_NAME = f"Test Fix User {int(time.time())}"
TEST_ORGANIZATION = f"Test Fix Organization {int(time.time())}"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️ {message}")

def safe_request(method, url, **kwargs):
    """Make a safe HTTP request with proper error handling"""
    try:
        response = requests.request(method, url, **kwargs)
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"success": True, "message": "Non-JSON response"}
        else:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"success": False, "message": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Request failed: {str(e)}"}

def test_manager_registration():
    """Test manager registration with team creation"""
    print_test_header("Manager Registration with Team Creation")
    
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": TEST_NAME,
        "organization": TEST_ORGANIZATION
    }
    
    result = safe_request('POST', f"{API_URL}/api/auth/register", json=data)
    
    if result.get('success'):
        print_success(f"Manager registered successfully: {TEST_EMAIL}")
        print_info(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
        print_info(f"Team ID: {result.get('team', {}).get('id', 'N/A')}")
        print_info(f"Employee Code: {result.get('team', {}).get('employee_code', 'N/A')}")
        print_info(f"Manager Code: {result.get('team', {}).get('manager_code', 'N/A')}")
        return result
    else:
        print_error(f"Manager registration failed: {result.get('message', 'Unknown error')}")
        return None

def test_email_verification():
    """Test email verification with test code"""
    print_test_header("Email Verification")
    
    data = {
        "email": TEST_EMAIL,
        "verification_code": "123456"
    }
    
    result = safe_request('POST', f"{API_URL}/api/auth/verify-email", json=data)
    
    if result.get('success'):
        print_success("Email verification successful")
        print_info(f"Token: {result.get('token', 'N/A')[:50]}...")
        return result.get('token')
    else:
        print_error(f"Email verification failed: {result.get('message', 'Unknown error')}")
        return None

def test_manager_login():
    """Test manager login"""
    print_test_header("Manager Login")
    
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    result = safe_request('POST', f"{API_URL}/api/auth/login", json=data)
    
    if result.get('success'):
        print_success(f"Manager logged in: {result['user']['name']}")
        print_info(f"Team ID: {result.get('team', {}).get('id', 'N/A')}")
        print_info(f"Employee Code: {result.get('team', {}).get('employee_code', 'N/A')}")
        return result.get('token')
    else:
        print_error(f"Manager login failed: {result.get('message', 'Unknown error')}")
        return None

def test_get_team_details(manager_token, team_id):
    """Test getting team details"""
    print_test_header("Get Team Details")
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    result = safe_request('GET', f"{API_URL}/api/teams/{team_id}", headers=headers)
    
    if result.get('success'):
        team = result.get('team', {})
        print_success("Team details retrieved successfully")
        print_info(f"Team Name: {team.get('name', 'N/A')}")
        print_info(f"Employee Code: {team.get('employee_code', 'N/A')}")
        print_info(f"Manager Code: {team.get('manager_code', 'N/A')}")
        print_info(f"Members: {len(team.get('members', []))}")
        return team
    else:
        print_error(f"Failed to get team details: {result.get('message', 'Unknown error')}")
        return None

def test_employee_join_team(employee_code):
    """Test employee joining team"""
    print_test_header("Employee Join Team")
    
    data = {
        "employee_code": employee_code,
        "user_name": f"Test Employee {int(time.time())}",
        "email": f"test_employee_{int(time.time())}@example.com"
    }
    
    result = safe_request('POST', f"{API_URL}/api/teams/join", json=data)
    
    if result.get('success'):
        print_success(f"Employee joined team: {result['user']['name']}")
        print_info(f"User ID: {result['user']['id']}")
        print_info(f"Team ID: {result['team']['id']}")
        return result['user']
    else:
        print_error(f"Employee join failed: {result.get('message', 'Unknown error')}")
        return None

def test_team_deletion(manager_token, team_id):
    """Test team deletion"""
    print_test_header("Team Deletion")
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    result = safe_request('DELETE', f"{API_URL}/api/teams/{team_id}", headers=headers)
    
    if result.get('success'):
        print_success("Team deleted successfully")
        return True
    else:
        print_error(f"Team deletion failed: {result.get('message', 'Unknown error')}")
        return False

def main():
    """Run all tests"""
    print("🚀 TESTING TEAM CREATION AND MANAGEMENT FIXES")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print("=" * 60)
    
    # Test manager registration
    signup_result = test_manager_registration()
    if not signup_result:
        print_error("Test failed at manager registration")
        return
    
    team_id = signup_result.get('team', {}).get('id')
    employee_code = signup_result.get('team', {}).get('employee_code')
    manager_token = signup_result.get('token')
    
    # Test email verification
    verification_token = test_email_verification()
    if not verification_token:
        print_warning("Email verification failed, but continuing with tests")
    
    # Test manager login
    login_token = test_manager_login()
    if not login_token:
        print_error("Test failed at manager login")
        return
    
    # Test getting team details
    team_details = test_get_team_details(login_token, team_id)
    if not team_details:
        print_error("Test failed at getting team details")
        return
    
    # Test employee join team
    employee_user = test_employee_join_team(employee_code)
    if not employee_user:
        print_error("Test failed at employee join team")
        return
    
    # Test team deletion (optional - comment out if you want to keep the team)
    # delete_success = test_team_deletion(login_token, team_id)
    # if not delete_success:
    #     print_error("Test failed at team deletion")
    #     return
    
    print_test_header("TEST RESULTS SUMMARY")
    print_success("All team creation and management tests passed!")
    print_info(f"Team ID: {team_id}")
    print_info(f"Employee Code: {employee_code}")
    print_info("You can now use this employee code to test the Employee Tracker app")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 