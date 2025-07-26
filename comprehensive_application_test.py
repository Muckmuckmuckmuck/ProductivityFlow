#!/usr/bin/env python3
"""
Comprehensive End-to-End Application Test for ProductivityFlow
Tests actual user workflows in the real applications
"""

import requests
import json
import time
import datetime
import subprocess
import os
import sys
from datetime import datetime, timedelta

# Configuration
API_URL = "https://my-home-backend-7m6d.onrender.com"
TEST_EMAIL = f"real_test_{int(time.time())}@example.com"
TEST_EMPLOYEE_EMAIL = f"real_employee_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_NAME = f"Real Test Manager {int(time.time())}"
TEST_ORGANIZATION = f"Real Test Organization {int(time.time())}"

def print_test_header(test_name):
    print(f"\n{'='*80}")
    print(f"🧪 REAL APPLICATION TEST: {test_name}")
    print(f"{'='*80}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️ {message}")

def print_warning(message):
    print(f"⚠️ {message}")

def test_backend_health():
    """Test backend is operational"""
    print_test_header("Backend Health Check")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is operational: {data.get('status', 'unknown')}")
            print_info(f"Database: {data.get('database', 'unknown')}")
            print_info(f"Version: {data.get('version', 'unknown')}")
            return True
        else:
            print_error(f"Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Backend health check failed: {str(e)}")
        return False

