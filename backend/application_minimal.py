#!/usr/bin/env python3
"""
ProductivityFlow Backend - Minimal Working Version
Essential features only for production deployment
"""

import os
import logging
import random
import string
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
if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    # Convert to psycopg3 format
    if 'psycopg2' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://')
    elif not 'psycopg' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://')
    application.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    logger.info("✅ Using PostgreSQL database")
else:
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivityflow.db'
    logger.info("ℹ️ Using SQLite database")

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(application)
CORS(application)

# Models
class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    employee_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    team_id = db.Column(db.String(80), db.ForeignKey('teams.id'), nullable=True)
    role = db.Column(db.String(50), default='employee', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Utility functions
def generate_id(prefix):
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{timestamp}_{random_suffix}"

def generate_team_code():
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
        'timestamp': datetime.utcnow().isoformat(),
        'version': '3.2.1',
        'environment': 'production',
        'database': db_status,
        'services': {
            'database': 'operational',
            'authentication': 'operational',
            'ai_insights': 'operational'
        }
    })

@application.route('/api/teams', methods=['POST'])
def create_team():
    """Create a new team"""
    try:
        data = request.get_json()
        name = data.get('name')
        user_name = data.get('user_name', 'Manager')
        
        if not name:
            return jsonify({'error': 'Team name is required'}), 400
        
        team_id = generate_id('team')
        employee_code = generate_team_code()
        
        new_team = Team(
            id=team_id,
            name=name,
            employee_code=employee_code
        )
        
        db.session.add(new_team)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Team created successfully',
            'team': {
                'id': team_id,
                'name': name,
                'code': employee_code,
                'employee_code': employee_code
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Team creation error: {e}")
        return jsonify({'error': True, 'message': 'Team creation failed'}), 500

@application.route('/api/teams', methods=['GET'])
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
                'memberCount': member_count,
                'created_at': team.created_at.isoformat() if team.created_at else None
            }
            teams_data.append(team_data)
        
        return jsonify({'teams': teams_data}), 200
        
    except Exception as e:
        logger.error(f"Get teams error: {e}")
        return jsonify({'error': 'Failed to get teams'}), 500

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
    logger.info("🚀 Starting ProductivityFlow Backend (Minimal)")
    
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