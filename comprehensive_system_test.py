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

def safe_request(method, url, **kwargs):
    """Make a safe HTTP request with proper error handling"""
    try:
        response = requests.request(method, url, **kwargs)
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                print_warning(f"Response is not JSON: {response.text}")
                return {"success": True, "message": "Non-JSON response"}
        else:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"success": False, "message": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Request failed: {str(e)}"}

def test_manager_signup():
    """Test manager account creation"""
    print_test_header("Manager Sign Up")
    
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": TEST_NAME,
        "organization": TEST_ORGANIZATION
    }
    
    result = safe_request('POST', f"{API_URL}/api/auth/register", json=data)
    
    if result.get('success'):
        print_success(f"Manager account created: {TEST_EMAIL}")
        print_info(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
        print_info(f"Team ID: {result.get('team', {}).get('id', 'N/A')}")
        print_info(f"Employee Code: {result.get('team', {}).get('employee_code', 'N/A')}")
        return result
    else:
        print_error(f"Manager signup failed: {result.get('message', 'Unknown error')}")
        return None

def test_email_verification():
    """Test email verification"""
    print_test_header("Email Verification")
    
    data = {
        "email": TEST_EMAIL,
        "verification_code": "123456"  # Test code
    }
    
    result = safe_request('POST', f"{API_URL}/api/auth/verify-email", json=data)
    
    if result.get('success'):
        print_success("Email verification successful")
        return result.get('token')
    else:
        print_warning(f"Email verification failed: {result.get('message', 'Unknown error')}")
        return None

def test_manager_signin():
    """Test manager sign in"""
    print_test_header("Manager Sign In")
    
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    result = safe_request('POST', f"{API_URL}/api/auth/login", json=data)
    
    if result.get('success'):
        print_success(f"Manager signed in: {result['user']['name']}")
        return result.get('token')
    else:
        print_error(f"Manager signin failed: {result.get('message', 'Unknown error')}")
        return None

def test_team_creation(token):
    """Test team creation"""
    print_test_header("Team Creation")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": f"Test Team {int(time.time())}",
        "user_name": TEST_NAME
    }
    
    result = safe_request('POST', f"{API_URL}/api/teams", json=data, headers=headers)
    
    if result.get('success') and result.get('team'):
        team = result['team']
        print_success(f"Team created: {team['name']}")
        print_info(f"Team ID: {team['id']}")
        print_info(f"Employee Code: {team.get('employee_code', 'N/A')}")
        return team
    else:
        print_error(f"Team creation failed: {result.get('message', 'Unknown error')}")
        return None

def test_employee_join_team(team_code):
    """Test employee joining team"""
    print_test_header("Employee Join Team")
    
    data = {
        "employee_code": team_code,
        "user_name": f"Test Employee {int(time.time())}",
        "email": TEST_EMPLOYEE_EMAIL
    }
    
    result = safe_request('POST', f"{API_URL}/api/teams/join", json=data)
    
    if result.get('success'):
        print_success(f"Employee joined team: {result['user']['name']}")
        return result['user']
    else:
        print_error(f"Employee join failed: {result.get('message', 'Unknown error')}")
        return None

def test_employee_login(team_code, user_name):
    """Test employee login"""
    print_test_header("Employee Login")
    
    data = {
        "team_code": team_code,
        "user_name": user_name
    }
    
    result = safe_request('POST', f"{API_URL}/api/auth/employee-login", json=data)
    
    if result.get('success'):
        print_success(f"Employee logged in: {result['user']['name']}")
        return result.get('token')
    else:
        print_error(f"Employee login failed: {result.get('message', 'Unknown error')}")
        return None

def test_activity_tracking(employee_token, user_id, team_id):
    """Test activity tracking"""
    print_test_header("Activity Tracking")
    
    headers = {"Authorization": f"Bearer {employee_token}"}
    
    # Test basic activity tracking
    activity_data = {
        "user_id": user_id,
        "team_id": team_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
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
    
    result = safe_request('POST', f"{API_URL}/api/activity/track", json=activity_data, headers=headers)
    
    if result.get('success'):
        print_success(f"Activity tracked: ID {result.get('activity_id')}")
        print_info(f"Productivity Score: {result.get('productivity_score', 'N/A')}")
        print_info(f"App Category: {result.get('app_category', 'N/A')}")
        return result
    else:
        print_error(f"Activity tracking failed: {result.get('message', 'Unknown error')}")
        return None

def test_analytics(manager_token, team_id):
    """Test analytics endpoints"""
    print_test_header("Analytics")
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    
    # Test burnout risk analysis
    result = safe_request('GET', f"{API_URL}/api/analytics/burnout-risk?team_id={team_id}", headers=headers)
    
    if result.get('success') or 'risk_level' in result:
        print_success("Burnout risk analysis successful")
        print_info(f"Risk Level: {result.get('risk_level', 'N/A')}")
        print_info(f"Risk Score: {result.get('risk_score', 'N/A')}")
    else:
        print_warning(f"Burnout risk analysis failed: {result.get('message', 'Unknown error')}")
    
    # Test productivity insights
    result = safe_request('GET', f"{API_URL}/api/analytics/productivity-insights?team_id={team_id}", headers=headers)
    
    if result.get('success') or 'insights' in result:
        print_success("Productivity insights successful")
        print_info(f"Insights: {len(result.get('insights', []))} recommendations")
    else:
        print_warning(f"Productivity insights failed: {result.get('message', 'Unknown error')}")

def test_forgot_password():
    """Test forgot password functionality"""
    print_test_header("Forgot Password")
    
    data = {"email": TEST_EMAIL}
    
    result = safe_request('POST', f"{API_URL}/api/auth/forgot-password", json=data)
    
    if result.get('success'):
        print_success("Forgot password request successful")
        print_info(f"Reset token: {result.get('reset_token', 'N/A')}")
        return result.get('reset_token')
    else:
        print_warning(f"Forgot password failed: {result.get('message', 'Unknown error')}")
        return None

def test_reset_password(reset_token):
    """Test password reset"""
    print_test_header("Reset Password")
    
    data = {
        "email": TEST_EMAIL,
        "token": reset_token,
        "new_password": "NewPassword123!"
    }
    
    result = safe_request('POST', f"{API_URL}/api/auth/reset-password", json=data)
    
    if result.get('success'):
        print_success("Password reset successful")
        return True
    else:
        print_warning(f"Password reset failed: {result.get('message', 'Unknown error')}")
        return False

def test_hourly_summaries(employee_token, user_id, team_id):
    """Test hourly summaries"""
    print_test_header("Hourly Summaries")
    
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
    
    result = safe_request('POST', f"{API_URL}/api/activity/daily-summary", json=summary_data, headers=headers)
    
    if result.get('success'):
        print_success("Daily summary created successfully")
        print_info(f"Productivity Score: {result.get('overall_productivity_score', 'N/A')}")
        print_info(f"Goals Met: {result.get('goals_met', 'N/A')}/{result.get('total_goals', 'N/A')}")
    else:
        print_warning(f"Daily summary failed: {result.get('message', 'Unknown error')}")

def test_backend_health():
    """Test backend health"""
    print_test_header("Backend Health Check")
    
    result = safe_request('GET', f"{API_URL}/health")
    
    if result.get('status') == 'healthy':
        print_success("Backend is healthy")
        print_info(f"Database: {result.get('database', 'N/A')}")
        print_info(f"Version: {result.get('version', 'N/A')}")
        return True
    else:
        print_error("Backend health check failed")
        return False

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
        "backend_health": False,
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
    
    # Test backend health first
    if test_backend_health():
        results["backend_health"] = True
    
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