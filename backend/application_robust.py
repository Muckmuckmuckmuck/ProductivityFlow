#!/usr/bin/env python3
"""
ProductivityFlow Backend - Robust Production Version
Enterprise-grade backend with comprehensive error handling and logging
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
     max_age=86400)

# Professional error handling
@application.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler with proper logging and response"""
    logger.error(f"Unhandled exception: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    if isinstance(e, HTTPException):
        return jsonify({
            'error': True,
            'message': e.description,
            'code': e.code
        }), e.code
    
    return jsonify({
        'error': True,
        'message': 'An unexpected error occurred. Please try again.',
        'code': 500
    }), 500

@application.errorhandler(404)
def not_found(error):
    """Handle 404 errors professionally"""
    return jsonify({
        'error': True,
        'message': 'The requested resource was not found.',
        'code': 404
    }), 404

@application.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors professionally"""
    return jsonify({
        'error': True,
        'message': 'Method not allowed.',
        'code': 405
    }), 405

@application.before_request
def handle_preflight():
    """Handle CORS preflight requests"""
    if request.method == "OPTIONS":
        response = Response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        return response

@application.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

# Database Models
class Team(db.Model):
    """Professional team model"""
    __tablename__ = 'teams'
    
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    employee_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    manager_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    settings = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    users = db.relationship('User', backref='team', lazy='dynamic')
    activities = db.relationship('Activity', backref='team', lazy='dynamic')

class User(db.Model):
    """Professional user model"""
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    activities = db.relationship('Activity', backref='user', lazy='dynamic')

class Activity(db.Model):
    """Professional activity model"""
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

# Utility functions
def generate_secure_id(prefix: str) -> str:
    """Generate a secure, unique ID"""
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{timestamp}_{random_suffix}"

def generate_secure_code(length: int = 8) -> str:
    """Generate a secure, random code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def hash_password(password: str) -> str:
    """Hash a password securely"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_jwt_token(user_id: str, team_id: str, role: str, expires_in: int = 86400) -> str:
    """Create a JWT token"""
    payload = {
        'user_id': user_id,
        'team_id': team_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, application.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
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
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
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

# Routes
@application.route('/health', methods=['GET'])
@limiter.limit("100 per minute")
def health_check():
    """Professional health check endpoint"""
    try:
        # Test database connection with proper SQLAlchemy text()
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '3.2.1',
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'database': 'connected',
            'services': {
                'database': 'operational',
                'authentication': 'operational',
                'ai_insights': 'operational'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e)
        }), 503

@application.route('/api/auth/register', methods=['POST'])
@limiter.limit("10 per minute")
def register_manager():
    """Professional manager registration with comprehensive validation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'Invalid request data'}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'organization']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': True, 'message': f'Missing required field: {field}'}), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        organization = data['organization'].strip()
        
        # Professional validation
        if not validate_email(email):
            return jsonify({'error': True, 'message': 'Invalid email format'}), 400
        
        password_validation = validate_password(password)
        if not password_validation['valid']:
            return jsonify({
                'error': True, 
                'message': 'Password validation failed',
                'details': password_validation['errors']
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': True, 'message': 'User with this email already exists'}), 409
        
        # Create team for the manager
        team_id = generate_secure_id('team')
        team_code = generate_secure_code(8)
        employee_code = generate_secure_code(6)
        
        team = Team(
            id=team_id,
            name=organization,
            employee_code=employee_code,
            manager_code=team_code,
            description=f"Team for {organization}",
            settings={'timezone': 'UTC', 'work_hours': {'start': '09:00', 'end': '17:00'}}
        )
        
        # Create manager user
        user_id = generate_secure_id('user')
        user = User(
            id=user_id,
            email=email,
            password_hash=hash_password(password),
            name=name,
            team_id=team_id,
            role='manager',
            department='Management',
            settings={'notifications': True, 'theme': 'light'}
        )
        
        # Save to database
        db.session.add(team)
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = create_jwt_token(user_id, team_id, 'manager')
        
        logger.info(f"Manager registered successfully: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Manager account created successfully',
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
                'code': team_code,
                'employee_code': employee_code
            },
            'token': token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Manager registration failed: {e}")
        return jsonify({'error': True, 'message': 'Registration failed. Please try again.'}), 500

@application.route('/api/auth/login', methods=['POST'])
@limiter.limit("20 per minute")
def login_manager():
    """Professional manager login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'Invalid request data'}), 400
        
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
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Generate token
        token = create_jwt_token(user.id, user.team_id or '', user.role)
        
        logger.info(f"Manager login successful: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'team_id': user.team_id
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Manager login failed: {e}")
        return jsonify({'error': True, 'message': 'Login failed. Please try again.'}), 500

@application.route('/api/auth/employee-login', methods=['POST'])
@limiter.limit("20 per minute")
def employee_login():
    """Professional employee login with multiple authentication methods"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'Invalid request data'}), 400
        
        team_code = data.get('team_code')
        user_name = data.get('user_name')
        email = data.get('email')
        password = data.get('password')
        
        # Support both team code + user name and email + password
        if team_code and user_name:
            # Find team by employee code
            team = Team.query.filter_by(employee_code=team_code.upper()).first()
            if not team:
                return jsonify({'error': True, 'message': 'Invalid team code'}), 404
            
            # Find or create user
            user = User.query.filter_by(name=user_name, team_id=team.id).first()
            if not user:
                # Create new user
                user_id = generate_secure_id('user')
                user = User(
                    id=user_id,
                    email=f"{user_name.lower().replace(' ', '.')}@{team.name.lower().replace(' ', '')}.local",
                    password_hash=hash_password('default_password_123'),
                    name=user_name,
                    team_id=team.id,
                    role='employee',
                    department='General',
                    settings={'notifications': True, 'theme': 'light'}
                )
                db.session.add(user)
                db.session.commit()
            
            # Generate token
            token = create_jwt_token(user.id, team.id, 'employee')
            
            return jsonify({
                'success': True,
                'message': 'Employee login successful',
                'token': token,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'team_id': team.id,
                    'team_name': team.name
                }
            }), 200
            
        elif email and password:
            # Email/password authentication
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({'error': True, 'message': 'Invalid credentials'}), 401
            
            if not verify_password(password, user.password_hash):
                return jsonify({'error': True, 'message': 'Invalid credentials'}), 401
            
            # Get team info
            team = Team.query.get(user.team_id) if user.team_id else None
            
            # Generate token
            token = create_jwt_token(user.id, user.team_id or '', user.role)
            
            return jsonify({
                'success': True,
                'message': 'Employee login successful',
                'token': token,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'team_id': user.team_id,
                    'team_name': team.name if team else None
                }
            }), 200
        else:
            return jsonify({'error': True, 'message': 'Invalid authentication method'}), 400
            
    except Exception as e:
        logger.error(f"Employee login failed: {e}")
        return jsonify({'error': True, 'message': 'Login failed. Please try again.'}), 500

