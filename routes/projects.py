from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from services.firestore_service import FirestoreService
from routes.auth import login_required
from datetime import datetime

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/')
@login_required
def list_projects():
    """List all projects"""
    projects = FirestoreService.get_projects()
    return render_template('projects.html', projects=projects)

@projects_bp.route('/create', methods=['GET', 'POST'])
def create_project():
    """Create a new project"""
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate access code
        access_code = data.get('access_code', '').strip()
        if len(access_code) < 4:
            return jsonify({'error': 'Access code must be at least 4 characters'}), 400
        
        # Convert deadline string to datetime if provided
        if data.get('deadline'):
            data['deadline'] = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
        
        # TODO: Replace 'anonymous' with actual current_user.uid when auth is implemented
        current_user_id = 'anonymous'  # Placeholder for Firebase Auth UID
        project_id = FirestoreService.create_project(data, current_user_id)
        return jsonify({'success': True, 'id': project_id})
    
    return render_template('project_form.html')

@projects_bp.route('/<project_id>')
def view_project(project_id):
    """View project details"""
    project = FirestoreService.get_project(project_id)
    if not project:
        return "Project not found", 404
    return render_template('project_detail.html', project=project)

@projects_bp.route('/<project_id>/board')
def project_board(project_id):
    """Kanban board for a project"""
    project = FirestoreService.get_project(project_id)
    if not project:
        return "Project not found", 404
    
    # TODO: Replace with actual current_user.uid when auth is implemented
    current_user_id = 'anonymous'
    
    # Check if user is a member of the project
    if current_user_id not in project.get('members', []):
        return redirect(url_for('main.dashboard'))
    
    tasks = FirestoreService.get_tasks(project_id)
    
    # Organize tasks by status
    board = {
        'todo': [t for t in tasks if t.get('status') == 'todo'],
        'in_progress': [t for t in tasks if t.get('status') == 'in_progress'],
        'done': [t for t in tasks if t.get('status') == 'done']
    }
    
    return render_template('board.html', project=project, board=board)

@projects_bp.route('/<project_id>/edit', methods=['PUT'])
def edit_project(project_id):
    """Edit a project"""
    data = request.get_json()
    
    if data.get('deadline'):
        data['deadline'] = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
    
    FirestoreService.update_project(project_id, data)
    return jsonify({'success': True})

@projects_bp.route('/<project_id>/join', methods=['POST'])
def join_specific_project(project_id):
    """Join a specific project by access code"""
    data = request.get_json()
    access_code = data.get('access_code', '').strip()
    
    if len(access_code) < 4:
        return jsonify({'success': False, 'message': 'Access code must be at least 4 characters'}), 400
    
    # Get the specific project
    project = FirestoreService.get_project(project_id)
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'}), 404
    
    # Verify access code
    if project.get('access_code') != access_code:
        return jsonify({'success': False, 'message': 'Invalid Access Code'}), 403
    
    # TODO: Replace with actual current_user.uid when auth is implemented
    current_user_id = 'anonymous'
    
    # Check if user is already a member
    if current_user_id in project.get('members', []):
        return jsonify({'success': True, 'message': 'Already a member'})
    
    # Add user to project members
    FirestoreService.add_member_to_project(project_id, current_user_id)
    return jsonify({'success': True})

@projects_bp.route('/join', methods=['POST'])
def join_project():
    """Join a project by access code"""
    data = request.get_json()
    access_code = data.get('access_code', '').strip()
    
    if len(access_code) < 4:
        return jsonify({'error': 'Access code must be at least 4 characters'}), 400
    
    # Find project by access code
    project = FirestoreService.find_project_by_access_code(access_code)
    if not project:
        return jsonify({'error': 'Invalid access code'}), 404
    
    # TODO: Replace with actual current_user.uid when auth is implemented
    current_user_id = 'anonymous'
    
    # Check if user is already a member
    if current_user_id in project.get('members', []):
        return jsonify({'message': 'Already a member', 'project_id': project['id']})
    
    # Add user to project members
    FirestoreService.add_member_to_project(project['id'], current_user_id)
    return jsonify({'success': True, 'project_id': project['id'], 'project_name': project['name']})