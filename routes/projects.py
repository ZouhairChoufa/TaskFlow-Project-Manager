from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from services.firestore_service import FirestoreService
from routes.auth import login_required
from datetime import datetime

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/')
@login_required
def list_projects():
    """List projects for current user only"""
    from flask import session
    current_user_id = session.get('user', {}).get('uid')
    
    if not current_user_id:
        current_user_id = 'anonymous'  # Fallback for development
    
    # Get all projects and filter by membership
    all_projects = FirestoreService.get_projects()
    user_projects = []
    
    for project in all_projects:
        is_owner = project.get('created_by') == current_user_id
        is_member = current_user_id in project.get('members', [])
        if is_owner or is_member:
            user_projects.append(project)
    
    return render_template('projects.html', projects=user_projects)

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    """Create a new project"""
    if request.method == 'POST':
        from flask import session
        data = request.get_json()
        
        # Validate access code
        access_code = data.get('access_code', '').strip()
        if len(access_code) < 4:
            return jsonify({'error': 'Le code d\'accès doit contenir au moins 4 caractères'}), 400
        
        # Convert deadline string to datetime if provided
        if data.get('deadline'):
            data['deadline'] = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
        
        # Get current user ID from session
        current_user_id = session.get('user', {}).get('uid')
        if not current_user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        project_id = FirestoreService.create_project(data, current_user_id)
        return jsonify({'success': True, 'id': project_id})
    
    return render_template('project_form.html')

@projects_bp.route('/<project_id>')
@login_required
def view_project(project_id):
    """View project details - Join Once Access Forever"""
    from flask import session
    current_user_id = session.get('user', {}).get('uid')
    
    if not current_user_id:
        current_user_id = 'anonymous'
    
    project = FirestoreService.get_project(project_id)
    if not project:
        return "Project not found", 404
    
    # Check access permission
    is_owner = project.get('created_by') == current_user_id
    is_member = current_user_id in project.get('members', [])
    
    if not (is_owner or is_member):
        # Show join page instead of 403
        return render_template('join_project.html', project=project)
        
    return redirect(url_for('projects.project_overview', project_id=project_id))

@projects_bp.route('/<project_id>/board')
@login_required
def project_board(project_id):
    """Kanban board for a project"""
    from flask import session
    project = FirestoreService.get_project(project_id)
    if not project:
        return "Project not found", 404
    
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return redirect(url_for('auth.login'))
    
    # Check if user is a member of the project
    is_owner = project.get('created_by') == current_user_id
    is_member = current_user_id in project.get('members', [])
    
    if not (is_owner or is_member):
        return render_template('join_project.html', project=project)
    
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
@login_required
def join_specific_project(project_id):
    """Join a specific project by access code"""
    from flask import session
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
    
    # Get current user ID from session
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return jsonify({'success': False, 'message': 'User not authenticated'}), 401
    
    # Check if user is already a member
    if current_user_id in project.get('members', []):
        return jsonify({'success': True, 'message': 'Vous êtes déjà membre de ce projet', 'already_member': True})
    
    # Add user to project members
    FirestoreService.add_member_to_project(project_id, current_user_id)
    return jsonify({'success': True, 'message': 'Vous avez rejoint le projet avec succès'})

@projects_bp.route('/<project_id>/overview')
@login_required
def project_overview(project_id):
    """Vue d'ensemble du projet"""
    from flask import session
    project = FirestoreService.get_project(project_id)
    if not project:
        return "Projet non trouvé", 404
    
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return redirect(url_for('auth.login'))
    
    # Check if user is a member of the project
    is_owner = project.get('created_by') == current_user_id
    is_member = current_user_id in project.get('members', [])
    
    if not (is_owner or is_member):
        return render_template('join_project.html', project=project)
    
    tasks = FirestoreService.get_tasks(project_id)
    
    # Get member data
    member_ids = project.get('members', [])
    members_data = FirestoreService.get_users_by_ids(member_ids)
    
    # Calculate project statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get('status') == 'done'])
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    pending_tasks = total_tasks - completed_tasks
    
    # Get recent activity (last 5 tasks)
    recent_tasks = sorted(tasks, key=lambda x: x.get('updated_at', x.get('created_at')), reverse=True)[:5]
    
    # Get team members (for now, just the member count)
    team_size = len(project.get('members', []))
    
    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_percentage': round(completion_percentage, 1),
        'pending_tasks': pending_tasks,
        'team_size': team_size
    }
    
    return render_template('project_overview.html', project=project, stats=stats, recent_tasks=recent_tasks, members_data=members_data)

