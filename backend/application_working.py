#!/usr/bin/env python3
"""
ProductivityFlow Backend - Working Production Version
Combines robust features with working database structure
"""

import os
import sys
import logging
import random
import string
import traceback
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any

from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bcrypt
import jwt
from werkzeug.exceptions import HTTPException

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('productivityflow.log') if os.environ.get('FLASK_ENV') == 'production' else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
application = Flask(__name__)

# Professional configuration
application.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(32).hex()),
    JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', os.urandom(32).hex()),
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=24),
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 10
    }
)

# Database configuration with robust fallback strategy
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    try:
        # Convert to psycopg3 format if needed
        if 'psycopg2' in DATABASE_URL:
            DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://')
        elif not 'psycopg' in DATABASE_URL:
            # Add psycopg3 driver if not specified
            DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://')
        application.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        logger.info("✅ Using PostgreSQL database with psycopg3")
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL connection failed: {e}")
        application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivityflow.db'
        logger.warning("⚠️ Falling back to SQLite database")
else:
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivityflow.db'
    logger.info("ℹ️ Using SQLite database (development mode)")

# Initialize extensions
db = SQLAlchemy(application)

# Rate limiting for security
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
limiter.init_app(application)

# Professional CORS configuration
CORS(application, 
     origins=[
         "http://localhost:1420", "http://localhost:1421", "http://localhost:3000",
         "tauri://localhost", "https://tauri.localhost",
         "https://productivityflow.com", "https://*.productivityflow.com",
         "*"  # Allow all origins for development
     ],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
     allow_headers=[
         "Content-Type", "Authorization", "X-Requested-With", "Accept",
         "Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers",
         "Cache-Control", "Pragma", "X-API-Key"
     ],
     supports_credentials=True,
     expose_headers=["Content-Length", "X-JSON", "Authorization", "X-Total-Count"],
     max_age=86400
)

# Security headers
@application.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    return response

# Error handling
@application.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        'error': True,
        'message': 'Internal server error. Please try again.'
    }), 500

@application.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': True,
        'message': 'Endpoint not found'
    }), 404

# Models - Simplified and working
class Team(db.Model):
    """Team model with working structure"""
    __tablename__ = 'teams'
    
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    employee_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    manager_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    settings = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    users = db.relationship('User', backref='team', lazy='dynamic')
    activities = db.relationship('Activity', backref='team', lazy='dynamic')

class User(db.Model):
    """User model with working structure"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False, index=True)
    team_id = db.Column(db.String(80), db.ForeignKey('teams.id'), nullable=True, index=True)
    role = db.Column(db.String(50), default='employee', nullable=False, index=True)
    department = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    settings = db.Column(db.JSON, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    email_verified = db.Column(db.Boolean, default=True, nullable=False)  # Set to True by default
    
    # Relationships
    activities = db.relationship('Activity', backref='user', lazy='dynamic')

class Activity(db.Model):
    """Activity model with working structure"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), db.ForeignKey('users.id'), nullable=False, index=True)
    team_id = db.Column(db.String(80), db.ForeignKey('teams.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    active_app = db.Column(db.String(255), nullable=True)
    window_title = db.Column(db.String(500), nullable=True)
    productive_hours = db.Column(db.Float, default=0.0, nullable=False)
    unproductive_hours = db.Column(db.Float, default=0.0, nullable=False)
    idle_hours = db.Column(db.Float, default=0.0, nullable=False)
    focus_sessions = db.Column(db.Integer, default=0, nullable=False)
    breaks_taken = db.Column(db.Integer, default=0, nullable=False)
    productivity_score = db.Column(db.Float, default=0.0, nullable=False)
    last_active = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    activity_metadata = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

# Utility functions
def generate_secure_id(prefix: str) -> str:
    """Generate a secure ID with prefix"""
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{timestamp}_{random_suffix}"

def generate_secure_code(length: int = 8) -> str:
    """Generate a secure team code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

def create_jwt_token(user_id: str, team_id: str, role: str, expires_in: int = 86400) -> str:
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'team_id': team_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, application.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
        return None

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """Password validation"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

# Health check endpoint
@application.route('/health', methods=['GET'])
@limiter.limit("100 per minute")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        database_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        database_status = "disconnected"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '3.2.1',
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'database': database_status,
        'services': {
            'database': 'operational' if database_status == "connected" else 'degraded',
            'authentication': 'operational',
            'ai_insights': 'operational'
        }
    }), 200

