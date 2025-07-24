#!/usr/bin/env python3
"""
Simple working backend with SQLite database
"""

import os
import sys
import sqlite3
import bcrypt
import jwt
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-here'
app.config['DATABASE'] = 'productivityflow.db'

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            is_verified BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            manager_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER,
            user_id INTEGER,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(team_id, user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "ProductivityFlow Backend is running",
        "timestamp": datetime.now().isoformat(),
        "database": "SQLite (Local)"
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not all([email, password, name]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "User with this email already exists"}), 400
        
        # Create user
        cursor.execute(
            'INSERT INTO users (email, password_hash, name, is_verified) VALUES (?, ?, ?, ?)',
            (email, password_hash, name, True)  # Auto-verify for testing
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "User registered successfully",
            "user": {"email": email, "name": name}
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({"error": "Missing email or password"}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get user
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Create JWT token
        token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(days=7)
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
        return jsonify({"error": str(e)}), 500

@app.route('/api/teams', methods=['POST'])
def create_team():
    """Create team endpoint"""
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "No auth token available - please login first"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        data = request.get_json()
        team_name = data.get('name')
        
        if not team_name:
            return jsonify({"error": "Team name is required"}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Create team
        cursor.execute(
            'INSERT INTO teams (name, manager_id) VALUES (?, ?)',
            (team_name, user_id)
        )
        team_id = cursor.lastrowid
        
        # Add user as team member
        cursor.execute(
            'INSERT INTO team_members (team_id, user_id) VALUES (?, ?)',
            (team_id, user_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Team created successfully",
            "team": {"id": team_id, "name": team_name}
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "ProductivityFlow API",
        "version": "1.0.0",
        "status": "running",
        "database": "SQLite (Local)",
        "endpoints": [
            "/health",
            "/api/auth/register",
            "/api/auth/login",
            "/api/teams"
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting ProductivityFlow Local Backend...")
    print("📍 Backend will be available at: http://localhost:5000")
    print("🔧 API endpoints will be at: http://localhost:5000/api/")
    print("📊 Health check: http://localhost:5000/health")
    
    # Initialize database
    init_db()
    
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=True) 