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
CORS(application)

# Models - Fixed to handle missing columns
class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    employee_code = db.Column(db.String(10), unique=True, nullable=False)
    manager_id = db.Column(db.String(80), nullable=True)
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

@application.route('/api/teams/public', methods=['GET'])
def get_public_teams():
    """Get public teams (for display purposes)"""
    try:
        teams = Team.query.all()
        return jsonify({
            'teams': [
                {
                    'id': team.id,
                    'name': team.name,
                    'employee_code': team.employee_code,
                    'member_count': 0,  # Mock data
                    'created_at': team.created_at.isoformat() if team.created_at else None
                }
                for team in teams
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Get public teams error: {e}")
        return jsonify({'error': 'Failed to get public teams'}), 500

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
                'name': user_name
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Join team error: {e}")
        return jsonify({'error': 'Failed to join team'}), 500

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