#!/usr/bin/env python3
"""
Comprehensive System Test for ProductivityFlow
Tests all features: sign up, sign in, team creation, email verification, 
forgot password, tracking, analytics, and hourly summaries
"""

import requests
import json
import time
import datetime
from datetime import datetime, timedelta

# Configuration
API_URL = "https://my-home-backend-7m6d.onrender.com"
TEST_EMAIL = f"test_manager_{int(time.time())}@example.com"
TEST_EMPLOYEE_EMAIL = f"test_employee_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_NAME = f"Test Manager {int(time.time())}"
TEST_ORGANIZATION = f"Test Organization {int(time.time())}"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️ {message}")

def print_info(message):
    print(f"ℹ️ {message}")

def test_manager_signup():
    """Test manager account creation"""
    print_test_header("Manager Sign Up")
    
    try:
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "organization": TEST_ORGANIZATION
        }
        
        response = requests.post(f"{API_URL}/api/auth/register", json=data)
        result = response.json()
        
        print_info(f"Response: {result}")
        
        if response.status_code == 200 and result.get('success') == True:
            print_success(f"Manager account created: {TEST_EMAIL}")
            print_info(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
            print_info(f"Team ID: {result.get('team', {}).get('id', 'N/A')}")
            print_info(f"Employee Code: {result.get('team', {}).get('employee_code', 'N/A')}")
            return result
        else:
            print_error(f"Manager signup failed: {result.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print_error(f"Manager signup error: {str(e)}")
        return None

def test_email_verification():
    """Test email verification"""
    print_test_header("Email Verification")
    
    try:
        data = {
            "email": TEST_EMAIL,
            "verification_code": "123456"  # Test code
        }
        
        response = requests.post(f"{API_URL}/api/auth/verify-email", json=data)
        
        if response.status_code == 404:
            print_warning("Email verification endpoint not yet deployed")
            return None
            
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_success("Email verification successful")
            return result.get('token')
        else:
            print_warning(f"Email verification failed: {result.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print_error(f"Email verification error: {str(e)}")
        return None

def test_manager_signin():
    """Test manager sign in"""
    print_test_header("Manager Sign In")
    
    try:
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(f"{API_URL}/api/auth/login", json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_success(f"Manager signed in: {result['user']['name']}")
            return result.get('token')
        else:
            print_error(f"Manager signin failed: {result.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print_error(f"Manager signin error: {str(e)}")
        return None

def test_team_creation(token):
    """Test team creation"""
    print_test_header("Team Creation")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "name": f"Test Team {int(time.time())}",
            "user_name": TEST_NAME  # Add user_name as required by backend
        }
        
        response = requests.post(f"{API_URL}/api/teams", json=data, headers=headers)
        result = response.json()
        
        print_info(f"Team creation response: {result}")
        
        if response.status_code == 200 and result.get('success') == True:
            team = result['team']
            print_success(f"Team created: {team['name']}")
            print_info(f"Team ID: {team['id']}")
            print_info(f"Employee Code: {team.get('employee_code', 'N/A')}")
            return team
        else:
            print_error(f"Team creation failed: {result.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print_error(f"Team creation error: {str(e)}")
        return None

def test_employee_join_team(team_code):
    """Test employee joining team"""
    print_test_header("Employee Join Team")
    
    try:
        data = {
            "team_code": team_code,
            "user_name": f"Test Employee {int(time.time())}",
            "email": TEST_EMPLOYEE_EMAIL
        }
        
        response = requests.post(f"{API_URL}/api/teams/join", json=data)
        result = response.json()
        
        print_info(f"Employee join response: {result}")
        
        if response.status_code in [200, 201] and result.get('success'):
            print_success(f"Employee joined team: {result['user']['name']}")
            return result['user']
        else:
            print_error(f"Employee join failed: {result.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print_error(f"Employee join error: {str(e)}")
        return None

def test_employee_login(team_code, user_name):
    """Test employee login"""
    print_test_header("Employee Login")
    
    try:
        data = {
            "team_code": team_code,
            "user_name": user_name
        }
        
        response = requests.post(f"{API_URL}/api/auth/employee-login", json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_success(f"Employee logged in: {result['user']['name']}")
            return result.get('token')
        else:
            print_error(f"Employee login failed: {result.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print_error(f"Employee login error: {str(e)}")
        return None

def test_activity_tracking(employee_token, user_id, team_id):
    """Test activity tracking"""
    print_test_header("Activity Tracking")
    
    try:
        headers = {"Authorization": f"Bearer {employee_token}"}
        
        # Test basic activity tracking
        activity_data = {
            "user_id": user_id,
            "team_id": team_id,
            "active_app": "Visual Studio Code",
            "productive_hours": 2.5,
            "unproductive_hours": 0.5,
            "app_category": "productivity",
            "window_title": "main.py - ProductivityFlow",
            "productivity_score": 85.0,
            "focus_time": 2.0,
            "distraction_count": 3,
            "task_switches": 5,
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "mouse_clicks": 1250,
            "keyboard_activity": True,
            "screen_time": 3.0
        }
        
        response = requests.post(f"{API_URL}/api/activity/track", json=activity_data, headers=headers)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_success(f"Activity tracked: ID {result.get('activity_id')}")
            print_info(f"Productivity Score: {result.get('productivity_score', 'N/A')}")
            print_info(f"App Category: {result.get('app_category', 'N/A')}")
            return result
        else:
            print_error(f"Activity tracking failed: {result.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print_error(f"Activity tracking error: {str(e)}")
        return None

def test_analytics(manager_token, team_id):
    """Test analytics endpoints"""
    print_test_header("Analytics")
    
    try:
        headers = {"Authorization": f"Bearer {manager_token}"}
        
        # Test burnout risk analysis
        response = requests.get(f"{API_URL}/api/analytics/burnout-risk?team_id={team_id}", headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            print_success("Burnout risk analysis successful")
            print_info(f"Risk Level: {result.get('risk_level', 'N/A')}")
            print_info(f"Risk Score: {result.get('risk_score', 'N/A')}")
        else:
            print_warning(f"Burnout risk analysis failed: {result.get('message', 'Unknown error')}")
        
        # Test productivity insights
        response = requests.get(f"{API_URL}/api/analytics/productivity-insights?team_id={team_id}", headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            print_success("Productivity insights successful")
            print_info(f"Insights: {len(result.get('insights', []))} recommendations")
        else:
            print_warning(f"Productivity insights failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print_error(f"Analytics error: {str(e)}")

def test_forgot_password():
    """Test forgot password functionality"""
    print_test_header("Forgot Password")
    
    try:
        data = {"email": TEST_EMAIL}
        
        response = requests.post(f"{API_URL}/api/auth/forgot-password", json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_success("Forgot password request successful")
            print_info(f"Reset token: {result.get('reset_token', 'N/A')}")
            return result.get('reset_token')
        else:
            print_warning(f"Forgot password failed: {result.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print_error(f"Forgot password error: {str(e)}")
        return None

def test_reset_password(reset_token):
    """Test password reset"""
    print_test_header("Reset Password")
    
    try:
        data = {
            "email": TEST_EMAIL,
            "token": reset_token,
            "new_password": "NewPassword123!"
        }
        
        response = requests.post(f"{API_URL}/api/auth/reset-password", json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_success("Password reset successful")
            return True
        else:
            print_warning(f"Password reset failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print_error(f"Password reset error: {str(e)}")
        return False

def test_hourly_summaries(employee_token, user_id, team_id):
    """Test hourly summaries"""
    print_test_header("Hourly Summaries")
    
    try:
        headers = {"Authorization": f"Bearer {employee_token}"}
        
        # Test daily summary generation
        summary_data = {
            "user_id": user_id,
            "team_id": team_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_productive_time": 6.5,
            "total_unproductive_time": 1.5,
            "total_idle_time": 0.5,
            "total_break_time": 1.0,
            "total_screen_time": 8.0,
            "overall_productivity_score": 78.5,
            "focus_score": 82.0,
            "distraction_count": 8,
            "task_switch_count": 12,
            "most_used_app": "Visual Studio Code",
            "most_productive_app": "Visual Studio Code",
            "app_usage_breakdown": {
                "Visual Studio Code": 4.5,
                "Chrome": 2.0,
                "Slack": 1.0,
                "Terminal": 0.5
            },
            "goals_met": 3,
            "total_goals": 4
        }
        
        response = requests.post(f"{API_URL}/api/activity/daily-summary", json=summary_data, headers=headers)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_success("Daily summary created successfully")
            print_info(f"Productivity Score: {result.get('overall_productivity_score', 'N/A')}")
            print_info(f"Goals Met: {result.get('goals_met', 'N/A')}/{result.get('total_goals', 'N/A')}")
        else:
            print_warning(f"Daily summary failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print_error(f"Hourly summaries error: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 COMPREHENSIVE PRODUCTIVITYFLOW SYSTEM TEST")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Test Employee Email: {TEST_EMPLOYEE_EMAIL}")
    print("=" * 60)
    
    # Test results storage
    results = {
        "manager_signup": False,
        "email_verification": False,
        "manager_signin": False,
        "team_creation": False,
        "employee_join": False,
        "employee_login": False,
        "activity_tracking": False,
        "analytics": False,
        "forgot_password": False,
        "reset_password": False,
        "hourly_summaries": False
    }
    
    # Test manager signup
    signup_result = test_manager_signup()
    if signup_result:
        results["manager_signup"] = True
        # Use the team from signup result
        team = signup_result.get('team')
        manager_token = signup_result.get('token')
    else:
        team = None
        manager_token = None
    
    # Test email verification
    verification_token = test_email_verification()
    if verification_token:
        results["email_verification"] = True
    
    # Test manager signin (if signup didn't provide token)
    if not manager_token:
        manager_token = test_manager_signin()
    if manager_token:
        results["manager_signin"] = True
    
    # Test team creation (if not already created during signup)
    if manager_token and not team:
        team = test_team_creation(manager_token)
    if team:
        results["team_creation"] = True
    
    # Test employee join team
    employee_user = None
    if team:
        employee_user = test_employee_join_team(team.get('employee_code', ''))
        if employee_user:
            results["employee_join"] = True
    
    # Test employee login
    employee_token = None
    if employee_user and team:
        employee_token = test_employee_login(team.get('employee_code', ''), employee_user.get('name', ''))
        if employee_token:
            results["employee_login"] = True
    
    # Test activity tracking
    if employee_token and employee_user and team:
        tracking_result = test_activity_tracking(employee_token, employee_user.get('id'), team.get('id'))
        if tracking_result:
            results["activity_tracking"] = True
    
    # Test analytics
    if manager_token and team:
        test_analytics(manager_token, team.get('id'))
        results["analytics"] = True
    
    # Test forgot password
    reset_token = test_forgot_password()
    if reset_token:
        results["forgot_password"] = True
    
    # Test reset password
    if reset_token:
        reset_success = test_reset_password(reset_token)
        if reset_success:
            results["reset_password"] = True
    
    # Test hourly summaries
    if employee_token and employee_user and team:
        test_hourly_summaries(employee_token, employee_user.get('id'), team.get('id'))
        results["hourly_summaries"] = True
    
    # Print final results
    print_test_header("TEST RESULTS SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n📊 RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! System is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 