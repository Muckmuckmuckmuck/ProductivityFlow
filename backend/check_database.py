#!/usr/bin/env python3
"""
Database Check Script - Check teams and users
"""

from application import application, db, Team, User

def check_database():
    with application.app_context():
        print("=== DATABASE CHECK ===")
        
        # Check teams
        print("\n=== TEAMS ===")
        teams = Team.query.all()
        if teams:
            for team in teams:
                print(f"ID: {team.id}")
                print(f"Name: {team.name}")
                print(f"Employee Code: {team.employee_code}")
                print(f"Manager Code: {team.manager_code}")
                print("-" * 40)
        else:
            print("No teams found in database")
        
        # Check users
        print("\n=== USERS ===")
        users = User.query.all()
        if users:
            for user in users:
                print(f"ID: {user.id}")
                print(f"Name: {user.name}")
                print(f"Email: {user.email}")
                print(f"Team ID: {user.team_id}")
                print(f"Role: {user.role}")
                print("-" * 40)
        else:
            print("No users found in database")
        
        # Check for orphaned users (users without teams)
        print("\n=== ORPHANED USERS ===")
        orphaned_users = User.query.filter_by(team_id=None).all()
        if orphaned_users:
            for user in orphaned_users:
                print(f"Orphaned user: {user.name} ({user.email}) - Role: {user.role}")
        else:
            print("No orphaned users found")
        
        # Check for teams without users
        print("\n=== EMPTY TEAMS ===")
        empty_teams = []
        for team in teams:
            team_users = User.query.filter_by(team_id=team.id).all()
            if not team_users:
                empty_teams.append(team)
        
        if empty_teams:
            for team in empty_teams:
                print(f"Empty team: {team.name} (ID: {team.id})")
        else:
            print("No empty teams found")

if __name__ == "__main__":
    check_database() 