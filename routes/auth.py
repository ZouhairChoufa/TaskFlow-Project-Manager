from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
from services.firestore_service import FirestoreService
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
        username = data.get('username')  # For new registrations
        
        if not id_token:
            return jsonify({'error': 'No ID token provided'}), 400
        
        # Verify the ID token
        decoded_token = firebase_admin.auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # If username is provided, create user profile (new registration)
        if username:
            FirestoreService.create_user_profile(uid, email, username)
        
        # Get or create user profile
        user_profile = FirestoreService.get_user_profile(uid)
        if not user_profile:
            # Fallback for existing users without profile
            FirestoreService.create_user_profile(uid, email, email.split('@')[0])
            user_profile = FirestoreService.get_user_profile(uid)
        
        # Store user info in session
        session['user'] = {
            'uid': uid,
            'email': email,
            'username': user_profile.get('username', ''),
            'full_name': user_profile.get('full_name', ''),
            'profile': user_profile
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
    """User profile page with dynamic stats"""
    user = session.get('user')
    user_id = user.get('uid')
    user_profile = FirestoreService.get_user_profile(user_id)
    
    # --- DYNAMIC STATS CALCULATION ---
    try:
        # 1. Get all projects
        all_projects = FirestoreService.get_projects()
        
        # 2. Filter projects where user is Owner OR Member
        my_projects = []
        tasks_count = 0
        
        for p in all_projects:
            # Check membership
            if p.get('created_by') == user_id or user_id in p.get('members', []):
                my_projects.append(p)
                
                # 3. Count tasks assigned to this user in this project
                # (Only fetch tasks if user is part of the project)
                project_tasks = FirestoreService.get_tasks(p['id'])
                
                # Check match against username OR email (covers both assignment types)
                user_identifiers = [
                    user_profile.get('username'), 
                    user.get('email'),
                    user_profile.get('full_name')
                ]
                
                # Count tasks where assignee matches any of the user's identifiers
                user_tasks = [
                    t for t in project_tasks 
                    if t.get('assignee') and t.get('assignee') in user_identifiers
                ]
                tasks_count += len(user_tasks)

        projects_count = len(my_projects)
        
    except Exception as e:
        print(f"Error calculating stats: {e}")
        projects_count = 0
        tasks_count = 0

    return render_template('auth/profile.html', 
                         user=user, 
                         profile=user_profile, 
                         stats={'projects': projects_count, 'tasks': tasks_count})

@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        user = session.get('user')
        uid = user['uid']
        
        # Get form data
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        location = request.form.get('location', '').strip()
        linkedin = request.form.get('linkedin', '').strip()
        github = request.form.get('github', '').strip()
        
        # Validate inputs
        if len(full_name) > 100:
            flash('Full name must be less than 100 characters', 'error')
            return redirect(url_for('auth.profile'))
        
        if len(bio) > 500:
            flash('Bio must be less than 500 characters', 'error')
            return redirect(url_for('auth.profile'))
        
        # Update profile data
        profile_data = {
            'full_name': full_name,
            'phone': phone,
            'bio': bio,
            'location': location,
            'linkedin': linkedin,
            'github': github
        }
        
        # Update in Firestore
        FirestoreService.update_user_profile(uid, profile_data)
        
        # Update session
        session['user']['full_name'] = full_name
        
        flash('Profil mis à jour avec succès !', 'success')
        return redirect(url_for('auth.profile'))
        
    except Exception as e:
        flash(f'Erreur lors de la mise à jour: {str(e)}', 'error')
        return redirect(url_for('auth.profile'))