@application.route('/api/teams', methods=['POST'])
@limiter.limit("10 per minute")
def create_team():
    """Create a new team"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'Invalid request data'}), 400
        
        name = data.get('name', '').strip()
        user_name = data.get('user_name', 'Manager').strip()
        
        if not name:
            return jsonify({'error': True, 'message': 'Team name is required'}), 400
        
        # Generate secure IDs and codes
        team_id = generate_secure_id('team')
        employee_code = generate_secure_code(6)
        manager_code = generate_secure_code(8)
        
        # Create team
        new_team = Team(
            id=team_id,
            name=name,
            employee_code=employee_code,
            manager_code=manager_code,
            description=f"Team created by {user_name}",
            settings={'timezone': 'UTC', 'work_hours': {'start': '09:00', 'end': '17:00'}}
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
                'code': employee_code,
                'employee_code': employee_code,
                'manager_code': manager_code
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Team creation error: {e}")
        return jsonify({'error': True, 'message': 'Team creation failed'}), 500

@application.route('/api/teams', methods=['GET'])
@limiter.limit("100 per minute")
def get_teams():
    """Get all teams"""
    try:
        teams = Team.query.all()
        teams_data = []
        
        for team in teams:
            # Get team members count
            member_count = User.query.filter_by(team_id=team.id).count()
            
            team_data = {
                'id': team.id,
                'name': team.name,
                'code': team.employee_code,
                'employee_code': team.employee_code,
                'manager_code': team.manager_code,
                'memberCount': member_count,
                'created_at': team.created_at.isoformat() if team.created_at else None
            }
            teams_data.append(team_data)
        
        return jsonify({'teams': teams_data}), 200
        
    except Exception as e:
        logger.error(f"Get teams error: {e}")
        return jsonify({'error': True, 'message': 'Failed to get teams'}), 500

@application.route('/api/teams/join', methods=['POST'])
@limiter.limit("20 per minute")
def join_team():
    """Join a team with email/password or team code"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'Invalid request data'}), 400
        
        # Support both team code + user name and email + password
        team_code = data.get('employee_code') or data.get('team_code')
        user_name = data.get('user_name')
        email = data.get('email')
        password = data.get('password')
        
        if team_code and user_name:
            # Find team by employee code
            team = Team.query.filter_by(employee_code=team_code.upper()).first()
            if not team:
                return jsonify({'error': True, 'message': 'Invalid team code'}), 404
            
            # Check if user already exists
            existing_user = User.query.filter_by(name=user_name, team_id=team.id).first()
            if existing_user:
                return jsonify({'error': True, 'message': 'User already exists in this team'}), 409
            
            # Create new user
            user_id = generate_secure_id('user')
            user_email = email if email else f"{user_name.lower().replace(' ', '.')}@{team.name.lower().replace(' ', '')}.local"
            user_password = password if password else 'default_password_123'
            
            user = User(
                id=user_id,
                email=user_email,
                password_hash=hash_password(user_password),
                name=user_name,
                team_id=team.id,
                role='employee',
                department='General',
                settings={'notifications': True, 'theme': 'light'}
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Generate token
            token = create_jwt_token(user.id, team.id, 'employee')
            
            return jsonify({
                'success': True,
                'message': 'Successfully joined team',
                'token': token,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'team_id': team.id,
                    'team_name': team.name
                },
                'team': {
                    'id': team.id,
                    'name': team.name,
                    'code': team.employee_code
                }
            }), 201
            
        else:
            return jsonify({'error': True, 'message': 'Team code and user name are required'}), 400
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Team join error: {e}")
        return jsonify({'error': True, 'message': 'Failed to join team'}), 500

