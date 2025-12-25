from flask import Blueprint, render_template, jsonify
from services.firestore_service import FirestoreService
from routes.auth import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Dashboard with analytics"""
    stats = FirestoreService.get_dashboard_stats()
    projects = FirestoreService.get_projects()
    return render_template('dashboard.html', stats=stats, projects=projects)

@main_bp.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    stats = FirestoreService.get_dashboard_stats()
    return jsonify(stats)