@projects_bp.route('/<project_id>/calendar/data/<int:year>/<int:month>')
@login_required
def calendar_data(project_id, year, month):
    """API pour récupérer les données du calendrier"""
    from flask import session
    project = FirestoreService.get_project(project_id)
    if not project:
        return jsonify({'error': 'Projet non trouvé'}), 404
    
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return jsonify({'error': 'Non authentifié'}), 401
    
    is_owner = project.get('created_by') == current_user_id
    is_member = current_user_id in project.get('members', [])
    
    if not (is_owner or is_member):
        return jsonify({'error': 'Accès refusé'}), 403
    
    tasks = FirestoreService.get_tasks(project_id)
    
    from datetime import datetime, timedelta
    
    first_day = datetime(year, month, 1)
    start_offset = first_day.weekday()
    start_date = first_day - timedelta(days=start_offset)
    
    calendar_days = []
    current_date = start_date
    
    for i in range(42):
        day_tasks = []
        for task in tasks:
            if task.get('due_date'):
                if hasattr(task['due_date'], 'date'):
                    task_date = task['due_date'].date()
                elif hasattr(task['due_date'], 'seconds'):
                    task_date = datetime.fromtimestamp(task['due_date'].seconds).date()
                else:
                    continue
                    
                if task_date == current_date.date():
                    day_tasks.append(task)
        
        calendar_days.append({
            'date': current_date.isoformat(),
            'day': current_date.day,
            'is_current_month': current_date.month == month,
            'is_today': current_date.date() == datetime.now().date(),
            'tasks': day_tasks[:3],
            'extra_tasks': max(0, len(day_tasks) - 3)
        })
        
        current_date += timedelta(days=1)
    
    month_names = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ]
    
    return jsonify({
        'calendar_days': calendar_days,
        'current_month': month_names[month-1],
        'current_year': year,
        'current_month_index': month
    })
@projects_bp.route('/<project_id>/calendar')
@login_required
def project_calendar(project_id):
    """Calendrier du projet"""
    from flask import session
    project = FirestoreService.get_project(project_id)
    if not project:
        return "Projet non trouvé", 404
    
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return redirect(url_for('auth.login'))
    
    # Check if user is a member of the project
    is_owner = project.get('created_by') == current_user_id
    is_member = current_user_id in project.get('members', [])
    
    if not (is_owner or is_member):
        return render_template('join_project.html', project=project)
    
    tasks = FirestoreService.get_tasks(project_id)
    
    # Generate calendar matrix for current month
    from datetime import datetime, timedelta
    import calendar
    
    today = datetime.now()
    year = today.year
    month = today.month
    
    # Get first day of month and calculate start of calendar grid
    first_day = datetime(year, month, 1)
    # Monday = 0, Sunday = 6 in Python's weekday()
    # We want Monday = 0 for our grid
    start_offset = first_day.weekday()
    
    # Calculate start date (may be from previous month)
    start_date = first_day - timedelta(days=start_offset)
    
    # Generate 42 days (6 weeks)
    calendar_days = []
    current_date = start_date
    
    for i in range(42):
        day_tasks = []
        
        # Find tasks for this date
        for task in tasks:
            if task.get('due_date'):
                # Handle Firestore timestamp
                if hasattr(task['due_date'], 'date'):
                    task_date = task['due_date'].date()
                elif hasattr(task['due_date'], 'seconds'):
                    task_date = datetime.fromtimestamp(task['due_date'].seconds).date()
                else:
                    continue
                    
                if task_date == current_date.date():
                    day_tasks.append(task)
        
        calendar_days.append({
            'date': current_date,
            'day': current_date.day,
            'is_current_month': current_date.month == month,
            'is_today': current_date.date() == today.date(),
            'tasks': day_tasks[:3],  # Limit to 3 tasks
            'extra_tasks': max(0, len(day_tasks) - 3)
        })
        
        current_date += timedelta(days=1)
    
    month_names = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ]
    
    return render_template('project_calendar.html', 
                         project=project, 
                         calendar_days=calendar_days,
                         current_month=month_names[month-1],
                         current_year=year,
                         current_month_index=month)
    
