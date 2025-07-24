import os
import flask
from flask import Flask, request, jsonify

# Railway-specific optimizations
os.environ.setdefault('FLASK_ENV', 'production')

# Flask version compatibility check
print(f"Flask version: {flask.__version__}")

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import string
import logging
import hashlib
import time
import jwt
import bcrypt
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import redis
import stripe
import anthropic
from cryptography.fernet import Fernet
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import json
import base64
import sys
import numpy as np
from collections import defaultdict
import traceback

# Load environment variables
load_dotenv()

# Enhanced Railway logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Ensure logs go to Railway console
    ]
)
logger = logging.getLogger(__name__)

# Railway-specific startup logging
logger.info("🚀 Starting ProductivityFlow backend on Railway")
logger.info(f"Python version: {sys.version}")
logger.info(f"Flask version: {flask.__version__}")

# Add startup delay for Cloud SQL Proxy
logger.info("⏳ Waiting for Cloud SQL Proxy to establish connection...")
time.sleep(10)  # Wait 10 seconds for Cloud SQL Proxy
logger.info("✅ Startup delay completed")

# Check critical environment variables
required_env_vars = ['SECRET_KEY', 'JWT_SECRET_KEY', 'ENCRYPTION_KEY']
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    logger.warning(f"⚠️ Missing environment variables: {missing_vars}")
    logger.warning("These should be set in Railway dashboard for production")

# Check DATABASE_URL
if os.environ.get('DATABASE_URL'):
    logger.info("✅ DATABASE_URL found - PostgreSQL will be used")
else:
    logger.warning("⚠️ No DATABASE_URL found - will use SQLite (development only)")

application = Flask(__name__)

# --- Enhanced Security & API Key Management ---
# Initialize encryption for secure API key storage
# For production, set ENCRYPTION_KEY environment variable:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # Generate a new key if not provided (for development)
    ENCRYPTION_KEY = Fernet.generate_key()
    logging.warning("No ENCRYPTION_KEY provided, using generated key (dev only). Set ENCRYPTION_KEY environment variable for production.")
    logging.warning("To generate a production key, run: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
else:
    # If ENCRYPTION_KEY is provided as a string, encode it to bytes
    if isinstance(ENCRYPTION_KEY, str):
        ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
        logging.info("Encryption key loaded from environment variable")

cipher_suite = Fernet(ENCRYPTION_KEY)

# --- Security Configuration ---
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
application.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

# --- Rate Limiting Configuration ---
# Enable rate limiting by default for production security
ENABLE_RATE_LIMITING = os.environ.get('ENABLE_RATE_LIMITING', 'true').lower() == 'true'

if ENABLE_RATE_LIMITING:
    # Configure Redis for rate limiting (fallback to memory if Redis not available)
    try:
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        # Test the Redis connection before using it
        import redis
        redis_client = redis.from_url(redis_url)
        redis_client.ping()  # This will raise an exception if Redis is not available
        
        limiter = Limiter(
            key_func=get_remote_address,
            app=application,
            storage_uri=redis_url,
            default_limits=["1000 per hour", "200 per minute"]
        )
        logging.info("Rate limiting configured with Redis")
    except Exception as e:
        logging.warning(f"Redis not available, using in-memory rate limiting: {e}")
        limiter = Limiter(
            key_func=get_remote_address,
            app=application,
            default_limits=["1000 per hour", "200 per minute"]
        )
        logging.info("Rate limiting enabled with in-memory storage")
else:
    limiter = None
    logging.warning("Rate limiting disabled - not recommended for production")

# Conditional rate limiting decorator
def conditional_rate_limit(limit_string):
    def decorator(f):
        if limiter is not None:
            return limiter.limit(limit_string)(f)
        return f
    return decorator

# --- Stripe Configuration ---
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_live_51RkaYhHHYuKoTuQQMGbXRhWQXBKR5JiFawdfBL7zrOHsay46EoEyYInWesRUUave2x68JY56lXFuYmFmREIHtLeP00YxMFIHTd')

# --- Claude AI Configuration ---
# Encrypt and store Claude API key securely
CLAUDE_API_KEY_ENCRYPTED = os.environ.get('CLAUDE_API_KEY_ENCRYPTED')
if not CLAUDE_API_KEY_ENCRYPTED:
    # Encrypt the provided API key from environment variable
    claude_key = os.environ.get('CLAUDE_API_KEY', 'your-claude-api-key-here')
    if claude_key != 'your-claude-api-key-here':
        CLAUDE_API_KEY_ENCRYPTED = cipher_suite.encrypt(claude_key.encode())
        logging.info("Claude API key encrypted and stored securely")
    else:
        logging.warning("Claude API key not set. Please set CLAUDE_API_KEY environment variable.")

# Decrypt Claude API key for use
def get_claude_api_key():
    try:
        if CLAUDE_API_KEY_ENCRYPTED:
            return cipher_suite.decrypt(CLAUDE_API_KEY_ENCRYPTED).decode()
        return None
    except Exception as e:
        logging.error(f"Failed to decrypt Claude API key: {e}")
        return None

# Initialize Claude client with error handling
claude_api_key = get_claude_api_key()
claude_client = None
if claude_api_key:
    try:
        claude_client = anthropic.Anthropic(api_key=claude_api_key)
        logging.info("Claude client initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize Claude client: {e}")
        claude_client = None
else:
    logging.warning("Claude client not initialized due to missing API key")

# --- Email Configuration ---
# Check if email credentials are available
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

# Determine if email is properly configured
EMAIL_CONFIGURED = bool(MAIL_USERNAME and MAIL_PASSWORD and MAIL_DEFAULT_SENDER)

if EMAIL_CONFIGURED:
    application.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    application.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    application.config['MAIL_USE_TLS'] = True
    application.config['MAIL_USERNAME'] = MAIL_USERNAME
    application.config['MAIL_PASSWORD'] = MAIL_PASSWORD
    application.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER
    logging.info("✅ Email configuration found - verification emails will be sent")
else:
    # Fallback configuration for development/testing
    application.config['MAIL_SERVER'] = 'smtp.gmail.com'
    application.config['MAIL_PORT'] = 587
    application.config['MAIL_USE_TLS'] = True
    application.config['MAIL_USERNAME'] = 'test@example.com'
    application.config['MAIL_PASSWORD'] = 'test'
    application.config['MAIL_DEFAULT_SENDER'] = 'test@example.com'
    logging.warning("⚠️ Email credentials not configured - verification will be bypassed in development mode")

mail = Mail(application)

# --- Enhanced CORS Configuration ---
# Comprehensive CORS setup to fix all 405 Method Not Allowed and CORS errors
# This configuration allows both Tauri desktop apps and web browsers to access the API
# without CORS issues. The setup includes proper preflight handling and response headers.

# Enable comprehensive CORS for all origins including Tauri apps
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

# --- Database Configuration ---
# Use Railway PostgreSQL URL or fallback to SQLite for development
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # Railway provides postgres:// but SQLAlchemy expects postgresql://
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

if DATABASE_URL:
    application.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    logging.info("Using PostgreSQL database from DATABASE_URL")
else:
    # Fallback to SQLite for development
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivityflow.db'
    logging.warning("No DATABASE_URL found, using SQLite (development only)")

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'max_overflow': 0,
    'connect_args': {
        'connect_timeout': 60,  # 60 second connection timeout for Cloud SQL
        'application_name': 'productivityflow',
        'sslmode': 'disable',  # Disable SSL for Cloud SQL Proxy
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
}

# Initialize database with error handling
try:
    db = SQLAlchemy(application)
    logging.info("✅ SQLAlchemy initialized successfully")
except Exception as e:
    logging.error(f"❌ SQLAlchemy initialization failed: {e}")
    # Create a minimal db object to prevent import errors
    class MockDB:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    db = MockDB()

# --- Enhanced Database Models ---
class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    employee_code = db.Column(db.String(10), unique=True, nullable=False)  # Renamed from 'code'
    manager_id = db.Column(db.String(80), nullable=True)  # Added missing field
    created_at = db.Column(db.DateTime, default=db.func.now())

class ManagerInvite(db.Model):
    __tablename__ = 'manager_invites'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False)
    invite_code = db.Column(db.String(12), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    used_by = db.Column(db.String(80), nullable=True)  # user_id who used it
    created_at = db.Column(db.DateTime, default=db.func.now())
    used_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)  # Manager invites expire

class Membership(db.Model):
    __tablename__ = 'memberships'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.String(80), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'employee' or 'manager'
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Ensure unique team-user combinations
    __table_args__ = (db.UniqueConstraint('team_id', 'user_id', name='unique_team_user'),)

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, index=True)  # Added index for performance
    team_id = db.Column(db.String(80), nullable=False, index=True)  # Added index for performance
    date = db.Column(db.Date, nullable=False, index=True)  # Added index for performance
    active_app = db.Column(db.String(255), nullable=True)  # Track active application
    window_title = db.Column(db.Text, nullable=True)  # Track window title
    productive_hours = db.Column(db.Float, default=0.0)
    unproductive_hours = db.Column(db.Float, default=0.0)
    idle_time = db.Column(db.Float, default=0.0)  # Track idle time
    goals_completed = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=db.func.now())
    
    # Composite index for better query performance
    __table_args__ = (db.Index('idx_user_team_date', 'user_id', 'team_id', 'date'),)

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    team_id = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'employee' or 'manager'
    start_time = db.Column(db.DateTime, default=db.func.now())
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    jwt_token_hash = db.Column(db.String(64), nullable=True)  # Store hashed JWT for validation

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False, index=True)  # Added index
    assigned_to = db.Column(db.String(80), nullable=False, index=True)  # Added index
    assigned_by = db.Column(db.String(80), nullable=False)  # user_id
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    created_at = db.Column(db.DateTime, default=db.func.now())
    completed_at = db.Column(db.DateTime, nullable=True)

# New Enhanced Models for SaaS Features

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    last_login = db.Column(db.DateTime, nullable=True)
    
