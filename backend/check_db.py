#!/usr/bin/env python3
from application import application, db, Team, Membership, User

with application.app_context():
    print("=== TEAMS ===")
    teams = Team.query.all()
    for team in teams:
        print(f"  {team.id}: {team.name}")
        
        # Find manager for this team
        manager_membership = Membership.query.filter_by(team_id=team.id, role='manager').first()
        if manager_membership:
            print(f"    Manager: {manager_membership.user_name} ({manager_membership.user_id})")
        else:
            print(f"    Manager: None")
    
    print("\n=== MEMBERSHIPS ===")
    memberships = Membership.query.all()
    for membership in memberships:
        print(f"  {membership.team_id}: {membership.user_name} ({membership.role})")
    
    print("\n=== USERS ===")
    users = User.query.all()
    for user in users:
        print(f"  {user.id}: {user.name} ({user.email})") 