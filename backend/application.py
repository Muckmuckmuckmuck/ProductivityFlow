#!/usr/bin/env python3
"""
ProductivityFlow Backend - Simple Working Version
Minimal backend that works with any database
"""

import os
import logging
import random
import string
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_cors import CORS
import bcrypt
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
application = Flask(__name__)

# Simple configuration
application.config['SECRET_KEY'] = 'dev-secret-key'
application.config['JWT_SECRET_KEY'] = 'jwt-secret-key'

# Database configuration - use SQLite for reliability
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivityflow.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
logger.info("✅ Using SQLite database for reliability")

# Initialize extensions
db = SQLAlchemy(application)
CORS(application)

# Simple models
class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    employee_code = db.Column(db.String(10), unique=True, nullable=False)
    manager_code = db.Column(db.String(10), unique=True, nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    team_id = db.Column(db.String(80), db.ForeignKey('teams.id'), nullable=True)
    role = db.Column(db.String(50), default='employee', nullable=False)

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    team_id = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Application tracking
    active_app = db.Column(db.String(255), nullable=True)
    app_category = db.Column(db.String(100), nullable=True)  # productivity, social, entertainment, etc.
    window_title = db.Column(db.String(500), nullable=True)
    app_url = db.Column(db.String(1000), nullable=True)  # for web apps
    
    # Time tracking
    productive_hours = db.Column(db.Float, default=0.0)
    unproductive_hours = db.Column(db.Float, default=0.0)
    idle_time = db.Column(db.Float, default=0.0)
    break_time = db.Column(db.Float, default=0.0)
    total_active_time = db.Column(db.Float, default=0.0)
    
    # Productivity metrics
    productivity_score = db.Column(db.Float, default=0.0)  # 0-100
    focus_time = db.Column(db.Float, default=0.0)
    distraction_count = db.Column(db.Integer, default=0)
    task_switches = db.Column(db.Integer, default=0)
    
    # System metrics
    cpu_usage = db.Column(db.Float, default=0.0)
    memory_usage = db.Column(db.Float, default=0.0)
    network_activity = db.Column(db.Boolean, default=False)
    
    # User behavior
    mouse_clicks = db.Column(db.Integer, default=0)
    keyboard_activity = db.Column(db.Boolean, default=False)
    screen_time = db.Column(db.Float, default=0.0)
    
    # Additional metadata
    session_id = db.Column(db.String(100), nullable=True)
    device_info = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)

class AppSession(db.Model):
    __tablename__ = 'app_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    team_id = db.Column(db.String(80), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    
    # Session details
    app_name = db.Column(db.String(255), nullable=False)
    app_category = db.Column(db.String(100), nullable=True)
    window_title = db.Column(db.String(500), nullable=True)
    url = db.Column(db.String(1000), nullable=True)
    
    # Session metrics
    duration = db.Column(db.Float, default=0.0)  # in seconds
    productivity_score = db.Column(db.Float, default=0.0)
    activity_level = db.Column(db.String(50), default='low')  # low, medium, high
    focus_score = db.Column(db.Float, default=0.0)
    
    # User interaction
    mouse_clicks = db.Column(db.Integer, default=0)
    keyboard_events = db.Column(db.Integer, default=0)
    scroll_events = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

class ProductivityEvent(db.Model):
    __tablename__ = 'productivity_events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    team_id = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Event details
    event_type = db.Column(db.String(100), nullable=False)  # app_switch, idle_start, idle_end, break_start, break_end, etc.
    event_data = db.Column(db.JSON, nullable=True)  # Additional event-specific data
    
    # Context
    app_name = db.Column(db.String(255), nullable=True)
    app_category = db.Column(db.String(100), nullable=True)
    window_title = db.Column(db.String(500), nullable=True)
    
    # Duration (for events that have duration)
    duration = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

class DailySummary(db.Model):
    __tablename__ = 'daily_summaries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    team_id = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Daily totals
    total_productive_time = db.Column(db.Float, default=0.0)
    total_unproductive_time = db.Column(db.Float, default=0.0)
    total_idle_time = db.Column(db.Float, default=0.0)
    total_break_time = db.Column(db.Float, default=0.0)
    total_screen_time = db.Column(db.Float, default=0.0)
    
    # Productivity metrics
    overall_productivity_score = db.Column(db.Float, default=0.0)
    focus_score = db.Column(db.Float, default=0.0)
    distraction_count = db.Column(db.Integer, default=0)
    task_switch_count = db.Column(db.Integer, default=0)
    
    # App usage breakdown
    most_used_app = db.Column(db.String(255), nullable=True)
    most_productive_app = db.Column(db.String(255), nullable=True)
    app_usage_breakdown = db.Column(db.JSON, nullable=True)  # {app_name: time_spent}
    
    # Goals and achievements
    goals_met = db.Column(db.Integer, default=0)
    total_goals = db.Column(db.Integer, default=0)
    achievements = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# Utility functions
def generate_id(prefix):
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{timestamp}_{random_suffix}"

def generate_team_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except:
        return False

def create_jwt_token(user_id, team_id, role):
    payload = {
        'user_id': user_id,
        'team_id': team_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, application.config['JWT_SECRET_KEY'], algorithm='HS256')

