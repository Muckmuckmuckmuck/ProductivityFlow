"""
Security Enhancements for ProductivityFlow Backend
Comprehensive security utilities, input validation, and protection mechanisms
"""

import re
import hashlib
import secrets
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
from functools import wraps
from flask import request, jsonify, current_app
import jwt
import hmac

# Configure logging
logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

class InputValidationError(Exception):
    """Custom exception for input validation errors"""
    pass

# --- Input Validation Patterns ---
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
TEAM_CODE_PATTERN = re.compile(r'^[A-Z0-9]{6}$')
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,50}$')
PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

# --- Input Validation Functions ---
def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_PATTERN.match(email.strip()))

def validate_team_code(team_code: str) -> bool:
    """Validate team code format (6 alphanumeric characters)"""
    if not team_code or not isinstance(team_code, str):
        return False
    return bool(TEAM_CODE_PATTERN.match(team_code.strip()))

def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username or not isinstance(username, str):
        return False
    return bool(USERNAME_PATTERN.match(username.strip()))

def validate_password_strength(password: str) -> bool:
    """Validate password strength requirements"""
    if not password or not isinstance(password, str):
        return False
    return bool(PASSWORD_PATTERN.match(password))

def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID format"""
    if not uuid_str or not isinstance(uuid_str, str):
        return False
    return bool(UUID_PATTERN.match(uuid_str.strip()))

def sanitize_string(input_str: str, max_length: int = 255) -> str:
    """Sanitize string input to prevent XSS and injection attacks"""
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', str(input_str))
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def validate_json_payload(required_fields: List[str], optional_fields: List[str] = None) -> Dict[str, Any]:
    """Validate JSON payload structure and content"""
    if not request.is_json:
        raise InputValidationError("Request must contain valid JSON")
    
    data = request.get_json()
    if not isinstance(data, dict):
        raise InputValidationError("Request body must be a JSON object")
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            raise InputValidationError(f"Missing required field: {field}")
        if data[field] is None:
            raise InputValidationError(f"Required field cannot be null: {field}")
    
    # Validate optional fields if provided
    if optional_fields:
        for field in optional_fields:
            if field in data and data[field] is not None:
                # Add validation logic for specific fields here
                pass
    
    return data

# --- Security Decorators ---
def require_authentication(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        try:
            # Extract token from "Bearer <token>" format
            if not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Invalid authorization header format'}), 401
            
            token = auth_header.split(' ')[1]
            
            # Verify token
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            # Add user info to request context
            request.user_id = payload.get('user_id')
            request.team_id = payload.get('team_id')
            request.user_role = payload.get('role')
            
            if not all([request.user_id, request.team_id, request.user_role]):
                return jsonify({'error': 'Invalid token payload'}), 401
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

def require_manager_role(f):
    """Decorator to require manager role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'user_role'):
            return jsonify({'error': 'Authentication required'}), 401
        
        if request.user_role != 'manager':
            return jsonify({'error': 'Manager role required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limit_by_ip(limit: str):
    """Custom rate limiting decorator based on IP address"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would integrate with your existing rate limiting system
            # For now, we'll use a simple implementation
            client_ip = get_client_ip()
            
            # Add rate limiting logic here
            # You can use Redis or in-memory storage to track requests per IP
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Security Utilities ---
def get_client_ip() -> str:
    """Get client IP address with proxy support"""
    # Check for forwarded headers (common with proxies)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    return request.remote_addr

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure token"""
    return secrets.token_urlsafe(length)

def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for storage"""
    return hashlib.sha256(data.encode()).hexdigest()

def verify_hash(data: str, hash_value: str) -> bool:
    """Verify hashed data"""
    return hmac.compare_digest(hash_sensitive_data(data), hash_value)

# --- SQL Injection Protection ---
def escape_sql_like_pattern(pattern: str) -> str:
    """Escape special characters in SQL LIKE patterns"""
    if not pattern:
        return ""
    
    # Escape SQL LIKE special characters
    escaped = pattern.replace('%', '\\%').replace('_', '\\_')
    return escaped

def validate_sql_identifier(identifier: str) -> bool:
    """Validate SQL identifier to prevent injection"""
    if not identifier:
        return False
    
    # Only allow alphanumeric characters, underscores, and hyphens
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', identifier))

# --- XSS Protection ---
def escape_html(text: str) -> str:
    """Escape HTML to prevent XSS attacks"""
    if not text:
        return ""
    
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }
    
    return "".join(html_escape_table.get(c, c) for c in text)

# --- Request Validation ---
def validate_request_headers() -> bool:
    """Validate request headers for security"""
    # Check for required headers
    content_type = request.headers.get('Content-Type', '')
    
    if request.method in ['POST', 'PUT', 'PATCH']:
        if not content_type.startswith('application/json'):
            return False
    
    return True

def validate_request_size(max_size: int = 1024 * 1024) -> bool:
    """Validate request size to prevent DoS attacks"""
    content_length = request.content_length
    if content_length and content_length > max_size:
        return False
    return True

# --- Error Handling ---
def handle_security_error(error: Exception) -> tuple:
    """Handle security-related errors consistently"""
    logger.warning(f"Security error: {error}")
    
    if isinstance(error, InputValidationError):
        return jsonify({'error': str(error)}), 400
    elif isinstance(error, SecurityError):
        return jsonify({'error': 'Security violation detected'}), 403
    else:
        return jsonify({'error': 'Internal server error'}), 500

# --- Security Headers ---
def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

# --- Validation Schemas ---
USER_REGISTRATION_SCHEMA = {
    'required_fields': ['email', 'password', 'name'],
    'email_validation': validate_email,
    'password_validation': validate_password_strength,
    'name_validation': lambda x: len(sanitize_string(x, 120)) >= 2
}

TEAM_CREATION_SCHEMA = {
    'required_fields': ['name'],
    'name_validation': lambda x: len(sanitize_string(x, 120)) >= 2
}

ACTIVITY_SUBMISSION_SCHEMA = {
    'required_fields': ['user_id', 'team_id'],
    'optional_fields': ['active_app', 'window_title', 'productive_hours', 'unproductive_hours']
}

# --- Usage Example ---
"""
Example usage in your Flask routes:

from security_enhancements import (
    require_authentication, require_manager_role, 
    validate_json_payload, validate_email, sanitize_string,
    handle_security_error, add_security_headers
)

@app.route('/api/secure-endpoint', methods=['POST'])
@require_authentication
@require_manager_role
def secure_endpoint():
    try:
        # Validate request
        if not validate_request_headers():
            return jsonify({'error': 'Invalid request headers'}), 400
        
        if not validate_request_size():
            return jsonify({'error': 'Request too large'}), 413
        
        # Validate JSON payload
        data = validate_json_payload(['required_field'])
        
        # Validate specific fields
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Sanitize input
        sanitized_name = sanitize_string(data['name'])
        
        # Process request...
        
        response = jsonify({'success': True})
        return add_security_headers(response)
        
    except Exception as e:
        return handle_security_error(e)
""" 