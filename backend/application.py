#!/usr/bin/env python3
"""
ProductivityFlow Backend - Minimal Working Version
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import bcrypt
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
application = Flask(__name__)

# Basic configuration
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
application.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Convert psycopg2 URL to psycopg3 URL if needed
    if DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://')
    
    # Try to use PostgreSQL, fallback to SQLite if there are issues
    try:
        application.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        logger.info("✅ Using PostgreSQL database")
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL connection failed: {e}")
        logger.warning("⚠️ Falling back to SQLite database")
        application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivityflow.db'
        application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivityflow.db'
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.info("⚠️ Using SQLite database (development mode)")

# Initialize extensions
db = SQLAlchemy(application)
CORS(application)

# Models
class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    employee_code = db.Column(db.String(10), unique=True, nullable=False)
    manager_id = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    team_id = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    active_app = db.Column(db.String(255), nullable=True)
    productive_hours = db.Column(db.Float, default=0.0)
    unproductive_hours = db.Column(db.Float, default=0.0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

# Utility functions
def generate_id(prefix):
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{timestamp}_{random_suffix}"

def generate_team_code():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_jwt_token(user_id, team_id, role):
    payload = {
        'user_id': user_id,
        'team_id': team_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, application.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except:
        return None

# Routes
@application.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "disconnected"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(datetime.UTC).isoformat(),
        'database': db_status
    })

@application.route('/api/auth/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not all([email, password, name]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        password_hash = hash_password(password)
        user_id = generate_id('user')
        
        new_user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            name=name
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@application.route('/api/auth/login', methods=['POST'])
def login_user():
    """Login user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not verify_password(password, user.password_hash):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = create_jwt_token(user.id, '', 'user')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@application.route('/api/teams', methods=['POST'])
