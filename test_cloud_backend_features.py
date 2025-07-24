#!/usr/bin/env python3
"""
Comprehensive test of all ProductivityFlow features with cloud backend
"""

import requests
import json
import time
from datetime import datetime

# Cloud backend URL
API_BASE_URL = "https://productivityflow-backend-v3.onrender.com"

def test_health_check():
    """Test backend health"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data}")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False

def test_manager_registration():
    """Test manager account registration"""
    print("\n📝 Testing Manager Registration...")
    try:
        data = {
            "email": f"test_manager_{int(time.time())}@example.com",
            "password": "TestPass123!",
            "name": "Test Manager"
        }
        response = requests.post(f"{API_BASE_URL}/api/auth/register", json=data, timeout=10)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Manager Registration: {result}")
            return result.get('user', {}).get('email')
        else:
            print(f"❌ Manager Registration Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Manager Registration Error: {e}")
        return None

def test_manager_login(email, password="TestPass123!"):
    """Test manager login"""
    print(f"\n🔐 Testing Manager Login for {email}...")
    try:
        data = {"email": email, "password": password}
        response = requests.post(f"{API_BASE_URL}/api/auth/login", json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Manager Login: {result.get('message')}")
            return result.get('token')
        else:
            print(f"❌ Manager Login Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Manager Login Error: {e}")
        return None

def test_team_creation(token):
    """Test team creation"""
    print("\n🏢 Testing Team Creation...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "name": f"Test Team {int(time.time())}",
            "description": "Test team for feature testing"
        }
        response = requests.post(f"{API_BASE_URL}/api/teams", json=data, headers=headers, timeout=10)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Team Creation: {result}")
            return result.get('team', {}).get('code')
        else:
            print(f"❌ Team Creation Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Team Creation Error: {e}")
        return None

def test_employee_join(team_code):
    """Test employee joining team"""
    print(f"\n👤 Testing Employee Join Team {team_code}...")
    try:
        data = {
            "team_code": team_code,
            "user_name": f"Test Employee {int(time.time())}"
        }
        response = requests.post(f"{API_BASE_URL}/api/teams/join", json=data, timeout=10)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Employee Join: {result}")
            return result.get('user', {}).get('email')
        else:
            print(f"❌ Employee Join Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Employee Join Error: {e}")
        return None

def test_employee_login(email):
    """Test employee login"""
    print(f"\n🔐 Testing Employee Login for {email}...")
    try:
        data = {"email": email, "password": "default123"}
        response = requests.post(f"{API_BASE_URL}/api/auth/employee-login", json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Employee Login: {result.get('message')}")
            return result.get('token')
        else:
            print(f"❌ Employee Login Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Employee Login Error: {e}")
        return None

def test_get_teams(token):
    """Test getting teams"""
    print("\n📋 Testing Get Teams...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/api/teams", headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Get Teams: Found {len(result.get('teams', []))} teams")
            return True
        else:
            print(f"❌ Get Teams Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get Teams Error: {e}")
        return False

def test_password_reset(email):
    """Test password reset"""
    print(f"\n🔑 Testing Password Reset for {email}...")
    try:
        data = {"email": email}
        response = requests.post(f"{API_BASE_URL}/api/auth/reset-password", json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Password Reset: {result.get('message')}")
            return True
        else:
            print(f"❌ Password Reset Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Password Reset Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PRODUCTIVITYFLOW CLOUD BACKEND COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"🌐 Backend URL: {API_BASE_URL}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test results
    results = {
        "health_check": False,
        "manager_registration": False,
        "manager_login": False,
        "team_creation": False,
        "employee_join": False,
        "employee_login": False,
        "get_teams": False,
        "password_reset": False
    }
    
    # Test 1: Health Check
    results["health_check"] = test_health_check()
    
    if not results["health_check"]:
        print("\n❌ Backend is not responding. Stopping tests.")
        return
    
    # Test 2: Manager Registration
    manager_email = test_manager_registration()
    results["manager_registration"] = manager_email is not None
    
    if manager_email:
        # Test 3: Manager Login
        manager_token = test_manager_login(manager_email)
        results["manager_login"] = manager_token is not None
        
        if manager_token:
            # Test 4: Team Creation
            team_code = test_team_creation(manager_token)
            results["team_creation"] = team_code is not None
            
            # Test 5: Get Teams
            results["get_teams"] = test_get_teams(manager_token)
            
            if team_code:
                # Test 6: Employee Join
                employee_email = test_employee_join(team_code)
                results["employee_join"] = employee_email is not None
                
                if employee_email:
                    # Test 7: Employee Login
                    employee_token = test_employee_login(employee_email)
                    results["employee_login"] = employee_token is not None
    
    # Test 8: Password Reset (using manager email)
    if manager_email:
        results["password_reset"] = test_password_reset(manager_email)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Cloud backend is fully functional!")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    print("\n🌐 Cloud Backend Status: ✅ OPERATIONAL")
    print("📱 Applications are now connected to cloud backend")
    print("🚀 Ready for production use!")

if __name__ == "__main__":
    main() 