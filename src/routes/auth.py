from flask import Blueprint, request, jsonify, session
from flask_cors import cross_origin
import hashlib
import os

auth_bp = Blueprint('auth', __name__)

# Admin credentials (in production, these should be stored securely in environment variables or database)
ADMIN_EMAIL = "infinitemobilecarwashdetailing@gmail.com"
ADMIN_PASSWORD_HASH = hashlib.sha256("InfinitePassword000*".encode()).hexdigest()

@auth_bp.route('/login', methods=['POST'])
@cross_origin()
def login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Hash the provided password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Check credentials
        if email == ADMIN_EMAIL.lower() and password_hash == ADMIN_PASSWORD_HASH:
            # Set session
            session['admin_logged_in'] = True
            session['admin_email'] = email
            session.permanent = True  # Make session persistent
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'email': email,
                    'role': 'admin'
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@cross_origin()
def logout():
    """Admin logout endpoint"""
    try:
        # Clear session
        session.pop('admin_logged_in', None)
        session.pop('admin_email', None)
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout error: {str(e)}'
        }), 500

@auth_bp.route('/check-auth', methods=['GET'])
@cross_origin()
def check_auth():
    """Check if admin is authenticated"""
    try:
        if session.get('admin_logged_in'):
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': {
                    'email': session.get('admin_email'),
                    'role': 'admin'
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'authenticated': False
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Auth check error: {str(e)}'
        }), 500

def require_admin_auth(f):
    """Decorator to require admin authentication for routes"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