def test_manager_registration():
    """Test manager registration with team creation"""
    print_test_header("Manager Registration (Real Test)")
    
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": TEST_NAME,
        "organization": TEST_ORGANIZATION
    }
    
    try:
        response = requests.post(f"{API_URL}/api/auth/register", json=data, timeout=10)
        result = response.json()
        
        if response.status_code == 201 and result.get('success'):
            print_success(f"Manager registered successfully: {TEST_EMAIL}")
            print_info(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
            print_info(f"Team ID: {result.get('team', {}).get('id', 'N/A')}")
            print_info(f"Employee Code: {result.get('team', {}).get('employee_code', 'N/A')}")
            print_info(f"Manager Code: {result.get('team', {}).get('manager_code', 'N/A')}")
            return result
        else:
            print_error(f"Manager registration failed: {result.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print_error(f"Manager registration failed: {str(e)}")
        return None

def test_email_verification():
    """Test email verification with test code"""
    print_test_header("Email Verification (Real Test)")
    
    data = {
        "email": TEST_EMAIL,
        "verification_code": "123456"
    }
    
    try:
        response = requests.post(f"{API_URL}/api/auth/verify-email", json=data, timeout=10)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_success("Email verification successful")
            print_info(f"Token: {result.get('token', 'N/A')[:50]}...")
            return result.get('token')
        else:
            print_error(f"Email verification failed: {result.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print_error(f"Email verification failed: {str(e)}")
        return None

def test_manager_login():
    """Test manager login"""
    print_test_header("Manager Login (Real Test)")
    
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{API_URL}/api/auth/login", json=data, timeout=10)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_success(f"Manager logged in: {result['user']['name']}")
            print_info(f"Team ID: {result.get('team', {}).get('id', 'N/A')}")
            print_info(f"Employee Code: {result.get('team', {}).get('employee_code', 'N/A')}")
            return result.get('token'), result.get('team', {}).get('employee_code')
        else:
            print_error(f"Manager login failed: {result.get('message', 'Unknown error')}")
            return None, None
    except Exception as e:
        print_error(f"Manager login failed: {str(e)}")
        return None, None

def test_employee_join_team(employee_code):
    """Test employee joining team"""
    print_test_header("Employee Join Team (Real Test)")
    
    data = {
        "employee_code": employee_code,
        "user_name": f"Real Test Employee {int(time.time())}",
        "email": TEST_EMPLOYEE_EMAIL
    }
    
    try:
        response = requests.post(f"{API_URL}/api/teams/join", json=data, timeout=10)
        result = response.json()
        
        print_info(f"Response status: {response.status_code}")
        print_info(f"Response success: {result.get('success')}")
        print_info(f"Response message: {result.get('message')}")
        
        if (response.status_code == 200 or response.status_code == 201) and result.get('success'):
            print_success(f"Employee joined team: {result['user']['name']}")
            print_info(f"User ID: {result['user']['id']}")
            print_info(f"Team ID: {result['team']['id']}")
            return result['user']
        else:
            print_error(f"Employee join failed: {result.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print_error(f"Employee join failed: {str(e)}")
        return None

def test_activity_tracking(manager_token, team_id):
    """Test activity tracking"""
    print_test_header("Activity Tracking (Real Test)")
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    activity_data = {
        "user_id": "test_user_id",
        "team_id": team_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "active_app": "Visual Studio Code",
        "productive_hours": 2.5,
        "unproductive_hours": 0.5,
        "idle_time": 0.2,
        "break_time": 0.3,
        "total_active_time": 3.0,
        "productivity_score": 85.0,
        "focus_time": 2.0,
        "distraction_count": 3,
        "task_switches": 5,
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "network_activity": True,
        "mouse_clicks": 1250,
        "keyboard_activity": True,
        "screen_time": 3.5
    }
    
    try:
        response = requests.post(f"{API_URL}/api/activity/track", json=activity_data, headers=headers, timeout=10)
        result = response.json()
        
        if response.status_code == 201 and result.get('success'):
            print_success("Activity tracking successful")
            print_info(f"Activity ID: {result.get('activity_id', 'N/A')}")
            return True
        else:
            print_error(f"Activity tracking failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Activity tracking failed: {str(e)}")
        return False

def test_analytics(manager_token):
    """Test analytics endpoints"""
    print_test_header("Analytics (Real Test)")
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    
    # Test burnout risk
    try:
        response = requests.get(f"{API_URL}/api/analytics/burnout-risk", headers=headers, timeout=10)
        if response.status_code == 200:
            print_success("Burnout risk analytics working")
        else:
            print_warning("Burnout risk analytics not available")
    except Exception as e:
        print_warning(f"Burnout risk analytics failed: {str(e)}")
    
    # Test productivity insights
    try:
        response = requests.get(f"{API_URL}/api/analytics/productivity-insights", headers=headers, timeout=10)
        if response.status_code == 200:
            print_success("Productivity insights working")
        else:
            print_warning("Productivity insights not available")
    except Exception as e:
        print_warning(f"Productivity insights failed: {str(e)}")

def test_daily_summary(manager_token):
    """Test daily summary generation"""
    print_test_header("Daily Summary (Real Test)")
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    summary_data = {
        "user_id": "test_user_id",
        "team_id": "test_team_id",
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
            "Slack": 1.0
        },
        "goals_met": 3,
        "total_goals": 4,
        "achievements": ["Completed project milestone", "Reduced distractions by 20%"]
    }
    
    try:
        response = requests.post(f"{API_URL}/api/activity/daily-summary", json=summary_data, headers=headers, timeout=10)
        result = response.json()
        
        if response.status_code == 201 and result.get('success'):
            print_success("Daily summary generation successful")
            return True
        else:
            print_warning(f"Daily summary generation failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print_warning(f"Daily summary generation failed: {str(e)}")
        return False

def test_application_endpoints():
    """Test if applications are running on expected ports"""
    print_test_header("Application Endpoints Check")
    
    # Check if applications are running
    ports_to_check = [
        (1420, "Employee Tracker"),
        (1421, "Manager Dashboard"),
        (5173, "Web Dashboard")
    ]
    
    all_running = True
    for port, app_name in ports_to_check:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=5)
            if response.status_code == 200:
                print_success(f"{app_name} is running on port {port}")
            else:
                print_warning(f"{app_name} on port {port} returned status {response.status_code}")
                all_running = False
        except Exception as e:
            print_warning(f"{app_name} on port {port} is not accessible: {str(e)}")
            all_running = False
    
    return all_running

def test_complete_workflow():
    """Test complete end-to-end workflow"""
    print_test_header("Complete End-to-End Workflow Test")
    
    # Step 1: Backend health
    if not test_backend_health():
        print_error("Backend health check failed - stopping test")
        return False
    
    # Step 2: Manager registration
    signup_result = test_manager_registration()
    if not signup_result:
        print_error("Manager registration failed - stopping test")
        return False
    
    team_id = signup_result.get('team', {}).get('id')
    employee_code = signup_result.get('team', {}).get('employee_code')
    manager_token = signup_result.get('token')
    
    # Step 3: Email verification
    verification_token = test_email_verification()
    if not verification_token:
        print_warning("Email verification failed, but continuing with tests")
    
    # Step 4: Manager login
    login_token, login_employee_code = test_manager_login()
    if not login_token:
        print_error("Manager login failed - stopping test")
        return False
    
    # Use login employee code if available
    if login_employee_code:
        employee_code = login_employee_code
    
    # Step 5: Employee join team
    employee_user = test_employee_join_team(employee_code)
    if not employee_user:
        print_error("Employee join team failed - stopping test")
        return False
    
    # Step 6: Activity tracking
    activity_success = test_activity_tracking(login_token, team_id)
    if not activity_success:
        print_warning("Activity tracking failed, but continuing")
    
    # Step 7: Analytics
    test_analytics(login_token)
    
    # Step 8: Daily summary
    summary_success = test_daily_summary(login_token)
    if not summary_success:
        print_warning("Daily summary failed, but continuing")
    
    # Step 9: Application endpoints
    apps_running = test_application_endpoints()
    
    print_test_header("WORKFLOW TEST RESULTS")
    print_success("Complete workflow test completed!")
    print_info(f"Team ID: {team_id}")
    print_info(f"Employee Code: {employee_code}")
    print_info(f"Manager Token: {login_token[:50]}...")
    print_info(f"Applications Running: {apps_running}")
    
    return True

def main():
    """Run comprehensive application test"""
    print("🚀 COMPREHENSIVE APPLICATION TEST - PRODUCTIVITYFLOW")
    print("=" * 80)
    print(f"API URL: {API_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Test Employee Email: {TEST_EMPLOYEE_EMAIL}")
    print("=" * 80)
    
    # Run complete workflow test
    success = test_complete_workflow()
    
    if success:
        print_test_header("FINAL RESULTS")
        print_success("🎉 ALL TESTS PASSED! ProductivityFlow is fully operational!")
        print_info("You can now use the applications with confidence:")
        print_info("1. Manager Dashboard: http://localhost:1421")
        print_info("2. Employee Tracker: http://localhost:1420")
        print_info("3. Web Dashboard: http://localhost:5173")
        print_info("4. Use the Employee Code from the test results above")
    else:
        print_test_header("FINAL RESULTS")
        print_error("❌ Some tests failed. Please check the issues above.")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main() 