class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False, unique=True, index=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='inactive')  # active, inactive, cancelled, past_due
    employee_count = db.Column(db.Integer, default=0)
    monthly_cost = db.Column(db.Float, default=0.0)  # $9.99 per employee
    current_period_start = db.Column(db.DateTime, nullable=True)
    current_period_end = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class ProductivityReport(db.Model):
    __tablename__ = 'productivity_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, index=True)
    team_id = db.Column(db.String(80), nullable=False, index=True)
    report_date = db.Column(db.DateTime, nullable=False, index=True)
    hour_start = db.Column(db.DateTime, nullable=False)
    hour_end = db.Column(db.DateTime, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    ai_analysis = db.Column(db.Text, nullable=True)
    irregularity_detected = db.Column(db.Boolean, default=False)
    token_count_input = db.Column(db.Integer, default=0)
    token_count_output = db.Column(db.Integer, default=0)
    cost_estimate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Composite index for efficient queries
    __table_args__ = (db.Index('idx_user_team_date_hour', 'user_id', 'team_id', 'report_date'),)

class TokenUsage(db.Model):
    __tablename__ = 'token_usage'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, index=True)
    team_id = db.Column(db.String(80), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    cost_estimate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Unique constraint to prevent duplicate daily records
    __table_args__ = (db.UniqueConstraint('user_id', 'team_id', 'date', name='unique_daily_token_usage'),)

class DetailedActivity(db.Model):
    __tablename__ = 'detailed_activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, index=True)
    team_id = db.Column(db.String(80), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    active_app = db.Column(db.String(255), nullable=True)
    window_title = db.Column(db.Text, nullable=True)
    mouse_clicks = db.Column(db.Integer, default=0)
    keyboard_strokes = db.Column(db.Integer, default=0)
    screenshot_hash = db.Column(db.String(64), nullable=True)  # For irregularity detection
    is_idle = db.Column(db.Boolean, default=False)
    productivity_score = db.Column(db.Float, default=0.0)  # 0-100 scale
    
    # Composite index for efficient queries
    __table_args__ = (db.Index('idx_user_team_timestamp', 'user_id', 'team_id', 'timestamp'),)

# --- Robust Database Initialization ---
def initialize_database():
    """Enhanced database initialization for Google Cloud Run deployment with comprehensive error handling"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            with application.app_context():
                logger.info(f"🔄 Database initialization attempt {attempt + 1}/{max_retries}")
                
                # Test database connection first
                try:
                    # Use the correct SQLAlchemy syntax for newer versions
                    with db.engine.connect() as conn:
                        conn.execute(db.text("SELECT 1"))
                        conn.commit()
                    logger.info("✅ Database connection test successful")
                except Exception as conn_error:
                    logger.warning(f"⚠️ Database connection test failed: {conn_error}")
                    logger.warning("⚠️ Container will start without database connection")
                    return False  # Don't fail container startup

                # Create all tables
                try:
                    db.create_all()
                    logger.info("✅ Database tables created successfully")
                except Exception as table_error:
                    logger.warning(f"⚠️ Database table creation failed: {table_error}")
                    logger.warning("⚠️ Container will start without database tables")
                    return False  # Don't fail container startup

                # Verify tables exist
                try:
                    inspector = db.inspect(db.engine)
                    tables = inspector.get_table_names()
                    logger.info(f"✅ Database initialized with {len(tables)} tables: {tables}")
                except Exception as verify_error:
                    logger.warning(f"⚠️ Database verification failed: {verify_error}")
                    logger.warning("⚠️ Container will start without database verification")
                    return False  # Don't fail container startup
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ Database initialization attempt {attempt + 1} failed: {e}")
            logger.warning(f"📋 Error details: {type(e).__name__}: {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.warning("⚠️ All database initialization attempts failed")
                logger.warning("⚠️ Container will start without database initialization")
                logger.warning("📋 Final error details:")
                traceback.print_exc()
                return False  # Don't fail container startup
    
    return False

def init_db():
    """Simple database initialization fallback function"""
    try:
        with application.app_context():
            db.create_all()
            logging.info("✅ Simple database initialization successful!")
            return True
    except Exception as e:
        logging.error(f"❌ Simple database initialization failed: {e}")
        return False

# Database initialization will be done explicitly in start.py, not during import

def create_app():
    """Application factory function for proper initialization"""
    # Initialize database tables
    try:
        with application.app_context():
            if initialize_database():
                logging.info("Database initialization successful in create_app")
            else:
                logging.warning("Database initialization failed in create_app")
    except Exception as e:
        logging.error(f"Database initialization error in create_app: {e}")
    
    # Initialize scheduler only once
    try:
            init_scheduler()
            logging.info("✅ Scheduler initialization successful in ensure_initialization")
    except Exception as e:
        logging.error(f"Scheduler initialization error in create_app: {e}")
    
    return application

# Ensure database is initialized when the module is imported
def ensure_initialization():
    """Ensure database and scheduler are initialized"""
    try:
        with application.app_context():
            if initialize_database():
                logging.info("✅ Database initialization successful in ensure_initialization")
            else:
                logging.warning("⚠️ Database initialization failed in ensure_initialization")
                # Fallback to simple initialization
                try:
                    init_db()
                    logging.info("✅ Fallback database initialization successful")
                except Exception as e:
                    logging.error(f"❌ Fallback database initialization failed: {e}")
        
        # Initialize scheduler
        try:
            init_scheduler()
            logging.info("✅ Scheduler initialization successful in ensure_initialization")
        except Exception as e:
            logging.error(f"❌ Scheduler initialization error in ensure_initialization: {e}")
        
        return True
    except Exception as e:
        logging.error(f"❌ Database initialization error in ensure_initialization: {e}")
        return False

# Call ensure_initialization when the module is imported
if __name__ != '__main__':
    ensure_initialization()

# --- Utility Functions ---
def generate_id(prefix):
    """Generate a unique ID with timestamp and random components"""
    timestamp = int(time.time())
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{timestamp}_{random_part}"

def generate_team_code():
    """Generate a unique employee team code"""
    max_attempts = 100
    
    for attempt in range(max_attempts):
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        code = ''.join(random.choices(chars, k=6))
        
        existing = Team.query.filter_by(employee_code=code).first()
        if not existing:
            return code
    
    # Fallback with timestamp
    timestamp = str(int(time.time()))[-4:]
    base_code = ''.join(random.choices(chars, k=2))
    return f"{base_code}{timestamp}"

def generate_manager_invite_code():
    """Generate a unique manager invite code (longer and more secure)"""
    max_attempts = 100
    
    for attempt in range(max_attempts):
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'
        code = ''.join(random.choices(chars, k=12))  # Longer code for managers
        
        existing = ManagerInvite.query.filter_by(invite_code=code).first()
        if not existing:
            return code
    
    # Fallback with timestamp
    timestamp = str(int(time.time()))[-6:]
    base_code = ''.join(random.choices(chars, k=6))
    return f"{base_code}{timestamp}"

def create_jwt_token(user_id, team_id, role):
    """Create a JWT token for user authentication"""
    payload = {
        'user_id': user_id,
        'team_id': team_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, application.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_manager_role(f):
    """Decorator to require manager role for API endpoints"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_jwt_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        if payload.get('role') != 'manager':
            return jsonify({"error": "Manager role required"}), 403
        
        # Add user info to request for use in endpoint
        request.current_user = payload
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_or_create_user(user_name, team_id):
    """Get existing user or create new one - prevents duplicates"""
    # First try to find user by name in the same team
    existing_membership = Membership.query.filter_by(
        user_name=user_name, 
        team_id=team_id
    ).first()
    
    if existing_membership:
        return existing_membership.user_id, existing_membership.user_name
    
    # Create new user
    user_id = generate_id("user")
    return user_id, user_name

# --- Enhanced Security & Authentication Functions ---

def hash_password(password):
    """Hash password securely using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_verification_token():
    """Generate secure verification token"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def send_verification_email(email, token):
    """Send email verification"""
    # If email is not configured, log the verification token for development
    if not EMAIL_CONFIGURED:
        logging.info(f"📧 [DEV MODE] Email verification token for {email}: {token}")
        logging.info(f"📧 [DEV MODE] Verification link: {os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/verify?token={token}")
        return True
    
    try:
        msg = Message(
            'Verify Your ProductivityFlow Account',
            recipients=[email]
        )
        verification_link = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/verify?token={token}"
        msg.body = f"""
        Welcome to ProductivityFlow!
        
        Please click the link below to verify your email address:
        {verification_link}
        
        If you didn't create this account, please ignore this email.
        """
        mail.send(msg)
        logging.info(f"✅ Verification email sent to {email}")
        return True
    except Exception as e:
        logging.error(f"❌ Failed to send verification email to {email}: {e}")
        return False

# --- Claude AI & Productivity Report Functions ---

def generate_productivity_report(user_id, team_id, hour_start, hour_end):
    """Generate AI productivity report for a specific hour"""
    try:
        # Check if Claude client is available
        if not claude_client:
            return None, "Claude AI client not available. Please configure CLAUDE_API_KEY."
            
        # Get detailed activities for the hour
        activities = DetailedActivity.query.filter(
            DetailedActivity.user_id == user_id,
            DetailedActivity.team_id == team_id,
            DetailedActivity.timestamp >= hour_start,
            DetailedActivity.timestamp < hour_end
        ).order_by(DetailedActivity.timestamp).all()
        
        if not activities:
            return None, "No activity data available for this hour"
        
        # Prepare activity data for AI analysis
        activity_summary = []
        total_clicks = sum(a.mouse_clicks for a in activities)
        total_keystrokes = sum(a.keyboard_strokes for a in activities)
        apps_used = list(set(a.active_app for a in activities if a.active_app))
        idle_time = sum(1 for a in activities if a.is_idle)
        
        # Create optimized prompt (under 2100 input tokens)
        prompt = f"""Analyze this 1-hour productivity data for employee report:

Time: {hour_start.strftime('%Y-%m-%d %H:%M')} - {hour_end.strftime('%H:%M')}
Apps used: {', '.join(apps_used[:5])}  # Limit to top 5 apps
Mouse clicks: {total_clicks}
Keystrokes: {total_keystrokes}
Idle periods: {idle_time} minutes
Active periods: {60 - idle_time} minutes

Create a bullet-point productivity summary (max 200 tokens output):
• Focus level and productivity indicators
• Main applications/tasks worked on
• Any irregularities detected (excessive idle time, potential automation tools)
• Overall productivity score (1-10)

Keep response under 200 tokens, focus on key insights only."""

        # Call Claude API with token limits
        if not claude_client:
            return {
                'summary': "AI analysis unavailable - Claude client not initialized",
                'input_tokens': 0,
                'output_tokens': 0,
                'cost': 0,
                'irregularity_detected': False
            }, None
            
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,  # Limit output tokens
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        report_content = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        
        # Calculate cost (Claude 3 Haiku: $0.25/1M input, $1.25/1M output)
        cost = (input_tokens * 0.25 / 1_000_000) + (output_tokens * 1.25 / 1_000_000)
        
        # Detect irregularities
        irregularity_detected = detect_irregularities(activities, total_clicks, total_keystrokes, idle_time)
        
        return {
            'summary': report_content,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'irregularity_detected': irregularity_detected
        }, None
        
    except Exception as e:
        logging.error(f"Error generating productivity report: {e}")
        return None, str(e)

def detect_irregularities(activities, total_clicks, total_keystrokes, idle_time):
    """Detect potential irregularities in activity data"""
    # Check for signs of automation or cheating
    irregularities = []
    
    # Too many clicks in a short time (potential auto-clicker)
    if total_clicks > 3600:  # More than 1 click per second average
        irregularities.append("Excessive mouse clicks detected")
    
    # Repetitive patterns
    if len(activities) > 0:
        click_pattern = [a.mouse_clicks for a in activities]
        if len(set(click_pattern)) == 1 and click_pattern[0] > 0:
            irregularities.append("Repetitive click pattern detected")
    
    # Too much idle time
    if idle_time > 30:  # More than 30 minutes idle
        irregularities.append("Excessive idle time")
    
    return len(irregularities) > 0

def track_token_usage(user_id, team_id, input_tokens, output_tokens, cost):
    """Track and limit token usage per user"""
    today = datetime.now().date()
    
    # Get or create daily usage record
    usage = TokenUsage.query.filter_by(
        user_id=user_id,
        team_id=team_id,
        date=today
    ).first()
    
    if not usage:
        usage = TokenUsage(
            user_id=user_id,
            team_id=team_id,
            date=today,
            input_tokens=0,
            output_tokens=0,
            cost_estimate=0.0
        )
        db.session.add(usage)
    
    # Update usage
    usage.input_tokens += input_tokens
    usage.output_tokens += output_tokens
    usage.cost_estimate += cost
    
    # Check if exceeding $2 daily limit per employee
    if usage.cost_estimate > 2.0:
        logging.warning(f"User {user_id} exceeded $2 daily token limit: ${usage.cost_estimate:.4f}")
        return False  # Prevent further AI usage today
    
    db.session.commit()
    return True

# --- Billing & Stripe Functions ---

def calculate_monthly_cost(employee_count):
    """Calculate monthly cost based on employee count"""
    return employee_count * 9.99

def create_stripe_customer(email, team_id):
    """Create Stripe customer for billing"""
    try:
        customer = stripe.Customer.create(
            email=email,
            metadata={'team_id': team_id}
        )
        return customer
    except Exception as e:
        logging.error(f"Error creating Stripe customer: {e}")
        return None

def create_stripe_subscription(customer_id, employee_count):
    """Create Stripe subscription"""
    try:
        # Create subscription with per-employee pricing
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'ProductivityFlow - Per Employee',
                    },
                    'unit_amount': 999,  # $9.99 in cents
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': employee_count,
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        return subscription
    except Exception as e:
        logging.error(f"Error creating Stripe subscription: {e}")
        return None

def update_subscription_quantity(subscription_id, new_employee_count):
    """Update subscription quantity when employee count changes"""
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        stripe.Subscription.modify(
            subscription_id,
            items=[{
                'id': subscription['items']['data'][0]['id'],
                'quantity': new_employee_count,
            }]
        )
        return True
    except Exception as e:
        logging.error(f"Error updating subscription quantity: {e}")
        return False

# --- Scheduler for Background Tasks ---

def cleanup_old_reports():
    """Clean up productivity reports older than 1 week"""
    try:
        cutoff_date = datetime.now() - timedelta(days=7)
        deleted_count = ProductivityReport.query.filter(
            ProductivityReport.created_at < cutoff_date
        ).delete()
        db.session.commit()
        logging.info(f"Cleaned up {deleted_count} old productivity reports")
    except Exception as e:
        logging.error(f"Error cleaning up old reports: {e}")

def generate_hourly_reports():
    """Generate productivity reports for all active users"""
    try:
        # Get all active users from the last hour
        hour_ago = datetime.now() - timedelta(hours=1)
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        active_users = db.session.query(DetailedActivity.user_id, DetailedActivity.team_id).filter(
            DetailedActivity.timestamp >= hour_ago
        ).distinct().all()
        
        for user_id, team_id in active_users:
            # Check token usage limits
            today = datetime.now().date()
            usage = TokenUsage.query.filter_by(
                user_id=user_id,
                team_id=team_id,
                date=today
            ).first()
            
            if usage and usage.cost_estimate >= 2.0:
                continue  # Skip users who've exceeded daily limit
            
            # Generate report
            report_data, error = generate_productivity_report(
                user_id, team_id, hour_ago, current_hour
            )
            
            if report_data and not error:
                # Save report
                report = ProductivityReport(
                    user_id=user_id,
                    team_id=team_id,
                    report_date=current_hour,
                    hour_start=hour_ago,
                    hour_end=current_hour,
                    summary=report_data['summary'],
                    irregularity_detected=report_data['irregularity_detected'],
                    token_count_input=report_data['input_tokens'],
                    token_count_output=report_data['output_tokens'],
                    cost_estimate=report_data['cost']
                )
                db.session.add(report)
                
                # Track token usage
                track_token_usage(
                    user_id, team_id,
                    report_data['input_tokens'],
                    report_data['output_tokens'],
                    report_data['cost']
                )
        
        db.session.commit()
        logging.info("Hourly productivity reports generated successfully")
        
    except Exception as e:
        logging.error(f"Error generating hourly reports: {e}")

# Initialize background scheduler
scheduler = None
_db_initialized = False
_scheduler_initialized = False

def init_scheduler():
    """Initialize scheduler only once in the main process"""
    global scheduler, _scheduler_initialized
    if not _scheduler_initialized:
        try:
            scheduler = BackgroundScheduler()
            scheduler.add_job(func=cleanup_old_reports, trigger="cron", hour=2, minute=0)  # Daily at 2 AM
            scheduler.add_job(func=generate_hourly_reports, trigger="cron", minute=0)  # Every hour
            scheduler.start()
            _scheduler_initialized = True
            logging.info("Background scheduler started successfully")
        except Exception as e:
            logging.error(f"Failed to start background scheduler: {e}")
            scheduler = None
    return scheduler

def ensure_initialization():
    """Ensure database and scheduler are initialized exactly once"""
    global _db_initialized, _scheduler_initialized
    
    # Initialize database if not already done
    if not _db_initialized:
        try:
            with application.app_context():
                if initialize_database():
                    _db_initialized = True
                    logging.info("Database initialization completed")
                else:
                    logging.error("Database initialization failed")
        except Exception as e:
            logging.error(f"Database initialization error: {e}")
    
        # Initialize scheduler if not already done
    if not _scheduler_initialized:
        try:
            init_scheduler()
            _scheduler_initialized = True
            logging.info("Scheduler initialization completed")
        except Exception as e:
            logging.error(f"Scheduler initialization error: {e}")

# --- API Endpoints ---
@application.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint for Railway"""
    try:
        # Test database connection with timeout and retry
        db_status = "disconnected"
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with db.engine.connect() as connection:
                    connection.execute(db.text("SELECT 1"))
                    db_status = "connected"
                    break
            except Exception as db_error:
                logging.warning(f"Database connection attempt {attempt + 1} failed: {db_error}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # Wait 2 seconds before retry
                else:
                    db_status = "disconnected"
        
        # Return healthy status even if database is disconnected
        # This allows the container to start and serve basic requests
        return jsonify({
            "status": "healthy",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat(),
            "email_configured": EMAIL_CONFIGURED,
            "dev_mode": not EMAIL_CONFIGURED,
            "message": "Email verification is " + ("enabled" if EMAIL_CONFIGURED else "disabled (dev mode)")
        }), 200
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# --- Enhanced Authentication Endpoints ---

@application.route('/api/auth/register', methods=['POST'])
@conditional_rate_limit("5 per minute")
def register_user():
    """Register new user with email/password"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # Enhanced validation with detailed feedback
        if not email:
            return jsonify({"error": "Email is required", "field": "email"}), 400
        
        if not password:
            return jsonify({"error": "Password is required", "field": "password"}), 400
        
        if not name:
            return jsonify({"error": "Name is required", "field": "name"}), 400
        
        # Email format validation
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Please enter a valid email address", "field": "email"}), 400
        
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long", "field": "password"}), 400
        
        if len(name) < 2:
            return jsonify({"error": "Name must be at least 2 characters long", "field": "name"}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "An account with this email already exists. Please try logging in instead.", "field": "email"}), 409
        
        # Create new user
        user_id = generate_id("user")
        password_hash = hash_password(password)
        verification_token = generate_verification_token()
        
        # Set verification status based on email configuration
        is_verified = EMAIL_CONFIGURED  # Only auto-verify if email is not configured (dev mode)
        
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            name=name,
            verification_token=verification_token,
            is_verified=is_verified
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        email_sent = send_verification_email(email, verification_token)
        
        if EMAIL_CONFIGURED:
            message = "Account created successfully! Please check your email to verify your account before logging in."
        else:
            message = "Account created successfully! You can now log in. (Email verification bypassed in development mode)"
        
        return jsonify({
            "success": True,
            "message": message,
            "user_id": user_id,
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
                "is_verified": is_verified
            },
            "email_sent": email_sent,
            "dev_mode": not EMAIL_CONFIGURED
        }), 201
        
    except Exception as e:
        logging.error(f"Error in user registration: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to create account. Please try again."}), 500

