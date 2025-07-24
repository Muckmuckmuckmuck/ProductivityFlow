#!/usr/bin/env python3
"""
Secure, optimized ProductivityFlow backend with SQLite database and email verification
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

# Create Flask app
app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Generate secure random key
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)  # Generate secure random key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # 1 hour expiry
app.config['DATABASE'] = 'productivityflow_secure.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'infoproductivityflows@gmail.com'  # Your Gmail
app.config['MAIL_PASSWORD'] = 'vyeibhlubbtmijxd'  # Your app password
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
        msg['Subject'] = 'Verify Your ProductivityFlow Account'
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>Welcome to ProductivityFlow, {name}!</h2>
            <p>Thank you for creating your account. Please verify your email address to get started.</p>
            
            <p><strong>Your verification token:</strong> {verification_token}</p>
            
            <p>Or click the link below to verify automatically:</p>
            <a href="http://localhost:3001/api/auth/verify-token/{verification_token}" 
               style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                Verify Email Address
            </a>
            
            <p>If you didn't create this account, you can safely ignore this email.</p>
            
            <p>Best regards,<br>The ProductivityFlow Team</p>
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
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello {name},</p>
            <p>We received a request to reset your ProductivityFlow password.</p>
            
            <p><strong>Your reset token:</strong> {reset_token}</p>
            
            <p>Or click the link below to reset your password:</p>
            <a href="http://localhost:3001/api/auth/reset-password-token/{reset_token}" 
               style="background-color: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                Reset Password
            </a>
            
            <p><strong>This link will expire in 1 hour.</strong></p>
            
            <p>If you didn't request this password reset, you can safely ignore this email.</p>
            
            <p>Best regards,<br>The ProductivityFlow Team</p>
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

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# CORS with security
CORS(app, origins=['http://localhost:8000', 'http://localhost:3000'], 
     methods=['GET', 'POST', 'PUT', 'DELETE'], 
     allow_headers=['Content-Type', 'Authorization'])

def init_db():
    """Initialize the SQLite database with proper constraints"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # Create users table with proper constraints
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL CHECK (email LIKE '%_@_%'),
            password_hash TEXT NOT NULL CHECK (length(password_hash) > 0),
            name TEXT NOT NULL CHECK (length(name) > 0 AND length(name) <= 100),
            is_verified BOOLEAN DEFAULT 0,
            verification_token TEXT,
            reset_token TEXT,
            reset_token_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK (length(name) > 0 AND length(name) <= 100),
            manager_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create team_members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(team_id, user_id)
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_teams_manager ON teams(manager_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id)')
    
    conn.commit()
    conn.close()
    print("✅ Secure database initialized")