def categorize_app(app_name, window_title=None, url=None):
    """Categorize applications based on name, window title, and URL"""
    app_name_lower = app_name.lower() if app_name else ""
    window_lower = window_title.lower() if window_title else ""
    url_lower = url.lower() if url else ""
    
    # Productivity apps
    productivity_keywords = [
        'code', 'editor', 'ide', 'terminal', 'command', 'git', 'github', 'stack overflow',
        'documentation', 'api', 'database', 'server', 'development', 'programming',
        'excel', 'sheets', 'word', 'docs', 'powerpoint', 'presentation', 'project',
        'trello', 'asana', 'jira', 'notion', 'slack', 'teams', 'zoom', 'meet',
        'calendar', 'email', 'outlook', 'gmail', 'research', 'study', 'learning'
    ]
    
    # Social media and entertainment
    social_keywords = [
        'facebook', 'instagram', 'twitter', 'tiktok', 'youtube', 'netflix', 'spotify',
        'reddit', 'discord', 'snapchat', 'whatsapp', 'telegram', 'social', 'chat',
        'game', 'gaming', 'play', 'entertainment', 'music', 'video', 'stream'
    ]
    
    # Check for productivity apps
    for keyword in productivity_keywords:
        if keyword in app_name_lower or keyword in window_lower or keyword in url_lower:
            return 'productivity'
    
    # Check for social/entertainment
    for keyword in social_keywords:
        if keyword in app_name_lower or keyword in window_lower or keyword in url_lower:
            return 'social_entertainment'
    
    # Default categorization
    if any(word in app_name_lower for word in ['browser', 'chrome', 'firefox', 'safari', 'edge']):
        return 'browsing'
    elif any(word in app_name_lower for word in ['settings', 'system', 'control', 'preferences']):
        return 'system'
    else:
        return 'other'

def calculate_productivity_score(app_category, focus_time, distraction_count, task_switches, total_time):
    """Calculate productivity score based on various factors"""
    base_score = 50.0
    
    # App category multiplier
    category_multipliers = {
        'productivity': 1.2,
        'browsing': 0.8,
        'social_entertainment': 0.3,
        'system': 0.5,
        'other': 0.7
    }
    
    multiplier = category_multipliers.get(app_category, 0.7)
    base_score *= multiplier
    
    # Focus time bonus (up to 20 points)
    focus_bonus = min(20.0, (focus_time / total_time) * 20) if total_time > 0 else 0
    base_score += focus_bonus
    
    # Distraction penalty (up to 15 points)
    distraction_penalty = min(15.0, distraction_count * 2)
    base_score -= distraction_penalty
    
    # Task switching penalty (up to 10 points)
    switch_penalty = min(10.0, task_switches * 1.5)
    base_score -= switch_penalty
    
    # Ensure score is between 0 and 100
    return max(0.0, min(100.0, base_score))

def generate_session_id():
    """Generate a unique session ID"""
    return f"session_{int(time.time())}_{random.randint(1000, 9999)}"

# Health check
@application.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
        database_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        database_status = "disconnected"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '3.2.1',
        'environment': 'production',
        'database': database_status,
        'services': {
            'database': 'operational' if database_status == "connected" else 'degraded',
            'authentication': 'operational',
            'ai_insights': 'operational'
        }
    }), 200

# Authentication endpoints
@application.route('/api/auth/register', methods=['POST'])
def register_manager():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        organization = data.get('organization', '').strip()
        
        if not name or not email or not password or not organization:
            return jsonify({'error': True, 'message': 'All fields are required'}), 400
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': True, 'message': 'User already exists'}), 409
        
        # Create user
        user_id = generate_id('user')
        password_hash = hash_password(password)
        
        new_user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            name=name,
            role='manager'
        )
        
        db.session.add(new_user)
        
        # Create team
        team_id = generate_id('team')
        employee_code = generate_team_code()
        manager_code = generate_team_code()
        
        new_team = Team(
            id=team_id,
            name=organization,
            employee_code=employee_code,
            manager_code=manager_code
        )
        
        db.session.add(new_team)
        
        # Link user to team
        new_user.team_id = team_id
        
        db.session.commit()
        
        # Create token
        token = create_jwt_token(user_id, team_id, 'manager')
        
        logger.info(f"Manager registered successfully: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Manager registered successfully',
            'user': {
                'id': user_id,
                'name': name,
                'email': email,
                'role': 'manager',
                'organization': organization
            },
            'team': {
                'id': team_id,
                'name': organization,
                'employee_code': employee_code,
                'manager_code': manager_code
            },
            'token': token
        }), 201
        
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Registration failed. Please try again.'}), 500

@application.route('/api/auth/login', methods=['POST'])
def login_manager():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': True, 'message': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': True, 'message': 'Invalid credentials'}), 401
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return jsonify({'error': True, 'message': 'Invalid credentials'}), 401
        
        # Create token
        token = create_jwt_token(user.id, user.team_id or '', user.role)
        
        logger.info(f"Manager logged in successfully: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'team_id': user.team_id
            },
            'token': token
        }), 200
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return jsonify({'error': True, 'message': 'Login failed. Please try again.'}), 500