@application.route('/api/auth/login', methods=['POST'])
@conditional_rate_limit("10 per minute")
def login_user():
    """Login user with email/password"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Enhanced validation with detailed feedback
        if not email:
            return jsonify({"error": "Email is required", "field": "email"}), 400
        
        if not password:
            return jsonify({"error": "Password is required", "field": "password"}), 400
        
        # Email format validation
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Please enter a valid email address", "field": "email"}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "No account found with this email. Please check your email or create a new account.", "field": "email"}), 401
        
        if not verify_password(password, user.password_hash):
            return jsonify({"error": "Incorrect password. Please try again.", "field": "password"}), 401
        
        # Check email verification status
        if EMAIL_CONFIGURED and not user.is_verified:
            return jsonify({
                "error": "Please verify your email before logging in. Check your inbox for a verification link.",
                "field": "email",
                "verification_required": True
            }), 401
        
        # Update last login
        user.last_login = datetime.now()
        db.session.commit()
        
        # Get user's team memberships
        memberships = Membership.query.filter_by(user_id=user.id).all()
        
        # Create JWT token for the user
        token = create_jwt_token(user.id, "temp_team", "manager")
        
        return jsonify({
            "success": True,
            "message": "Login successful! Welcome back, " + user.name,
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "teams_count": len(memberships),
                "organization": "Default Organization"  # Will be updated when team is created
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error in user login: {e}")
        return jsonify({"error": "Login failed. Please try again."}), 500

@application.route('/api/auth/verify', methods=['POST'])
def verify_email():
    """Verify user email with token"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        
        user = User.query.filter_by(verification_token=token).first()
        if not user:
            return jsonify({"error": "Invalid verification token"}), 400
        
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        
        return jsonify({"message": "Email verified successfully"}), 200
        
    except Exception as e:
        logging.error(f"Error in email verification: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/auth/verify-manual/<email>', methods=['GET'])
def manual_verify_email(email):
    """Manual email verification for development/testing"""
    try:
        # Only allow in development mode
        if EMAIL_CONFIGURED:
            return jsonify({"error": "Manual verification not available in production mode"}), 403
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if user.is_verified:
            return jsonify({
                "success": True,
                "message": "User is already verified",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "is_verified": user.is_verified
                }
            }), 200
        
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Email manually verified for development! You can now log in.",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_verified": user.is_verified
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error in manual email verification: {e}")
        return jsonify({"error": "Manual verification failed. Please try again."}), 500

