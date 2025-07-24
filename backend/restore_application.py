#!/usr/bin/env python3
"""
Restore application.py from backup and apply fixes
"""

import shutil
import os

def restore_application():
    """Restore application.py from backup"""
    
    # Check if backup exists
    if os.path.exists('application_backup.py'):
        print("Restoring from backup...")
        shutil.copy('application_backup.py', 'application.py')
        print("✅ Restored from backup")
    else:
        print("❌ No backup found")
        return False
    
    return True

def apply_fixes():
    """Apply the necessary fixes to the restored file"""
    
    with open('application.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Replace the problematic manager_id query in burnout risk endpoint
    old_burnout = '''        # Get user's teams where they are a manager (using both methods for compatibility)
        manager_teams = Team.query.filter_by(manager_id=current_user_id).all()
        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role='manager').all()
        
        # Combine both methods to get all teams where user is manager
        team_ids_from_teams = [team.id for team in manager_teams]
        team_ids_from_memberships = [membership.team_id for membership in manager_memberships]
        all_team_ids = list(set(team_ids_from_teams + team_ids_from_memberships))'''
    
    new_burnout = '''        # Get user's teams where they are a manager
        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role='manager').all()
        all_team_ids = [membership.team_id for membership in manager_memberships]'''
    
    content = content.replace(old_burnout, new_burnout)
    
    # Fix 2: Replace the problematic manager_id query in distraction profile endpoint
    old_distraction = '''        # Get user's teams where they are a manager (using both methods for compatibility)
        manager_teams = Team.query.filter_by(manager_id=current_user_id).all()
        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role='manager').all()
        
        # Combine both methods to get all teams where user is manager
        team_ids_from_teams = [team.id for team in manager_teams]
        team_ids_from_memberships = [membership.team_id for membership in manager_memberships]
        all_team_ids = list(set(team_ids_from_teams + team_ids_from_memberships))'''
    
    new_distraction = '''        # Get user's teams where they are a manager
        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role='manager').all()
        all_team_ids = [membership.team_id for membership in manager_memberships]'''
    
    content = content.replace(old_distraction, new_distraction)
    
    # Fix 3: Fix the distraction profile field names
    old_activity_query = '''        activities = Activity.query.filter(
            Activity.user_id.in_(member_ids),
            Activity.timestamp >= seven_days_ago,
            Activity.is_productive == False  # Focus on unproductive activities
        ).all()'''
    
    new_activity_query = '''        activities = Activity.query.filter(
            Activity.user_id.in_(member_ids),
            Activity.last_active >= seven_days_ago
        ).all()'''
    
    content = content.replace(old_activity_query, new_activity_query)
    
    old_app_name = '''            app_name = activity.application_name.lower()
            duration = activity.duration or 0'''
    
    new_app_name = '''            app_name = (activity.active_app or '').lower()
            duration = activity.unproductive_hours or 0'''
    
    content = content.replace(old_app_name, new_app_name)
    
    # Write the fixed content back
    with open('application.py', 'w') as f:
        f.write(content)
    
    print("✅ Applied fixes to application.py")

if __name__ == "__main__":
    if restore_application():
        apply_fixes()
        print("🎉 Application.py restored and fixed successfully!")
    else:
        print("❌ Failed to restore application.py") 