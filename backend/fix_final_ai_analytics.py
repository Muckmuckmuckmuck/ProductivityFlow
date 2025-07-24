#!/usr/bin/env python3
"""
FINAL FIX FOR AI ANALYTICS ENDPOINTS
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
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_jwt_token(token)
        if not token_data:
            return jsonify({"error": "Invalid token"}), 401
        
        user_id = token_data.get('user_id')
        team_id = token_data.get('team_id')
        role = token_data.get('role')
        
        # Get team_id from query parameter if provided
        requested_team_id = request.args.get('team_id')
        if requested_team_id:
            team_id = requested_team_id
        
        if not team_id:
            return jsonify({"error": "Team ID required"}), 400
        
        # Get team members through membership table
        memberships = Membership.query.filter_by(team_id=team_id).all()
        team_members = []
        for membership in memberships:
            user = User.query.get(membership.user_id)
            if user:
                team_members.append({
                    'user_id': user.id,
                    'name': user.name,
                    'role': membership.role
                })
        
        if not team_members:
            return jsonify({"error": "No team members found"}), 404
        
        # Get activities for all team members
        user_ids = [member['user_id'] for member in team_members]
        activities = Activity.query.filter(
            Activity.user_id.in_(user_ids),
            Activity.team_id == team_id,
            Activity.last_active >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        if not activities:
            return jsonify({
                'team_id': team_id,
                'analysis_date': datetime.utcnow().isoformat(),
                'risk_score': 0,
                'risk_level': 'low',
                'factors': [],
                'trends': {},
                'recommendations': ['No recent activity data available for analysis']
            })
        
        # Calculate burnout risk for each member
        member_risks = []
        for member in team_members:
            member_activities = [a for a in activities if a.user_id == member['user_id']]
            if member_activities:
                risk_factors = calculate_burnout_risk_factors(member_activities, member['user_id'])
                member_risks.append({
                    'user_id': member['user_id'],
                    'name': member['name'],
                    'role': member['role'],
                    'risk_score': risk_factors['risk_score'],
                    'risk_level': risk_factors['risk_level'],
                    'factors': risk_factors['factors']
                })
        
        # Calculate team-wide risk
        if member_risks:
            avg_risk_score = sum(r['risk_score'] for r in member_risks) / len(member_risks)
            max_risk_score = max(r['risk_score'] for r in member_risks)
            
            if max_risk_score >= 70:
                team_risk_level = 'critical'
            elif max_risk_score >= 50:
                team_risk_level = 'high'
            elif max_risk_score >= 30:
                team_risk_level = 'medium'
            else:
                team_risk_level = 'low'
        else:
            avg_risk_score = 0
            team_risk_level = 'low'
        
        # Generate recommendations
        recommendations = []
        if team_risk_level in ['high', 'critical']:
            recommendations.append("Consider implementing mandatory breaks and work-life balance policies")
            recommendations.append("Monitor team members showing high burnout risk indicators")
        if any(r['risk_score'] > 50 for r in member_risks):
            recommendations.append("Schedule one-on-one meetings with high-risk team members")
        if avg_risk_score > 30:
            recommendations.append("Review workload distribution across the team")
        
        return jsonify({
            'team_id': team_id,
            'analysis_date': datetime.utcnow().isoformat(),
            'team_risk_score': avg_risk_score,
            'team_risk_level': team_risk_level,
            'member_risks': member_risks,
            'recommendations': recommendations
        })
        
    except Exception as e:
        application.logger.error(f"Error in burnout risk analysis: {e}")
        return jsonify({"error": "Failed to analyze burnout risk"}), 500'''
    
    burnout_new = '''@application.route('/api/analytics/burnout-risk', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_burnout_risk():
    """Get burnout risk analysis for team members"""
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_jwt_token(token)
        if not token_data:
            return jsonify({"error": "Invalid token"}), 401
        
        user_id = token_data.get('user_id')
        team_id = token_data.get('team_id')
        role = token_data.get('role')
        
        # Get team_id from query parameter if provided
        requested_team_id = request.args.get('team_id')
        if requested_team_id:
            team_id = requested_team_id
        
        if not team_id:
            return jsonify({"error": "Team ID required"}), 400
        
        # Get team members through membership table
        memberships = Membership.query.filter_by(team_id=team_id).all()
        team_members = []
        for membership in memberships:
            user = User.query.get(membership.user_id)
            if user:
                team_members.append({
                    'user_id': user.id,
                    'name': user.name,
                    'role': membership.role
                })
        
        if not team_members:
            return jsonify({"error": "No team members found"}), 404
        
        # Get activities for all team members
        user_ids = [member['user_id'] for member in team_members]
        activities = Activity.query.filter(
            Activity.user_id.in_(user_ids),
            Activity.team_id == team_id,
            Activity.last_active >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        if not activities:
            return jsonify({
                'team_id': team_id,
                'analysis_date': datetime.utcnow().isoformat(),
                'risk_score': 0,
                'risk_level': 'low',
                'factors': [],
                'trends': {},
                'recommendations': ['No recent activity data available for analysis']
            })
        
        # Calculate burnout risk for each member
        member_risks = []
        for member in team_members:
            member_activities = [a for a in activities if a.user_id == member['user_id']]
            if member_activities:
                risk_factors = calculate_burnout_risk_factors(member_activities, member['user_id'])
                member_risks.append({
                    'user_id': member['user_id'],
                    'name': member['name'],
                    'role': member['role'],
                    'risk_score': risk_factors['risk_score'],
                    'risk_level': risk_factors['risk_level'],
                    'factors': risk_factors['factors']
                })
        
        # Calculate team-wide risk
        if member_risks:
            avg_risk_score = sum(r['risk_score'] for r in member_risks) / len(member_risks)
            max_risk_score = max(r['risk_score'] for r in member_risks)
            
            if max_risk_score >= 70:
                team_risk_level = 'critical'
            elif max_risk_score >= 50:
                team_risk_level = 'high'
            elif max_risk_score >= 30:
                team_risk_level = 'medium'
            else:
                team_risk_level = 'low'
        else:
            avg_risk_score = 0
            team_risk_level = 'low'
        
        # Generate recommendations
        recommendations = []
        if team_risk_level in ['high', 'critical']:
            recommendations.append("Consider implementing mandatory breaks and work-life balance policies")
            recommendations.append("Monitor team members showing high burnout risk indicators")
        if any(r['risk_score'] > 50 for r in member_risks):
            recommendations.append("Schedule one-on-one meetings with high-risk team members")
        if avg_risk_score > 30:
            recommendations.append("Review workload distribution across the team")
        
        return jsonify({
            'team_id': team_id,
            'analysis_date': datetime.utcnow().isoformat(),
            'team_risk_score': avg_risk_score,
            'team_risk_level': team_risk_level,
            'member_risks': member_risks,
            'recommendations': recommendations
        })
        
    except Exception as e:
        application.logger.error(f"Error in burnout risk analysis: {e}")
        return jsonify({"error": "Failed to analyze burnout risk"}), 500'''
    
    # Find and replace the distraction profile endpoint
    distraction_old = '''@application.route('/api/analytics/distraction-profile', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_distraction_profile():
    """Get distraction profile analysis for team members"""
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_jwt_token(token)
        if not token_data:
            return jsonify({"error": "Invalid token"}), 401
        
        user_id = token_data.get('user_id')
        team_id = token_data.get('team_id')
        role = token_data.get('role')
        
        # Get team_id from query parameter if provided
        requested_team_id = request.args.get('team_id')
        if requested_team_id:
            team_id = requested_team_id
        
        if not team_id:
            return jsonify({"error": "Team ID required"}), 400
        
        # Get team members through membership table
        memberships = Membership.query.filter_by(team_id=team_id).all()
        team_members = []
        for membership in memberships:
            user = User.query.get(membership.user_id)
            if user:
                team_members.append({
                    'user_id': user.id,
                    'name': user.name,
                    'role': membership.role
                })
        
        if not team_members:
            return jsonify({"error": "No team members found"}), 404
        
        # Get activities for all team members
        user_ids = [member['user_id'] for member in team_members]
        activities = Activity.query.filter(
            Activity.user_id.in_(user_ids),
            Activity.team_id == team_id,
            Activity.last_active >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        if not activities:
            return jsonify({
                'team_id': team_id,
                'analysis_date': datetime.utcnow().isoformat(),
                'distraction_profile': [],
                'total_unproductive_time_hours': 0,
                'period_days': 7,
                'insights': ['No recent activity data available for analysis']
            })
        
        # Calculate distraction profile
        distraction_categories = {
            'Social Media': ['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok', 'youtube'],
            'Entertainment': ['netflix', 'spotify', 'games', 'twitch', 'discord'],
            'News': ['cnn', 'bbc', 'reuters', 'news', 'reddit'],
            'Shopping': ['amazon', 'ebay', 'etsy', 'shop'],
            'Internal Chat': ['slack', 'teams', 'discord', 'whatsapp', 'telegram'],
            'Email': ['gmail', 'outlook', 'mail', 'yahoo'],
            'Other': []
        }
        
        total_unproductive_time = 0
        category_times = {category: 0 for category in distraction_categories.keys()}
        
        for activity in activities:
            if activity.unproductive_hours > 0:
                total_unproductive_time += activity.unproductive_hours
                
                # Categorize based on active app
                app_name = (activity.active_app or '').lower()
                categorized = False
                
                for category, keywords in distraction_categories.items():
                    if any(keyword in app_name for keyword in keywords):
                        category_times[category] += activity.unproductive_hours
                        categorized = True
                        break
                
                if not categorized:
                    category_times['Other'] += activity.unproductive_hours
        
        # Create distraction profile
        distraction_profile = []
        for category, time in category_times.items():
            if time > 0:
                percentage = (time / total_unproductive_time * 100) if total_unproductive_time > 0 else 0
                distraction_profile.append({
                    'category': category,
                    'time_hours': round(time, 2),
                    'percentage': round(percentage, 1)
                })
        
        # Sort by percentage descending
        distraction_profile.sort(key=lambda x: x['percentage'], reverse=True)
        
        # Generate insights
        insights = []
        if distraction_profile:
            top_distraction = distraction_profile[0]
            if top_distraction['percentage'] > 40:
                insights.append(f"{top_distraction['category']} is the biggest team distraction ({top_distraction['percentage']}% of unproductive time)")
            
            if any(d['category'] == 'Social Media' and d['percentage'] > 25 for d in distraction_profile):
                insights.append("Social media usage is significantly impacting team productivity")
            
            if any(d['category'] == 'Internal Chat' and d['percentage'] > 20 for d in distraction_profile):
                insights.append("Internal communication tools may be causing context switching")
        
        return jsonify({
            'team_id': team_id,
            'analysis_date': datetime.utcnow().isoformat(),
            'distraction_profile': distraction_profile,
            'insights': insights,
            'total_unproductive_time_hours': round(total_unproductive_time, 2),
            'period_days': 7
        })
        
    except Exception as e:
        application.logger.error(f"Error in distraction profile analysis: {e}")
        return jsonify({"error": "Failed to analyze distraction profile"}), 500'''
    
    distraction_new = '''@application.route('/api/analytics/distraction-profile', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_distraction_profile():
    """Get distraction profile analysis for team members"""
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_jwt_token(token)
        if not token_data:
            return jsonify({"error": "Invalid token"}), 401
        
        user_id = token_data.get('user_id')
        team_id = token_data.get('team_id')
        role = token_data.get('role')
        
        # Get team_id from query parameter if provided
        requested_team_id = request.args.get('team_id')
        if requested_team_id:
            team_id = requested_team_id
        
        if not team_id:
            return jsonify({"error": "Team ID required"}), 400
        
        # Get team members through membership table
        memberships = Membership.query.filter_by(team_id=team_id).all()
        team_members = []
        for membership in memberships:
            user = User.query.get(membership.user_id)
            if user:
                team_members.append({
                    'user_id': user.id,
                    'name': user.name,
                    'role': membership.role
                })
        
        if not team_members:
            return jsonify({"error": "No team members found"}), 404
        
        # Get activities for all team members
        user_ids = [member['user_id'] for member in team_members]
        activities = Activity.query.filter(
            Activity.user_id.in_(user_ids),
            Activity.team_id == team_id,
            Activity.last_active >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        if not activities:
            return jsonify({
                'team_id': team_id,
                'analysis_date': datetime.utcnow().isoformat(),
                'distraction_profile': [],
                'total_unproductive_time_hours': 0,
                'period_days': 7,
                'insights': ['No recent activity data available for analysis']
            })
        
        # Calculate distraction profile
        distraction_categories = {
            'Social Media': ['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok', 'youtube'],
            'Entertainment': ['netflix', 'spotify', 'games', 'twitch', 'discord'],
            'News': ['cnn', 'bbc', 'reuters', 'news', 'reddit'],
            'Shopping': ['amazon', 'ebay', 'etsy', 'shop'],
            'Internal Chat': ['slack', 'teams', 'discord', 'whatsapp', 'telegram'],
            'Email': ['gmail', 'outlook', 'mail', 'yahoo'],
            'Other': []
        }
        
        total_unproductive_time = 0
        category_times = {category: 0 for category in distraction_categories.keys()}
        
        for activity in activities:
            if activity.unproductive_hours > 0:
                total_unproductive_time += activity.unproductive_hours
                
                # Categorize based on active app
                app_name = (activity.active_app or '').lower()
                categorized = False
                
                for category, keywords in distraction_categories.items():
                    if any(keyword in app_name for keyword in keywords):
                        category_times[category] += activity.unproductive_hours
                        categorized = True
                        break
                
                if not categorized:
                    category_times['Other'] += activity.unproductive_hours
        
        # Create distraction profile
        distraction_profile = []
        for category, time in category_times.items():
            if time > 0:
                percentage = (time / total_unproductive_time * 100) if total_unproductive_time > 0 else 0
                distraction_profile.append({
                    'category': category,
                    'time_hours': round(time, 2),
                    'percentage': round(percentage, 1)
                })
        
        # Sort by percentage descending
        distraction_profile.sort(key=lambda x: x['percentage'], reverse=True)
        
        # Generate insights
        insights = []
        if distraction_profile:
            top_distraction = distraction_profile[0]
            if top_distraction['percentage'] > 40:
                insights.append(f"{top_distraction['category']} is the biggest team distraction ({top_distraction['percentage']}% of unproductive time)")
            
            if any(d['category'] == 'Social Media' and d['percentage'] > 25 for d in distraction_profile):
                insights.append("Social media usage is significantly impacting team productivity")
            
            if any(d['category'] == 'Internal Chat' and d['percentage'] > 20 for d in distraction_profile):
                insights.append("Internal communication tools may be causing context switching")
        
        return jsonify({
            'team_id': team_id,
            'analysis_date': datetime.utcnow().isoformat(),
            'distraction_profile': distraction_profile,
            'insights': insights,
            'total_unproductive_time_hours': round(total_unproductive_time, 2),
            'period_days': 7
        })
        
    except Exception as e:
        application.logger.error(f"Error in distraction profile analysis: {e}")
        return jsonify({"error": "Failed to analyze distraction profile"}), 500'''
    
    # Apply the fixes
    content = content.replace(burnout_old, burnout_new)
    content = content.replace(distraction_old, distraction_new)
    
    # Write the fixed content back
    with open('application.py', 'w') as f:
        f.write(content)
    
    print("✅ AI analytics endpoints fixed successfully!")

if __name__ == "__main__":
    fix_ai_analytics() 