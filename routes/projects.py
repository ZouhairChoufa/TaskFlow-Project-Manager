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

@projects_bp.route('/<project_id>/overview')
@login_required
def project_overview(project_id):
    """Vue d'ensemble du projet"""
    project = FirestoreService.get_project(project_id)
    if not project:
        return "Projet non trouvé", 404
    
    # TODO: Replace with actual current_user.uid when auth is implemented
    current_user_id = 'anonymous'
    
    # Check if user is a member of the project
    if current_user_id not in project.get('members', []):
        return redirect(url_for('main.dashboard'))
    
    tasks = FirestoreService.get_tasks(project_id)
    
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
    
    return render_template('project_overview.html', project=project, stats=stats, recent_tasks=recent_tasks)

@projects_bp.route('/<project_id>/calendar/data/<int:year>/<int:month>')
@login_required
def calendar_data(project_id, year, month):
    """API pour récupérer les données du calendrier"""
    project = FirestoreService.get_project(project_id)
    if not project:
        return jsonify({'error': 'Projet non trouvé'}), 404
    
    current_user_id = 'anonymous'
    if current_user_id not in project.get('members', []):
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
    project = FirestoreService.get_project(project_id)
    if not project:
        return "Projet non trouvé", 404
    
    # TODO: Replace with actual current_user.uid when auth is implemented
    current_user_id = 'anonymous'
    
    # Check if user is a member of the project
    if current_user_id not in project.get('members', []):
        return redirect(url_for('main.dashboard'))
    
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
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'error': 'Email requis'}), 400
    
    project = FirestoreService.get_project(project_id)
    if not project:
        return jsonify({'error': 'Projet non trouvé'}), 404
    
    # TODO: Replace with actual current_user.uid when auth is implemented
    current_user_id = 'anonymous'
    
    # Check if user is a member of the project
    if current_user_id not in project.get('members', []):
        return jsonify({'error': 'Accès refusé'}), 403
    
    # Add email to project invitations
    FirestoreService.add_invitation_to_project(project_id, email)
    return jsonify({'success': True, 'message': f'Invitation envoyée à {email}'})
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