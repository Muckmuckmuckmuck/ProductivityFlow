#!/usr/bin/env python3
"""
Test Team Creation Script
Tests the team creation functionality to ensure it's working properly
"""

import requests
import json

def test_team_creation():
    base_url = "https://my-home-backend-7m6d.onrender.com"
    
    print("=== TESTING TEAM CREATION ===")
    
    # Test 1: Create a new team
    print("\n1. Testing team creation...")
    team_data = {
        "name": "Test Team Creation",
        "user_name": "Test User"
    }
    
    try:
        response = requests.post(f"{base_url}/api/teams", json=team_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Team created successfully!")
            print(f"Team ID: {result['team']['id']}")
            print(f"Team Name: {result['team']['name']}")
            print(f"Employee Code: {result['team']['employee_code']}")
            print(f"Manager Code: {result['team']['manager_code']}")
        else:
            print(f"❌ Team creation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating team: {e}")
    
    # Test 2: Get all teams
    print("\n2. Testing get teams...")
    try:
        response = requests.get(f"{base_url}/api/teams")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {len(result['teams'])} teams")
            for team in result['teams'][:3]:  # Show first 3 teams
                print(f"  - {team['name']} (Employee Code: {team['employee_code']})")
        else:
            print(f"❌ Get teams failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting teams: {e}")
    
    # Test 3: Join team with employee code
    print("\n3. Testing team join...")
    try:
        # First get a team to join
        response = requests.get(f"{base_url}/api/teams")
        if response.status_code == 200:
            teams = response.json()['teams']
            if teams:
                team_to_join = teams[0]
                join_data = {
                    "employee_code": team_to_join['employee_code'],
                    "user_name": "New Employee"
                }
                
                response = requests.post(f"{base_url}/api/teams/join", json=join_data)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 201:
                    result = response.json()
                    print("✅ Successfully joined team!")
                    print(f"User ID: {result['user']['id']}")
                    print(f"Team ID: {result['user']['team_id']}")
                else:
                    print(f"❌ Team join failed: {response.text}")
            else:
                print("❌ No teams available to join")
        else:
            print(f"❌ Could not get teams for join test: {response.text}")
            
    except Exception as e:
        print(f"❌ Error joining team: {e}")
    
    # Test 4: Health check
    print("\n4. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check passed!")
            print(f"Database: {result['database']}")
            print(f"Services: {result['services']}")
        else:
            print(f"❌ Health check failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error in health check: {e}")

if __name__ == "__main__":
    test_team_creation() 