#!/usr/bin/env python3
"""
ProductivityFlow Backend - Fixed Version
Handles database schema issues and removes email verification
"""

import os
import sys
import logging
from datetime import datetime, timedelta, timezone
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

# Enhanced CORS Configuration for desktop apps
CORS(application, 
     origins=["http://localhost:1420", "http://localhost:1421", "http://localhost:3000", 
              "tauri://localhost", "https://tauri.localhost", "*"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", 
                   "Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers",
                   "Cache-Control", "Pragma"],
     supports_credentials=True,
     expose_headers=["Content-Length", "X-JSON", "Authorization"],
     max_age=86400)

# Enhanced preflight OPTIONS handler for all routes
@application.before_request
def handle_preflight():
    """Handle all CORS preflight requests globally"""
    if request.method == "OPTIONS":
        response = jsonify({
            'status': 'OK', 
            'message': 'CORS preflight successful',
            'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'],
            'allowed_origins': '*'
        })
        
        # Set comprehensive CORS headers
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add('Access-Control-Allow-Headers', 
                           "Content-Type,Authorization,X-Requested-With,Accept,Origin," +
                           "Access-Control-Request-Method,Access-Control-Request-Headers," +
                           "Cache-Control,Pragma")
        response.headers.add('Access-Control-Allow-Methods', 
                           "GET,PUT,POST,DELETE,OPTIONS,PATCH,HEAD")
        response.headers.add('Access-Control-Max-Age', "86400")
        response.status_code = 200
        return response

# Add comprehensive CORS headers to all responses
@application.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    origin = request.headers.get('Origin')
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', '*')
    
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 
                        'Content-Type,Authorization,X-Requested-With,Accept,Origin,' +
                        'Cache-Control,Pragma')
    response.headers.add('Access-Control-Allow-Methods', 
                        'GET,PUT,POST,DELETE,OPTIONS,PATCH,HEAD')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Length,X-JSON,Authorization')
    
    # Prevent caching of API responses unless explicitly set
    if not response.headers.get('Cache-Control'):
        response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
        response.headers.add('Pragma', 'no-cache')
        response.headers.add('Expires', '0')
    
    return response

# Models - Fixed to handle missing columns
class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    employee_code = db.Column(db.String(10), unique=True, nullable=False)
    # Make created_at optional to handle existing databases
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    # Make created_at optional to handle existing databases
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

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
        'timestamp': datetime.now(timezone.utc).isoformat(),
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
            return jsonify({'error': 'User with this email already exists'}), 409
        
        password_hash = hash_password(password)
        user_id = generate_id('user')
        
        new_user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            name=name,
            created_at=datetime.utcnow()
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
    """Login user - No email verification required"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not verify_password(password, user.password_hash):
            return jsonify({'error': 'Invalid email or password'}), 401
        
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

@application.route('/api/auth/employee-login', methods=['POST'])
def employee_login():
    """Employee login with email and password"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not verify_password(password, user.password_hash):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Find the team this user belongs to (for employees created via join team)
        # For now, we'll use a default team or create a mock response
        team_id = 'default_team'
        team_name = 'Default Team'
        
        # Try to find team by user's email domain
        if '@' in user.email and '.local' in user.email:
            team_id_from_email = user.email.split('@')[1].replace('.local', '')
            team = Team.query.filter_by(id=team_id_from_email).first()
            if team:
                team_id = team.id
                team_name = team.name
        
        token = create_jwt_token(user.id, team_id, 'employee')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'team_id': team_id,
                'team_name': team_name,
                'role': 'employee'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Employee login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@application.route('/api/teams', methods=['POST'])