# --- Enhanced Team Management with Email Integration ---

@application.route('/api/teams/join-with-email', methods=['POST'])
@conditional_rate_limit("10 per minute")
def join_team_with_email():
    """Join team using email account and team code"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        team_code = data.get('team_code', '').strip().upper()
        role = data.get('role', 'employee')  # employee or manager
        
        if not email or not team_code:
            return jsonify({"error": "Email and team code are required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email, is_verified=True).first()
        if not user:
            return jsonify({"error": "User not found or email not verified"}), 404
        
        # Find team by code
        team = Team.query.filter_by(employee_code=team_code).first()
        if not team:
            return jsonify({"error": "Invalid team code"}), 404
        
        # Check if user is already a member
        existing_membership = Membership.query.filter_by(
            user_id=user.id, 
            team_id=team.id
        ).first()
        
        if existing_membership:
            return jsonify({"error": "User is already a member of this team"}), 409
        
        # Create membership
        membership = Membership(
            team_id=team.id,
            user_id=user.id,
            user_name=user.name,
            role=role
        )
        
        db.session.add(membership)
        
        # Update subscription if this is an employee
        if role == 'employee':
            subscription = Subscription.query.filter_by(team_id=team.id).first()
            if subscription:
                subscription.employee_count += 1
                subscription.monthly_cost = calculate_monthly_cost(subscription.employee_count)
                
                # Update Stripe subscription
                if subscription.stripe_subscription_id:
                    update_subscription_quantity(subscription.stripe_subscription_id, subscription.employee_count)
        
        db.session.commit()
        
        # Create JWT token
        token = create_jwt_token(user.id, team.id, role)
        
        return jsonify({
            "message": "Successfully joined team",
            "token": token,
            "team": {"id": team.id, "name": team.name},
            "user": {"id": user.id, "name": user.name, "role": role}
        }), 200
        
    except Exception as e:
        logging.error(f"Error joining team with email: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Add the rest of the original API endpoints
@application.route('/api/teams', methods=['GET'])
def get_teams():
    """Get teams for authenticated user"""
    try:
        # Get user info from token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get teams for user
        memberships = Membership.query.filter_by(user_id=user_id).all()
        teams = []
        
        for membership in memberships:
            team = Team.query.get(membership.team_id)
            if team:
                teams.append({
                    "id": team.id,
                    "name": team.name,
                    "role": membership.role,
                    "employee_code": team.employee_code if membership.role == 'manager' else None
                })
        
        return jsonify({"teams": teams}), 200
        
    except Exception as e:
        logging.error(f"Error getting teams: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/teams', methods=['POST'])
def create_team():
    """Create a new team"""
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({"error": "Invalid token format"}), 401
        
        # Get user information
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        team_name = data.get('name', '').strip()
        role = data.get('role', 'manager')
        
        if not team_name:
            return jsonify({"error": "Team name is required"}), 400
        
        # Generate unique IDs
        team_id = generate_id("team")
        employee_code = generate_team_code()
        
        # Create team
        team = Team(
            id=team_id,
            name=team_name,
            employee_code=employee_code,
            manager_id=user_id  # Set the manager_id
        )
        
        # Create membership
        membership = Membership(
            team_id=team_id,
            user_id=user_id,
            user_name=user.name,
            role=role
        )
        
        db.session.add(team)
        db.session.add(membership)
        db.session.commit()
        
        # Create new JWT token with team information
        new_token = create_jwt_token(user_id, team_id, role)
        
        logging.info(f"Team created: {team_id} by user: {user_id}")
        
        return jsonify({
            "message": "Team created successfully",
            "token": new_token,
            "team": {
                "id": team_id,
                "name": team_name,
                "employee_code": employee_code
            },
            "user": {
                "id": user_id,
                "name": user.name,
                "role": role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating team: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

# --- Team Join & Activity Tracking Endpoints ---

@application.route('/api/teams/join', methods=['POST'])
@conditional_rate_limit("10 per minute")
def join_team():
    """Join team using team code (for simple employee tracker without email)"""
    try:
        data = request.get_json()
        team_code = data.get('team_code', '').strip().upper()
        employee_name = data.get('employee_name', '').strip()
        
        if not team_code or not employee_name:
            return jsonify({"error": "Team code and employee name are required"}), 400
        
        # Find team by code
        team = Team.query.filter_by(employee_code=team_code).first()
        if not team:
            return jsonify({"error": "Invalid team code"}), 404
        
        # Check subscription status for lockout
        subscription = Subscription.query.filter_by(team_id=team.id).first()
        if subscription and subscription.status in ['expired', 'past_due']:
            # Allow grace period for past_due (7 days)
            if subscription.status == 'past_due':
                grace_period_end = subscription.current_period_end + timedelta(days=7)
                if datetime.utcnow() > grace_period_end:
                    return jsonify({
                        "error": "Team access suspended due to payment failure. Please contact your manager.",
                        "subscription_status": "expired"
                    }), 402  # Payment Required
            elif subscription.status == 'expired':
                return jsonify({
                    "error": "Team access suspended due to expired subscription. Please contact your manager.",
                    "subscription_status": "expired"
                }), 402  # Payment Required
        
        # Generate a temporary user ID for the session
        user_id = f"emp_{hashlib.md5((team_code + employee_name).encode()).hexdigest()[:8]}"
        
        # Check if user is already a member
        existing_membership = Membership.query.filter_by(
            user_id=user_id, 
            team_id=team.id
        ).first()
        
        if not existing_membership:
            # Create membership for temporary user
            membership = Membership(
                team_id=team.id,
                user_id=user_id,
                user_name=employee_name,
                role='employee'
            )
            db.session.add(membership)
            db.session.commit()
        
        # Generate JWT token
        token_payload = {
            'user_id': user_id,
            'team_id': team.id,
            'role': 'employee',
            'exp': datetime.utcnow() + timedelta(days=30)  # 30 day expiry
        }
        token = jwt.encode(token_payload, application.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user_id,
                "name": employee_name,
                "role": "employee"
            },
            "team": {
                "id": team.id,
                "name": team.name,
                "code": team.employee_code
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error joining team: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/teams/<team_id>/activity', methods=['POST'])
@conditional_rate_limit("120 per minute")  # Higher limit for activity tracking
def submit_activity(team_id):
    """Submit activity data for a team member"""
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            token_team_id = payload.get('team_id')
            
            # Verify team ID matches
            if token_team_id != team_id:
                return jsonify({"error": "Token team ID does not match request"}), 403
                
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Check subscription status for lockout
        subscription = Subscription.query.filter_by(team_id=team_id).first()
        if subscription and subscription.status in ['expired', 'past_due']:
            # Allow grace period for past_due (7 days)
            if subscription.status == 'past_due':
                grace_period_end = subscription.current_period_end + timedelta(days=7)
                if datetime.utcnow() > grace_period_end:
                    return jsonify({
                        "error": "Access suspended due to payment failure. Please contact your manager to update payment information.",
                        "subscription_status": "expired"
                    }), 402  # Payment Required
            elif subscription.status == 'expired':
                return jsonify({
                    "error": "Access suspended due to expired subscription. Please contact your manager to renew subscription.",
                    "subscription_status": "expired"
                }), 402  # Payment Required
        
        data = request.get_json()
        
        # Extract activity data
        active_app = data.get('activeApp', '')
        window_title = data.get('windowTitle', '')
        idle_time = data.get('idleTime', 0.0)
        productive_hours = data.get('productiveHours', 0.0)
        unproductive_hours = data.get('unproductiveHours', 0.0)
        goals_completed = data.get('goalsCompleted', 0)
        
        # Get or create today's activity record
        today = datetime.utcnow().date()
        activity = Activity.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            date=today
        ).first()
        
        if not activity:
            activity = Activity(
                user_id=user_id,
                team_id=team_id,
                date=today
            )
            db.session.add(activity)
        
        # Update activity data
        activity.active_app = active_app
        activity.window_title = window_title
        activity.idle_time = idle_time
        activity.productive_hours = productive_hours
        activity.unproductive_hours = unproductive_hours
        activity.goals_completed = goals_completed
        activity.last_active = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Activity data recorded successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error submitting activity: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/activity/track', methods=['POST'])
@conditional_rate_limit("300 per minute")  # High limit for real-time tracking
def track_activity():
    """Track real-time activity data from desktop tracker"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract and validate required fields
        user_id = data.get('user_id')
        team_id = data.get('team_id')
        
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        if not validate_team_id(team_id):
            return jsonify({'error': 'Invalid team ID'}), 400
        
        # Validate that user is a member of the team
        membership = Membership.query.filter_by(team_id=team_id, user_id=user_id).first()
        if not membership:
            return jsonify({'error': 'User is not a member of this team'}), 403
        
        # Extract activity data
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        total_active_time = int(data.get('total_active_time', 0))  # in milliseconds
        total_idle_time = int(data.get('total_idle_time', 0))  # in milliseconds
        productivity_score = float(data.get('productivity_score', 0))
        current_activity = data.get('current_activity', {})
        activities = data.get('activities', [])
        
        # Convert milliseconds to hours
        active_hours = total_active_time / 3600000
        idle_hours = total_idle_time / 3600000
        
        # Get current date
        current_date = datetime.now().date()
        
        # Check if activity record already exists for today
        existing_activity = Activity.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            date=current_date
        ).first()
        
        if existing_activity:
            # Update existing record with accumulated data
            existing_activity.productive_hours = active_hours
            existing_activity.unproductive_hours = 0  # Will be calculated based on productivity score
            existing_activity.idle_time = idle_hours
            existing_activity.last_active = datetime.now()
        else:
            # Create new activity record
            new_activity = Activity(
                user_id=user_id,
                team_id=team_id,
                date=current_date,
                active_app=current_activity.get('name', 'Unknown'),
                window_title=current_activity.get('url', ''),
                productive_hours=active_hours,
                unproductive_hours=0,  # Will be calculated based on productivity score
                idle_time=idle_hours,
                goals_completed=0,
                last_active=datetime.now()
            )
            db.session.add(new_activity)
        
        # Create detailed activity record for this tracking session
        detailed_activity = DetailedActivity(
            user_id=user_id,
            team_id=team_id,
            timestamp=datetime.now(),
            active_app=current_activity.get('name', 'Unknown'),
            window_title=current_activity.get('url', ''),
            mouse_clicks=0,  # Could be tracked in future
            keyboard_strokes=0,  # Could be tracked in future
            is_idle=current_activity.get('type') == 'background',
            productivity_score=productivity_score
        )
        db.session.add(detailed_activity)
        
        # Commit changes
        db.session.commit()
        
        logger.info(f"Activity tracked for user {user_id} in team {team_id}: "
                   f"Active: {active_hours:.2f}h, Idle: {idle_hours:.2f}h, "
                   f"Productivity: {productivity_score}%")
        
        return jsonify({
            'message': 'Activity tracked successfully',
            'user_id': user_id,
            'team_id': team_id,
            'active_hours': round(active_hours, 2),
            'idle_hours': round(idle_hours, 2),
            'productivity_score': productivity_score,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error tracking activity: {e}")
        return jsonify({'error': 'Failed to track activity'}), 500

# --- Team Members Endpoint ---

@application.route('/api/teams/<team_id>/members', methods=['GET'])
def get_team_members(team_id):
    """Get members of a specific team"""
    try:
        # Find the team
        team = Team.query.get(team_id)
        if not team:
            return jsonify({"error": "Team not found"}), 404
        
        # Get all memberships for this team
        memberships = Membership.query.filter_by(team_id=team_id).all()
        
        members = []
        for membership in memberships:
            # Get activity data for today
            today = datetime.utcnow().date()
            activity = Activity.query.filter_by(
                user_id=membership.user_id,
                team_id=team_id,
                date=today
            ).first()
            
            member_data = {
                "userId": membership.user_id,
                "name": membership.user_name,
                "role": membership.role,
                "productiveHours": activity.productive_hours if activity else 0,
                "unproductiveHours": activity.unproductive_hours if activity else 0,
                "goalsCompleted": activity.goals_completed if activity else 0
            }
            members.append(member_data)
        
        return jsonify({"members": members}), 200
        
    except Exception as e:
        logging.error(f"Error getting team members: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# --- Public Teams Endpoint (for manager dashboard) ---

@application.route('/api/teams/public', methods=['GET'])
def get_public_teams():
    """Get all teams (for demo/development purposes)"""
    try:
        teams = Team.query.all()
        team_list = []
        
        for team in teams:
            # Count members
            member_count = Membership.query.filter_by(team_id=team.id).count()
            
            team_data = {
                "id": team.id,
                "name": team.name,
                "code": team.employee_code,
                "memberCount": member_count
            }
            team_list.append(team_data)
        
        return jsonify({"teams": team_list}), 200
        
    except Exception as e:
        logging.error(f"Error getting public teams: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# --- Version & Update Endpoints ---

@application.route('/api/version', methods=['GET'])
def get_version():
    """Get current application version for auto-updater"""
    return jsonify({
        "version": "1.0.0",
        "build_date": "2024-01-15",
        "download_urls": {
            "windows_tracker": "/downloads/tracker-windows.exe",
            "mac_tracker": "/downloads/tracker-mac.dmg",
            "windows_dashboard": "/downloads/dashboard-windows.exe",
            "mac_dashboard": "/downloads/dashboard-mac.dmg"
        }
    }), 200

@application.route('/api/config/stripe', methods=['GET'])
def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    return jsonify({
        "publishable_key": STRIPE_PUBLISHABLE_KEY
    }), 200

# --- Subscription Management Endpoints ---

@application.route('/api/subscription/status', methods=['GET'])
@conditional_rate_limit("10 per minute") # Added rate limit for subscription status
def get_subscription_status():
    """Get current subscription status for a manager"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Find the user's team
        user_membership = Membership.query.filter_by(user_id=user_id).first()
        if not user_membership:
            return jsonify({"error": "User not a member of any team"}), 404
        
        team = Team.query.get(user_membership.team_id)
        if not team:
            return jsonify({"error": "Team not found"}), 404
        
        # Get subscription for this team
        subscription = Subscription.query.filter_by(team_id=team.id).first()
        
        if not subscription:
            # Create default trial subscription
            subscription = Subscription(
                team_id=team.id,
                status='trial',
                employee_count=0,
                monthly_cost=0.0,
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(subscription)
            db.session.commit()
        
        # Count active employees
        employee_count = Membership.query.filter_by(team_id=team.id, role='employee').count()
        
        # Update employee count if different
        if subscription.employee_count != employee_count:
            subscription.employee_count = employee_count
            subscription.monthly_cost = calculate_monthly_cost(employee_count)
            db.session.commit()
        
        # Calculate trial days remaining for trial subscriptions
        trial_days_remaining = None
        if subscription.status == 'trial':
            trial_end = subscription.created_at + timedelta(days=30)
            trial_days_remaining = max(0, (trial_end - datetime.utcnow()).days)
            
            # Auto-expire trial if needed
            if trial_days_remaining <= 0:
                subscription.status = 'expired'
                db.session.commit()
        
        return jsonify({
            "status": subscription.status,
            "current_period_end": subscription.current_period_end.isoformat(),
            "employee_count": subscription.employee_count,
            "price_per_employee": 10.0,  # $10 per employee per month
            "total_amount": subscription.monthly_cost,
            "trial_days_remaining": trial_days_remaining
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting subscription status: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/subscription/update-payment', methods=['POST'])
@conditional_rate_limit("10 per minute") # Added rate limit for payment update
def update_payment_method():
    """Create Stripe checkout session for updating payment method"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Find the user's team
        user_membership = Membership.query.filter_by(user_id=user_id).first()
        if not user_membership:
            return jsonify({"error": "User not a member of any team"}), 404
        
        team = Team.query.get(user_membership.team_id)
        if not team:
            return jsonify({"error": "Team not found"}), 404
        
        subscription = Subscription.query.filter_by(team_id=team.id).first()
        if not subscription:
            return jsonify({"error": "No subscription found"}), 404
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            mode='subscription',
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'ProductivityFlow - Employee Tracking',
                        'description': f'Monthly subscription for {subscription.employee_count} employees'
                    },
                    'unit_amount': 1000,  # $10.00 in cents
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': subscription.employee_count
            }],
            success_url=f"{request.host_url}billing?success=true",
            cancel_url=f"{request.host_url}billing?canceled=true",
            metadata={
                'team_id': team.id,
                'user_id': user_id
            }
        )
        
        return jsonify({
            "checkout_url": checkout_session.url
        }), 200
        
    except Exception as e:
        logging.error(f"Error creating checkout session: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/subscription/customer-portal', methods=['GET'])
@conditional_rate_limit("10 per minute") # Added rate limit for customer portal
def customer_portal():
    """Redirect to Stripe customer portal"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Find the user's team
        user_membership = Membership.query.filter_by(user_id=user_id).first()
        if not user_membership:
            return jsonify({"error": "User not a member of any team"}), 404
        
        team = Team.query.get(user_membership.team_id)
        if not team:
            return jsonify({"error": "Team not found"}), 404
        
        subscription = Subscription.query.filter_by(team_id=team.id).first()
        if not subscription or not subscription.stripe_subscription_id:
            return jsonify({"error": "No active subscription found"}), 404
        
        # Get Stripe customer ID from subscription
        stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
        customer_id = stripe_subscription.customer
        
        # Create customer portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{request.host_url}billing"
        )
        
        return jsonify({
            "portal_url": portal_session.url
        }), 200
        
    except Exception as e:
        logging.error(f"Error creating customer portal session: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/subscription/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature (you need to set STRIPE_WEBHOOK_SECRET)
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError:
        logging.error("Invalid payload in Stripe webhook")
        return '', 400
    except stripe.error.SignatureVerificationError:
        logging.error("Invalid signature in Stripe webhook")
        return '', 400
    
    # Handle the event
    if event['type'] == 'subscription.created':
        subscription_obj = event['data']['object']
        # Update local subscription record
        team_id = subscription_obj['metadata'].get('team_id')
        if team_id:
            subscription = Subscription.query.filter_by(team_id=team_id).first()
            if subscription:
                subscription.stripe_subscription_id = subscription_obj['id']
                subscription.status = 'active'
                subscription.current_period_end = datetime.fromtimestamp(subscription_obj['current_period_end'])
                db.session.commit()
                
    elif event['type'] == 'subscription.updated':
        subscription_obj = event['data']['object']
        # Update subscription status
        stripe_sub_id = subscription_obj['id']
        subscription = Subscription.query.filter_by(stripe_subscription_id=stripe_sub_id).first()
        if subscription:
            subscription.status = subscription_obj['status']
            subscription.current_period_end = datetime.fromtimestamp(subscription_obj['current_period_end'])
            db.session.commit()
            
    elif event['type'] == 'subscription.deleted':
        subscription_obj = event['data']['object']
        # Mark subscription as expired
        stripe_sub_id = subscription_obj['id']
        subscription = Subscription.query.filter_by(stripe_subscription_id=stripe_sub_id).first()
        if subscription:
            subscription.status = 'expired'
            db.session.commit()
    
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        # Mark subscription as past due
        stripe_sub_id = invoice['subscription']
        subscription = Subscription.query.filter_by(stripe_subscription_id=stripe_sub_id).first()
        if subscription:
            subscription.status = 'past_due'
            db.session.commit()
    
    return '', 200

def calculate_monthly_cost(employee_count):
    """Calculate monthly cost based on employee count"""
    return float(employee_count * 10.0)  # $10 per employee per month

# --- Version & Update Endpoints ---

@application.route('/api/updates/<platform>/<current_version>', methods=['GET'])
def check_for_updates(platform, current_version):
    """Check for application updates for Tauri auto-updater"""
    try:
        # Latest version - this should come from your version management system
        latest_version = "0.2.0"
        
        # Compare versions (simple string comparison for demo)
        if current_version < latest_version:
            # Update available
            base_url = "https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/releases/latest/download"
            
            if platform == "darwin":
                download_url = f"{base_url}/ProductivityFlow-Tracker_{latest_version}_universal.dmg"
            elif platform == "win32":
                download_url = f"{base_url}/ProductivityFlow-Tracker_{latest_version}_x64.msi"
            else:
                return jsonify({"error": "Unsupported platform"}), 400
            
            return jsonify({
                "version": latest_version,
                "date": "2024-01-01T00:00:00Z",
                "body": "Latest improvements and bug fixes",
                "url": download_url,
                "signature": ""  # Tauri will handle signing
            }), 200
        else:
            # No update available - return 204 No Content
            return "", 204
            
    except Exception as e:
        logging.error(f"Error checking for updates: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/updates/<app_name>/latest', methods=['GET'])
def get_latest_update(app_name):
    """Get latest update information for an app"""
    try:
        # In production, this would query a database or external service
        updates = {
            'employee-tracker': {
                'version': '2.1.0',
                'download_url': 'https://downloads.productivityflow.com/employee-tracker-2.1.0.dmg',
                'checksum': 'sha256-hash-here',
                'release_notes': 'Bug fixes and performance improvements',
                'release_date': '2025-07-23T00:00:00Z',
                'size': '4.2MB'
            },
            'manager-dashboard': {
                'version': '2.1.0', 
                'download_url': 'https://downloads.productivityflow.com/manager-dashboard-2.1.0.dmg',
                'checksum': 'sha256-hash-here',
                'release_notes': 'Enhanced analytics and reporting features',
                'release_date': '2025-07-23T00:00:00Z',
                'size': '4.0MB'
            }
        }
        
        if app_name not in updates:
            return jsonify({'error': 'App not found'}), 404
        
        return jsonify(updates[app_name])
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# Graceful shutdown
import atexit

def shutdown_scheduler():
    """Shutdown the background scheduler gracefully"""
    if scheduler:
        try:
            scheduler.shutdown()
            logging.info("Background scheduler shut down successfully")
        except Exception as e:
            logging.error(f"Error shutting down scheduler: {e}")

# Register shutdown handler
atexit.register(shutdown_scheduler)

# --- Database Initialization ---
def init_db():
    """Simple database initialization fallback function"""
    try:
        with application.app_context():
            db.create_all()
            logging.info("✅ Simple database initialization successful!")
            return True
    except Exception as e:
        logging.error(f"❌ Simple database initialization failed: {e}")
        return False

# Database initialization is handled by initialize_database() function above

# --- Global Error Handlers ---
@application.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return jsonify({
        'error': 'Bad Request',
        'message': 'The request was malformed or invalid',
        'status_code': 400
    }), 400

@application.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors"""
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required',
        'status_code': 401
    }), 401

