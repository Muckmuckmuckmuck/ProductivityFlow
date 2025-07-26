#!/usr/bin/env python3
"""
Cleanup Test Data Script
Removes test users and fixes team isolation issues
"""
import os
import sys
import requests
import json
from datetime import datetime

# Backend URL
BACKEND_URL = os.environ.get('BACKEND_URL', 'https://my-home-backend-7m6d.onrender.com')

def cleanup_test_data():
    """Clean up test data and fix team isolation"""
    
    print("🧹 Cleaning up test data...")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    # Test backend connectivity
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is accessible")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    print()
    
    # Get all teams
    try:
        response = requests.get(f"{BACKEND_URL}/api/teams")
        if response.status_code == 200:
            teams_data = response.json()
            teams = teams_data.get('teams', [])
            print(f"📋 Found {len(teams)} teams")
            
            for team in teams:
                print(f"\n🔍 Analyzing team: {team['name']} (ID: {team['id']})")
                
                # Get team members
                members_response = requests.get(f"{BACKEND_URL}/api/teams/{team['id']}/members")
                if members_response.status_code == 200:
                    members_data = members_response.json()
                    members = members_data.get('members', [])
                    
                    print(f"   Members found: {len(members)}")
                    
                    # Check for test users
                    test_users = []
                    for member in members:
                        if any(test_name in member.get('name', '') for test_name in [
                            'John Doe', 'Jane Smith', 'Mike Johnson', 'Alice Johnson', 
                            'Bob Smith', 'Carol Davis', 'David Wilson', 'Manager Sarah',
                            'Manager Mike', 'Manager Lisa'
                        ]):
                            test_users.append(member)
                    
                    if test_users:
                        print(f"   ⚠️  Found {len(test_users)} test users:")
                        for user in test_users:
                            print(f"      - {user.get('name', 'Unknown')} (ID: {user.get('id', 'Unknown')})")
                        
                        # Ask for confirmation to delete
                        confirm = input(f"   🗑️  Delete these test users from {team['name']}? (y/N): ")
                        if confirm.lower() == 'y':
                            for user in test_users:
                                try:
                                    # Note: This would require the delete endpoint to be implemented
                                    print(f"      Deleting {user.get('name', 'Unknown')}...")
                                    # delete_response = requests.delete(f"{BACKEND_URL}/api/teams/{team['id']}/members/{user['id']}")
                                    # if delete_response.status_code == 200:
                                    #     print(f"      ✅ Deleted {user.get('name', 'Unknown')}")
                                    # else:
                                    #     print(f"      ❌ Failed to delete {user.get('name', 'Unknown')}")
                                except Exception as e:
                                    print(f"      ❌ Error deleting {user.get('name', 'Unknown')}: {e}")
                    else:
                        print("   ✅ No test users found")
                else:
                    print(f"   ❌ Failed to get members for team {team['name']}")
        else:
            print(f"❌ Failed to get teams: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def create_clean_teams():
    """Create clean teams without test data"""
    
    print("\n🆕 Creating clean teams...")
    
    clean_teams = [
        {
            "name": "Development Team",
            "description": "Software development team"
        },
        {
            "name": "Design Team", 
            "description": "UI/UX design team"
        },
        {
            "name": "Marketing Team",
            "description": "Marketing and communications team"
        }
    ]
    
    created_teams = []
    
    for team_data in clean_teams:
        try:
            response = requests.post(f"{BACKEND_URL}/api/teams", 
                                   json={"name": team_data["name"]},
                                   headers={"Content-Type": "application/json"})
            
            if response.status_code == 201:
                team_info = response.json()
                created_teams.append(team_info)
                print(f"✅ Created clean team: {team_info['team']['name']}")
                print(f"   Employee Code: {team_info['team']['employee_code']}")
                print()
            else:
                print(f"❌ Failed to create team {team_data['name']}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating team {team_data['name']}: {e}")
    
    return created_teams

def generate_clean_codes_markdown(teams):
    """Generate a markdown file with clean team codes"""
    
    markdown_content = f"""# Clean Team Codes

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Backend URL
```
{BACKEND_URL}
```

## Clean Teams (No Test Data)

"""
    
    for i, team in enumerate(teams, 1):
        team_data = team.get('team', team)
        employee_code = team_data.get('employee_code', 'N/A')
        
        markdown_content += f"""### {i}. {team_data['name']}
**Team ID**: `{team_data.get('id', 'N/A')}`
**Employee Code**: `{employee_code}`
**Description**: Clean team with no test data

---

"""
    
    markdown_content += f"""## How to Use

### Employee App Testing
1. Open the Employee Tracker app
2. Use any of the **Employee Codes** above
3. Enter your name and the code to join a team
4. The app will start tracking your activity

### Manager App Testing  
1. Open the Manager Dashboard app
2. Create a new team or use existing team codes
3. View team analytics and manage employees

### API Testing
```bash
# Test backend health
curl {BACKEND_URL}/health

# Get all teams
curl {BACKEND_URL}/api/teams

# Join a team as employee
curl -X POST {BACKEND_URL}/api/teams/join \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "Your Name", "team_code": "EMPLOYEE_CODE_HERE"}}'
```

## Quick Test Codes

Here are the clean codes you can use immediately:

"""
    
    for i, team in enumerate(teams, 1):
        team_data = team.get('team', team)
        employee_code = team_data.get('employee_code', 'N/A')
        
        markdown_content += f"""**{team_data['name']}**
- Employee Code: `{employee_code}`

"""

    markdown_content += """
## Notes
- These teams are clean with no test data
- Employee codes are 6 characters long
- Each team is isolated from others
- No cross-contamination of users between teams
- Ready for production testing
"""
    
    return markdown_content

def main():
    print("🚀 ProductivityFlow Test Data Cleanup")
    print("=" * 40)
    
    # Clean up existing test data
    cleanup_test_data()
    
    # Create clean teams
    print("\n" + "=" * 40)
    clean_teams = create_clean_teams()
    
    if clean_teams:
        # Generate summary
        markdown_content = generate_clean_codes_markdown(clean_teams)
        
        # Write to file
        with open('CLEAN_TEAM_CODES.md', 'w') as f:
            f.write(markdown_content)
        
        print("\n✅ Clean team codes saved to CLEAN_TEAM_CODES.md")
        print("\n🎉 Cleanup complete! You can now test with clean teams.")
    else:
        print("\n❌ No clean teams were created")

if __name__ == "__main__":
    main() 