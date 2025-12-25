from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import firebase_admin.auth

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login')
def login():
    """Login page"""
    if session.get('user'):
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login.html')

@auth_bp.route('/register')
def register():
    """Register page"""
    if session.get('user'):
        return redirect(url_for('main.dashboard'))
    return render_template('auth/register.html')

@auth_bp.route('/api/session_login', methods=['POST'])
def session_login():
    """Create Flask session from Firebase ID token"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'No ID token provided'}), 400
        
        # Verify the ID token
        decoded_token = firebase_admin.auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # Store user info in session
        session['user'] = {
            'uid': uid,
            'email': email
        }
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('home'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=session.get('user'))