#!/usr/bin/env python3
"""
Fix AI Analytics Endpoints
This script completely replaces the problematic AI analytics endpoints with correct implementations
"""

import re

def fix_ai_analytics():
    """Fix the AI analytics endpoints"""
    
    # Read the current file
    with open('application.py', 'r') as f:
        content = f.read()
    
    # Find and replace the burnout risk endpoint
    burnout_old = '''@application.route('/api/analytics/burnout-risk', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_burnout_risk():
    """Get burnout risk analysis for team members"""
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = payload.get('user_id')
            
            if not current_user_id:
                return jsonify({"error": "Invalid token"}), 401
                
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get user's teams where they are a manager
        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role='manager').all()
        if not manager_memberships:
            return jsonify({'error': 'No teams found where you are a manager'}), 404
        
        team_id = request.args.get('team_id', manager_memberships[0].team_id)
        
        # Get team members via membership
        team_memberships = Membership.query.filter_by(team_id=team_id).all()
        member_ids = [membership.user_id for membership in team_memberships]
        
        if not member_ids:
            return jsonify({'error': 'No team members found'}), 404
        
        # Get team members
        team_members = User.query.filter(User.id.in_(member_ids)).all()
        
        # Calculate burnout risk for each member
        burnout_data = []
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        for member in team_members:
            # Get member's activities
            activities = Activity.query.filter(
                Activity.user_id == member.id,
                Activity.last_active >= thirty_days_ago
            ).order_by(Activity.last_active).all()
            
            # Calculate burnout risk factors
            risk_factors = calculate_burnout_risk(activities)
            
            burnout_data.append({
                'user_id': member.id,
                'user_name': member.name,
                'risk_score': risk_factors['overall_risk'],
                'risk_level': risk_factors['risk_level'],
                'factors': risk_factors['factors'],
                'trends': risk_factors['trends'],
                'recommendations': risk_factors['recommendations']
            })
        
        return jsonify({
            'team_id': team_id,
            'analysis_date': datetime.utcnow().isoformat(),
            'burnout_data': burnout_data
        })
        
    except Exception as e:
        application.logger.error(f"Error in burnout risk analysis: {e}")
        return jsonify({"error": "Internal server error"}), 500'''
    
    burnout_new = '''@application.route('/api/analytics/burnout-risk', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_burnout_risk():
    """Get burnout risk analysis for team members"""
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = payload.get('user_id')
            
            if not current_user_id:
                return jsonify({"error": "Invalid token"}), 401
                
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get user's teams where they are a manager
        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role='manager').all()
        if not manager_memberships:
            return jsonify({'error': 'No teams found where you are a manager'}), 404
        
        team_id = request.args.get('team_id', manager_memberships[0].team_id)
        
        # Get team members via membership
        team_memberships = Membership.query.filter_by(team_id=team_id).all()
        member_ids = [membership.user_id for membership in team_memberships]
        
        if not member_ids:
            return jsonify({'error': 'No team members found'}), 404
        
        # Get team members
        team_members = User.query.filter(User.id.in_(member_ids)).all()
        
        # Calculate burnout risk for each member
        burnout_data = []
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        for member in team_members:
            # Get member's activities
            activities = Activity.query.filter(
                Activity.user_id == member.id,
                Activity.last_active >= thirty_days_ago
            ).order_by(Activity.last_active).all()
            
            # Calculate burnout risk factors
            risk_factors = calculate_burnout_risk(activities)
            
            burnout_data.append({
                'user_id': member.id,
                'user_name': member.name,
                'risk_score': risk_factors['overall_risk'],
                'risk_level': risk_factors['risk_level'],
                'factors': risk_factors['factors'],
                'trends': risk_factors['trends'],
                'recommendations': risk_factors['recommendations']
            })
        
        return jsonify({
            'team_id': team_id,
            'analysis_date': datetime.utcnow().isoformat(),
            'burnout_data': burnout_data
        })
        
    except Exception as e:
        application.logger.error(f"Error in burnout risk analysis: {e}")
        return jsonify({"error": "Internal server error"}), 500'''
    
    # Replace burnout endpoint
    content = content.replace(burnout_old, burnout_new)
    
    # Find and replace the distraction profile endpoint
    distraction_old = '''@application.route('/api/analytics/distraction-profile', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_distraction_profile():
    """Get distraction profile analysis for team members"""
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = payload.get('user_id')
            
            if not current_user_id:
                return jsonify({"error": "Invalid token"}), 401
                
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get user's teams
        user_teams = Team.query.filter_by(manager_id=current_user_id).all()
        if not user_teams:
            return jsonify({'error': 'No teams found'}), 404
        
        team_id = request.args.get('team_id', user_teams[0].id)
        
        # Get team members
        team_members = User.query.filter_by(team_id=team_id).all()
        member_ids = [member.id for member in team_members]'''
    
    distraction_new = '''@application.route('/api/analytics/distraction-profile', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_distraction_profile():
    """Get distraction profile analysis for team members"""
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = payload.get('user_id')
            
            if not current_user_id:
                return jsonify({"error": "Invalid token"}), 401
                
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get user's teams where they are a manager
        manager_memberships = Membership.query.filter_by(user_id=current_user_id, role='manager').all()
        if not manager_memberships:
            return jsonify({'error': 'No teams found where you are a manager'}), 404
        
        team_id = request.args.get('team_id', manager_memberships[0].team_id)
        
        # Get team members via membership
        team_memberships = Membership.query.filter_by(team_id=team_id).all()
        member_ids = [membership.user_id for membership in team_memberships]'''
    
    # Replace distraction endpoint
    content = content.replace(distraction_old, distraction_new)
    
    # Write the fixed content back
    with open('application.py', 'w') as f:
        f.write(content)
    
    print("✅ AI analytics endpoints fixed successfully!")

if __name__ == "__main__":
    fix_ai_analytics() 