# Authentication endpoints
@application.route('/api/auth/register', methods=['POST'])
@limiter.limit("10 per minute")
def register_manager():
    """Register a new manager"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'organization']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': True, 'message': f'{field} is required'}), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        organization = data['organization'].strip()
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': True, 'message': 'Invalid email format'}), 400
        
        # Validate password
        password_validation = validate_password(password)
        if not password_validation['valid']:
            return jsonify({'error': True, 'message': 'Password validation failed', 'details': password_validation['errors']}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': True, 'message': 'User with this email already exists'}), 409
        
        # Create user
        user_id = generate_secure_id('user')
        password_hash = hash_password(password)
        
        new_user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            name=name,
            role='manager',
            department=organization,
            email_verified=True
        )
        
        db.session.add(new_user)
        
        # Create team for the manager
        team_id = generate_secure_id('team')
        employee_code = generate_secure_code(6)
        manager_code = generate_secure_code(6)
        
        new_team = Team(
            id=team_id,
            name=organization,
            employee_code=employee_code,
            manager_code=manager_code,
            description=f"Team for {organization}"
        )
        
        db.session.add(new_team)
        
        # Update user with team_id
        new_user.team_id = team_id
        
        db.session.commit()
        
        # Create JWT token
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
        logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Registration failed. Please try again.'}), 500

@application.route('/api/auth/login', methods=['POST'])
@limiter.limit("20 per minute")
def login_manager():
    """Login manager"""
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
            return jsonify({'error': True, 'message': 'Invalid email or password'}), 401
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return jsonify({'error': True, 'message': 'Invalid email or password'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': True, 'message': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Create JWT token
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
        logger.error(traceback.format_exc())
        return jsonify({'error': True, 'message': 'Login failed. Please try again.'}), 500

@application.route('/api/auth/employee-login', methods=['POST'])
@limiter.limit("20 per minute")
def employee_login():
    """Employee login with team code"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        team_code = data.get('team_code', '').strip().upper()
        user_name = data.get('user_name', '').strip()
        
        if not team_code or not user_name:
            return jsonify({'error': True, 'message': 'Team code and user name are required'}), 400
        
        # Find team by employee code
        team = Team.query.filter_by(employee_code=team_code).first()
        if not team:
            return jsonify({'error': True, 'message': 'Invalid team code'}), 401
        
        # Check if user already exists in this team
        existing_user = User.query.filter_by(team_id=team.id, name=user_name).first()
        
        if existing_user:
            # Update last login
            existing_user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            # Create JWT token
            token = create_jwt_token(existing_user.id, team.id, 'employee')
            
            logger.info(f"Employee logged in successfully: {user_name} in team {team.name}")
            
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
            # Create new employee user
            user_id = generate_secure_id('user')
            
            new_user = User(
                id=user_id,
                email=f"{user_name.lower().replace(' ', '.')}@{team.id}.local",
                password_hash=hash_password('default_password'),  # Will be changed later
                name=user_name,
                team_id=team.id,
                role='employee',
                email_verified=True
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Create JWT token
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
        logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Login failed. Please try again.'}), 500

# Team management endpoints
@application.route('/api/teams', methods=['POST'])
@limiter.limit("10 per minute")
def create_team():
    """Create a new team"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        user_name = data.get('user_name', '').strip()
        
        if not name or not user_name:
            return jsonify({'error': True, 'message': 'Team name and user name are required'}), 400
        
        # Generate team codes
        employee_code = generate_secure_code(6)
        manager_code = generate_secure_code(6)
        
        # Create team
        team_id = generate_secure_id('team')
        new_team = Team(
            id=team_id,
            name=name,
            employee_code=employee_code,
            manager_code=manager_code,
            description=f"Team created by {user_name}"
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
        logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Team creation failed'}), 500

@application.route('/api/teams', methods=['GET'])
@limiter.limit("100 per minute")
def get_teams():
    """Get all teams"""
    try:
        teams = Team.query.all()
        return jsonify({
            'success': True,
            'teams': [{
                'id': team.id,
                'name': team.name,
                'employee_code': team.employee_code,
                'created_at': team.created_at.isoformat() if team.created_at else None
            } for team in teams]
        }), 200
    except Exception as e:
        logger.error(f"Failed to get teams: {str(e)}")
        return jsonify({'error': True, 'message': 'Failed to get teams'}), 500

@application.route('/api/teams/join', methods=['POST'])
@limiter.limit("20 per minute")
def join_team():
    """Join a team with employee code"""
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
        
        # Check if user already exists
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
        user_id = generate_secure_id('user')
        new_user = User(
            id=user_id,
            email=f"{user_name.lower().replace(' ', '.')}@{team.id}.local",
            password_hash=hash_password('default_password'),
            name=user_name,
            team_id=team.id,
            role='employee',
            email_verified=True
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
        logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Failed to join team'}), 500

# Activity tracking endpoints
@application.route('/api/activity/track', methods=['POST'])
@limiter.limit("100 per minute")
def track_activity():
    """Track user activity"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['user_id', 'team_id', 'date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': True, 'message': f'{field} is required'}), 400
        
        user_id = data['user_id']
        team_id = data['team_id']
        date_str = data['date']
        
        # Parse date
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': True, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Check if activity already exists for this user and date
        existing_activity = Activity.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            date=date
        ).first()
        
        if existing_activity:
            # Update existing activity
            existing_activity.active_app = data.get('active_app')
            existing_activity.window_title = data.get('window_title')
            existing_activity.productive_hours = data.get('productive_hours', 0.0)
            existing_activity.unproductive_hours = data.get('unproductive_hours', 0.0)
            existing_activity.idle_hours = data.get('idle_hours', 0.0)
            existing_activity.focus_sessions = data.get('focus_sessions', 0)
            existing_activity.breaks_taken = data.get('breaks_taken', 0)
            existing_activity.productivity_score = data.get('productivity_score', 0.0)
            existing_activity.last_active = datetime.now(timezone.utc)
            existing_activity.activity_metadata = data.get('metadata')
            existing_activity.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Activity updated successfully',
                'activity_id': existing_activity.id
            }), 200
        else:
            # Create new activity
            new_activity = Activity(
                user_id=user_id,
                team_id=team_id,
                date=date,
                active_app=data.get('active_app'),
                window_title=data.get('window_title'),
                productive_hours=data.get('productive_hours', 0.0),
                unproductive_hours=data.get('unproductive_hours', 0.0),
                idle_hours=data.get('idle_hours', 0.0),
                focus_sessions=data.get('focus_sessions', 0),
                breaks_taken=data.get('breaks_taken', 0),
                productivity_score=data.get('productivity_score', 0.0),
                last_active=datetime.now(timezone.utc),
                activity_metadata=data.get('metadata')
            )
            
            db.session.add(new_activity)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Activity tracked successfully',
                'activity_id': new_activity.id
            }), 201
        
    except Exception as e:
        logger.error(f"Activity tracking failed: {str(e)}")
        logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Failed to track activity'}), 500

