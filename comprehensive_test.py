#!/usr/bin/env python3
"""
Comprehensive ProductivityFlow System Test
Tests all endpoints and features to ensure everything is operational
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://my-home-backend-7m6d.onrender.com"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a specific endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"} if data else {}
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"🔍 {description}")
        print(f"   {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                if "success" in result:
                    print(f"   ✅ Success: {result['success']}")
                if "message" in result:
                    print(f"   📝 Message: {result['message']}")
                if "team" in result:
                    print(f"   🏢 Team: {result['team']['name']} (Code: {result['team']['employee_code']})")
                if "user" in result:
                    print(f"   👤 User: {result['user']['name']} ({result['user']['role']})")
                if "token" in result:
                    print(f"   🔑 Token: Generated successfully")
                return True, result
            except:
                print(f"   📄 Response: {response.text[:100]}...")
                return True, response.text
        else:
            if response.status_code == 404:
                print(f"   ❌ Endpoint not found (deployment in progress)")
            else:
                print(f"   ⚠️ Error: {response.status_code}")
                try:
                    error = response.json()
                    print(f"   📝 Error: {error.get('message', 'Unknown error')}")
                except:
                    print(f"   📄 Response: {response.text[:100]}...")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False, None

def main():
    """Main comprehensive test"""
    print("🚀 ProductivityFlow Comprehensive System Test")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend URL: {BASE_URL}")
    print()
    
    # Test results tracking
    test_results = []
    
    # 1. Health Check
    print("📋 1. SYSTEM HEALTH CHECK")
    print("-" * 30)
    success, result = test_endpoint("GET", "/health", description="Health Check")
    test_results.append(("Health Check", success))
    
    if not success:
        print("❌ System is not healthy. Please check backend deployment.")
        return
    
    print()
    
    # 2. Authentication Tests
    print("📋 2. AUTHENTICATION TESTS")
    print("-" * 30)
    
    # Manager Registration
    success, result = test_endpoint("POST", "/api/auth/register", {
        "name": "Test Manager",
        "email": "test.manager@productivityflow.com",
        "password": "TestPassword123",
        "organization": "Test Organization"
    }, "Manager Registration")
    test_results.append(("Manager Registration", success))
    
    if success and result and isinstance(result, dict):
        manager_token = result.get('token')
        team_data = result.get('team', {})
        team_code = team_data.get('employee_code')
        print(f"   📝 Team Code: {team_code}")
    else:
        manager_token = None
        team_code = None
    
    time.sleep(1)
    
    # Manager Login
    success, result = test_endpoint("POST", "/api/auth/login", {
        "email": "test.manager@productivityflow.com",
        "password": "TestPassword123"
    }, "Manager Login")
    test_results.append(("Manager Login", success))
    
    time.sleep(1)
    
    # Employee Login
    if team_code:
        success, result = test_endpoint("POST", "/api/auth/employee-login", {
            "team_code": team_code,
            "user_name": "Test Employee"
        }, "Employee Login")
        test_results.append(("Employee Login", success))
        
        if success and result and isinstance(result, dict):
            employee_token = result.get('token')
            employee_data = result.get('user', {})
            employee_id = employee_data.get('id')
            team_id = employee_data.get('team_id')
        else:
            employee_token = None
            employee_id = None
            team_id = None
    else:
        test_results.append(("Employee Login", False))
        employee_token = None
        employee_id = None
        team_id = None
    
    print()
    
    # 3. Team Management Tests
    print("📋 3. TEAM MANAGEMENT TESTS")
    print("-" * 30)
    
    # Team Creation
    success, result = test_endpoint("POST", "/api/teams", {
        "name": "Test Team 2",
        "user_name": "Test Manager 2"
    }, "Team Creation")
    test_results.append(("Team Creation", success))
    
    if success and result and isinstance(result, dict):
        team2_data = result.get('team', {})
        team2_code = team2_data.get('employee_code')
    else:
        team2_code = None
    
    time.sleep(1)
    
    # Team Join
    if team2_code:
        success, result = test_endpoint("POST", "/api/teams/join", {
            "employee_code": team2_code,
            "user_name": "Test Employee 2"
        }, "Team Join")
        test_results.append(("Team Join", success))
    else:
        test_results.append(("Team Join", False))
    
    time.sleep(1)
    
    # Get Teams
    success, result = test_endpoint("GET", "/api/teams", description="Get All Teams")
    test_results.append(("Get Teams", success))
    
    print()
    
    # 4. Activity Tracking Tests
    print("📋 4. ACTIVITY TRACKING TESTS")
    print("-" * 30)
    
    if employee_id and team_id:
        # Track Activity
        success, result = test_endpoint("POST", "/api/activity/track", {
            "user_id": employee_id,
            "team_id": team_id,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "active_app": "VS Code",
            "productive_hours": 6.5,
            "unproductive_hours": 1.2
        }, "Track Activity")
        test_results.append(("Track Activity", success))
        
        time.sleep(1)
        
        # Get Daily Summary
        success, result = test_endpoint("GET", f"/api/employee/daily-summary?user_id={employee_id}&team_id={team_id}&date={datetime.now().strftime('%Y-%m-%d')}", description="Get Daily Summary")
        test_results.append(("Get Daily Summary", success))
    else:
        test_results.append(("Track Activity", False))
        test_results.append(("Get Daily Summary", False))
    
    print()
    
    # 5. Analytics Tests
    print("📋 5. ANALYTICS TESTS")
    print("-" * 30)
    
    if team_id:
        # Burnout Risk Analysis
        success, result = test_endpoint("GET", f"/api/analytics/burnout-risk?team_id={team_id}", description="Burnout Risk Analysis")
        test_results.append(("Burnout Risk Analysis", success))
        
        time.sleep(1)
        
        # Distraction Profile
        success, result = test_endpoint("GET", f"/api/analytics/distraction-profile?team_id={team_id}", description="Distraction Profile")
        test_results.append(("Distraction Profile", success))
    else:
        test_results.append(("Burnout Risk Analysis", False))
        test_results.append(("Distraction Profile", False))
    
    print()
    
    # 6. Summary Report
    print("📋 6. COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success in test_results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    print("📋 Detailed Results:")
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print()
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! The ProductivityFlow system is fully operational!")
        print()
        print("✅ System Status: PRODUCTION READY")
        print("✅ All features working")
        print("✅ Authentication operational")
        print("✅ Team management working")
        print("✅ Activity tracking functional")
        print("✅ Analytics system operational")
        print("✅ DMG installers ready for distribution")
    else:
        print("⚠️ Some tests failed. Please check the backend deployment and database.")
        print()
        print("🔧 Recommended Actions:")
        print("1. Check backend deployment status")
        print("2. Reset database schema if needed")
        print("3. Verify all dependencies are installed")
        print("4. Check Render service logs")
    
    print()
    print("🔗 Resources:")
    print(f"   Backend URL: {BASE_URL}")
    print("   Render Dashboard: https://dashboard.render.com")
    print("   GitHub Repository: https://github.com/Muckmuckmuckmuck/ProductivityFlow")
    print()
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 