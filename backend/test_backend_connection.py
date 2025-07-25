#!/usr/bin/env python3
"""
Test Backend Connection Script
"""

import requests
import json
import sys

# Backend URL
API_URL = "https://my-home-backend-7m6d.onrender.com"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        print(f"✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Status: {data.get('status', 'unknown')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_public_teams():
    """Test public teams endpoint"""
    try:
        response = requests.get(f"{API_URL}/api/teams/public", timeout=10)
        print(f"✅ Public Teams: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            teams = data.get('teams', [])
            print(f"   Found {len(teams)} teams")
            for team in teams:
                print(f"   - {team.get('name')}: {team.get('employee_code')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Public Teams Failed: {e}")
        return False

def test_login(email, password):
    """Test login endpoint"""
    try:
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"✅ Login Test ({email}): {response.status_code}")
        if response.status_code == 200:
            print("   Login successful!")
        else:
            print(f"   Login failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Login Test Failed: {e}")
        return False

def test_employee_login(email, password):
    """Test employee login endpoint"""
    try:
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(
            f"{API_URL}/api/auth/employee-login",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"✅ Employee Login Test ({email}): {response.status_code}")
        if response.status_code == 200:
            print("   Employee login successful!")
        else:
            print(f"   Employee login failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Employee Login Test Failed: {e}")
        return False

def main():
    print("🚀 Testing ProductivityFlow Backend Connection")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health()
    print()
    
    # Test public teams endpoint
    teams_ok = test_public_teams()
    print()
    
    # Test login endpoints
    print("Testing Login Endpoints:")
    print("-" * 30)
    
    test_credentials = [
        ("manager@productivityflow.com", "password123"),
        ("employee@productivityflow.com", "password123"),
        ("test@example.com", "password123")
    ]
    
    login_results = []
    for email, password in test_credentials:
        result = test_login(email, password)
        login_results.append(result)
        print()
    
    # Test employee login
    employee_result = test_employee_login("employee@productivityflow.com", "password123")
    print()
    
    # Summary
    print("=" * 50)
    print("📊 Test Summary:")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Public Teams: {'✅ PASS' if teams_ok else '❌ FAIL'}")
    print(f"   Login Tests: {'✅ PASS' if any(login_results) else '❌ FAIL'}")
    print(f"   Employee Login: {'✅ PASS' if employee_result else '❌ FAIL'}")
    
    if health_ok and teams_ok:
        print("\n✅ Backend is working correctly!")
        return 0
    else:
        print("\n❌ Backend has issues that need to be fixed.")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 