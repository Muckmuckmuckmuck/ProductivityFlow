#!/usr/bin/env python3
"""
Fix syntax errors in application.py
"""

import re

def fix_syntax_errors():
    """Fix the syntax errors in application.py"""
    
    # Read the current file
    with open('application.py', 'r') as f:
        content = f.read()
    
    # Fix the corrupted burnout risk endpoint
    burnout_pattern = r'# Get user\\\'s teams where they are a manager\s*manager_memberships = Membership\.query\.filter_by\(user_id=current_user_id, role=\\\'manager\\\'\)\.all\(\)\s*all_team_ids = \[membership\.team_id for membership in manager_memberships\]# Get user\'s teams where they are a manager \(using both methods for compatibility\)\s*manager_teams = Team\.query\.filter_by\(manager_id=current_user_id\)\.all\(\)\s*manager_memberships = Membership\.query\.filter_by\(user_id=current_user_id, role=\'manager\'\)\.all\(\)\s*# Combine both methods to get all teams where user is manager\s*team_ids_from_teams = \[team\.id for team in manager_teams\]\s*team_ids_from_memberships = \[membership\.team_id for membership in manager_memberships\]\s*all_team_ids = list\(set\(team_ids_from_teams \+ team_ids_from_memberships\)\)\s*\s*\s*return jsonify\(\{\'error\': \'No teams found where you are a manager\'\), 404'
    
    burnout_replacement = '''# Get user's teams where they are a manager
        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role='manager').all()
        all_team_ids = [membership.team_id for membership in manager_memberships]
        
        if not all_team_ids:
            return jsonify({'error': 'No teams found where you are a manager'}), 404'''
    
    content = re.sub(burnout_pattern, burnout_replacement, content, flags=re.DOTALL)
    
    # Fix the corrupted distraction profile endpoint
    distraction_pattern = r'# Get user\\\'s teams where they are a manager\s*manager_memberships = Membership\.query\.filter_by\(user_id=current_user_id, role=\\\'manager\\\'\)\.all\(\)\s*all_team_ids = \[membership\.team_id for membership in manager_memberships\]# Get user\'s teams where they are a manager \(using both methods for compatibility\)\s*manager_teams = Team\.query\.filter_by\(manager_id=current_user_id\)\.all\(\)\s*manager_memberships = Membership\.query\.filter_by\(user_id=current_user_id, role=\'manager\'\)\.all\(\)\s*# Combine both methods to get all teams where user is manager\s*team_ids_from_teams = \[team\.id for team in manager_teams\]\s*team_ids_from_memberships = \[membership\.team_id for membership in manager_memberships\]\s*all_team_ids = list\(set\(team_ids_from_teams \+ team_ids_from_memberships\)\)\s*\s*\s*return jsonify\(\{\'error\': \'No teams found where you are a manager\'\), 404'
    
    distraction_replacement = '''# Get user's teams where they are a manager
        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role='manager').all()
        all_team_ids = [membership.team_id for membership in manager_memberships]
        
        if not all_team_ids:
            return jsonify({'error': 'No teams found where you are a manager'}), 404'''
    
    content = re.sub(distraction_pattern, distraction_replacement, content, flags=re.DOTALL)
    
    # Write the fixed content back
    with open('application.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed syntax errors in application.py")

if __name__ == "__main__":
    fix_syntax_errors() 