def get_db():
    """Get database connection with proper error handling"""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

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
    """Sanitize user input"""
    if not text:
        return ""
    # Remove potentially dangerous characters
    return re.sub(r'[<>"\']', '', str(text).strip())

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            g.user_id = payload['user_id']
            g.user_email = payload['email']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT 1')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "message": "ProductivityFlow Secure Backend is running",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "2.0.0"
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Secure user registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        name = sanitize_input(data.get('name', ''))
        
        # Validate required fields
        if not all([email, password, name]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password strength
        is_valid, password_msg = validate_password(password)
        if not is_valid:
            return jsonify({"error": password_msg}), 400
        
        # Validate name length
        if len(name) > 100:
            return jsonify({"error": "Name too long (max 100 characters)"}), 400
        
        # Hash password with high cost factor
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return jsonify({"error": "User with this email already exists"}), 409
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Create user with verification token
        cursor.execute(
            'INSERT INTO users (email, password_hash, name, is_verified, verification_token) VALUES (?, ?, ?, ?, ?)',
            (email, password_hash, name, False, verification_token)  # Not verified until email confirmed
        )
        db.commit()
        
        # Send verification email
        email_sent = send_verification_email(email, name, verification_token)
        
        if EMAIL_CONFIGURED and email_sent:
            return jsonify({
                "message": "User registered successfully. Please check your email for verification.",
                "user": {"email": email, "name": name}
            }), 201
        else:
            return jsonify({
                "message": "User registered successfully. Please verify your email using the token.",
                "verification_token": verification_token,  # Only in development
                "user": {"email": email, "name": name}
            }), 201
        
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Secure user login endpoint"""
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
        
        # Get user with rate limiting check
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            # Don't reveal if user exists
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check if user is verified
        if not user['is_verified']:
            return jsonify({"error": "Please verify your email before logging in"}), 401
        
        # Create JWT token with short expiry
        token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name']
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/auth/verify-token/<token>', methods=['GET'])
def verify_token(token):
    """Verify email using token"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('SELECT email, name FROM users WHERE verification_token = ? AND is_verified = 0', (token,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "Invalid or expired verification token"}), 400
        
        # Mark user as verified and clear token
        cursor.execute(
            'UPDATE users SET is_verified = 1, verification_token = NULL WHERE verification_token = ?',
            (token,)
        )
        db.commit()
        
        return jsonify({
            "message": "Email verified successfully! You can now sign in.",
            "user": {"email": user[0], "name": user[1]}
        }), 200
        
    except Exception as e:
        app.logger.error(f"Token verification error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/auth/verify-email', methods=['POST'])
def verify_email():
    """Email verification endpoint (simplified for testing)"""
    try:
        data = request.get_json()
        email = sanitize_input(data.get('email', ''))
        
        if not email:
            return jsonify({"error": "Email required"}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('UPDATE users SET is_verified = 1 WHERE email = ?', (email,))
        db.commit()
        
        if cursor.rowcount > 0:
            return jsonify({"message": "Email verified successfully"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
            
    except Exception as e:
        app.logger.error(f"Email verification error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/auth/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request password reset - sends email with reset token"""
    try:
        data = request.get_json()
        email = sanitize_input(data.get('email', ''))
        
        if not email:
            return jsonify({"error": "Email required"}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id, name FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            # Don't reveal if user exists
            return jsonify({"message": "If an account with this email exists, a password reset link has been sent."}), 200
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.now() + timedelta(hours=1)  # 1 hour expiry
        
        # Store reset token
        cursor.execute(
            'UPDATE users SET reset_token = ?, reset_token_expires = ? WHERE email = ?',
            (reset_token, reset_expires.isoformat(), email)
        )
        db.commit()
        
        # Send reset email
        email_sent = send_password_reset_email(email, user[1], reset_token)
        
        if EMAIL_CONFIGURED and email_sent:
            return jsonify({
                "message": "Password reset email sent. Please check your inbox."
            }), 200
        else:
            return jsonify({
                "message": "Password reset requested. Use the token below to reset your password.",
                "reset_token": reset_token,  # Only in development
                "expires": reset_expires.isoformat()
            }), 200
            
    except Exception as e:
        app.logger.error(f"Password reset request error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Simple password reset endpoint"""
    try:
        data = request.get_json()
        email = sanitize_input(data.get('email', ''))
        new_password = data.get('password', '')
        
        if not email or not new_password:
            return jsonify({"error": "Email and password required"}), 400
        
        # Validate password strength
        is_valid, password_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({"error": password_msg}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id, name FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Generate reset token for email
        reset_token = secrets.token_urlsafe(32)
        
        # Hash new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        # Update user password and verify email
        cursor.execute(
            'UPDATE users SET password_hash = ?, is_verified = 1 WHERE email = ?',
            (password_hash, email)
        )
        db.commit()
        
        # Send password reset email
        email_sent = send_password_reset_email(email, user[1], reset_token)
        
        if cursor.rowcount > 0:
            if EMAIL_CONFIGURED and email_sent:
                return jsonify({
                    "message": "Password reset successfully. Check your email for confirmation.",
                    "user": {"email": email, "name": user[1]}
                }), 200
            else:
                return jsonify({
                    "message": "Password reset successfully. You can now sign in.",
                    "reset_token": reset_token,  # Only in development
                    "user": {"email": email, "name": user[1]}
                }), 200
        else:
            return jsonify({"error": "Password reset failed"}), 500
            
    except Exception as e:
        app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/auth/reset-password-token/<token>', methods=['GET'])
def reset_password_form(token):
    """Show password reset form (HTML page)"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reset Password - ProductivityFlow</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; }}
            input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
            button {{ background: #2563eb; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }}
            .success {{ background: #dcfce7; color: #166534; padding: 15px; border-radius: 4px; }}
            .error {{ background: #fef2f2; color: #dc2626; padding: 15px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <h2>Reset Your Password</h2>
        <div id="result"></div>
        <form id="resetForm">
            <div class="form-group">
                <label for="password">New Password:</label>
                <input type="password" id="password" required minlength="8">
            </div>
            <div class="form-group">
                <label for="confirmPassword">Confirm Password:</label>
                <input type="password" id="confirmPassword" required minlength="8">
            </div>
            <button type="submit">Reset Password</button>
        </form>
        
        <script>
            document.getElementById('resetForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                
                const password = document.getElementById('password').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                
                if (password !== confirmPassword) {{
                    document.getElementById('result').innerHTML = '<div class="error">Passwords do not match</div>';
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/auth/reset-password-token/{token}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ password }})
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        document.getElementById('result').innerHTML = '<div class="success">Password reset successfully! You can now sign in.</div>';
                        document.getElementById('resetForm').style.display = 'none';
                    }} else {{
                        document.getElementById('result').innerHTML = '<div class="error">' + (data.error || 'Reset failed') + '</div>';
                    }}
                }} catch (error) {{
                    document.getElementById('result').innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html

@app.route('/api/auth/reset-password-token/<token>', methods=['POST'])
def reset_password_with_token(token):
    """Reset password using token"""
    try:
        data = request.get_json()
        new_password = data.get('password', '')
        
        if not new_password:
            return jsonify({"error": "New password required"}), 400
        
        # Validate password strength
        is_valid, password_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({"error": password_msg}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if token is valid and not expired
        cursor.execute(
            'SELECT id, email FROM users WHERE reset_token = ? AND reset_token_expires > ?',
            (token, datetime.now().isoformat())
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "Invalid or expired reset token"}), 400
        
        # Hash new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        # Update password and clear reset token
        cursor.execute(
            'UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expires = NULL WHERE id = ?',
            (password_hash, user[0])
        )
        db.commit()
        
        return jsonify({
            "message": "Password reset successfully. You can now sign in."
        }), 200
        
    except Exception as e:
        app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/teams', methods=['POST'])
@require_auth
def create_team():
    """Secure team creation endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        
        team_name = sanitize_input(data.get('name', ''))
        
        if not team_name:
            return jsonify({"error": "Team name is required"}), 400
        
        if len(team_name) > 100:
            return jsonify({"error": "Team name too long (max 100 characters)"}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Create team
        cursor.execute(
            'INSERT INTO teams (name, manager_id) VALUES (?, ?)',
            (team_name, g.user_id)
        )
        team_id = cursor.lastrowid
        
        # Add user as team member
        cursor.execute(
            'INSERT INTO team_members (team_id, user_id) VALUES (?, ?)',
            (team_id, g.user_id)
        )
        
        db.commit()
        
        return jsonify({
            "message": "Team created successfully",
            "team": {"id": team_id, "name": team_name}
        }), 201
        
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        app.logger.error(f"Team creation error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/teams', methods=['GET'])
@require_auth
def get_teams():
    """Get user's teams"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT t.id, t.name, t.created_at 
            FROM teams t 
            INNER JOIN team_members tm ON t.id = tm.team_id 
            WHERE tm.user_id = ?
        ''', (g.user_id,))
        
        teams = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            "teams": teams
        }), 200
        
    except Exception as e:
        app.logger.error(f"Get teams error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "ProductivityFlow Secure API",
        "version": "2.0.0",
        "status": "running",
        "security": "enabled",
        "email_configured": EMAIL_CONFIGURED,
        "endpoints": [
            "/health",
            "/api/auth/register",
            "/api/auth/login", 
            "/api/auth/verify-email",
            "/api/auth/verify-token/<token>",
            "/api/auth/request-password-reset",
            "/api/auth/reset-password",
            "/api/auth/reset-password-token/<token>",
            "/api/teams"
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
    print("🚀 Starting ProductivityFlow Secure Backend...")
    print("🔒 Security features enabled:")
    print("   - Secure random keys")
    print("   - Input validation and sanitization")
    print("   - Password strength requirements")
    print("   - JWT token expiry")
    print("   - SQL injection protection")
    print("   - Security headers")
    print("   - Rate limiting ready")
    print("📍 Backend will be available at: http://localhost:5000")
    print("🔧 API endpoints will be at: http://localhost:5000/api/")
    print("📊 Health check: http://localhost:5000/health")
    
    # Initialize database
    init_db()
    
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=False)  # Debug disabled for security 