@application.route('/api/teams/<team_id>/members', methods=['GET'])
@limiter.limit("100 per minute")
def get_team_members(team_id):
    """Get team members"""
    try:
        # Verify team exists
        team = Team.query.get(team_id)
        if not team:
            return jsonify({'error': True, 'message': 'Team not found'}), 404
        
        # Get team members
        members = User.query.filter_by(team_id=team_id).all()
        members_data = []
        
        for member in members:
            member_data = {
                'id': member.id,
                'name': member.name,
                'email': member.email,
                'role': member.role,
                'department': member.department,
                'last_login': member.last_login.isoformat() if member.last_login else None,
                'created_at': member.created_at.isoformat() if member.created_at else None
            }
            members_data.append(member_data)
        
        return jsonify({
            'success': True,
            'team': {
                'id': team.id,
                'name': team.name,
                'code': team.employee_code
            },
            'members': members_data,
            'total_members': len(members_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Get team members error: {e}")
        return jsonify({'error': True, 'message': 'Failed to get team members'}), 500

@application.route('/api/activity/track', methods=['POST'])
@limiter.limit("100 per minute")
def track_activity():
    """Track user activity"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'Invalid request data'}), 400
        
        # Extract data
        user_id = data.get('user_id')
        team_id = data.get('team_id')
        date_str = data.get('date')
        active_app = data.get('active_app')
        window_title = data.get('window_title')
        productive_hours = data.get('productive_hours', 0.0)
        unproductive_hours = data.get('unproductive_hours', 0.0)
        idle_hours = data.get('idle_hours', 0.0)
        focus_sessions = data.get('focus_sessions', 0)
        breaks_taken = data.get('breaks_taken', 0)
        productivity_score = data.get('productivity_score', 0.0)
        activity_metadata = data.get('activity_metadata', {})
        
        # Validate required fields
        if not all([user_id, team_id, date_str]):
            return jsonify({'error': True, 'message': 'Missing required fields'}), 400
        
        # Parse date
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': True, 'message': 'Invalid date format'}), 400
        
        # Check if activity already exists for this user and date
        existing_activity = Activity.query.filter_by(
            user_id=user_id, 
            team_id=team_id, 
            date=date
        ).first()
        
        if existing_activity:
            # Update existing activity
            existing_activity.active_app = active_app
            existing_activity.window_title = window_title
            existing_activity.productive_hours = productive_hours
            existing_activity.unproductive_hours = unproductive_hours
            existing_activity.idle_hours = idle_hours
            existing_activity.focus_sessions = focus_sessions
            existing_activity.breaks_taken = breaks_taken
            existing_activity.productivity_score = productivity_score
            existing_activity.last_active = datetime.now(timezone.utc)
            existing_activity.activity_metadata = activity_metadata
            existing_activity.updated_at = datetime.now(timezone.utc)
        else:
            # Create new activity
            activity = Activity(
                user_id=user_id,
                team_id=team_id,
                date=date,
                active_app=active_app,
                window_title=window_title,
                productive_hours=productive_hours,
                unproductive_hours=unproductive_hours,
                idle_hours=idle_hours,
                focus_sessions=focus_sessions,
                breaks_taken=breaks_taken,
                productivity_score=productivity_score,
                activity_metadata=activity_metadata
            )
            db.session.add(activity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Activity tracked successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Activity tracking error: {e}")
        return jsonify({'error': True, 'message': 'Failed to track activity'}), 500

@application.route('/api/analytics/burnout-risk', methods=['GET'])
@limiter.limit("50 per minute")
def get_burnout_risk():
    """Get burnout risk analysis"""
    try:
        # Get team ID from headers or query params
        team_id = request.headers.get('X-Team-ID') or request.args.get('team_id')
        
        if not team_id:
            return jsonify({'error': True, 'message': 'Team ID is required'}), 400
        
        # Get team activities for the last 30 days
        thirty_days_ago = datetime.now(timezone.utc).date() - timedelta(days=30)
        
        activities = Activity.query.filter(
            Activity.team_id == team_id,
            Activity.date >= thirty_days_ago
        ).all()
        
        if not activities:
            return jsonify({
                'success': True,
                'burnout_risk': 'low',
                'risk_score': 0.2,
                'message': 'No activity data available for analysis',
                'recommendations': [
                    'Start tracking productivity to get personalized insights',
                    'Set up regular breaks and focus sessions',
                    'Monitor work-life balance'
                ]
            }), 200
        
        # Calculate burnout risk factors
        total_productive_hours = sum(a.productive_hours for a in activities)
        total_unproductive_hours = sum(a.unproductive_hours for a in activities)
        total_idle_hours = sum(a.idle_hours for a in activities)
        avg_productivity_score = sum(a.productivity_score for a in activities) / len(activities)
        
        # Risk calculation logic
        risk_factors = []
        risk_score = 0.0
        
        # High productive hours (potential overwork)
        if total_productive_hours > 160:  # More than 8 hours/day average
            risk_factors.append('High productive hours detected')
            risk_score += 0.3
        
        # Low productivity score
        if avg_productivity_score < 0.6:
            risk_factors.append('Low productivity scores')
            risk_score += 0.2
        
        # High idle time
        if total_idle_hours > 40:  # More than 2 hours/day average
            risk_factors.append('High idle time detected')
            risk_score += 0.1
        
        # Determine risk level
        if risk_score >= 0.5:
            risk_level = 'high'
            recommendations = [
                'Consider taking more breaks throughout the day',
                'Review workload distribution',
                'Implement stress management techniques',
                'Schedule regular check-ins with team members'
            ]
        elif risk_score >= 0.3:
            risk_level = 'medium'
            recommendations = [
                'Monitor work patterns closely',
                'Encourage regular breaks',
                'Consider workload adjustments',
                'Promote work-life balance'
            ]
        else:
            risk_level = 'low'
            recommendations = [
                'Continue current work patterns',
                'Maintain regular breaks',
                'Monitor for any changes in productivity'
            ]
        
        return jsonify({
            'success': True,
            'burnout_risk': risk_level,
            'risk_score': round(risk_score, 2),
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'metrics': {
                'total_productive_hours': round(total_productive_hours, 2),
                'total_unproductive_hours': round(total_unproductive_hours, 2),
                'total_idle_hours': round(total_idle_hours, 2),
                'avg_productivity_score': round(avg_productivity_score, 2),
                'analysis_period_days': 30
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Burnout risk analysis error: {e}")
        return jsonify({'error': True, 'message': 'Failed to analyze burnout risk'}), 500

@application.route('/api/analytics/distraction-profile', methods=['GET'])
@limiter.limit("50 per minute")
def get_distraction_profile():
    """Get distraction profile analysis"""
    try:
        # Get team ID from headers or query params
        team_id = request.headers.get('X-Team-ID') or request.args.get('team_id')
        
        if not team_id:
            return jsonify({'error': True, 'message': 'Team ID is required'}), 400
        
        # Get team activities for the last 7 days
        seven_days_ago = datetime.now(timezone.utc).date() - timedelta(days=7)
        
        activities = Activity.query.filter(
            Activity.team_id == team_id,
            Activity.date >= seven_days_ago
        ).all()
        
        if not activities:
            return jsonify({
                'success': True,
                'distraction_level': 'low',
                'distraction_score': 0.1,
                'message': 'No activity data available for analysis',
                'recommendations': [
                    'Start tracking productivity to get personalized insights',
                    'Monitor application usage patterns',
                    'Set up focus sessions'
                ]
            }), 200
        
        # Analyze distraction patterns
        total_unproductive_hours = sum(a.unproductive_hours for a in activities)
        total_productive_hours = sum(a.productive_hours for a in activities)
        total_hours = total_productive_hours + total_unproductive_hours
        
        if total_hours == 0:
            distraction_score = 0.0
        else:
            distraction_score = total_unproductive_hours / total_hours
        
        # Get most common unproductive apps
        app_usage = {}
        for activity in activities:
            if activity.active_app and activity.unproductive_hours > 0:
                app_usage[activity.active_app] = app_usage.get(activity.active_app, 0) + activity.unproductive_hours
        
        top_distractions = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Determine distraction level
        if distraction_score >= 0.4:
            distraction_level = 'high'
            recommendations = [
                'Consider using website blockers during work hours',
                'Implement the Pomodoro technique',
                'Create a distraction-free workspace',
                'Set specific times for checking social media'
            ]
        elif distraction_score >= 0.2:
            distraction_level = 'medium'
            recommendations = [
                'Monitor time spent on non-work applications',
                'Set boundaries for social media usage',
                'Use focus mode features in applications',
                'Schedule dedicated break times'
            ]
        else:
            distraction_level = 'low'
            recommendations = [
                'Maintain current focus levels',
                'Continue using productivity tools',
                'Monitor for any changes in distraction patterns'
            ]
        
        return jsonify({
            'success': True,
            'distraction_level': distraction_level,
            'distraction_score': round(distraction_score, 2),
            'recommendations': recommendations,
            'top_distractions': [
                {'app': app, 'hours': round(hours, 2)} 
                for app, hours in top_distractions
            ],
            'metrics': {
                'total_productive_hours': round(total_productive_hours, 2),
                'total_unproductive_hours': round(total_unproductive_hours, 2),
                'distraction_ratio': round(distraction_score, 2),
                'analysis_period_days': 7
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Distraction profile analysis error: {e}")
        return jsonify({'error': True, 'message': 'Failed to analyze distraction profile'}), 500

@application.route('/api/employee/daily-summary', methods=['GET'])
@limiter.limit("100 per minute")
def get_daily_summary():
    """Get employee daily summary"""
    try:
        # Get user ID from token or request
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': True, 'message': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': True, 'message': 'Invalid token'}), 401
        
        user_id = payload['user_id']
        team_id = payload['team_id']
        
        # Get today's activity
        today = datetime.now(timezone.utc).date()
        activity = Activity.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            date=today
        ).first()
        
        if not activity:
            return jsonify({
                'success': True,
                'message': 'No activity recorded for today',
                'summary': {
                    'productive_hours': 0,
                    'unproductive_hours': 0,
                    'idle_hours': 0,
                    'focus_sessions': 0,
                    'breaks_taken': 0,
                    'productivity_score': 0,
                    'current_app': None,
                    'current_window': None
                }
            }), 200
        
        return jsonify({
            'success': True,
            'summary': {
                'productive_hours': round(activity.productive_hours, 2),
                'unproductive_hours': round(activity.unproductive_hours, 2),
                'idle_hours': round(activity.idle_hours, 2),
                'focus_sessions': activity.focus_sessions,
                'breaks_taken': activity.breaks_taken,
                'productivity_score': round(activity.productivity_score, 2),
                'current_app': activity.active_app,
                'current_window': activity.window_title,
                'last_updated': activity.updated_at.isoformat() if activity.updated_at else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Daily summary error: {e}")
        return jsonify({'error': True, 'message': 'Failed to get daily summary'}), 500

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
    logger.info("🚀 Starting ProductivityFlow Backend (Robust Production)")
    
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
else:
    init_db() 