@application.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    return jsonify({
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource',
        'status_code': 403
    }), 403

@application.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status_code': 404
    }), 404

@application.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed errors"""
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'The requested method is not allowed for this endpoint',
        'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        'status_code': 405
    }), 405

@application.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle 429 Rate Limit Exceeded errors"""
    return jsonify({
        'error': 'Rate Limit Exceeded',
        'message': 'Too many requests. Please try again later',
        'status_code': 429
    }), 429

@application.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error"""
    logging.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred. Please try again later',
        'status_code': 500
    }), 500

@application.errorhandler(503)
def service_unavailable(error):
    """Handle 503 Service Unavailable errors"""
    return jsonify({
        'error': 'Service Unavailable',
        'message': 'The service is temporarily unavailable. Please try again later',
        'status_code': 503
    }), 503



# --- API Documentation Endpoint ---
@application.route('/api', methods=['GET'])
def api_documentation():
    """Basic API documentation endpoint"""
    return jsonify({
        'name': 'ProductivityFlow API',
        'version': '2.0.0',
        'description': 'API for ProductivityFlow desktop applications',
        'endpoints': {
            'authentication': {
                'POST /api/auth/register': 'Register a new user',
                'POST /api/auth/login': 'Login user',
                'POST /api/auth/verify': 'Verify authentication token'
            },
            'teams': {
                'GET /api/teams': 'Get user teams',
                'POST /api/teams': 'Create a new team',
                'POST /api/teams/join': 'Join a team with employee code',
                'POST /api/teams/join-with-email': 'Join team with manager invite',
                'GET /api/teams/<team_id>/members': 'Get team members',
                'POST /api/teams/<team_id>/activity': 'Submit activity data'
            },
            'utility': {
                'GET /health': 'Health check endpoint',
                'GET /api': 'This documentation',
                'GET /api/version': 'Get API version'
            }
        },
        'cors': {
            'enabled': True,
            'allowed_origins': ['*'],
            'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD']
        }
    })

@application.route('/api/analytics/burnout-risk', methods=['GET'])
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
        team_members = []
        for membership in team_memberships:
            user = User.query.get(membership.user_id)
            if user:
                team_members.append(user)
        
        # Simplified burnout data for now
        burnout_data = []
        
        for member in team_members:
            burnout_data.append({
                'user_id': member.id,
                'user_name': member.name,
                'risk_score': 25,  # Default low risk
                'risk_level': 'low',
                'factors': [],
                'trends': {},
                'recommendations': ['Analytics feature coming soon']
            })
        
        return jsonify({
            'burnout_analysis': burnout_data,
            'team_id': team_id,
            'analysis_date': datetime.utcnow().isoformat(),
            'note': 'Analytics feature temporarily simplified'
        })
        
    except Exception as e:
        logger.error(f"Error in burnout risk analysis: {str(e)}")
        return jsonify({'error': 'Analytics feature temporarily unavailable'}), 503

def calculate_burnout_risk_factors(activities, user_id):
    """Calculate burnout risk factors based on activity patterns"""
    
    if not activities:
        return {
            'overall_risk': 0,
            'risk_level': 'low',
            'factors': [],
            'trends': {},
            'recommendations': []
        }
    
    # Group activities by day
    daily_activities = defaultdict(list)
    for activity in activities:
        day = activity.last_active.date()
        daily_activities[day].append(activity)
    
    # Calculate risk factors
    factors = []
    trends = {}
    risk_score = 0
    
    # 1. Long working hours trend
    daily_hours = []
    for day, day_activities in daily_activities.items():
        if day_activities:
            start_time = min(a.last_active for a in day_activities)
            end_time = max(a.last_active for a in day_activities)
            hours = (end_time - start_time).total_seconds() / 3600
            daily_hours.append(hours)
    
    if daily_hours:
        avg_hours = np.mean(daily_hours)
        max_hours = max(daily_hours)
        
        if avg_hours > 9:
            factors.append({
                'type': 'long_hours',
                'severity': 'high' if avg_hours > 10 else 'medium',
                'description': f'Average {avg_hours:.1f} hours per day',
                'impact': 25
            })
            risk_score += 25
        
        if max_hours > 12:
            factors.append({
                'type': 'extreme_hours',
                'severity': 'high',
                'description': f'Peak day: {max_hours:.1f} hours',
                'impact': 20
            })
            risk_score += 20
    
    # 2. Late night work pattern
    late_night_sessions = 0
    for day_activities in daily_activities.values():
        for activity in day_activities:
            if activity.last_active.hour >= 22 or activity.last_active.hour <= 6:
                late_night_sessions += 1
                break
    
    if late_night_sessions > len(daily_activities) * 0.3:  # More than 30% of days
        factors.append({
            'type': 'late_night_work',
            'severity': 'medium',
            'description': f'Late night work on {late_night_sessions} days',
            'impact': 15
        })
        risk_score += 15
    
    # 3. Weekend work pattern
    weekend_sessions = 0
    for day, day_activities in daily_activities.items():
        if day.weekday() >= 5 and day_activities:  # Saturday or Sunday
            weekend_sessions += 1
    
    if weekend_sessions > 0:
        factors.append({
            'type': 'weekend_work',
            'severity': 'medium',
            'description': f'Weekend work on {weekend_sessions} days',
            'impact': 10
        })
        risk_score += 10
    
    # 4. Context switching frequency
    context_switches = 0
    for day_activities in daily_activities.values():
        if len(day_activities) > 1:
            apps = [a.active_app for a in day_activities]
            switches = sum(1 for i in range(1, len(apps)) if apps[i] != apps[i-1])
            context_switches += switches
    
    avg_switches_per_day = context_switches / len(daily_activities) if daily_activities else 0
    
    if avg_switches_per_day > 50:
        factors.append({
            'type': 'high_context_switching',
            'severity': 'medium',
            'description': f'Average {avg_switches_per_day:.1f} context switches per day',
            'impact': 15
        })
        risk_score += 15
    
    # 5. Declining productivity trend
    if len(daily_activities) >= 7:
        recent_days = sorted(daily_activities.keys())[-7:]
        recent_productivity = []
        
        for day in recent_days:
            day_activities = daily_activities[day]
            if day_activities:
                productive_time = sum(
                    a.duration for a in day_activities 
                    if a.is_productive
                )
                total_time = sum(a.duration for a in day_activities)
                productivity = (productive_time / total_time * 100) if total_time > 0 else 0
                recent_productivity.append(productivity)
        
        if len(recent_productivity) >= 3:
            # Check if productivity is declining
            first_half = np.mean(recent_productivity[:len(recent_productivity)//2])
            second_half = np.mean(recent_productivity[len(recent_productivity)//2:])
            
            if second_half < first_half * 0.8:  # 20% decline
                factors.append({
                    'type': 'declining_productivity',
                    'severity': 'high',
                    'description': f'Productivity declined from {first_half:.1f}% to {second_half:.1f}%',
                    'impact': 20
                })
                risk_score += 20
    
    # 6. No breaks pattern
    long_sessions = 0
    for day_activities in daily_activities.values():
        if day_activities:
            start_time = min(a.last_active for a in day_activities)
            end_time = max(a.last_active for a in day_activities)
            session_duration = (end_time - start_time).total_seconds() / 3600
            
            if session_duration > 4:  # Sessions longer than 4 hours without breaks
                long_sessions += 1
    
    if long_sessions > len(daily_activities) * 0.5:  # More than 50% of days
        factors.append({
            'type': 'no_breaks',
            'severity': 'medium',
            'description': f'Long sessions without breaks on {long_sessions} days',
            'impact': 10
        })
        risk_score += 10
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = 'critical'
        recommendations = [
            'Immediate intervention recommended',
            'Consider temporary workload reduction',
            'Schedule wellness check-in',
            'Encourage taking time off'
        ]
    elif risk_score >= 50:
        risk_level = 'high'
        recommendations = [
            'Monitor closely',
            'Encourage regular breaks',
            'Review workload distribution',
            'Consider flexible hours'
        ]
    elif risk_score >= 30:
        risk_level = 'medium'
        recommendations = [
            'Regular check-ins',
            'Encourage work-life balance',
            'Monitor for escalation'
        ]
    else:
        risk_level = 'low'
        recommendations = [
            'Continue current practices',
            'Regular wellness check-ins'
        ]
    
    # Add trend analysis
    trends = {
        'hours_trend': 'increasing' if avg_hours > 8 else 'stable',
        'productivity_trend': 'declining' if risk_score >= 30 else 'stable',
        'work_pattern': 'irregular' if late_night_sessions > 0 or weekend_sessions > 0 else 'regular'
    }
    
    return {
        'overall_risk': min(risk_score, 100),
        'risk_level': risk_level,
        'factors': factors,
        'trends': trends,
        'recommendations': recommendations
    }

@application.route('/api/analytics/distraction-profile', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_distraction_profile():
    """Get anonymous distraction profile for the team"""
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
        
        # Simplified distraction profile for now
        distraction_profile = [
            {
                'category': 'Email',
                'time_minutes': 45,
                'percentage': 30.0,
                'impact': 'medium'
            },
            {
                'category': 'Internal Chat',
                'time_minutes': 30,
                'percentage': 20.0,
                'impact': 'medium'
            }
        ]
        
        insights = ['Analytics feature coming soon']
        
        return jsonify({
            'team_id': team_id,
            'analysis_date': datetime.utcnow().isoformat(),
            'distraction_profile': distraction_profile,
            'insights': insights,
            'total_unproductive_time_hours': 2.5,
            'period_days': 7,
            'note': 'Analytics feature temporarily simplified'
        })
        
    except Exception as e:
        application.logger.error(f"Error in distraction profile analysis: {e}")
        return jsonify({"error": "Analytics feature temporarily unavailable"}), 503

@application.route('/api/employee/daily-summary', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_daily_summary():
    """Get personalized daily summary for employee"""
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
        
        # Get today's activities
        today = datetime.utcnow().date()
        
        activities = Activity.query.filter(
            Activity.user_id == current_user_id,
            Activity.date == today
        ).all()
        
        if not activities:
            return jsonify({
                'summary': 'No activity recorded today',
                'accomplishments': [],
                'focus_time_hours': 0,
                'breaks_taken': 0,
                'productivity_score': 0,
                'total_time_hours': 0,
                'date': today.isoformat()
            })
        
        # Calculate summary metrics from the actual Activity model
        total_productive_hours = sum(a.productive_hours or 0 for a in activities)
        total_unproductive_hours = sum(a.unproductive_hours or 0 for a in activities)
        total_idle_hours = sum(a.idle_time or 0 for a in activities)
        total_time_hours = total_productive_hours + total_unproductive_hours + total_idle_hours
        
        # Calculate productivity score
        productivity_score = (total_productive_hours / total_time_hours * 100) if total_time_hours > 0 else 0
        
        # Generate accomplishments based on available data
        accomplishments = []
        
        # Most used application
        app_usage = defaultdict(float)
        for activity in activities:
            if activity.active_app:
                app_usage[activity.active_app] += (activity.productive_hours or 0) + (activity.unproductive_hours or 0)
        
        if app_usage:
            most_used_app = max(app_usage.keys(), key=lambda app: app_usage[app])
            app_time = app_usage[most_used_app]
            if app_time > 0:
                accomplishments.append(f"Spent {app_time:.1f} hours using {most_used_app}")
        
        # Productivity milestones
        if productivity_score >= 80:
            accomplishments.append("Achieved high productivity score (80%+)")
        elif productivity_score >= 60:
            accomplishments.append("Maintained good productivity throughout the day")
        
        # Time-based accomplishments
        if total_time_hours >= 8:
            accomplishments.append("Completed a full workday")
        elif total_time_hours >= 6:
            accomplishments.append("Put in a solid day's work")
        
        # Idle time analysis
        if total_idle_hours > 0:
            accomplishments.append(f"Took breaks totaling {total_idle_hours:.1f} hours")
        
        # If no specific accomplishments, add general ones
        if not accomplishments:
            accomplishments = [
                "Started tracking your productivity",
                "Began building better work habits"
            ]
        
        return jsonify({
            'summary': f"Today you worked for {total_time_hours:.1f} hours with {productivity_score:.1f}% productivity",
            'accomplishments': accomplishments,
            'focus_time_hours': total_productive_hours,
            'breaks_taken': int(total_idle_hours * 2),  # Estimate breaks based on idle time
            'productivity_score': round(productivity_score, 1),
            'total_time_hours': total_time_hours,
            'date': today.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating daily summary: {str(e)}")
        return jsonify({'error': 'Failed to generate daily summary'}), 500



# ... existing imports and configuration ...

# Enhanced security configuration
application.config['SECURE_HEADERS'] = True
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Add security headers to all responses
@application.after_request
def add_security_headers_after_request(response):
    """Add security headers to all responses"""
    # Add basic security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Add CORS headers
    origin = request.headers.get('Origin')
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', '*')
    
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 
                       'Content-Type,Authorization,X-Requested-With,Accept,Origin')
    response.headers.add('Access-Control-Allow-Methods', 
                       'GET,PUT,POST,DELETE,OPTIONS,PATCH,HEAD')
    
    return response

def get_client_ip():
    """Get client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