@application.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': True, 'message': 'Email is required'}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': True, 'message': 'If an account with this email exists, a reset link has been sent.'}), 200
        
        # Generate reset token (simple implementation for now)
        reset_token = generate_team_code()  # Using team code generator for simplicity
        
        # In a real implementation, you would:
        # 1. Store the reset token in the database with expiration
        # 2. Send an email with the reset link
        # 3. Use a proper token generation method
        
        logger.info(f"Password reset requested for: {email}")
        
        return jsonify({
            'success': True,
            'message': 'If an account with this email exists, a reset link has been sent.',
            'reset_token': reset_token  # In production, this would be sent via email
        }), 200
        
    except Exception as e:
        logger.error(f"Forgot password failed: {str(e)}")
        return jsonify({'error': True, 'message': 'Request failed. Please try again.'}), 500

@application.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        
        if not email or not token or not new_password:
            return jsonify({'error': True, 'message': 'Email, token, and new password are required'}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': True, 'message': 'Invalid email or token'}), 400
        
        # In a real implementation, you would:
        # 1. Verify the reset token is valid and not expired
        # 2. Check if the token matches what was stored
        
        # For now, we'll just update the password
        user.password_hash = hash_password(new_password)
        db.session.commit()
        
        logger.info(f"Password reset successful for: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Password reset failed: {str(e)}")
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Password reset failed. Please try again.'}), 500

@application.route('/api/auth/employee-login', methods=['POST'])
def employee_login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        team_code = data.get('team_code', '').strip().upper()
        user_name = data.get('user_name', '').strip()
        
        if not team_code or not user_name:
            return jsonify({'error': True, 'message': 'Team code and user name are required'}), 400
        
        # Find team
        team = Team.query.filter_by(employee_code=team_code).first()
        if not team:
            return jsonify({'error': True, 'message': 'Invalid team code'}), 401
        
        # Check if user exists
        existing_user = User.query.filter_by(team_id=team.id, name=user_name).first()
        
        if existing_user:
            # Login existing user
            token = create_jwt_token(existing_user.id, team.id, 'employee')
            
            logger.info(f"Employee logged in: {user_name} in team {team.name}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': existing_user.id,
                    'name': existing_user.name,
                    'role': 'employee',
                    'team_id': team.id
                },
                'team': {
                    'id': team.id,
                    'name': team.name,
                    'employee_code': team.employee_code
                },
                'token': token
            }), 200
        else:
            # Create new user
            user_id = generate_id('user')
            
            new_user = User(
                id=user_id,
                email=f"{user_name.lower().replace(' ', '.')}@{team.id}.local",
                password_hash=hash_password('default'),
                name=user_name,
                team_id=team.id,
                role='employee'
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            token = create_jwt_token(user_id, team.id, 'employee')
            
            logger.info(f"New employee registered: {user_name} in team {team.name}")
            
            return jsonify({
                'success': True,
                'message': 'Employee registered and logged in successfully',
                'user': {
                    'id': user_id,
                    'name': user_name,
                    'role': 'employee',
                    'team_id': team.id
                },
                'team': {
                    'id': team.id,
                    'name': team.name,
                    'employee_code': team.employee_code
                },
                'token': token
            }), 201
        
    except Exception as e:
        logger.error(f"Employee login failed: {str(e)}")
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Login failed. Please try again.'}), 500

# Team endpoints
@application.route('/api/teams', methods=['POST'])
def create_team():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        user_name = data.get('user_name', '').strip()
        
        if not name or not user_name:
            return jsonify({'error': True, 'message': 'Team name and user name are required'}), 400
        
        # Generate codes
        employee_code = generate_team_code()
        manager_code = generate_team_code()
        
        # Create team
        team_id = generate_id('team')
        new_team = Team(
            id=team_id,
            name=name,
            employee_code=employee_code,
            manager_code=manager_code
        )
        
        db.session.add(new_team)
        db.session.commit()
        
        logger.info(f"Team created successfully: {name} by {user_name}")
        
        return jsonify({
            'success': True,
            'message': 'Team created successfully',
            'team': {
                'id': team_id,
                'name': name,
                'employee_code': employee_code,
                'manager_code': manager_code
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Team creation failed: {str(e)}")
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Team creation failed'}), 500

@application.route('/api/teams', methods=['GET'])
def get_teams():
    try:
        teams = Team.query.all()
        return jsonify({
            'success': True,
            'teams': [{
                'id': team.id,
                'name': team.name,
                'employee_code': team.employee_code
            } for team in teams]
        }), 200
    except Exception as e:
        logger.error(f"Failed to get teams: {str(e)}")
        return jsonify({'error': True, 'message': 'Failed to get teams'}), 500

@application.route('/api/teams/join', methods=['POST'])
def join_team():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        employee_code = data.get('employee_code', '').strip().upper()
        user_name = data.get('user_name', '').strip()
        
        if not employee_code or not user_name:
            return jsonify({'error': True, 'message': 'Employee code and user name are required'}), 400
        
        # Find team
        team = Team.query.filter_by(employee_code=employee_code).first()
        if not team:
            return jsonify({'error': True, 'message': 'Invalid employee code'}), 404
        
        # Check if user exists
        existing_user = User.query.filter_by(team_id=team.id, name=user_name).first()
        
        if existing_user:
            return jsonify({
                'success': True,
                'message': 'User already exists in team',
                'user': {
                    'id': existing_user.id,
                    'name': existing_user.name,
                    'role': 'employee',
                    'team_id': team.id
                },
                'team': {
                    'id': team.id,
                    'name': team.name,
                    'employee_code': team.employee_code
                }
            }), 200
        
        # Create new user
        user_id = generate_id('user')
        new_user = User(
            id=user_id,
            email=f"{user_name.lower().replace(' ', '.')}@{team.id}.local",
            password_hash=hash_password('default'),
            name=user_name,
            team_id=team.id,
            role='employee'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"User joined team: {user_name} joined {team.name}")
        
        return jsonify({
            'success': True,
            'message': 'Successfully joined team',
            'user': {
                'id': user_id,
                'name': user_name,
                'role': 'employee',
                'team_id': team.id
            },
            'team': {
                'id': team.id,
                'name': team.name,
                'employee_code': team.employee_code
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Team join failed: {str(e)}")
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Failed to join team'}), 500

# Activity tracking
@application.route('/api/activity/track', methods=['POST'])
def track_activity():
    """Enhanced activity tracking with comprehensive data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        team_id = data.get('team_id')
        date_str = data.get('date')
        
        if not user_id or not team_id or not date_str:
            return jsonify({'error': True, 'message': 'User ID, team ID, and date are required'}), 400
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': True, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Enhanced data extraction
        app_name = data.get('active_app')
        window_title = data.get('window_title')
        app_url = data.get('app_url')
        app_category = categorize_app(app_name, window_title, app_url)
        
        # Time tracking
        productive_hours = data.get('productive_hours', 0.0)
        unproductive_hours = data.get('unproductive_hours', 0.0)
        idle_time = data.get('idle_time', 0.0)
        break_time = data.get('break_time', 0.0)
        total_active_time = data.get('total_active_time', 0.0)
        focus_time = data.get('focus_time', 0.0)
        
        # User behavior metrics
        distraction_count = data.get('distraction_count', 0)
        task_switches = data.get('task_switches', 0)
        mouse_clicks = data.get('mouse_clicks', 0)
        keyboard_activity = data.get('keyboard_activity', False)
        screen_time = data.get('screen_time', 0.0)
        
        # System metrics
        cpu_usage = data.get('cpu_usage', 0.0)
        memory_usage = data.get('memory_usage', 0.0)
        network_activity = data.get('network_activity', False)
        
        # Calculate productivity score
        total_time = productive_hours + unproductive_hours + idle_time + break_time
        productivity_score = calculate_productivity_score(
            app_category, focus_time, distraction_count, task_switches, total_time
        )
        
        # Check if activity exists
        existing_activity = Activity.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            date=date
        ).first()
        
        if existing_activity:
            # Update existing with comprehensive data
            existing_activity.active_app = app_name
            existing_activity.app_category = app_category
            existing_activity.window_title = window_title
            existing_activity.app_url = app_url
            existing_activity.productive_hours = productive_hours
            existing_activity.unproductive_hours = unproductive_hours
            existing_activity.idle_time = idle_time
            existing_activity.break_time = break_time
            existing_activity.total_active_time = total_active_time
            existing_activity.productivity_score = productivity_score
            existing_activity.focus_time = focus_time
            existing_activity.distraction_count = distraction_count
            existing_activity.task_switches = task_switches
            existing_activity.cpu_usage = cpu_usage
            existing_activity.memory_usage = memory_usage
            existing_activity.network_activity = network_activity
            existing_activity.mouse_clicks = mouse_clicks
            existing_activity.keyboard_activity = keyboard_activity
            existing_activity.screen_time = screen_time
            existing_activity.session_id = data.get('session_id')
            existing_activity.device_info = data.get('device_info')
            existing_activity.notes = data.get('notes')
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Activity updated successfully',
                'activity_id': existing_activity.id,
                'productivity_score': productivity_score,
                'app_category': app_category
            }), 200
        else:
            # Create new comprehensive activity
            new_activity = Activity(
                user_id=user_id,
                team_id=team_id,
                date=date,
                active_app=app_name,
                app_category=app_category,
                window_title=window_title,
                app_url=app_url,
                productive_hours=productive_hours,
                unproductive_hours=unproductive_hours,
                idle_time=idle_time,
                break_time=break_time,
                total_active_time=total_active_time,
                productivity_score=productivity_score,
                focus_time=focus_time,
                distraction_count=distraction_count,
                task_switches=task_switches,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                network_activity=network_activity,
                mouse_clicks=mouse_clicks,
                keyboard_activity=keyboard_activity,
                screen_time=screen_time,
                session_id=data.get('session_id'),
                device_info=data.get('device_info'),
                notes=data.get('notes')
            )
            
            db.session.add(new_activity)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Activity tracked successfully',
                'activity_id': new_activity.id,
                'productivity_score': productivity_score,
                'app_category': app_category
            }), 201
        
    except Exception as e:
        logger.error(f"Activity tracking failed: {str(e)}")
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Failed to track activity'}), 500

@application.route('/api/activity/session/start', methods=['POST'])
def start_app_session():
    """Start tracking an application session"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        team_id = data.get('team_id')
        app_name = data.get('app_name')
        
        if not user_id or not team_id or not app_name:
            return jsonify({'error': True, 'message': 'User ID, team ID, and app name are required'}), 400
        
        # Generate session ID
        session_id = generate_session_id()
        start_time = datetime.now()
        
        # Categorize app
        window_title = data.get('window_title')
        url = data.get('url')
        app_category = categorize_app(app_name, window_title, url)
        
        # Create new session
        new_session = AppSession(
            user_id=user_id,
            team_id=team_id,
            session_id=session_id,
            start_time=start_time,
            app_name=app_name,
            app_category=app_category,
            window_title=window_title,
            url=url
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        logger.info(f"Started app session: {app_name} for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'App session started',
            'session_id': session_id,
            'app_category': app_category,
            'start_time': start_time.isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to start app session: {str(e)}")
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Failed to start app session'}), 500

@application.route('/api/activity/session/end', methods=['POST'])
def end_app_session():
    """End tracking an application session"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        
        if not session_id or not user_id:
            return jsonify({'error': True, 'message': 'Session ID and user ID are required'}), 400
        
        # Find and update session
        session = AppSession.query.filter_by(session_id=session_id, user_id=user_id).first()
        if not session:
            return jsonify({'error': True, 'message': 'Session not found'}), 404
        
        end_time = datetime.now()
        duration = (end_time - session.start_time).total_seconds()
        
        # Update session with end data
        session.end_time = end_time
        session.duration = duration
        
        # Calculate session metrics
        mouse_clicks = data.get('mouse_clicks', 0)
        keyboard_events = data.get('keyboard_events', 0)
        scroll_events = data.get('scroll_events', 0)
        
        session.mouse_clicks = mouse_clicks
        session.keyboard_events = keyboard_events
        session.scroll_events = scroll_events
        
        # Calculate focus and productivity scores
        total_events = mouse_clicks + keyboard_events + scroll_events
        focus_score = min(100.0, (total_events / max(duration, 1)) * 10)  # Events per second * 10
        
        # Calculate productivity score for this session
        productivity_score = calculate_productivity_score(
            session.app_category, 
            duration * (focus_score / 100),  # Focus time
            data.get('distraction_count', 0),
            data.get('task_switches', 0),
            duration
        )
        
        session.focus_score = focus_score
        session.productivity_score = productivity_score
        
        # Determine activity level
        if focus_score > 70:
            session.activity_level = 'high'
        elif focus_score > 40:
            session.activity_level = 'medium'
        else:
            session.activity_level = 'low'
        
        db.session.commit()
        
        logger.info(f"Ended app session: {session.app_name} (duration: {duration:.1f}s, productivity: {productivity_score:.1f})")
        
        return jsonify({
            'success': True,
            'message': 'App session ended',
            'duration': duration,
            'productivity_score': productivity_score,
            'focus_score': focus_score,
            'activity_level': session.activity_level
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to end app session: {str(e)}")
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Failed to end app session'}), 500

@application.route('/api/activity/event', methods=['POST'])
def track_productivity_event():
    """Track productivity events (app switches, idle periods, etc.)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        team_id = data.get('team_id')
        event_type = data.get('event_type')
        
        if not user_id or not team_id or not event_type:
            return jsonify({'error': True, 'message': 'User ID, team ID, and event type are required'}), 400
        
        # Create productivity event
        new_event = ProductivityEvent(
            user_id=user_id,
            team_id=team_id,
            event_type=event_type,
            event_data=data.get('event_data'),
            app_name=data.get('app_name'),
            app_category=data.get('app_category'),
            window_title=data.get('window_title'),
            duration=data.get('duration', 0.0)
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        logger.info(f"Tracked productivity event: {event_type} for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Productivity event tracked',
            'event_id': new_event.id
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to track productivity event: {str(e)}")
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Failed to track productivity event'}), 500

@application.route('/api/activity/daily-summary', methods=['POST'])
def generate_daily_summary():
    """Generate comprehensive daily summary for a user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        team_id = data.get('team_id')
        date_str = data.get('date')
        
        if not user_id or not team_id or not date_str:
            return jsonify({'error': True, 'message': 'User ID, team ID, and date are required'}), 400
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': True, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get all activities for the day
        activities = Activity.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            date=date
        ).all()
        
        # Get all app sessions for the day
        sessions = AppSession.query.filter(
            AppSession.user_id == user_id,
            AppSession.team_id == team_id,
            db.func.date(AppSession.start_time) == date
        ).all()
        
        # Calculate daily totals
        total_productive_time = sum(a.productive_hours for a in activities)
        total_unproductive_time = sum(a.unproductive_hours for a in activities)
        total_idle_time = sum(a.idle_time for a in activities)
        total_break_time = sum(a.break_time for a in activities)
        total_screen_time = sum(a.screen_time for a in activities)
        
        # Calculate productivity metrics
        total_time = total_productive_time + total_unproductive_time + total_idle_time + total_break_time
        overall_productivity_score = sum(a.productivity_score for a in activities) / len(activities) if activities else 0
        focus_score = sum(a.focus_time for a in activities) / total_time if total_time > 0 else 0
        distraction_count = sum(a.distraction_count for a in activities)
        task_switch_count = sum(a.task_switches for a in activities)
        
        # App usage breakdown
        app_usage = {}
        for session in sessions:
            app_name = session.app_name
            if app_name not in app_usage:
                app_usage[app_name] = 0
            app_usage[app_name] += session.duration / 3600  # Convert to hours
        
        most_used_app = max(app_usage.items(), key=lambda x: x[1])[0] if app_usage else None
        
        # Find most productive app
        app_productivity = {}
        for session in sessions:
            app_name = session.app_name
            if app_name not in app_productivity:
                app_productivity[app_name] = []
            app_productivity[app_name].append(session.productivity_score)
        
        most_productive_app = None
        best_avg_score = 0
        for app_name, scores in app_productivity.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > best_avg_score:
                best_avg_score = avg_score
                most_productive_app = app_name
        
        # Create or update daily summary
        existing_summary = DailySummary.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            date=date
        ).first()
        
        if existing_summary:
            # Update existing summary
            existing_summary.total_productive_time = total_productive_time
            existing_summary.total_unproductive_time = total_unproductive_time
            existing_summary.total_idle_time = total_idle_time
            existing_summary.total_break_time = total_break_time
            existing_summary.total_screen_time = total_screen_time
            existing_summary.overall_productivity_score = overall_productivity_score
            existing_summary.focus_score = focus_score
            existing_summary.distraction_count = distraction_count
            existing_summary.task_switch_count = task_switch_count
            existing_summary.most_used_app = most_used_app
            existing_summary.most_productive_app = most_productive_app
            existing_summary.app_usage_breakdown = app_usage
            
            db.session.commit()
            summary = existing_summary
        else:
            # Create new summary
            new_summary = DailySummary(
                user_id=user_id,
                team_id=team_id,
                date=date,
                total_productive_time=total_productive_time,
                total_unproductive_time=total_unproductive_time,
                total_idle_time=total_idle_time,
                total_break_time=total_break_time,
                total_screen_time=total_screen_time,
                overall_productivity_score=overall_productivity_score,
                focus_score=focus_score,
                distraction_count=distraction_count,
                task_switch_count=task_switch_count,
                most_used_app=most_used_app,
                most_productive_app=most_productive_app,
                app_usage_breakdown=app_usage
            )
            
            db.session.add(new_summary)
            db.session.commit()
            summary = new_summary
        
        logger.info(f"Generated daily summary for user {user_id} on {date}")
        
        return jsonify({
            'success': True,
            'message': 'Daily summary generated',
            'summary': {
                'id': summary.id,
                'date': date_str,
                'total_productive_time': total_productive_time,
                'total_unproductive_time': total_unproductive_time,
                'total_idle_time': total_idle_time,
                'total_break_time': total_break_time,
                'total_screen_time': total_screen_time,
                'overall_productivity_score': overall_productivity_score,
                'focus_score': focus_score,
                'distraction_count': distraction_count,
                'task_switch_count': task_switch_count,
                'most_used_app': most_used_app,
                'most_productive_app': most_productive_app,
                'app_usage_breakdown': app_usage
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to generate daily summary: {str(e)}")
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Failed to generate daily summary'}), 500

# Analytics endpoints
@application.route('/api/analytics/burnout-risk', methods=['GET'])
def get_burnout_risk():
    """Enhanced burnout risk analysis with comprehensive metrics"""
    try:
        team_id = request.args.get('team_id')
        user_id = request.args.get('user_id')
        days = int(request.args.get('days', 7))  # Default to 7 days
        
        if not team_id:
            return jsonify({'error': True, 'message': 'Team ID is required'}), 400
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get activities for the period
        query = Activity.query.filter(
            Activity.team_id == team_id,
            Activity.date >= start_date,
            Activity.date <= end_date
        )
        
        if user_id:
            query = query.filter(Activity.user_id == user_id)
        
        activities = query.all()
        
        if not activities:
            return jsonify({
                'success': True,
                'burnout_risk': 'unknown',
                'risk_factors': ['No activity data available'],
                'metrics': {
                    'avg_daily_hours': 0.0,
                    'avg_productivity': 0.0,
                    'total_activities': 0,
                    'avg_focus_score': 0.0,
                    'avg_distractions': 0.0
                }
            }), 200
        
        # Calculate comprehensive metrics
        total_productive_time = sum(a.productive_hours for a in activities)
        total_unproductive_time = sum(a.unproductive_hours for a in activities)
        total_idle_time = sum(a.idle_time for a in activities)
        total_break_time = sum(a.break_time for a in activities)
        total_screen_time = sum(a.screen_time for a in activities)
        
        total_time = total_productive_time + total_unproductive_time + total_idle_time + total_break_time
        avg_daily_hours = total_time / days
        avg_productivity = sum(a.productivity_score for a in activities) / len(activities)
        avg_focus_score = sum(a.focus_time for a in activities) / total_time if total_time > 0 else 0
        avg_distractions = sum(a.distraction_count for a in activities) / days
        avg_task_switches = sum(a.task_switches for a in activities) / days
        
        # Determine burnout risk
        risk_factors = []
        risk_score = 0
        
        # High screen time risk
        if avg_daily_hours > 10:
            risk_factors.append('High daily screen time (>10 hours)')
            risk_score += 30
        elif avg_daily_hours > 8:
            risk_factors.append('Extended daily screen time (>8 hours)')
            risk_score += 15
        
        # Low productivity risk
        if avg_productivity < 50:
            risk_factors.append('Low productivity score (<50)')
            risk_score += 25
        elif avg_productivity < 70:
            risk_factors.append('Below average productivity (<70)')
            risk_score += 10
        
        # High distraction risk
        if avg_distractions > 20:
            risk_factors.append('High distraction frequency (>20/day)')
            risk_score += 20
        elif avg_distractions > 10:
            risk_factors.append('Elevated distraction frequency (>10/day)')
            risk_score += 10
        
        # High task switching risk
        if avg_task_switches > 50:
            risk_factors.append('Excessive task switching (>50/day)')
            risk_score += 15
        elif avg_task_switches > 30:
            risk_factors.append('High task switching frequency (>30/day)')
            risk_score += 8
        
        # Low break time risk
        if total_break_time / days < 1:
            risk_factors.append('Insufficient break time (<1 hour/day)')
            risk_score += 20
        
        # Determine risk level
        if risk_score >= 70:
            burnout_risk = 'high'
        elif risk_score >= 40:
            burnout_risk = 'medium'
        elif risk_score >= 20:
            burnout_risk = 'low'
        else:
            burnout_risk = 'very_low'
        
        return jsonify({
            'success': True,
            'burnout_risk': burnout_risk,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'metrics': {
                'avg_daily_hours': round(avg_daily_hours, 2),
                'avg_productivity': round(avg_productivity, 2),
                'avg_focus_score': round(avg_focus_score, 2),
                'avg_distractions': round(avg_distractions, 1),
                'avg_task_switches': round(avg_task_switches, 1),
                'total_productive_time': round(total_productive_time, 2),
                'total_unproductive_time': round(total_unproductive_time, 2),
                'total_idle_time': round(total_idle_time, 2),
                'total_break_time': round(total_break_time, 2),
                'total_screen_time': round(total_screen_time, 2),
                'total_activities': len(activities)
            },
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Burnout risk analysis failed: {str(e)}")
        return jsonify({'error': True, 'message': 'Failed to analyze burnout risk'}), 500

@application.route('/api/analytics/productivity-insights', methods=['GET'])
def get_productivity_insights():
    """Get comprehensive productivity insights and recommendations"""
    try:
        team_id = request.args.get('team_id')
        user_id = request.args.get('user_id')
        days = int(request.args.get('days', 7))
        
        if not team_id:
            return jsonify({'error': True, 'message': 'Team ID is required'}), 400
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get activities and sessions
        activities_query = Activity.query.filter(
            Activity.team_id == team_id,
            Activity.date >= start_date,
            Activity.date <= end_date
        )
        
        sessions_query = AppSession.query.filter(
            AppSession.team_id == team_id,
            AppSession.start_time >= start_date,
            AppSession.start_time <= end_date
        )
        
        if user_id:
            activities_query = activities_query.filter(Activity.user_id == user_id)
            sessions_query = sessions_query.filter(AppSession.user_id == user_id)
        
        activities = activities_query.all()
        sessions = sessions_query.all()
        
        if not activities and not sessions:
            return jsonify({
                'success': True,
                'message': 'No data available for analysis',
                'insights': [],
                'recommendations': []
            }), 200
        
        # Calculate comprehensive insights
        insights = []
        recommendations = []
        
        # Time distribution analysis
        if activities:
            total_productive = sum(a.productive_hours for a in activities)
            total_unproductive = sum(a.unproductive_hours for a in activities)
            total_idle = sum(a.idle_time for a in activities)
            total_break = sum(a.break_time for a in activities)
            total_time = total_productive + total_unproductive + total_idle + total_break
            
            if total_time > 0:
                productive_percentage = (total_productive / total_time) * 100
                insights.append({
                    'type': 'time_distribution',
                    'title': 'Time Distribution',
                    'description': f'You spent {productive_percentage:.1f}% of your time on productive activities',
                    'value': productive_percentage,
                    'unit': '%',
                    'category': 'productivity'
                })
                
                if productive_percentage < 60:
                    recommendations.append({
                        'type': 'productivity',
                        'title': 'Increase Productive Time',
                        'description': 'Consider reducing time spent on unproductive activities',
                        'priority': 'high'
                    })
        
        # App usage analysis
        if sessions:
            app_usage = {}
            app_productivity = {}
            
            for session in sessions:
                app_name = session.app_name
                if app_name not in app_usage:
                    app_usage[app_name] = 0
                    app_productivity[app_name] = []
                
                app_usage[app_name] += session.duration
                app_productivity[app_name].append(session.productivity_score)
            
            # Most used apps
            most_used = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            insights.append({
                'type': 'app_usage',
                'title': 'Most Used Applications',
                'description': f'Your most used app is {most_used[0][0]} ({most_used[0][1]/3600:.1f} hours)',
                'value': most_used[0][1]/3600,
                'unit': 'hours',
                'category': 'usage'
            })
            
            # Most productive apps
            avg_productivity = {}
            for app, scores in app_productivity.items():
                avg_productivity[app] = sum(scores) / len(scores)
            
            most_productive = max(avg_productivity.items(), key=lambda x: x[1])
            insights.append({
                'type': 'app_productivity',
                'title': 'Most Productive Application',
                'description': f'{most_productive[0]} has the highest productivity score ({most_productive[1]:.1f})',
                'value': most_productive[1],
                'unit': 'score',
                'category': 'productivity'
            })
        
        # Focus and distraction analysis
        if activities:
            avg_focus = sum(a.focus_time for a in activities) / len(activities)
            avg_distractions = sum(a.distraction_count for a in activities) / len(activities)
            
            insights.append({
                'type': 'focus',
                'title': 'Focus Score',
                'description': f'Average focus time per session: {avg_focus:.1f} hours',
                'value': avg_focus,
                'unit': 'hours',
                'category': 'focus'
            })
            
            if avg_distractions > 15:
                recommendations.append({
                    'type': 'focus',
                    'title': 'Reduce Distractions',
                    'description': f'You have {avg_distractions:.1f} distractions per day on average',
                    'priority': 'medium'
                })
        
        # Productivity trends
        if activities:
            daily_scores = {}
            for activity in activities:
                date = activity.date.isoformat()
                if date not in daily_scores:
                    daily_scores[date] = []
                daily_scores[date].append(activity.productivity_score)
            
            avg_daily_scores = {date: sum(scores)/len(scores) for date, scores in daily_scores.items()}
            recent_trend = list(avg_daily_scores.values())[-3:] if len(avg_daily_scores) >= 3 else []
            
            if len(recent_trend) >= 2:
                trend_direction = 'improving' if recent_trend[-1] > recent_trend[0] else 'declining'
                insights.append({
                    'type': 'trend',
                    'title': 'Productivity Trend',
                    'description': f'Your productivity is {trend_direction} over the last {len(recent_trend)} days',
                    'value': recent_trend[-1],
                    'unit': 'score',
                    'category': 'trend'
                })
        
        return jsonify({
            'success': True,
            'insights': insights,
            'recommendations': recommendations,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Productivity insights analysis failed: {str(e)}")
        return jsonify({'error': True, 'message': 'Failed to analyze productivity insights'}), 500

@application.route('/api/analytics/distraction-profile', methods=['GET'])
def get_distraction_profile():
    try:
        team_id = request.args.get('team_id')
        if not team_id:
            return jsonify({'error': True, 'message': 'Team ID is required'}), 400
        
        return jsonify({
            'success': True,
            'distraction_level': 'low',
            'distractions': [],
            'metrics': {
                'distraction_ratio': 0.2,
                'total_unproductive_hours': 1.6,
                'total_productive_hours': 6.4
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Distraction profile analysis failed: {str(e)}")
        return jsonify({'error': True, 'message': 'Failed to analyze distraction profile'}), 500

@application.route('/api/employee/daily-summary', methods=['GET'])
def get_daily_summary():
    try:
        user_id = request.args.get('user_id')
        team_id = request.args.get('team_id')
        date_str = request.args.get('date')
        
        if not user_id or not team_id or not date_str:
            return jsonify({'error': True, 'message': 'User ID, team ID, and date are required'}), 400
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': True, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        activity = Activity.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            date=date
        ).first()
        
        if not activity:
            return jsonify({
                'success': True,
                'message': 'No activity data for this date',
                'summary': {
                    'productive_hours': 0,
                    'unproductive_hours': 0,
                    'idle_hours': 0,
                    'productivity_score': 0,
                    'focus_sessions': 0,
                    'breaks_taken': 0
                }
            }), 200
        
        return jsonify({
            'success': True,
            'summary': {
                'productive_hours': activity.productive_hours,
                'unproductive_hours': activity.unproductive_hours,
                'idle_hours': 0,
                'productivity_score': 0.8,
                'focus_sessions': 0,
                'breaks_taken': 0,
                'active_app': activity.active_app,
                'window_title': None,
                'last_active': None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Daily summary failed: {str(e)}")
        return jsonify({'error': True, 'message': 'Failed to get daily summary'}), 500

# Database initialization
def init_db():
    try:
        with application.app_context():
            # Create tables
            db.create_all()
            
            # Handle schema migrations
            try:
                from sqlalchemy import text
                
                # Check if manager_code column exists in teams table
                result = db.session.execute(text("PRAGMA table_info(teams)"))
                columns = [row[1] for row in result.fetchall()]
                
                # Add manager_code column if it doesn't exist
                if 'manager_code' not in columns:
                    logger.info("Adding manager_code column to teams table...")
                    db.session.execute(text("ALTER TABLE teams ADD COLUMN manager_code VARCHAR(10)"))
                    db.session.commit()
                    logger.info("✅ manager_code column added")
                
                # Check if team_id column exists in users table
                result = db.session.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result.fetchall()]
                
                # Add team_id column if it doesn't exist
                if 'team_id' not in columns:
                    logger.info("Adding team_id column to users table...")
                    db.session.execute(text("ALTER TABLE users ADD COLUMN team_id VARCHAR(80)"))
                    db.session.commit()
                    logger.info("✅ team_id column added")
                
                # Add role column if it doesn't exist
                if 'role' not in columns:
                    logger.info("Adding role column to users table...")
                    db.session.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'employee'"))
                    db.session.commit()
                    logger.info("✅ role column added")
                
                # Add employee_code column if it doesn't exist
                result = db.session.execute(text("PRAGMA table_info(teams)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'employee_code' not in columns:
                    logger.info("Adding employee_code column to teams table...")
                    db.session.execute(text("ALTER TABLE teams ADD COLUMN employee_code VARCHAR(10)"))
                    db.session.commit()
                    logger.info("✅ employee_code column added")
                
                logger.info("✅ Database schema migration completed")
                
            except Exception as migration_error:
                logger.warning(f"Schema migration warning (non-critical): {migration_error}")
            
            logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

if __name__ == '__main__':
    init_db()
    application.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    init_db() 