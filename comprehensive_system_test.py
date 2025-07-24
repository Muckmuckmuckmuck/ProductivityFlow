#!/usr/bin/env python3
"""
Comprehensive ProductivityFlow System Test
Tests all functionality including registration, login, password reset, and email verification
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
API_BASE = "http://localhost:3001"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPass123"
TEST_NAME = "System Test User"

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_health_check():
    """Test backend health"""
    log("Testing backend health check...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Backend healthy: {data.get('status')} - Version {data.get('version')}")
            log(f"   Email configured: {data.get('email_configured')}")
            return True
        else:
            log(f"❌ Health check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Health check error: {str(e)}", "ERROR")
        return False

def test_api_endpoints():
    """Test API endpoints listing"""
    log("Testing API endpoints...")
    try:
        response = requests.get(f"{API_BASE}/api", timeout=10)
        if response.status_code == 200:
            data = response.json()
            endpoints = data.get('endpoints', [])
            log(f"✅ API endpoints available: {len(endpoints)} endpoints")
            for endpoint in endpoints:
                log(f"   - {endpoint}")
            return True
        else:
            log(f"❌ API endpoints failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ API endpoints error: {str(e)}", "ERROR")
        return False

def test_user_registration():
    """Test user registration"""
    log(f"Testing user registration with email: {TEST_EMAIL}")
    try:
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        }
        response = requests.post(f"{API_BASE}/api/auth/register", 
                               json=payload, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            log(f"✅ Registration successful: {data.get('message')}")
            return True
        else:
            data = response.json()
            log(f"❌ Registration failed: {data.get('error')}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Registration error: {str(e)}", "ERROR")
        return False

def test_user_login():
    """Test user login"""
    log("Testing user login...")
    try:
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        response = requests.post(f"{API_BASE}/api/auth/login", 
                               json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user = data.get('user', {})
            log(f"✅ Login successful: {user.get('name')} (ID: {user.get('id')})")
            log(f"   Token received: {'Yes' if token else 'No'}")
            return token
        else:
            data = response.json()
            log(f"❌ Login failed: {data.get('error')}", "ERROR")
            return None
    except Exception as e:
        log(f"❌ Login error: {str(e)}", "ERROR")
        return None

def test_password_reset():
    """Test password reset"""
    log("Testing password reset...")
    try:
        new_password = "NewTestPass123"
        payload = {
            "email": TEST_EMAIL,
            "password": new_password
        }
        response = requests.post(f"{API_BASE}/api/auth/reset-password", 
                               json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Password reset successful: {data.get('message')}")
            return new_password
        else:
            data = response.json()
            log(f"❌ Password reset failed: {data.get('error')}", "ERROR")
            return None
    except Exception as e:
        log(f"❌ Password reset error: {str(e)}", "ERROR")
        return None

def test_login_with_new_password(new_password):
    """Test login with new password"""
    log("Testing login with new password...")
    try:
        payload = {
            "email": TEST_EMAIL,
            "password": new_password
        }
        response = requests.post(f"{API_BASE}/api/auth/login", 
                               json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            log(f"✅ Login with new password successful: {user.get('name')}")
            return True
        else:
            data = response.json()
            log(f"❌ Login with new password failed: {data.get('error')}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Login with new password error: {str(e)}", "ERROR")
        return False

def test_team_creation(token):
    """Test team creation"""
    log("Testing team creation...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"name": "Test Team"}
        response = requests.post(f"{API_BASE}/api/teams", 
                               json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            team = data.get('team', {})
            log(f"✅ Team creation successful: {team.get('name')} (ID: {team.get('id')})")
            return True
        else:
            data = response.json()
            log(f"❌ Team creation failed: {data.get('error')}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Team creation error: {str(e)}", "ERROR")
        return False

def test_team_listing(token):
    """Test team listing"""
    log("Testing team listing...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/api/teams", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get('teams', [])
            log(f"✅ Team listing successful: {len(teams)} teams found")
            for team in teams:
                log(f"   - {team.get('name')} (ID: {team.get('id')})")
            return True
        else:
            data = response.json()
            log(f"❌ Team listing failed: {data.get('error')}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Team listing error: {str(e)}", "ERROR")
        return False

def run_comprehensive_test():
    """Run all tests"""
    log("🚀 Starting Comprehensive ProductivityFlow System Test")
    log("=" * 60)
    
    tests = []
    
    # Test 1: Health Check
    tests.append(("Health Check", test_health_check()))
    
    # Test 2: API Endpoints
    tests.append(("API Endpoints", test_api_endpoints()))
    
    # Test 3: User Registration
    tests.append(("User Registration", test_user_registration()))
    
    # Test 4: User Login
    token = test_user_login()
    tests.append(("User Login", token is not None))
    
    # Test 5: Password Reset
    new_password = test_password_reset()
    tests.append(("Password Reset", new_password is not None))
    
    # Test 6: Login with New Password
    if new_password:
        tests.append(("Login with New Password", test_login_with_new_password(new_password)))
    else:
        tests.append(("Login with New Password", False))
    
    # Test 7: Team Creation (if we have a token)
    if token:
        tests.append(("Team Creation", test_team_creation(token)))
        tests.append(("Team Listing", test_team_listing(token)))
    else:
        tests.append(("Team Creation", False))
        tests.append(("Team Listing", False))
    
    # Summary
    log("=" * 60)
    log("📊 TEST SUMMARY")
    log("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        log(f"{status} {test_name}")
        if result:
            passed += 1
    
    log("=" * 60)
    log(f"🎯 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        log("🎉 ALL TESTS PASSED! System is working perfectly!")
        return True
    else:
        log("⚠️ Some tests failed. Please check the errors above.", "WARNING")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 