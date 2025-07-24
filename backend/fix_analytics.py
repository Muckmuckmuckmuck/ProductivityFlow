#!/usr/bin/env python3
"""
Fix AI Analytics Endpoints
This script fixes the issues in the AI analytics endpoints
"""

import re

def fix_application_py():
    """Fix the application.py file"""
    
    # Read the current file
    with open('application.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Replace the problematic manager_id query in burnout risk endpoint
    # Find the burnout risk endpoint specifically
    burnout_pattern = r'(@application\.route\(\'/api/analytics/burnout-risk\', methods=\[\'GET\'\]\)\s*@conditional_rate_limit\("10 per minute"\)\s*def get_burnout_risk\(\):.*?)(# Get user\'s teams where they are a manager \(using both methods for compatibility\)\s*manager_teams = Team\.query\.filter_by\(manager_id=current_user_id\)\.all\(\)\s*manager_memberships = Membership\.query\.filter_by\(user_id=current_user_id, role=\'manager\'\)\.all\(\)\s*# Combine both methods to get all teams where user is manager\s*team_ids_from_teams = \[team\.id for team in manager_teams\]\s*team_ids_from_memberships = \[membership\.team_id for membership in manager_memberships\]\s*all_team_ids = list\(set\(team_ids_from_teams \+ team_ids_from_memberships\)\))(.*?)(if not all_team_ids:)'
    
    burnout_replacement = r'\1# Get user\'s teams where they are a manager\n        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role=\'manager\').all()\n        all_team_ids = [membership.team_id for membership in manager_memberships]\2\3'
    
    content = re.sub(burnout_pattern, burnout_replacement, content, flags=re.DOTALL)
    
    # Fix 2: Replace the problematic manager_id query in distraction profile endpoint
    distraction_pattern = r'(@application\.route\(\'/api/analytics/distraction-profile\', methods=\[\'GET\'\]\)\s*@conditional_rate_limit\("10 per minute"\)\s*def get_distraction_profile\(\):.*?)(# Get user\'s teams where they are a manager \(using both methods for compatibility\)\s*manager_teams = Team\.query\.filter_by\(manager_id=current_user_id\)\.all\(\)\s*manager_memberships = Membership\.query\.filter_by\(user_id=current_user_id, role=\'manager\'\)\.all\(\)\s*# Combine both methods to get all teams where user is manager\s*team_ids_from_teams = \[team\.id for team in manager_teams\]\s*team_ids_from_memberships = \[membership\.team_id for membership in manager_memberships\]\s*all_team_ids = list\(set\(team_ids_from_teams \+ team_ids_from_memberships\)\))(.*?)(if not all_team_ids:)'
    
    distraction_replacement = r'\1# Get user\'s teams where they are a manager\n        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role=\'manager\').all()\n        all_team_ids = [membership.team_id for membership in manager_memberships]\2\3'
    
    content = re.sub(distraction_pattern, distraction_replacement, content, flags=re.DOTALL)
    
    # Write the fixed content back
    with open('application.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed AI analytics endpoints in application.py")

if __name__ == "__main__":
    fix_application_py() 