def create_team():
    """Create a new team"""
    try:
        data = request.get_json()
        team_name = data.get('name', '').strip()
        user_name = data.get('user_name', '').strip()
        
        if not team_name:
            return jsonify({'error': 'Team name is required'}), 400
        
        # Generate unique team ID and employee code
        team_id = generate_id('team')
        employee_code = generate_team_code()
        
        # Create team
        new_team = Team(
            id=team_id,
            name=team_name,
            employee_code=employee_code,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_team)
        db.session.commit()
        
        return jsonify({
            'message': 'Team created successfully',
            'team': {
                'id': team_id,
                'name': team_name,
                'employee_code': employee_code
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Create team error: {e}")
        return jsonify({'error': 'Failed to create team'}), 500

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
                    'created_at': team.created_at.isoformat() if team.created_at else None
                }
                for team in teams
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Get teams error: {e}")
        return jsonify({'error': 'Failed to get teams'}), 500

@application.route('/api/teams/public', methods=['GET'])
def get_public_teams():
    """Get public teams with mock member data for Dashboard"""
    try:
        teams = Team.query.all()
        
        # If no teams exist, create a default team
        if not teams:
            default_team = Team(
                id='default_team',
                name='Default Team',
                employee_code='TEAM001',
                created_at=datetime.utcnow()
            )
            db.session.add(default_team)
            db.session.commit()
            teams = [default_team]
        
        teams_data = []
        for team in teams:
            # Mock team data with members
            mock_members = [
                {
                    'userId': 'user_001',
                    'name': 'John Doe',
                    'role': 'Developer',
                    'department': 'Engineering',
                    'productiveHours': 6.5,
                    'unproductiveHours': 1.5,
                    'totalHours': 8.0,
                    'productivityScore': 85,
                    'lastActive': datetime.utcnow().isoformat(),
                    'status': 'online',
                    'teamName': team.name,
                    'isOnline': True,
                    'currentActivity': 'Coding',
                    'focusSessions': 4,
                    'breaksTaken': 2,
                    'weeklyAverage': 82,
                    'monthlyAverage': 78
                },
                {
                    'userId': 'user_002',
                    'name': 'Jane Smith',
                    'role': 'Designer',
                    'department': 'Design',
                    'productiveHours': 7.0,
                    'unproductiveHours': 1.0,
                    'totalHours': 8.0,
                    'productivityScore': 90,
                    'lastActive': datetime.utcnow().isoformat(),
                    'status': 'online',
                    'teamName': team.name,
                    'isOnline': True,
                    'currentActivity': 'Design Review',
                    'focusSessions': 5,
                    'breaksTaken': 1,
                    'weeklyAverage': 88,
                    'monthlyAverage': 85
                },
                {
                    'userId': 'user_003',
                    'name': 'Mike Johnson',
                    'role': 'Manager',
                    'department': 'Management',
                    'productiveHours': 5.5,
                    'unproductiveHours': 2.5,
                    'totalHours': 8.0,
                    'productivityScore': 70,
                    'lastActive': datetime.utcnow().isoformat(),
                    'status': 'away',
                    'teamName': team.name,
                    'isOnline': False,
                    'currentActivity': 'Meeting',
                    'focusSessions': 3,
                    'breaksTaken': 3,
                    'weeklyAverage': 75,
                    'monthlyAverage': 72
                }
            ]
            
            total_productive = sum(m['productiveHours'] for m in mock_members)
            total_unproductive = sum(m['unproductiveHours'] for m in mock_members)
            avg_productivity = sum(m['productivityScore'] for m in mock_members) / len(mock_members)
            active_members = len([m for m in mock_members if m['isOnline']])
            
            teams_data.append({
                'id': team.id,
                'name': team.name,
                'employee_code': team.employee_code,
                'members': mock_members,
                'totalProductiveHours': total_productive,
                'totalUnproductiveHours': total_unproductive,
                'averageProductivity': round(avg_productivity, 1),
                'activeMembers': active_members,
                'totalMembers': len(mock_members),
                'created_at': team.created_at.isoformat() if team.created_at else None
            })
        
        return jsonify({
            'teams': teams_data
        }), 200
        
    except Exception as e:
        logger.error(f"Get public teams error: {e}")
        return jsonify({'error': 'Failed to get public teams'}), 500

@application.route('/api/teams/join', methods=['POST'])
def join_team():
    """Join a team with employee code - supports both field name formats"""
    try:
        data = request.get_json()
        
        # Support both field name formats for backward compatibility
        employee_code = data.get('employee_code') or data.get('team_code')
        user_name = data.get('user_name') or data.get('employee_name') or data.get('name')
        
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
            name=user_name,
            created_at=datetime.utcnow()
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
                'name': user_name,
                'role': 'employee'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Join team error: {e}")
        return jsonify({'error': 'Failed to join team'}), 500

@application.route('/api/teams/<team_id>/members', methods=['GET'])
def get_team_members(team_id):
    """Get team members with mock data for now"""
    try:
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        
        # Mock team members data for now
        mock_members = [
            {
                'userId': 'user_001',
                'name': 'John Doe',
                'role': 'Developer',
                'department': 'Engineering',
                'productiveHours': 6.5,
                'unproductiveHours': 1.5,
                'totalHours': 8.0,
                'productivityScore': 85,
                'lastActive': datetime.utcnow().isoformat(),
                'status': 'online',
                'isOnline': True,
                'currentActivity': 'Coding',
                'focusSessions': 4,
                'breaksTaken': 2,
                'weeklyAverage': 82,
                'monthlyAverage': 78
            },
            {
                'userId': 'user_002',
                'name': 'Jane Smith',
                'role': 'Designer',
                'department': 'Design',
                'productiveHours': 7.0,
                'unproductiveHours': 1.0,
                'totalHours': 8.0,
                'productivityScore': 90,
                'lastActive': datetime.utcnow().isoformat(),
                'status': 'online',
                'isOnline': True,
                'currentActivity': 'Design Review',
                'focusSessions': 5,
                'breaksTaken': 1,
                'weeklyAverage': 88,
                'monthlyAverage': 85
            },
            {
                'userId': 'user_003',
                'name': 'Mike Johnson',
                'role': 'Manager',
                'department': 'Management',
                'productiveHours': 5.5,
                'unproductiveHours': 2.5,
                'totalHours': 8.0,
                'productivityScore': 70,
                'lastActive': datetime.utcnow().isoformat(),
                'status': 'away',
                'isOnline': False,
                'currentActivity': 'Meeting',
                'focusSessions': 3,
                'breaksTaken': 3,
                'weeklyAverage': 75,
                'monthlyAverage': 72
            }
        ]
        
        return jsonify({
            'success': True,
            'members': mock_members
        }), 200
        
    except Exception as e:
        logger.error(f"Get team members error: {e}")
        return jsonify({'error': 'Failed to get team members'}), 500

@application.route('/api/teams/<team_id>/stats', methods=['GET'])
def get_team_stats(team_id):
    """Get team statistics"""
    try:
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        
        # Mock stats data
        stats = {
            'totalMembers': 3,
            'activeMembers': 2,
            'totalProductiveHours': 19.0,
            'totalUnproductiveHours': 5.0,
            'averageProductivity': 82.5,
            'weeklyGrowth': 5.2,
            'monthlyGrowth': 12.8,
            'topPerformer': 'Jane Smith',
            'mostImproved': 'John Doe',
            'teamEfficiency': 85.7
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Get team stats error: {e}")
        return jsonify({'error': 'Failed to get team stats'}), 500

@application.route('/api/teams/<team_id>/performance', methods=['GET'])
def get_team_performance(team_id):
    """Get team performance data"""
    try:
        team = Team.query.filter_by(id=team_id).first()
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        
        # Mock performance data
        performance = {
            'topPerformers': [
                {
                    'name': 'Jane Smith',
                    'productivityScore': 90,
                    'role': 'Designer',
                    'improvement': '+15%'
                },
                {
                    'name': 'John Doe',
                    'productivityScore': 85,
                    'role': 'Developer',
                    'improvement': '+8%'
                }
            ],
            'needsImprovement': [
                {
                    'name': 'Mike Johnson',
                    'productivityScore': 70,
                    'role': 'Manager',
                    'issue': 'Too many meetings'
                }
            ],
            'teamAverage': 82.5,
            'weeklyTrend': 'up',
            'monthlyTrend': 'up'
        }
        
        return jsonify(performance), 200
        
    except Exception as e:
        logger.error(f"Get team performance error: {e}")
        return jsonify({'error': 'Failed to get team performance'}), 500

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
    logger.info("🚀 Starting Fixed ProductivityFlow Backend")
    
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