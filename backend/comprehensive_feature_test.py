#!/usr/bin/env python3
"""
Comprehensive Feature Test Script
Tests all authentication and core features of the ProductivityFlow system
"""

import requests
import json
import time
import random
import string
from datetime import datetime

def generate_random_string(length=8):
    """Generate a random string for unique test data"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def test_manager_authentication():
    """Test manager sign up, sign in, and team creation"""
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print("=== TESTING MANAGER AUTHENTICATION ===")
    
    # Generate unique test data
    test_id = generate_random_string()
    manager_name = f"Test Manager {test_id}"
    manager_email = f"manager{test_id}@test.com"
    manager_password = "TestPassword123!"
    
    # Test 1: Manager Sign Up
    print(f"\n1. Testing manager sign up...")
    signup_data = {
        "name": manager_name,
        "email": manager_email,
        "password": manager_password,
        "organization": f"Test Organization {test_id}"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=signup_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Manager sign up successful!")
            print(f"User ID: {result['user']['id']}")
            print(f"Team ID: {result['team']['id']}")
            # Add team_id to user object for consistency
            result['user']['team_id'] = result['team']['id']
            return result['user'], result['token']
        else:
            print(f"❌ Manager sign up failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Manager sign up error: {e}")
        return None, None

def test_manager_signin(manager_email, manager_password):
    """Test manager sign in"""
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n2. Testing manager sign in...")
    signin_data = {
        "email": manager_email,
        "password": manager_password
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=signin_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Manager sign in successful!")
            print(f"User ID: {result['user']['id']}")
            print(f"Team ID: {result['user']['team_id']}")
            return result['user'], result['token']
        else:
            print(f"❌ Manager sign in failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Manager sign in error: {e}")
        return None, None

def test_team_creation(token):
    """Test team creation by manager"""
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n3. Testing team creation...")
    test_id = generate_random_string()
    team_name = f"Test Team {test_id}"
    
    team_data = {
        "name": team_name,
        "user_name": f"Manager {test_id}"
    }
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        response = requests.post(f"{base_url}/api/teams", json=team_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Team creation successful!")
            print(f"Team ID: {result['team']['id']}")
            print(f"Employee Code: {result['team']['employee_code']}")
            print(f"Manager Code: {result['team']['manager_code']}")
            return result['team']
        else:
            print(f"❌ Team creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Team creation error: {e}")
        return None

def test_employee_authentication(team):
    """Test employee authentication and team joining"""
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n4. Testing employee authentication...")
    test_id = generate_random_string()
    employee_name = f"Test Employee {test_id}"
    
    # Test employee joining team
    join_data = {
        "employee_code": team['employee_code'],
        "user_name": employee_name
    }
    
    try:
        response = requests.post(f"{base_url}/api/teams/join", json=join_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Employee joined team successfully!")
            print(f"User ID: {result['user']['id']}")
            print(f"Team ID: {result['user']['team_id']}")
            return result['user']
        else:
            print(f"❌ Employee join team failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Employee join team error: {e}")
        return None

def test_employee_login(employee_user, team):
    """Test employee login"""
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n5. Testing employee login...")
    login_data = {
        "team_code": team['employee_code'],
        "user_name": employee_user['name']
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/employee-login", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Employee login successful!")
            print(f"User ID: {result['user']['id']}")
            return result['user'], result['token']
        else:
            print(f"❌ Employee login failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Employee login error: {e}")
        return None, None

def test_forgot_password(manager_email):
    """Test forgot password functionality"""
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n6. Testing forgot password...")
    forgot_data = {
        "email": manager_email
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/forgot-password", json=forgot_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Forgot password request successful!")
            print(f"Message: {result.get('message', 'No message')}")
            return result.get('reset_token')
        else:
            print(f"❌ Forgot password failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Forgot password error: {e}")
        return None

def test_reset_password(manager_email, reset_token):
    """Test password reset functionality"""
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n7. Testing password reset...")
    new_password = "NewPassword123!"
    reset_data = {
        "email": manager_email,
        "token": reset_token,
        "new_password": new_password
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/reset-password", json=reset_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Password reset successful!")
            return new_password
        else:
            print(f"❌ Password reset failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Password reset error: {e}")
        return None

def test_tracking_functionality(employee_token, employee_user):
    """Test activity tracking functionality"""
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n8. Testing activity tracking...")
    
    # Test submitting activity data
    activity_data = {
        "user_id": employee_user['id'],
        "team_id": employee_user['team_id'],
        "date": datetime.now().strftime('%Y-%m-%d'),
        "active_app": "VS Code",
        "productive_hours": 2.5,
        "unproductive_hours": 0.5
    }
    
    headers = {"Authorization": f"Bearer {employee_token}"} if employee_token else {}
    
    try:
        response = requests.post(f"{base_url}/api/activity/track", json=activity_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print("✅ Activity tracking submission successful!")
            print(f"Activity ID: {result.get('activity_id', 'N/A')}")
            return True
        else:
            print(f"❌ Activity tracking failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Activity tracking error: {e}")
        return False

def test_analytics_functionality(manager_token, manager_user):
    """Test analytics and reporting functionality"""
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n9. Testing analytics functionality...")
    
    headers = {"Authorization": f"Bearer {manager_token}"} if manager_token else {}
    
    try:
        # Test getting team analytics
        response = requests.get(f"{base_url}/api/analytics/burnout-risk?team_id={manager_user['team_id']}", headers=headers)
        print(f"Analytics Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analytics retrieval successful!")
            return True
        else:
            print(f"❌ Analytics failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return False

def main():
    """Run all comprehensive tests"""
    print("🚀 STARTING COMPREHENSIVE FEATURE TEST")
    print("=" * 50)
    
    test_results = {}
    
    # Test 1: Manager Authentication
    manager_user, manager_token = test_manager_authentication()
    test_results['manager_signup'] = manager_user is not None
    
    if manager_user:
        # Test 2: Manager Sign In
        signed_in_user, signed_in_token = test_manager_signin(manager_user['email'], "TestPassword123!")
        test_results['manager_signin'] = signed_in_user is not None
        
        # Test 3: Team Creation
        team = test_team_creation(signed_in_token)
        test_results['team_creation'] = team is not None
        
        if team:
            # Test 4: Employee Authentication
            employee_user = test_employee_authentication(team)
            test_results['employee_join'] = employee_user is not None
            
            if employee_user:
                # Test 5: Employee Login
                logged_in_employee, employee_token = test_employee_login(employee_user, team)
                test_results['employee_login'] = logged_in_employee is not None
                
                if logged_in_employee:
                    # Test 6: Activity Tracking
                    tracking_success = test_tracking_functionality(employee_token, logged_in_employee)
                    test_results['activity_tracking'] = tracking_success
                
                # Test 7: Analytics
                analytics_success = test_analytics_functionality(signed_in_token, signed_in_user)
                test_results['analytics'] = analytics_success
        
        # Test 8: Forgot Password
        reset_token = test_forgot_password(manager_user['email'])
        test_results['forgot_password'] = reset_token is not None
        
        if reset_token:
            # Test 9: Reset Password
            new_password = test_reset_password(manager_user['email'], reset_token)
            test_results['reset_password'] = new_password is not None
    
    # Print test summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! System is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main() 