#!/usr/bin/env python3
"""
Minimal ProductivityFlow Backend
Simplified version to ensure deployment works
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
import bcrypt
import jwt
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
application = Flask(__name__)

# Basic configuration
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
application.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
application.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    application.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.info("✅ Using PostgreSQL database")
else:
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivityflow.db'
    logger.info("⚠️ Using SQLite database (development mode)")

# Email configuration
application.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
application.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'test@example.com')
application.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'test')
application.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'test@example.com')

# Initialize extensions
db = SQLAlchemy(application)
mail = Mail(application)
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
    is_verified = db.Column(db.Boolean, default=False)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@application.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "disconnected"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'python_version': sys.version,
        'flask_version': '2.3.3',
        'database': db_status,
        'environment': os.environ.get('FLASK_ENV', 'development')
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
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        user_id = f"user_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
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
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'email': user.email,
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            application.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
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
        
        # Generate team ID and employee code
        team_id = f"team_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        employee_code = f"EMP{datetime.utcnow().strftime('%H%M%S')}"
        
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
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Flask version: 2.3.3")
    
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