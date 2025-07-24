#!/usr/bin/env python3
"""
Comprehensive Integration Test for ProductivityFlow
Tests all major functionality including AI analytics
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "integration_test@example.com"
TEST_PASSWORD = "testpassword123"
TEST_NAME = "Integration Test User"

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_comprehensive_integration():
    """Run comprehensive integration test"""
    
    print("🚀 PRODUCTIVITYFLOW COMPREHENSIVE INTEGRATION TEST")
    print("=" * 60)
    
    # Step 1: Health Check
    print_step(1, "Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print_success(f"Backend is healthy: {health_data.get('status')}")
            print_info(f"Database: {health_data.get('database')}")
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False
    
    # Step 2: Register User
    print_step(2, "User Registration")
    try:
        register_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 201:
            print_success("User registered successfully")
        elif response.status_code == 409 and "already exists" in response.text:
            print_success("User already exists (expected)")
        else:
            print_error(f"Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Registration error: {e}")
        return False
    
    # Step 3: Login
    print_step(3, "User Login")
    try:
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get('token')
            user_id = login_result.get('manager', {}).get('id')
            print_success("Login successful")
            print_info(f"User ID: {user_id}")
            print_info(f"Token: {token[:50]}...")
        else:
            print_error(f"Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Login error: {e}")
        return False
    
    # Step 4: Create Team
    print_step(4, "Team Creation")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        team_data = {
            "name": "Integration Test Team",
            "user_name": TEST_NAME
        }
        
        response = requests.post(f"{BASE_URL}/api/teams", json=team_data, headers=headers)
        if response.status_code == 201:
            team_result = response.json()
            team_id = team_result.get('team', {}).get('id')
            new_token = team_result.get('token')
            print_success("Team created successfully")
            print_info(f"Team ID: {team_id}")
            print_info(f"New Token: {new_token[:50]}...")
            
            # Use the new token for subsequent requests
            token = new_token
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print_error(f"Team creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Team creation error: {e}")
        return False
    
    # Step 5: Add Activity Data
    print_step(5, "Activity Data Submission")
    try:
        activity_data = {
            "activeApp": "VS Code",
            "windowTitle": "integration_test.py - ProductivityFlow",
            "idleTime": 0.25,
            "productiveHours": 2.5,
            "unproductiveHours": 0.5,
            "goalsCompleted": 3
        }
        
        response = requests.post(f"{BASE_URL}/api/teams/{team_id}/activity", 
                               json=activity_data, headers=headers)
        if response.status_code in [200, 201]:
            print_success("Activity data submitted successfully")
        else:
            print_error(f"Activity submission failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Activity submission error: {e}")
        return False
    
    # Step 6: Test Daily Summary
    print_step(6, "Daily Summary Generation")
    try:
        response = requests.get(f"{BASE_URL}/api/employee/daily-summary", headers=headers)
        if response.status_code == 200:
            summary_result = response.json()
            print_success("Daily summary generated successfully")
            print_info(f"Summary: {summary_result.get('summary', 'N/A')[:100]}...")
        else:
            print_error(f"Daily summary failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Daily summary error: {e}")
        return False
    
    # Step 7: Test Burnout Risk Analysis
    print_step(7, "Burnout Risk Analysis")
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/burnout-risk", headers=headers)
        if response.status_code == 200:
            burnout_result = response.json()
            print_success("Burnout risk analysis successful")
            print_info(f"Analysis date: {burnout_result.get('analysis_date')}")
            print_info(f"Team ID: {burnout_result.get('team_id')}")
            print_info(f"Burnout data entries: {len(burnout_result.get('burnout_analysis', []))}")
        else:
            print_error(f"Burnout analysis failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Burnout analysis error: {e}")
        return False
    
    # Step 8: Test Distraction Profile Analysis
    print_step(8, "Distraction Profile Analysis")
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/distraction-profile", headers=headers)
        if response.status_code == 200:
            distraction_result = response.json()
            print_success("Distraction profile analysis successful")
            print_info(f"Analysis date: {distraction_result.get('analysis_date')}")
            print_info(f"Team size: {distraction_result.get('team_size')}")
            print_info(f"Distraction categories: {len(distraction_result.get('distraction_profile', []))}")
            print_info(f"Insights: {len(distraction_result.get('insights', []))}")
        else:
            print_error(f"Distraction analysis failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Distraction analysis error: {e}")
        return False
    
    # Step 9: Test Team Analytics
    print_step(9, "Team Analytics")
    try:
        response = requests.get(f"{BASE_URL}/api/teams/{team_id}/analytics", headers=headers)
        if response.status_code == 200:
            analytics_result = response.json()
            print_success("Team analytics successful")
            print_info(f"Team members: {len(analytics_result.get('members', []))}")
            print_info(f"Total productive hours: {analytics_result.get('total_productive_hours', 0)}")
        else:
            print_error(f"Team analytics failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Team analytics error: {e}")
        return False
    
    # Step 10: Test Team Members
    print_step(10, "Team Members Listing")
    try:
        response = requests.get(f"{BASE_URL}/api/teams/{team_id}/members", headers=headers)
        if response.status_code == 200:
            members_result = response.json()
            print_success("Team members listing successful")
            print_info(f"Members count: {len(members_result.get('members', []))}")
        else:
            print_error(f"Team members failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Team members error: {e}")
        return False
    
    # Final Results
    print("\n" + "="*60)
    print("🎉 COMPREHENSIVE INTEGRATION TEST COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n✅ All major features are working correctly:")
    print("   • User registration and authentication")
    print("   • Team creation and management")
    print("   • Activity tracking and submission")
    print("   • Daily summary generation with AI insights")
    print("   • AI-powered burnout risk analysis")
    print("   • AI-powered distraction profile analysis")
    print("   • Team analytics and member management")
    print("\n🚀 ProductivityFlow is ready for production use!")
    
    return True

if __name__ == "__main__":
    success = test_comprehensive_integration()
    sys.exit(0 if success else 1) 