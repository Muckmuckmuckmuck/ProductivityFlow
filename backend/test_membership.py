#!/usr/bin/env python3
"""
Test script to debug membership lookup
"""

from application import application, db, Membership, User

with application.app_context():
    user_id = "user_1753283145_u4xnct55"
    
    print(f"Looking for memberships for user: {user_id}")
    
    # Check all memberships
    all_memberships = Membership.query.all()
    print(f"Total memberships: {len(all_memberships)}")
    for m in all_memberships:
        print(f"  {m.team_id}: {m.user_name} ({m.role}) - user_id: {m.user_id}")
    
    # Check specific user memberships
    user_memberships = Membership.query.filter_by(user_id=user_id).all()
    print(f"\nMemberships for user {user_id}: {len(user_memberships)}")
    for m in user_memberships:
        print(f"  {m.team_id}: {m.user_name} ({m.role})")
    
    # Check manager memberships
    manager_memberships = Membership.query.filter_by(user_id=user_id, role='manager').all()
    print(f"\nManager memberships for user {user_id}: {len(manager_memberships)}")
    for m in manager_memberships:
        print(f"  {m.team_id}: {m.user_name} ({m.role})")
    
    # Check all manager memberships
    all_managers = Membership.query.filter_by(role='manager').all()
    print(f"\nAll manager memberships: {len(all_managers)}")
    for m in all_managers:
        print(f"  {m.team_id}: {m.user_name} ({m.role}) - user_id: {m.user_id}") 