def create_team():
    """Create a new team"""
    try:
        data = request.get_json()
        name = data.get('name')
        manager_id = data.get('manager_id')
        
        if not name:
            return jsonify({'error': 'Team name is required'}), 400
        
        team_id = generate_id('team')
        employee_code = generate_team_code()
        
        new_team = Team(
            id=team_id,
            name=name,
            employee_code=employee_code,
            manager_id=manager_id
        )
        
        db.session.add(new_team)
        db.session.commit()
        
        return jsonify({
            'message': 'Team created successfully',
            'team': {
                'id': team_id,
                'name': name,
                'employee_code': employee_code
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Team creation error: {e}")
        return jsonify({'error': 'Team creation failed'}), 500

@application.route('/api/teams', methods=['GET'])
def get_teams():
    """Get all teams"""
    try:
        teams = Team.query.all()
        return jsonify({
            'teams': [
                {
                    'id': team.id,
                    'name': team.name,
                    'employee_code': team.employee_code,
                    'created_at': team.created_at.isoformat()
                }
                for team in teams
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Get teams error: {e}")
        return jsonify({'error': 'Failed to get teams'}), 500

@application.route('/api/activity/track', methods=['POST'])
def track_activity():
    """Track user activity"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        team_id = data.get('team_id')
        active_app = data.get('active_app')
        productive_hours = data.get('productive_hours', 0.0)
        unproductive_hours = data.get('unproductive_hours', 0.0)
        
        if not all([user_id, team_id]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        new_activity = Activity(
            user_id=user_id,
            team_id=team_id,
            date=datetime.utcnow().date(),
            active_app=active_app,
            productive_hours=productive_hours,
            unproductive_hours=unproductive_hours
        )
        
        db.session.add(new_activity)
        db.session.commit()
        
        return jsonify({
            'message': 'Activity tracked successfully',
            'activity_id': new_activity.id
        }), 201
        
    except Exception as e:
        logger.error(f"Activity tracking error: {e}")
        return jsonify({'error': 'Activity tracking failed'}), 500

@application.route('/api/teams/join', methods=['POST'])
def join_team():
    """Join a team with employee code"""
    try:
        data = request.get_json()
        employee_code = data.get('employee_code')
        user_name = data.get('user_name')
        
        if not all([employee_code, user_name]):
            return jsonify({'error': 'Employee code and user name required'}), 400
        
        team = Team.query.filter_by(employee_code=employee_code).first()
        if not team:
            return jsonify({'error': 'Invalid employee code'}), 404
        
        # Create user if doesn't exist
        user_id = generate_id('user')
        new_user = User(
            id=user_id,
            email=f"{user_name.lower().replace(' ', '.')}@{team.id}.local",
            password_hash=hash_password('default123'),
            name=user_name
        )
        db.session.add(new_user)
        db.session.commit()
        
        token = create_jwt_token(user_id, team.id, 'employee')
        
        return jsonify({
            'message': 'Successfully joined team',
            'token': token,
            'team': {
                'id': team.id,
                'name': team.name
            },
            'user': {
                'id': user_id,
                'name': user_name
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Join team error: {e}")
        return jsonify({'error': 'Failed to join team'}), 500

@application.route('/api/teams/<team_id>/members', methods=['GET'])
def get_team_members(team_id):
    """Get team members"""
    try:
        # Mock team members data
        members = [
            {
                'userId': 'user_1',
                'name': 'John Doe',
                'role': 'employee',
                'department': 'Engineering',
                'productiveHours': 8.5,
                'unproductiveHours': 1.2,
                'totalHours': 9.7,
                'productivityScore': 85,
                'lastActive': datetime.utcnow().isoformat(),
                'status': 'online',
                'isOnline': True,
                'focusSessions': 3,
                'breaksTaken': 2,
                'weeklyAverage': 85,
                'monthlyAverage': 82
            },
            {
                'userId': 'user_2',
                'name': 'Jane Smith',
                'role': 'manager',
                'department': 'Management',
                'productiveHours': 9.2,
                'unproductiveHours': 0.8,
                'totalHours': 10.0,
                'productivityScore': 92,
                'lastActive': datetime.utcnow().isoformat(),
                'status': 'online',
                'isOnline': True,
                'focusSessions': 4,
                'breaksTaken': 3,
                'weeklyAverage': 88,
                'monthlyAverage': 85
            }
        ]
        
        return jsonify({'members': members}), 200
        
    except Exception as e:
        logger.error(f"Get team members error: {e}")
        return jsonify({'error': 'Failed to get team members'}), 500

@application.route('/api/analytics/burnout-risk', methods=['GET'])
def get_burnout_risk():
    """Get burnout risk analysis"""
    try:
        # Mock burnout risk data
        burnout_data = {
            'overall_risk': 'low',
            'risk_score': 25,
            'factors': [
                {
                    'factor': 'Work Hours',
                    'risk': 'low',
                    'score': 20,
                    'description': 'Working reasonable hours'
                },
                {
                    'factor': 'Break Frequency',
                    'risk': 'medium',
                    'score': 45,
                    'description': 'Taking adequate breaks'
                },
                {
                    'factor': 'Focus Sessions',
                    'risk': 'low',
                    'score': 15,
                    'description': 'Good focus session management'
                }
            ],
            'recommendations': [
                'Continue taking regular breaks',
                'Maintain current work schedule',
                'Consider implementing focus blocks'
            ]
        }
        
        return jsonify(burnout_data), 200
        
    except Exception as e:
        logger.error(f"Burnout risk error: {e}")
        return jsonify({'error': 'Failed to get burnout risk'}), 500

@application.route('/api/analytics/distraction-profile', methods=['GET'])
def get_distraction_profile():
    """Get distraction profile analysis"""
    try:
        # Mock distraction profile data
        distraction_data = {
            'overall_score': 75,
            'category': 'moderate',
            'breakdown': {
                'social_media': 30,
                'email': 25,
                'meetings': 20,
                'other': 25
            },
            'trends': [
                {'day': 'Monday', 'score': 70},
                {'day': 'Tuesday', 'score': 75},
                {'day': 'Wednesday', 'score': 80},
                {'day': 'Thursday', 'score': 72},
                {'day': 'Friday', 'score': 68}
            ],
            'recommendations': [
                'Limit social media usage during work hours',
                'Batch email checking to specific times',
                'Reduce unnecessary meetings'
            ]
        }
        
        return jsonify(distraction_data), 200
        
    except Exception as e:
        logger.error(f"Distraction profile error: {e}")
        return jsonify({'error': 'Failed to get distraction profile'}), 500

@application.route('/api/subscription/status', methods=['GET'])
def get_subscription_status():
    """Get subscription status"""
    try:
        # Mock subscription data
        status_data = {
            'status': 'active',
            'employee_count': 5,
            'monthly_cost': 49.95,
            'current_period_start': datetime.utcnow().isoformat(),
            'current_period_end': (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        return jsonify(status_data), 200
        
    except Exception as e:
        logger.error(f"Subscription status error: {e}")
        return jsonify({'error': 'Failed to get subscription status'}), 500

@application.route('/api/teams/<team_id>/tasks', methods=['GET'])
def get_team_tasks(team_id):
    """Get team tasks"""
    try:
        # Mock tasks data
        tasks = [
            {
                'id': 1,
                'title': 'Complete frontend dashboard',
                'description': 'Finish the manager dashboard UI',
                'assignedTo': 'user_1',
                'assignedToName': 'John Doe',
                'assignedBy': 'user_2',
                'assignedByName': 'Jane Smith',
                'status': 'in_progress',
                'priority': 'high',
                'dueDate': (datetime.utcnow() + timedelta(days=3)).isoformat(),
                'createdAt': datetime.utcnow().isoformat(),
                'updatedAt': datetime.utcnow().isoformat(),
                'estimatedHours': 8,
                'actualHours': 6,
                'tags': ['urgent', 'frontend'],
                'comments': []
            },
            {
                'id': 2,
                'title': 'Backend API testing',
                'description': 'Test all API endpoints',
                'assignedTo': 'user_2',
                'assignedToName': 'Jane Smith',
                'assignedBy': 'user_1',
                'assignedByName': 'John Doe',
                'status': 'pending',
                'priority': 'medium',
                'dueDate': (datetime.utcnow() + timedelta(days=5)).isoformat(),
                'createdAt': datetime.utcnow().isoformat(),
                'updatedAt': datetime.utcnow().isoformat(),
                'estimatedHours': 4,
                'actualHours': 0,
                'tags': ['testing', 'backend'],
                'comments': []
            }
        ]
        
        return jsonify({'tasks': tasks}), 200
        
    except Exception as e:
        logger.error(f"Get team tasks error: {e}")
        return jsonify({'error': 'Failed to get team tasks'}), 500

@application.route('/api/teams/<team_id>/analytics', methods=['GET'])
def get_team_analytics(team_id):
    """Get team analytics"""
    try:
        # Mock analytics data
        analytics_data = {
            'team_id': team_id,
            'total_members': 5,
            'active_members': 4,
            'total_productive_hours': 120.5,
            'total_unproductive_hours': 15.2,
            'average_productivity': 85.2,
            'weekly_trend': [
                {'day': 'Monday', 'productive': 8.5, 'unproductive': 1.2},
                {'day': 'Tuesday', 'productive': 9.2, 'unproductive': 0.8},
                {'day': 'Wednesday', 'productive': 7.8, 'unproductive': 1.5},
                {'day': 'Thursday', 'productive': 8.9, 'unproductive': 1.1},
                {'day': 'Friday', 'productive': 7.1, 'unproductive': 1.8}
            ],
            'top_performers': [
                {'name': 'John Doe', 'productivity': 92, 'hours': 9.5},
                {'name': 'Jane Smith', 'productivity': 88, 'hours': 8.8},
                {'name': 'Mike Johnson', 'productivity': 85, 'hours': 8.2}
            ],
            'productivity_distribution': {
                'high': 3,
                'medium': 5,
                'low': 2
            }
        }
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        logger.error(f"Get team analytics error: {e}")
        return jsonify({'error': 'Failed to get team analytics'}), 500

@application.route('/api/teams/<team_id>/members/realtime', methods=['GET'])
def get_realtime_members(team_id):
    """Get real-time team member status"""
    try:
        # Mock realtime members data
        realtime_members = [
            {
                'userId': 'user_1',
                'name': 'John Doe',
                'role': 'employee',
                'isOnline': True,
                'status': 'online',
                'lastActive': datetime.utcnow().isoformat(),
                'currentActivity': 'VS Code',
                'productiveHours': 8.5,
                'unproductiveHours': 1.2
            },
            {
                'userId': 'user_2',
                'name': 'Jane Smith',
                'role': 'manager',
                'isOnline': True,
                'status': 'online',
                'lastActive': datetime.utcnow().isoformat(),
                'currentActivity': 'Slack',
                'productiveHours': 9.2,
                'unproductiveHours': 0.8
            }
        ]
        
        return jsonify({'members': realtime_members}), 200
        
    except Exception as e:
        logger.error(f"Get realtime members error: {e}")
        return jsonify({'error': 'Failed to get realtime members'}), 500

@application.route('/api/employee/daily-summary', methods=['GET'])
def get_daily_summary():
    """Get employee daily summary"""
    try:
        # Mock daily summary data
        summary = {
            'total_hours': 9.7,
            'productive_hours': 8.5,
            'unproductive_hours': 1.2,
            'productivity_score': 87.6,
            'focus_sessions': 3,
            'breaks_taken': 2,
            'apps_used': 8,
            'websites_visited': 12
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Get daily summary error: {e}")
        return jsonify({'error': 'Failed to get daily summary'}), 500

# Initialize database
def init_db():
    """Initialize the database"""
    try:
        with application.app_context():
            db.create_all()
            logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

if __name__ == '__main__':
    logger.info("🚀 Starting Minimal ProductivityFlow Backend")
    
    # Initialize database
    init_db()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Start the application
    application.run(
        host='0.0.0.0',
        port=port,
        debug=False
    ) 