@projects_bp.route('/<project_id>/invite', methods=['POST'])
@login_required
def invite_member(project_id):
    """Inviter un membre par email"""
    from flask import session
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'error': 'Email requis'}), 400
    
    project = FirestoreService.get_project(project_id)
    if not project:
        return jsonify({'error': 'Projet non trouvé'}), 404
    
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return jsonify({'error': 'Non authentifié'}), 401
    
    # Check if user is a member of the project
    is_owner = project.get('created_by') == current_user_id
    is_member = current_user_id in project.get('members', [])
    
    if not (is_owner or is_member):
        return jsonify({'error': 'Accès refusé'}), 403
    
    # Add email to project invitations
    FirestoreService.add_invitation_to_project(project_id, email)
    return jsonify({'success': True, 'message': f'Invitation envoyée à {email}'})
@projects_bp.route('/join_project/<project_id>', methods=['POST'])
@login_required
def join_project_route(project_id):
    """ID-based password verification - prevents duplicate code conflicts"""
    from flask import session
    data = request.get_json()
    access_code = data.get('access_code', '').strip()
    
    if not access_code:
        return jsonify({'success': False, 'message': 'Code d\'accès requis'}), 400
    
    # Get current user ID
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return jsonify({'success': False, 'message': 'Utilisateur non authentifié'}), 401
    
    # Get project by ID (not by access code)
    project = FirestoreService.get_project(project_id)
    if not project:
        return jsonify({'success': False, 'message': 'Projet non trouvé'}), 404
    
    # Verify access code matches this specific project
    if project.get('access_code') != access_code:
        return jsonify({'success': False, 'message': 'Code incorrect'}), 403
    
    # Check if already a member
    if current_user_id in project.get('members', []):
        return jsonify({'success': True, 'message': 'Vous êtes déjà membre de ce projet', 'already_member': True})
    
    # Add user to members array using arrayUnion
    from google.cloud.firestore import ArrayUnion
    db = FirestoreService._get_db()
    db.collection('projects').document(project_id).update({
        'members': ArrayUnion([current_user_id]),
        'updated_at': datetime.utcnow()
    })
    
    return jsonify({'success': True, 'message': 'Projet rejoint avec succès'})
@projects_bp.route('/search_and_join', methods=['POST'])
@login_required
def search_and_join():
    """Search project by name and join with access code"""
    from flask import session
    data = request.get_json()
    project_name = data.get('project_name', '').strip()
    access_code = data.get('access_code', '').strip()
    
    if not project_name or not access_code:
        return jsonify({'error': 'Nom du projet et code d\'accès requis'}), 400
    
    # Get current user ID
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return jsonify({'error': 'Utilisateur non authentifié'}), 401
    
    # Find project by name
    all_projects = FirestoreService.get_projects()
    project = None
    for p in all_projects:
        if p.get('name', '').lower() == project_name.lower():
            project = p
            break
    
    if not project:
        return jsonify({'error': 'Projet non trouvé'}), 404
    
    # Verify access code
    if project.get('access_code') != access_code:
        return jsonify({'error': 'Code incorrect'}), 403
    
    # Check if already a member
    if current_user_id in project.get('members', []):
        return jsonify({'success': True, 'message': 'Vous êtes déjà membre de ce projet', 'already_member': True})
    
    # Add user to members array
    from google.cloud.firestore import ArrayUnion
    db = FirestoreService._get_db()
    db.collection('projects').document(project['id']).update({
        'members': ArrayUnion([current_user_id]),
        'updated_at': datetime.utcnow()
    })
    
    return jsonify({'success': True, 'message': f'Projet "{project_name}" rejoint avec succès'})
    """Join a project by access code"""
    from flask import session
    data = request.get_json()
    access_code = data.get('access_code', '').strip()
    
    if len(access_code) < 4:
        return jsonify({'error': 'Access code must be at least 4 characters'}), 400
    
    # Find project by access code
    project = FirestoreService.find_project_by_access_code(access_code)
    if not project:
        return jsonify({'error': 'Invalid access code'}), 404
    
    # Get current user ID from session
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return jsonify({'error': 'User not authenticated'}), 401
    
    # Check if user is already a member
    if current_user_id in project.get('members', []):
        return jsonify({'success': True, 'message': 'Vous êtes déjà membre de ce projet', 'project_id': project['id'], 'already_member': True})
    
    # Add user to project members
    FirestoreService.add_member_to_project(project['id'], current_user_id)
    return jsonify({'success': True, 'project_id': project['id'], 'project_name': project['name']})