# Analytics endpoints
@application.route('/api/analytics/burnout-risk', methods=['GET'])
@limiter.limit("50 per minute")
def get_burnout_risk():
    """Get burnout risk analysis"""
    try:
        team_id = request.args.get('team_id')
        if not team_id:
            return jsonify({'error': True, 'message': 'Team ID is required'}), 400
        
        # Get team activities for the last 7 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        activities = Activity.query.filter(
            Activity.team_id == team_id,
            Activity.date >= start_date,
            Activity.date <= end_date
        ).all()
        
        if not activities:
            return jsonify({
                'success': True,
                'burnout_risk': 'low',
                'message': 'No activity data available',
                'risk_factors': []
            }), 200
        
        # Calculate risk factors
        total_hours = sum(a.productive_hours + a.unproductive_hours + a.idle_hours for a in activities)
        avg_daily_hours = total_hours / 7
        avg_productivity = sum(a.productivity_score for a in activities) / len(activities)
        
        risk_factors = []
        risk_level = 'low'
        
        if avg_daily_hours > 10:
            risk_factors.append('High daily work hours')
            risk_level = 'medium'
        
        if avg_productivity < 0.6:
            risk_factors.append('Low productivity scores')
            risk_level = 'medium'
        
        if any(a.productive_hours > 12 for a in activities):
            risk_factors.append('Extended work sessions detected')
            risk_level = 'high'
        
        if len(risk_factors) >= 2:
            risk_level = 'high'
        
        return jsonify({
            'success': True,
            'burnout_risk': risk_level,
            'risk_factors': risk_factors,
            'metrics': {
                'avg_daily_hours': round(avg_daily_hours, 2),
                'avg_productivity': round(avg_productivity, 2),
                'total_activities': len(activities)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Burnout risk analysis failed: {str(e)}")
        return jsonify({'error': True, 'message': 'Failed to analyze burnout risk'}), 500

@application.route('/api/analytics/distraction-profile', methods=['GET'])
@limiter.limit("50 per minute")
def get_distraction_profile():
    """Get distraction profile analysis"""
    try:
        team_id = request.args.get('team_id')
        if not team_id:
            return jsonify({'error': True, 'message': 'Team ID is required'}), 400
        
        # Get team activities for the last 7 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        activities = Activity.query.filter(
            Activity.team_id == team_id,
            Activity.date >= start_date,
            Activity.date <= end_date
        ).all()
        
        if not activities:
            return jsonify({
                'success': True,
                'distraction_level': 'low',
                'message': 'No activity data available',
                'distractions': []
            }), 200
        
        # Analyze distractions
        total_unproductive = sum(a.unproductive_hours for a in activities)
        total_productive = sum(a.productive_hours for a in activities)
        total_hours = total_productive + total_unproductive
        
        if total_hours == 0:
            distraction_ratio = 0
        else:
            distraction_ratio = total_unproductive / total_hours
        
        distractions = []
        distraction_level = 'low'
        
        if distraction_ratio > 0.3:
            distractions.append('High unproductive time ratio')
            distraction_level = 'medium'
        
        if any(a.unproductive_hours > 4 for a in activities):
            distractions.append('Extended unproductive sessions')
            distraction_level = 'high'
        
        if any(a.idle_hours > 2 for a in activities):
            distractions.append('High idle time detected')
            distraction_level = 'medium'
        
        return jsonify({
            'success': True,
            'distraction_level': distraction_level,
            'distractions': distractions,
            'metrics': {
                'distraction_ratio': round(distraction_ratio, 2),
                'total_unproductive_hours': round(total_unproductive, 2),
                'total_productive_hours': round(total_productive, 2)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Distraction profile analysis failed: {str(e)}")
        return jsonify({'error': True, 'message': 'Failed to analyze distraction profile'}), 500

@application.route('/api/employee/daily-summary', methods=['GET'])
@limiter.limit("100 per minute")
def get_daily_summary():
    """Get daily activity summary"""
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
                'idle_hours': activity.idle_hours,
                'productivity_score': activity.productivity_score,
                'focus_sessions': activity.focus_sessions,
                'breaks_taken': activity.breaks_taken,
                'active_app': activity.active_app,
                'window_title': activity.window_title,
                'last_active': activity.last_active.isoformat() if activity.last_active else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Daily summary failed: {str(e)}")
        return jsonify({'error': True, 'message': 'Failed to get daily summary'}), 500

# Database initialization
def init_db():
    """Initialize database tables"""
    try:
        with application.app_context():
            db.create_all()
            logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

if __name__ == '__main__':
    init_db()
    application.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    # Initialize database when imported
    init_db() 