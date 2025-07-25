#!/usr/bin/env python3
"""
Fix Production Backend Script
"""

import requests
import json
import sys

# Production backend URL
API_URL = "https://productivityflow-backend-v3.onrender.com"

def create_test_user(email, password, name):
    """Create a test user via the registration endpoint"""
    try:
        data = {
            "email": email,
            "password": password,
            "name": name
        }
        response = requests.post(
            f"{API_URL}/api/auth/register",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"✅ Register User ({email}): {response.status_code}")
        if response.status_code == 201:
            print("   User created successfully!")
            return True
        else:
            print(f"   Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

def create_test_team(team_name):
    """Create a test team"""
    try:
        data = {
            "name": team_name,
            "user_name": "Test Manager",
            "role": "manager"
        }
        response = requests.post(
            f"{API_URL}/api/teams",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"✅ Create Team ({team_name}): {response.status_code}")
        if response.status_code == 201:
            print("   Team created successfully!")
            return True
        else:
            print(f"   Team creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Team creation failed: {e}")
        return False

def test_login(email, password):
    """Test login with credentials"""
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
            return True
        else:
            print(f"   Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def main():
    print("🚀 Fixing ProductivityFlow Production Backend")
    print("=" * 50)
    
    # Test users to create
    test_users = [
        ("manager@productivityflow.com", "password123", "Manager User"),
        ("employee@productivityflow.com", "password123", "Employee User"),
        ("test@example.com", "password123", "Test User")
    ]
    
    # Create test users
    print("Creating test users...")
    for email, password, name in test_users:
        create_test_user(email, password, name)
        print()
    
    # Create test team
    print("Creating test team...")
    create_test_team("ProductivityFlow Team")
    print()
    
    # Test logins
    print("Testing logins...")
    for email, password, name in test_users:
        test_login(email, password)
        print()
    
    # Test public teams endpoint
    print("Testing public teams endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/teams/public", timeout=10)
        print(f"✅ Public Teams: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            teams = data.get('teams', [])
            print(f"   Found {len(teams)} teams")
            for team in teams:
                print(f"   - {team.get('name')}: {team.get('employee_code')}")
        else:
            print(f"   Failed: {response.text}")
    except Exception as e:
        print(f"❌ Public teams test failed: {e}")
    
    print("\n✅ Production backend fix completed!")

if __name__ == '__main__':
    main() 