#!/usr/bin/env python3
"""
Working ProductivityFlow backend with email verification and password reset
"""

import os
import sys
import sqlite3
import bcrypt
import jwt
import json
import secrets
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
import time

# Create Flask app
app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['DATABASE'] = 'productivityflow_working.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'infoproductivityflows@gmail.com'
app.config['MAIL_PASSWORD'] = 'vyeibhlubbtmijxd'
app.config['MAIL_DEFAULT_SENDER'] = 'infoproductivityflows@gmail.com'

# Check if email is configured
EMAIL_CONFIGURED = bool(app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD'])

def send_verification_email(email, name, verification_token):
    """Send verification email to user"""
    if not EMAIL_CONFIGURED:
        print(f"⚠️ Email not configured. Verification token for {email}: {verification_token}")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = email
        msg['Subject'] = 'Welcome to ProductivityFlow - Verify Your Email'
        
        # Professional HTML email body
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to ProductivityFlow</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8fafc;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin-bottom: 10px;
                }}
                .tagline {{
                    color: #6b7280;
                    font-size: 16px;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                .welcome {{
                    font-size: 24px;
                    color: #1f2937;
                    margin-bottom: 20px;
                    font-weight: 600;
                }}
                .description {{
                    color: #6b7280;
                    margin-bottom: 30px;
                    font-size: 16px;
                }}
                .button-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .verify-button {{
                    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                    color: white;
                    padding: 16px 32px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 16px;
                    display: inline-block;
                    box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
                    transition: transform 0.2s;
                }}
                .verify-button:hover {{
                    transform: translateY(-2px);
                }}
                .token-info {{
                    background: #f3f4f6;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .token-label {{
                    font-weight: 600;
                    color: #374151;
                    margin-bottom: 10px;
                }}
                .token {{
                    font-family: 'Courier New', monospace;
                    background: white;
                    padding: 10px;
                    border-radius: 4px;
                    border: 1px solid #d1d5db;
                    color: #1f2937;
                    font-size: 14px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    color: #6b7280;
                    font-size: 14px;
                }}
                .security-note {{
                    background: #fef3c7;
                    border: 1px solid #f59e0b;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #92400e;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">ProductivityFlow</div>
                    <div class="tagline">Streamline Your Team's Productivity</div>
                </div>
                
                <div class="content">
                    <div class="welcome">Welcome, {name}! 👋</div>
                    <div class="description">
                        Thank you for joining ProductivityFlow! We're excited to help you and your team achieve peak productivity. 
                        To get started, please verify your email address by clicking the button below.
                    </div>
                    
                    <div class="button-container">
                        <a href="http://localhost:3001/api/auth/verify-token/{verification_token}" class="verify-button">
                            ✅ Verify Email Address
                        </a>
                    </div>
                    
                    <div class="security-note">
                        <strong>🔒 Security Note:</strong> This verification link will expire in 24 hours. 
                        If you didn't create this account, you can safely ignore this email.
                    </div>
                    
                    <div class="token-info">
                        <div class="token-label">Manual Verification Token:</div>
                        <div class="token">{verification_token}</div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Best regards,<br>The ProductivityFlow Team</p>
                    <p>Need help? Contact us at support@productivityflow.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Verification email sent to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {str(e)}")
        return False

def send_password_reset_email(email, name, reset_token):
    """Send password reset email to user"""
    if not EMAIL_CONFIGURED:
        print(f"⚠️ Email not configured. Reset token for {email}: {reset_token}")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = email
        msg['Subject'] = 'Reset Your ProductivityFlow Password'
        
        # Professional HTML email body
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset - ProductivityFlow</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8fafc;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin-bottom: 10px;
                }}
                .tagline {{
                    color: #6b7280;
                    font-size: 16px;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                .title {{
                    font-size: 24px;
                    color: #1f2937;
                    margin-bottom: 20px;
                    font-weight: 600;
                }}
                .description {{
                    color: #6b7280;
                    margin-bottom: 30px;
                    font-size: 16px;
                }}
                .button-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .reset-button {{
                    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                    color: white;
                    padding: 16px 32px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 16px;
                    display: inline-block;
                    box-shadow: 0 4px 6px rgba(220, 38, 38, 0.3);
                    transition: transform 0.2s;
                }}
                .reset-button:hover {{
                    transform: translateY(-2px);
                }}
                .token-info {{
                    background: #f3f4f6;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .token-label {{
                    font-weight: 600;
                    color: #374151;
                    margin-bottom: 10px;
                }}
                .token {{
                    font-family: 'Courier New', monospace;
                    background: white;
                    padding: 10px;
                    border-radius: 4px;
                    border: 1px solid #d1d5db;
                    color: #1f2937;
                    font-size: 14px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    color: #6b7280;
                    font-size: 14px;
                }}
                .security-note {{
                    background: #fef3c7;
                    border: 1px solid #f59e0b;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #92400e;
                    font-size: 14px;
                }}
                .warning {{
                    background: #fef2f2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #991b1b;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">ProductivityFlow</div>
                    <div class="tagline">Streamline Your Team's Productivity</div>
                </div>
                
                <div class="content">
                    <div class="title">Password Reset Request 🔐</div>
                    <div class="description">
                        Hello {name},<br><br>
                        We received a request to reset your ProductivityFlow password. If you made this request, 
                        please click the button below to securely reset your password.
                    </div>
                    
                    <div class="button-container">
                        <a href="http://localhost:3001/api/auth/reset-password-token/{reset_token}" class="reset-button">
                            🔄 Reset Password
                        </a>
                    </div>
                    
                    <div class="security-note">
                        <strong>⏰ Time Limit:</strong> This reset link will expire in 1 hour for your security.
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Security Warning:</strong> If you didn't request this password reset, 
                        please ignore this email and contact our support team immediately.
                    </div>
                    
                    <div class="token-info">
                        <div class="token-label">Manual Reset Token:</div>
                        <div class="token">{reset_token}</div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Best regards,<br>The ProductivityFlow Team</p>
                    <p>Need help? Contact us at support@productivityflow.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Password reset email sent to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send password reset email to {email}: {str(e)}")
        return False

# CORS
CORS(app, origins=['http://localhost:8000', 'http://localhost:3000'], 
     methods=['GET', 'POST', 'PUT', 'DELETE'], 
     allow_headers=['Content-Type', 'Authorization'])

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('PRAGMA foreign_keys = ON')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            is_verified BOOLEAN DEFAULT 0,
            verification_token TEXT,
            reset_token TEXT,
            reset_token_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            manager_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manager_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(team_id, user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection"""
    if hasattr(g, 'db'):
        g.db.close()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def sanitize_input(text):
    """Sanitize input text"""
    if not text:
        return ""
    return re.sub(r'[<>"\']', '', str(text)).strip()

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            g.user_id = payload['user_id']
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT 1')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "message": "ProductivityFlow Working Backend is running",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "email_configured": EMAIL_CONFIGURED,
        "version": "2.1.0"
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        name = sanitize_input(data.get('name', ''))
        
        if not all([email, password, name]):
            return jsonify({"error": "Missing required fields"}), 400
        
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        is_valid, password_msg = validate_password(password)
        if not is_valid:
            return jsonify({"error": password_msg}), 400
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return jsonify({"error": "User with this email already exists"}), 409
        
        verification_token = secrets.token_urlsafe(32)
        
        cursor.execute(
            'INSERT INTO users (email, password_hash, name, is_verified, verification_token) VALUES (?, ?, ?, ?, ?)',
            (email, password_hash, name, False, verification_token)
        )
        db.commit()
        
        email_sent = send_verification_email(email, name, verification_token)
        
        if EMAIL_CONFIGURED and email_sent:
            return jsonify({
                "message": "User registered successfully. Please check your email for verification.",
                "user": {"email": email, "name": name}
            }), 201
        else:
            return jsonify({
                "message": "User registered successfully. Please verify your email using the token.",
                "verification_token": verification_token,
                "user": {"email": email, "name": name}
            }), 201
        
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        
        if not all([email, password]):
            return jsonify({"error": "Missing email or password"}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Find user
        cursor.execute('SELECT id, email, password_hash, name, is_verified FROM users WHERE LOWER(email) = ?', (email.lower(),))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({"error": "Invalid email or password"}), 401
        
        if not user['is_verified']:
            return jsonify({"error": "Please verify your email before signing in"}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user['id'],
            'email': email,
            'name': user['name'],
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user['id'],
                "email": email,
                "name": user['name']
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/auth/verify-token/<token>', methods=['GET'])
def verify_token(token):
    """Verify email using token - returns beautiful HTML page"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT email, name FROM users WHERE verification_token = ? AND is_verified = 0', (token,))
        user = cursor.fetchone()
        
        if not user:
            # Return error page
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Email Verification Failed - ProductivityFlow</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 0;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 20px;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                        text-align: center;
                        max-width: 500px;
                        width: 90%;
                    }}
                    .icon {{
                        font-size: 64px;
                        margin-bottom: 20px;
                    }}
                    .success {{ color: #10b981; }}
                    .error {{ color: #ef4444; }}
                    h1 {{
                        color: #1f2937;
                        margin-bottom: 20px;
                        font-size: 28px;
                    }}
                    p {{
                        color: #6b7280;
                        line-height: 1.6;
                        margin-bottom: 30px;
                    }}
                    .button {{
                        background: #3b82f6;
                        color: white;
                        padding: 15px 30px;
                        border: none;
                        border-radius: 10px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        text-decoration: none;
                        display: inline-block;
                        transition: background 0.3s;
                    }}
                    .button:hover {{
                        background: #2563eb;
                    }}
                    .logo {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #3b82f6;
                        margin-bottom: 30px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="logo">ProductivityFlow</div>
                    <div class="icon error">❌</div>
                    <h1>Verification Failed</h1>
                    <p>Sorry, this verification link is invalid or has expired. Please try registering again or contact support if you continue to have issues.</p>
                    <a href="http://localhost:8000" class="button">Return to App</a>
                </div>
            </body>
            </html>
            """
            return html
        
        # Mark user as verified and clear token
        cursor.execute(
            'UPDATE users SET is_verified = 1, verification_token = NULL WHERE verification_token = ?',
            (token,)
        )
        db.commit()
        
        # Return success page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Verified - ProductivityFlow</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                    width: 90%;
                }}
                .icon {{
                    font-size: 64px;
                    margin-bottom: 20px;
                }}
                .success {{ color: #10b981; }}
                .error {{ color: #ef4444; }}
                h1 {{
                    color: #1f2937;
                    margin-bottom: 20px;
                    font-size: 28px;
                }}
                p {{
                    color: #6b7280;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .button {{
                    background: #10b981;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                    transition: background 0.3s;
                }}
                .button:hover {{
                    background: #059669;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin-bottom: 30px;
                }}
                .user-info {{
                    background: #f3f4f6;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                }}
                .user-info strong {{
                    color: #1f2937;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">ProductivityFlow</div>
                <div class="icon success">✅</div>
                <h1>Email Verified Successfully!</h1>
                <p>Welcome to ProductivityFlow! Your email address has been verified and your account is now active.</p>
                
                <div class="user-info">
                    <p><strong>Account Details:</strong></p>
                    <p>Name: <strong>{user['name']}</strong></p>
                    <p>Email: <strong>{user['email']}</strong></p>
                </div>
                
                <p>You can now sign in to your ProductivityFlow account and start managing your team's productivity.</p>
                
                <a href="http://localhost:8000" class="button">Sign In to ProductivityFlow</a>
            </div>
        </body>
        </html>
        """
        return html
        
    except Exception as e:
        app.logger.error(f"Token verification error: {str(e)}")
        # Return error page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Verification Error - ProductivityFlow</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                    width: 90%;
                }}
                .icon {{
                    font-size: 64px;
                    margin-bottom: 20px;
                }}
                .error {{ color: #ef4444; }}
                h1 {{
                    color: #1f2937;
                    margin-bottom: 20px;
                    font-size: 28px;
                }}
                p {{
                    color: #6b7280;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .button {{
                    background: #3b82f6;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                    transition: background 0.3s;
                }}
                .button:hover {{
                    background: #2563eb;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin-bottom: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">ProductivityFlow</div>
                <div class="icon error">⚠️</div>
                <h1>Verification Error</h1>
                <p>We encountered an error while verifying your email. Please try again or contact support if the problem persists.</p>
                <a href="http://localhost:8000" class="button">Return to App</a>
            </div>
        </body>
        </html>
        """
        return html

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Password reset endpoint"""
    try:
        data = request.get_json()
        email = sanitize_input(data.get('email', ''))
        new_password = data.get('password', '')
        
        if not email or not new_password:
            return jsonify({"error": "Email and password required"}), 400
        
        is_valid, password_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({"error": password_msg}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT id, name FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        reset_token = secrets.token_urlsafe(32)
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        cursor.execute(
            'UPDATE users SET password_hash = ?, is_verified = 1 WHERE email = ?',
            (password_hash, email)
        )
        db.commit()
        
        email_sent = send_password_reset_email(email, user['name'], reset_token)
        
        if cursor.rowcount > 0:
            if EMAIL_CONFIGURED and email_sent:
                return jsonify({
                    "message": "Password reset successfully. Check your email for confirmation.",
                    "user": {"email": email, "name": user['name']}
                }), 200
            else:
                return jsonify({
                    "message": "Password reset successfully. You can now sign in.",
                    "reset_token": reset_token,
                    "user": {"email": email, "name": user['name']}
                }), 200
        else:
            return jsonify({"error": "Password reset failed"}), 500
            
    except Exception as e:
        app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/teams', methods=['POST'])
@require_auth
def create_team():
    """Create a new team"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({"error": "Team name is required"}), 400
        
        team_name = data['name'].strip()
        if not team_name:
            return jsonify({"error": "Team name cannot be empty"}), 400
        
        # Get current user from token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        
        db = get_db()
        cursor = db.cursor()
        
        # Create team
        cursor.execute(
            'INSERT INTO teams (name, manager_id) VALUES (?, ?)',
            (team_name, user_id)
        )
        team_id = cursor.lastrowid
        
        # Add manager as team member
        cursor.execute(
            'INSERT INTO team_members (team_id, user_id) VALUES (?, ?)',
            (team_id, user_id)
        )
        
        db.commit()
        
        return jsonify({
            "message": "Team created successfully",
            "team": {
                "id": team_id,
                "name": team_name
            }
        }), 201
        
    except Exception as e:
        app.logger.error(f"Team creation error: {str(e)}")
        return jsonify({"error": "Failed to create team"}), 500

@app.route('/api/teams', methods=['GET'])
@require_auth
def get_teams():
    """Get all teams for the current user"""
    try:
        # Get current user from token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        
        db = get_db()
        cursor = db.cursor()
        
        # Get teams where user is a member
        cursor.execute('''
            SELECT DISTINCT t.id, t.name, t.created_at,
                   COUNT(tm.user_id) as member_count
            FROM teams t
            JOIN team_members tm ON t.id = tm.team_id
            WHERE t.id IN (
                SELECT team_id FROM team_members WHERE user_id = ?
            )
            GROUP BY t.id, t.name, t.created_at
            ORDER BY t.created_at DESC
        ''', (user_id,))
        
        teams = []
        for row in cursor.fetchall():
            teams.append({
                "id": row['id'],
                "name": row['name'],
                "code": f"TEAM{row['id']}",
                "memberCount": row['member_count'],
                "createdAt": row['created_at']
            })
        
        return jsonify({
            "teams": teams
        }), 200
        
    except Exception as e:
        app.logger.error(f"Get teams error: {str(e)}")
        return jsonify({"error": "Failed to get teams"}), 500

@app.route('/api/teams/<int:team_id>/members', methods=['GET'])
@require_auth
def get_team_members(team_id):
    """Get members of a specific team"""
    try:
        # Get current user from token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if user is a member of this team
        cursor.execute(
            'SELECT 1 FROM team_members WHERE team_id = ? AND user_id = ?',
            (team_id, user_id)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Access denied"}), 403
        
        # Get team members
        cursor.execute('''
            SELECT u.id, u.name, u.email, tm.joined_at
            FROM team_members tm
            JOIN users u ON tm.user_id = u.id
            WHERE tm.team_id = ?
            ORDER BY tm.joined_at ASC
        ''', (team_id,))
        
        members = []
        for row in cursor.fetchall():
            members.append({
                "userId": row['id'],
                "name": row['name'],
                "email": row['email'],
                "joinedAt": row['joined_at']
            })
        
        return jsonify({
            "members": members
        }), 200
        
    except Exception as e:
        app.logger.error(f"Get team members error: {str(e)}")
        return jsonify({"error": "Failed to get team members"}), 500

@app.route('/api/teams/join', methods=['POST'])
def join_team():
    """Join a team using team code"""
    try:
        data = request.get_json()
        
        if not data or 'team_code' not in data or 'user_name' not in data:
            return jsonify({"error": "Team code and user name are required"}), 400
        
        team_code = data['team_code'].strip().upper()
        user_name = data['user_name'].strip()
        
        if not team_code or not user_name:
            return jsonify({"error": "Team code and user name cannot be empty"}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Find team by code (format: TEAM{id})
        if not team_code.startswith('TEAM'):
            return jsonify({"error": "Invalid team code format"}), 400
        
        try:
            team_id = int(team_code[4:])  # Extract ID from TEAM{id}
        except ValueError:
            return jsonify({"error": "Invalid team code"}), 400
        
        # Check if team exists
        cursor.execute('SELECT id, name FROM teams WHERE id = ?', (team_id,))
        team = cursor.fetchone()
        
        if not team:
            return jsonify({"error": "Team not found"}), 404
        
        # Create a new user account for the employee
        email = f"employee_{team_id}_{int(time.time())}@productivityflow.local"
        password_hash = bcrypt.hashpw("default_password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute(
            'INSERT INTO users (email, password_hash, name, is_verified) VALUES (?, ?, ?, ?)',
            (email, password_hash, user_name, 1)  # Auto-verify employees
        )
        user_id = cursor.lastrowid
        
        # Add user to team
        cursor.execute(
            'INSERT INTO team_members (team_id, user_id) VALUES (?, ?)',
            (team_id, user_id)
        )
        
        db.commit()
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'name': user_name,
            'exp': datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry for employees
        }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "success": True,
            "message": "Successfully joined team",
            "token": token,
            "user": {
                "id": user_id,
                "name": user_name,
                "email": email,
                "team_id": team_id,
                "team_name": team['name'],
                "role": "employee"
            },
            "team": {
                "id": team_id,
                "name": team['name'],
                "code": team_code
            }
        }), 201
        
    except Exception as e:
        app.logger.error(f"Team join error: {str(e)}")
        return jsonify({"error": "Failed to join team"}), 500

@app.route('/api/auth/employee-login', methods=['POST'])
def employee_login():
    """Employee login endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password are required"}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        if not email or not password:
            return jsonify({"error": "Email and password cannot be empty"}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Find user
        cursor.execute('SELECT id, email, password_hash, name, is_verified FROM users WHERE LOWER(email) = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check if user is verified
        if not user['is_verified']:
            return jsonify({"error": "Please verify your email before signing in"}), 401
        
        # Verify password
        password_hash = user['password_hash']
        if isinstance(password_hash, bytes):
            password_hash = password_hash.decode('utf-8')
        
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check if user is a team member
        cursor.execute('''
            SELECT t.id, t.name 
            FROM teams t 
            JOIN team_members tm ON t.id = tm.team_id 
            WHERE tm.user_id = ?
        ''', (user['id'],))
        team = cursor.fetchone()
        
        if not team:
            return jsonify({"error": "You are not a member of any team. Please ask your manager to add you to a team."}), 403
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'exp': datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry for employees
        }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "team_id": team['id'],
                "team_name": team['name'],
                "role": "employee"
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Employee login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "ProductivityFlow Working API",
        "version": "2.1.0",
        "status": "running",
        "security": "enabled",
        "email_configured": EMAIL_CONFIGURED,
        "endpoints": [
            "/health",
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/employee-login",
            "/api/auth/verify-token/<token>",
            "/api/auth/request-password-reset",
            "/api/auth/reset-password-token/<token>",
            "/api/auth/reset-password",
            "/api/teams",
            "/api/teams/<id>/members",
            "/api/teams/join"
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🚀 Starting ProductivityFlow Working Backend...")
    print("📧 Email configuration:", "✅ Enabled" if EMAIL_CONFIGURED else "❌ Disabled")
    print("📍 Backend will be available at: http://localhost:5000")
    print("🔧 API endpoints will be at: http://localhost:5000/api/")
    print("📊 Health check: http://localhost:5000/health")
    
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False) 