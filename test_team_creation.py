#!/usr/bin/env python3
"""
Test script to verify team creation functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:3001"
TEST_EMAIL = "teamtest@example.com"
TEST_PASSWORD = "TestPass123"

def test_team_creation():
    print("🧪 Testing Team Creation Functionality")
    print("=" * 50)
    
    # Step 1: Login to get token
    print("1. Logging in...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('token')
            print(f"   ✅ Login successful, got token")
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Step 2: Get current teams
    print("\n2. Getting current teams...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        teams_response = requests.get(f"{BASE_URL}/api/teams", headers=headers)
        print(f"   Get teams status: {teams_response.status_code}")
        
        if teams_response.status_code == 200:
            teams_result = teams_response.json()
            current_teams = teams_result.get('teams', [])
            print(f"   ✅ Found {len(current_teams)} teams")
            for team in current_teams:
                print(f"      - {team['name']} (ID: {team['id']}, Code: {team['code']})")
        else:
            print(f"   ❌ Get teams failed: {teams_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Get teams error: {e}")
        return False
    
    # Step 3: Create new team
    print("\n3. Creating new team...")
    team_data = {
        "name": f"Test Team {len(current_teams) + 1}"
    }
    
    try:
        create_response = requests.post(f"{BASE_URL}/api/teams", json=team_data, headers=headers)
        print(f"   Create team status: {create_response.status_code}")
        
        if create_response.status_code == 201:
            create_result = create_response.json()
            new_team = create_result.get('team')
            print(f"   ✅ Team created successfully!")
            print(f"      - Name: {new_team['name']}")
            print(f"      - ID: {new_team['id']}")
        else:
            print(f"   ❌ Create team failed: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Create team error: {e}")
        return False
    
    # Step 4: Verify team was created
    print("\n4. Verifying team creation...")
    try:
        teams_response = requests.get(f"{BASE_URL}/api/teams", headers=headers)
        
        if teams_response.status_code == 200:
            teams_result = teams_response.json()
            updated_teams = teams_result.get('teams', [])
            print(f"   ✅ Now have {len(updated_teams)} teams")
            
            # Find the new team
            new_team_found = None
            for team in updated_teams:
                if team['name'] == team_data['name']:
                    new_team_found = team
                    break
            
            if new_team_found:
                print(f"   ✅ New team found: {new_team_found['name']} (Code: {new_team_found['code']})")
                
                # Test getting team members
                print(f"\n5. Testing team members...")
                members_response = requests.get(f"{BASE_URL}/api/teams/{new_team_found['id']}/members", headers=headers)
                
                if members_response.status_code == 200:
                    members_result = members_response.json()
                    members = members_result.get('members', [])
                    print(f"   ✅ Team has {len(members)} members")
                    for member in members:
                        print(f"      - {member['name']} ({member['email']})")
                else:
                    print(f"   ❌ Get members failed: {members_response.text}")
                    
            else:
                print(f"   ❌ New team not found in list")
                return False
        else:
            print(f"   ❌ Get teams failed: {teams_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Verification error: {e}")
        return False
    
    print("\n🎉 All tests passed! Team creation is working correctly.")
    return True

if __name__ == "__main__":
    success = test_team_creation()
    if not success:
        print("\n❌ Tests failed. Check the backend and try again.")
        exit(1) 