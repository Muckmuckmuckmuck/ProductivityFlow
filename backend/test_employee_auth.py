#!/usr/bin/env python3
"""
Employee Authentication Test Script
Tests employee sign-in and account creation functionality
"""

import requests
import json
import time

def test_employee_auth():
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print("=== TESTING EMPLOYEE AUTHENTICATION ===")
    
    # Test 1: Get available teams for employee to join
    print("\n1. Testing get teams for employee to join...")
    try:
        response = requests.get(f"{base_url}/api/teams")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            teams = result['teams']
            print(f"✅ Found {len(teams)} teams available")
            
            if teams:
                # Use the first team for testing
                test_team = teams[0]
                print(f"Using team: {test_team['name']}")
                print(f"Employee Code: {test_team['employee_code']}")
                return test_team
            else:
                print("❌ No teams available for testing")
                return None
        else:
            print(f"❌ Failed to get teams: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting teams: {e}")
        return None
    
    return None

def test_employee_join_team(team):
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n2. Testing employee join team...")
    print(f"Team: {team['name']}")
    print(f"Employee Code: {team['employee_code']}")
    
    join_data = {
        "employee_code": team['employee_code'],
        "user_name": f"Test Employee User {int(time.time())}"
    }
    
    try:
        response = requests.post(f"{base_url}/api/teams/join", json=join_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201 or response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Successfully joined team!")
                print(f"User ID: {result['user']['id']}")
                print(f"User Name: {result['user']['name']}")
                print(f"Team ID: {result['user']['team_id']}")
                print(f"Role: {result['user']['role']}")
                return result['user']
            else:
                print(f"❌ Failed to join team: {response.text}")
                return None
        else:
            print(f"❌ Failed to join team: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error joining team: {e}")
        return None

def test_employee_login(user, team_code):
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n3. Testing employee login...")
    print(f"User: {user['name']}")
    print(f"Team Code: {team_code}")
    
    # Try to login with team code and user name
    login_data = {
        "team_code": team_code,
        "user_name": user['name']
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/employee-login", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Employee login successful!")
            print(f"User ID: {result['user']['id']}")
            print(f"User Name: {result['user']['name']}")
            print(f"Team ID: {result['user']['team_id']}")
            print(f"Role: {result['user']['role']}")
            print(f"Token: {result['token'][:50]}...")
            return result
        else:
            print(f"❌ Employee login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in employee login: {e}")
        return None

def test_employee_account_creation():
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n4. Testing employee account creation with new team...")
    
    # First create a new team
    team_data = {
        "name": "Employee Test Team",
        "user_name": "Test Manager"
    }
    
    try:
        response = requests.post(f"{base_url}/api/teams", json=team_data)
        print(f"Team Creation Status Code: {response.status_code}")
        
        if response.status_code == 201:
            team_result = response.json()
            new_team = team_result['team']
            print(f"✅ Created new team: {new_team['name']}")
            print(f"Employee Code: {new_team['employee_code']}")
            
            # Now join the team as an employee
            join_data = {
                "employee_code": new_team['employee_code'],
                "user_name": f"New Employee Account {int(time.time())}"
            }
            
            response = requests.post(f"{base_url}/api/teams/join", json=join_data)
            print(f"Join Team Status Code: {response.status_code}")
            
            if response.status_code == 201:
                user_result = response.json()
                new_user = user_result['user']
                print(f"✅ Created new employee account!")
                print(f"User ID: {new_user['id']}")
                print(f"User Name: {new_user['name']}")
                print(f"Team ID: {new_user['team_id']}")
                print(f"Role: {new_user['role']}")
                
                # Test login with the new account
                login_data = {
                    "team_code": new_team['employee_code'],
                    "user_name": new_user['name']
                }
                
                response = requests.post(f"{base_url}/api/auth/employee-login", json=login_data)
                print(f"New Account Login Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    login_result = response.json()
                    print("✅ New employee account login successful!")
                    print(f"Token: {login_result['token'][:50]}...")
                    return True
                else:
                    print(f"❌ New account login failed: {response.text}")
                    return False
            else:
                print(f"❌ Failed to join new team: {response.text}")
                return False
        else:
            print(f"❌ Failed to create new team: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in account creation test: {e}")
        return False

def test_employee_login_with_invalid_credentials():
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print(f"\n5. Testing employee login with invalid credentials...")
    
    invalid_login_data = {
        "team_code": "INVALID",
        "user_name": "nonexistent"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/employee-login", json=invalid_login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid credentials")
            return True
        else:
            print(f"❌ Unexpected response for invalid credentials: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing invalid credentials: {e}")
        return False

def main():
    print("🚀 Starting Employee Authentication Tests")
    
    # Test 1: Get teams
    team = test_employee_auth()
    if not team:
        print("❌ Cannot proceed without available teams")
        return
    
    # Test 2: Join team
    user = test_employee_join_team(team)
    if not user:
        print("❌ Cannot proceed without joining team")
        return
    
    # Test 3: Login with joined account
    login_result = test_employee_login(user, team['employee_code'])
    if not login_result:
        print("❌ Employee login failed")
        return
    
    # Test 4: Create new employee account
    account_creation = test_employee_account_creation()
    
    # Test 5: Test invalid credentials
    invalid_test = test_employee_login_with_invalid_credentials()
    
    # Summary
    print(f"\n=== TEST SUMMARY ===")
    print(f"✅ Team retrieval: {'PASS' if team else 'FAIL'}")
    print(f"✅ Team joining: {'PASS' if user else 'FAIL'}")
    print(f"✅ Employee login: {'PASS' if login_result else 'FAIL'}")
    print(f"✅ Account creation: {'PASS' if account_creation else 'FAIL'}")
    print(f"✅ Invalid credentials: {'PASS' if invalid_test else 'FAIL'}")
    
    if all([team, user, login_result, account_creation, invalid_test]):
        print(f"\n🎉 ALL EMPLOYEE AUTHENTICATION TESTS PASSED!")
    else:
        print(f"\n❌ SOME TESTS FAILED - Review the output above")

if __name__ == "__main__":
    main() 