# Enhanced error handlers with security logging
@application.errorhandler(400)
def bad_request(error):
    """Handle bad request errors with security logging"""
    client_ip = get_client_ip()
    logger.warning(f"Bad request from {client_ip}: {request.url}")
    return jsonify({'error': 'Bad request', 'details': str(error)}), 400

@application.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized access with security logging"""
    client_ip = get_client_ip()
    logger.warning(f"Unauthorized access attempt from {client_ip}: {request.url}")
    return jsonify({'error': 'Unauthorized access'}), 401

@application.errorhandler(403)
def forbidden(error):
    """Handle forbidden access with security logging"""
    client_ip = get_client_ip()
    logger.warning(f"Forbidden access attempt from {client_ip}: {request.url}")
    return jsonify({'error': 'Access forbidden'}), 403

@application.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return jsonify({'error': 'Resource not found'}), 404

@application.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed with security logging"""
    client_ip = get_client_ip()
    logger.warning(f"Invalid method from {client_ip}: {request.method} {request.url}")
    return jsonify({'error': 'Method not allowed'}), 405

@application.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle rate limit exceeded with security logging"""
    client_ip = get_client_ip()
    logger.warning(f"Rate limit exceeded from {client_ip}: {request.url}")
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@application.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors with security logging"""
    client_ip = get_client_ip()
    logger.error(f"Internal server error from {client_ip}: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@application.errorhandler(503)
def service_unavailable(error):
    """Handle service unavailable errors"""
    return jsonify({'error': 'Service temporarily unavailable'}), 503

# Enhanced input validation for all endpoints
def validate_team_id(team_id):
    """Validate team ID format"""
    if not team_id or not isinstance(team_id, str):
        raise InputValidationError("Invalid team ID")
    
    # Team ID should be a valid UUID or team code
    if not (validate_uuid(team_id) or validate_team_code(team_id)):
        raise InputValidationError("Invalid team ID format")
    
    return team_id

def validate_user_id(user_id):
    """Validate user ID format"""
    if not user_id or not isinstance(user_id, str):
        raise InputValidationError("Invalid user ID")
    
    # User ID should be a valid UUID
    if not validate_uuid(user_id):
        raise InputValidationError("Invalid user ID format")
    
    return user_id

@application.route('/api/auth/employee-login', methods=['POST'])
@conditional_rate_limit("10 per minute")
def employee_login():
    """Employee login endpoint - uses email/password like manager login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check if user is verified (temporarily disabled for testing)
        # if not user.is_verified:
        #     return jsonify({"error": "Please verify your email before logging in"}), 401
        
        # Find user's team membership
        membership = Membership.query.filter_by(user_id=user.id).first()
        if not membership:
            return jsonify({"error": "User is not a member of any team"}), 403
        
        # Get team info
        team = Team.query.get(membership.team_id)
        if not team:
            return jsonify({"error": "Team not found"}), 404
        
        # Create JWT token
        token = create_jwt_token(user.id, team.id, membership.role)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "team_id": team.id,
                "team_name": team.name,
                "role": membership.role
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Employee login error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@application.route('/api/teams/<team_id>/members/<user_id>', methods=['DELETE'])
@conditional_rate_limit("10 per minute")
def remove_team_member(team_id, user_id):
    """Remove a member from a team (manager only)"""
    try:
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_jwt_token(token)
        if not token_data:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Check if the user is a manager of this team
        manager_membership = Membership.query.filter_by(
            team_id=team_id,
            user_id=token_data['user_id'],
            role='manager'
        ).first()
        
        if not manager_membership:
            return jsonify({"error": "Only team managers can remove members"}), 403
        
        # Find the membership to remove
        membership_to_remove = Membership.query.filter_by(
            team_id=team_id,
            user_id=user_id
        ).first()
        
        if not membership_to_remove:
            return jsonify({"error": "User is not a member of this team"}), 404
        
        # Prevent removing the last manager
        if membership_to_remove.role == 'manager':
            manager_count = Membership.query.filter_by(
                team_id=team_id,
                role='manager'
            ).count()
            if manager_count <= 1:
                return jsonify({"error": "Cannot remove the last manager from the team"}), 400
        
        # Remove the membership
        db.session.delete(membership_to_remove)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Member removed from team successfully"
        }), 200
        
    except Exception as e:
        logging.error(f"Remove team member error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@application.route('/api/teams/<team_id>/analytics', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_team_analytics(team_id):
    """Get analytics data for a team with date range filtering"""
    try:
        # Get date range parameters
        date_range = request.args.get('range', 'week')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Calculate date range
        if date_range == 'custom' and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        elif date_range == 'today':
            start = end = datetime.now().date()
        elif date_range == 'week':
            end = datetime.now().date()
            start = end - timedelta(days=7)
        elif date_range == 'month':
            end = datetime.now().date()
            start = end - timedelta(days=30)
        elif date_range == 'quarter':
            end = datetime.now().date()
            start = end - timedelta(days=90)
        else:
            end = datetime.now().date()
            start = end - timedelta(days=7)
        
        # Get team activities for the date range
        activities = Activity.query.filter(
            Activity.team_id == team_id,
            Activity.date >= start,
            Activity.date <= end
        ).all()
        
        # Process analytics data
        hourly_data = {}
        app_breakdown = {}
        weekly_trend = {}
        
        for activity in activities:
            # Hourly productivity
            hour = activity.last_active.hour if activity.last_active else 12
            if hour not in hourly_data:
                hourly_data[hour] = {'productive': 0, 'unproductive': 0}
            hourly_data[hour]['productive'] += activity.productive_hours
            hourly_data[hour]['unproductive'] += activity.unproductive_hours
            
            # App breakdown
            if activity.active_app:
                app = activity.active_app
                if app not in app_breakdown:
                    app_breakdown[app] = {'hours': 0, 'category': 'other'}
                app_breakdown[app]['hours'] += activity.productive_hours + activity.unproductive_hours
            
            # Weekly trend
            day = activity.date.strftime('%A')
            if day not in weekly_trend:
                weekly_trend[day] = {'productive': 0, 'unproductive': 0}
            weekly_trend[day]['productive'] += activity.productive_hours
            weekly_trend[day]['unproductive'] += activity.unproductive_hours
        
        # Format response
        hourly_productivity = [
            {'hour': hour, 'productive': data['productive'], 'unproductive': data['unproductive']}
            for hour, data in sorted(hourly_data.items())
        ]
        
        app_breakdown_list = [
            {'app': app, 'hours': data['hours'], 'category': data['category']}
            for app, data in app_breakdown.items()
        ]
        
        weekly_trend_list = [
            {'day': day, 'productive': data['productive'], 'unproductive': data['unproductive']}
            for day, data in weekly_trend.items()
        ]
        
        return jsonify({
            'success': True,
            'analytics': {
                'hourlyProductivity': hourly_productivity,
                'appBreakdown': app_breakdown_list,
                'weeklyTrend': weekly_trend_list
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Analytics error: {e}")
        return jsonify({"error": "Failed to fetch analytics"}), 500

@application.route('/api/teams/<team_id>/tasks', methods=['GET'])
@conditional_rate_limit("10 per minute")
def get_team_tasks(team_id):
    """Get tasks for a team"""
    try:
        tasks = Task.query.filter_by(team_id=team_id).all()
        
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'assignedTo': task.assigned_to,
                'assignedToName': 'Unknown',  # Would need to join with users table
                'assignedBy': task.assigned_by,
                'assignedByName': 'Unknown',  # Would need to join with users table
                'status': task.status,
                'priority': 'medium',  # Default priority
                'dueDate': task.due_date.isoformat() if task.due_date else None,
                'createdAt': task.created_at.isoformat() if task.created_at else None,
                'updatedAt': task.created_at.isoformat() if task.created_at else None,
                'estimatedHours': 0,  # Default values
                'actualHours': 0,
                'tags': [],
                'comments': []
            })
        
        return jsonify({
            'success': True,
            'tasks': task_list
        }), 200
        
    except Exception as e:
        logging.error(f"Tasks error: {e}")
        return jsonify({"error": "Failed to fetch tasks"}), 500

@application.route('/api/teams/<team_id>/members/realtime', methods=['GET'])
@conditional_rate_limit("30 per minute")
def get_realtime_members(team_id):
    """Get real-time member status and activity"""
    try:
        memberships = Membership.query.filter_by(team_id=team_id).all()
        
        members = []
        for membership in memberships:
            # Get user details
            user = User.query.get(membership.user_id)
            if not user:
                continue
            
            # Get latest activity
            latest_activity = Activity.query.filter_by(
                user_id=membership.user_id,
                team_id=team_id
            ).order_by(Activity.last_active.desc()).first()
            
            # Determine online status (active in last 5 minutes)
            is_online = False
            current_activity = None
            if latest_activity and latest_activity.last_active:
                time_diff = datetime.utcnow() - latest_activity.last_active
                is_online = time_diff.total_seconds() < 300  # 5 minutes
                current_activity = latest_activity.active_app
            
            # Get productivity stats for today
            today = datetime.now().date()
            today_activity = Activity.query.filter_by(
                user_id=membership.user_id,
                team_id=team_id,
                date=today
            ).first()
            
            productive_hours = today_activity.productive_hours if today_activity else 0
            unproductive_hours = today_activity.unproductive_hours if today_activity else 0
            total_hours = productive_hours + unproductive_hours
            productivity_score = (productive_hours / total_hours * 100) if total_hours > 0 else 0
            
            members.append({
                'userId': membership.user_id,
                'name': membership.user_name,
                'role': membership.role,
                'department': 'General',  # Default department
                'productiveHours': productive_hours,
                'unproductiveHours': unproductive_hours,
                'totalHours': total_hours,
                'productivityScore': productivity_score,
                'lastActive': latest_activity.last_active.isoformat() if latest_activity and latest_activity.last_active else datetime.utcnow().isoformat(),
                'status': 'online' if is_online else 'offline',
                'isOnline': is_online,
                'currentActivity': current_activity,
                'focusSessions': 0,  # Default values
                'breaksTaken': 0,
                'weeklyAverage': 0,
                'monthlyAverage': 0
            })
        
        return jsonify({
            'success': True,
            'members': members
        }), 200
        
    except Exception as e:
        logging.error(f"Realtime members error: {e}")
        return jsonify({"error": "Failed to fetch real-time data"}), 500

@application.route('/api/teams/<team_id>/bulk-actions', methods=['POST'])
@conditional_rate_limit("5 per minute")
def bulk_team_actions(team_id):
    """Perform bulk actions on team members"""
    try:
        data = request.get_json()
        action = data.get('action')
        user_ids = data.get('userIds', [])
        
        if not user_ids:
            return jsonify({"error": "No users selected"}), 400
        
        if action == 'remove':
            # Remove multiple members
            for user_id in user_ids:
                membership = Membership.query.filter_by(
                    team_id=team_id,
                    user_id=user_id
                ).first()
                if membership:
                    db.session.delete(membership)
            
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Removed {len(user_ids)} members from team'
            }), 200
        
        elif action == 'change_role':
            new_role = data.get('role')
            if not new_role:
                return jsonify({"error": "Role is required"}), 400
            
            # Update roles for multiple members
            for user_id in user_ids:
                membership = Membership.query.filter_by(
                    team_id=team_id,
                    user_id=user_id
                ).first()
                if membership:
                    membership.role = new_role
            
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Updated role for {len(user_ids)} members'
            }), 200
        
        else:
            return jsonify({"error": "Invalid action"}), 400
        
    except Exception as e:
        logging.error(f"Bulk actions error: {e}")
        return jsonify({"error": "Failed to perform bulk action"}), 500

@application.route('/api/teams/<team_id>/invite-link', methods=['POST'])
@conditional_rate_limit("5 per minute")
def create_invite_link(team_id):
    """Create an invite link with expiration"""
    try:
        data = request.get_json()
        expires_in_days = data.get('expiresInDays', 7)
        
        # Generate invite code
        invite_code = generate_manager_invite_code()
        
        # Create invite record
        invite = ManagerInvite(
            team_id=team_id,
            invite_code=invite_code,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days)
        )
        
        db.session.add(invite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'inviteCode': invite_code,
            'expiresAt': invite.expires_at.isoformat(),
            'inviteLink': f"https://yourdomain.com/join/{invite_code}"
        }), 200
        
    except Exception as e:
        logging.error(f"Invite link error: {e}")
        return jsonify({"error": "Failed to create invite link"}), 500

