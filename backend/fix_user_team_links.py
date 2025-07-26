#!/usr/bin/env python3
"""
Fix User-Team Links Script
Fixes the relationships between users and teams, and assigns proper roles
"""

from application import application, db, Team, User
from sqlalchemy import text

def fix_user_team_links():
    with application.app_context():
        print("=== FIXING USER-TEAM RELATIONSHIPS ===")
        
        try:
            # Get all users and teams
            users = User.query.all()
            teams = Team.query.all()
            
            print(f"Found {len(users)} users and {len(teams)} teams")
            
            # Fix 1: Link users to teams based on email patterns
            print("\n=== LINKING USERS TO TEAMS ===")
            linked_count = 0
            
            for user in users:
                # Check if user email contains team ID
                for team in teams:
                    if team.id in user.email:
                        user.team_id = team.id
                        linked_count += 1
                        print(f"Linked {user.name} ({user.email}) to team {team.name}")
                        break
                
                # Check for manager users (those with @productivityflow.com)
                if 'productivityflow.com' in user.email and 'manager' in user.email.lower():
                    user.role = 'manager'
                    print(f"Set {user.name} role to manager")
                
                # Check for employee users (those with @productivityflow.com)
                elif 'productivityflow.com' in user.email and 'employee' in user.email.lower():
                    user.role = 'employee'
                    print(f"Set {user.name} role to employee")
            
            db.session.commit()
            print(f"✅ Linked {linked_count} users to teams")
            
            # Fix 2: Create a proper team for managers who don't have one
            print("\n=== CREATING TEAMS FOR MANAGERS ===")
            managers_without_teams = User.query.filter_by(role='manager', team_id=None).all()
            
            for manager in managers_without_teams:
                # Create a new team for this manager
                from application import generate_id, generate_team_code
                
                team_id = generate_id('team')
                employee_code = generate_team_code()
                manager_code = generate_team_code()
                
                new_team = Team(
                    id=team_id,
                    name=f"{manager.name}'s Team",
                    employee_code=employee_code,
                    manager_code=manager_code
                )
                
                db.session.add(new_team)
                manager.team_id = team_id
                
                print(f"Created team '{new_team.name}' for manager {manager.name}")
                print(f"  Employee Code: {employee_code}")
                print(f"  Manager Code: {manager_code}")
            
            db.session.commit()
            
            # Fix 3: Assign orphaned employees to the first available team
            print("\n=== ASSIGNING ORPHANED EMPLOYEES ===")
            orphaned_employees = User.query.filter_by(role='employee', team_id=None).all()
            
            if orphaned_employees and teams:
                # Use the first team as default
                default_team = teams[0]
                for employee in orphaned_employees:
                    employee.team_id = default_team.id
                    print(f"Assigned {employee.name} to default team: {default_team.name}")
                
                db.session.commit()
            
            # Show final state
            print("\n=== FINAL STATE ===")
            
            print("\n--- TEAMS ---")
            teams = Team.query.all()
            for team in teams:
                team_users = User.query.filter_by(team_id=team.id).all()
                print(f"Team: {team.name}")
                print(f"  ID: {team.id}")
                print(f"  Employee Code: {team.employee_code}")
                print(f"  Manager Code: {team.manager_code}")
                print(f"  Members: {len(team_users)}")
                for user in team_users:
                    print(f"    - {user.name} ({user.role})")
                print("-" * 40)
            
            print("\n--- USERS WITHOUT TEAMS ---")
            users_without_teams = User.query.filter_by(team_id=None).all()
            if users_without_teams:
                for user in users_without_teams:
                    print(f"  {user.name} ({user.email}) - Role: {user.role}")
            else:
                print("  All users are now linked to teams!")
            
            print(f"\n✅ User-team relationships fixed successfully!")
            
        except Exception as e:
            print(f"Error fixing user-team relationships: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    fix_user_team_links() 