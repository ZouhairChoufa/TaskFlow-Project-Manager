from flask import Blueprint, render_template, jsonify
from services.firestore_service import FirestoreService
from routes.auth import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Dashboard with analytics"""
    stats = FirestoreService.get_dashboard_stats()
    
    # Get user's projects (member + invited)
    from flask import session
    user_email = session.get('user', {}).get('email', 'anonymous@example.com')
    projects = FirestoreService.get_projects()
    
    # Filter projects where user is member or invited
    user_projects = []
    for project in projects:
        if 'anonymous' in project.get('members', []) or user_email in project.get('invitations', []):
            user_projects.append(project)
    
    return render_template('dashboard.html', stats=stats, projects=user_projects)

@main_bp.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    stats = FirestoreService.get_dashboard_stats()
    return jsonify(stats)