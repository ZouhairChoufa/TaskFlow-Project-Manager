from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from services.firestore_service import FirestoreService
from routes.auth import login_required
from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/')
@login_required
def list_projects():
    """List projects for current user only"""
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
        data = request.get_json()
        
        # 1. Nettoyage du code d'accès
        access_code = data.get('access_code', '').strip()
        if len(access_code) < 4:
            return jsonify({'error': 'Le code d\'accès doit contenir au moins 4 caractères'}), 400
        
        # --- NOUVEAU : Vérifier si le code existe déjà ---
        all_projects = FirestoreService.get_projects()
        for p in all_projects:
            if p.get('access_code') == access_code:
                # Si on trouve un doublon, on génère une erreur
                return jsonify({'error': 'Ce code d\'accès est déjà utilisé par un autre projet. Veuillez en générer un nouveau.'}), 409
        # -----------------------------------------------

        # Convert deadline string to datetime if provided
        if data.get('deadline'):
            try:
                # Gestion simple de la date (YYYY-MM-DD)
                data['deadline'] = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            except:
                pass # Ou gérer l'erreur de format
        
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
    
    # FIX IS HERE: Use datetime.now(timezone.utc)
    return render_template('board.html', project=project, board=board, now=datetime.now(timezone.utc))

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
    
@projects_bp.route('/<project_id>/invite_member', methods=['POST'])
@login_required
def invite_member_by_email(project_id):
    """Invite a member by email"""
    data = request.get_json()
    print(f"DEBUG: Received data: {data}")  # Debug line
    
    email = data.get('email', '').strip().lower() if data else ''
    print(f"DEBUG: Email after processing: '{email}'")  # Debug line
    
    if not email:
        print("DEBUG: Email validation failed")
        return jsonify({'success': False, 'error': 'Email requis'}), 400
    
    project = FirestoreService.get_project(project_id)
    if not project:
        return jsonify({'success': False, 'error': 'Projet non trouvé'}), 404
    
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return jsonify({'success': False, 'error': 'Non authentifié'}), 401
    
    # Check if user is owner or member
    is_owner = project.get('created_by') == current_user_id
    is_member = current_user_id in project.get('members', [])
    
    if not (is_owner or is_member):
        return jsonify({'success': False, 'error': 'Accès refusé'}), 403
    
    # Find user by email
    user = FirestoreService.find_user_by_email(email)
    if not user:
        return jsonify({'success': False, 'error': 'Utilisateur non trouvé avec cet email'}), 404
    
    user_id = user.get('uid')
    
    # Check if already a member
    if user_id in project.get('members', []):
        return jsonify({'success': False, 'error': 'Cet utilisateur est déjà membre du projet', 'category': 'warning'}), 200
    
    # Check if already has pending invite
    if user_id in project.get('pending_invites', []):
        return jsonify({'success': False, 'error': 'Une invitation est déjà en attente pour cet utilisateur', 'category': 'warning'}), 200
    
    # Add to pending invites
    FirestoreService.add_pending_invite(project_id, user_id)
    
    # Send email notification
    try:
        send_invitation_email(email, project.get('name'), project_id)
    except Exception as e:
        print(f"Failed to send email: {e}")
    
    return jsonify({'success': True, 'message': 'Invitation envoyée avec succès'})

@projects_bp.route('/accept_invite/<project_id>', methods=['POST'])
@login_required
def accept_invite(project_id):
    """Accept project invitation"""
    current_user_id = session.get('user', {}).get('uid')
    
    if not current_user_id:
        return jsonify({'success': False, 'error': 'Non authentifié'}), 401
    
    project = FirestoreService.get_project(project_id)
    if not project:
        return jsonify({'success': False, 'error': 'Projet non trouvé'}), 404
    
    # Check if user has pending invite
    if current_user_id not in project.get('pending_invites', []):
        return jsonify({'success': False, 'error': 'Aucune invitation en attente'}), 400
    
    # Move from pending_invites to members
    FirestoreService.accept_invitation(project_id, current_user_id)
    
    flash('Bienvenue dans le projet !', 'success')
    return jsonify({'success': True, 'redirect': url_for('projects.project_overview', project_id=project_id)})

@projects_bp.route('/decline_invite/<project_id>', methods=['POST'])
@login_required
def decline_invite(project_id):
    """Decline project invitation"""
    current_user_id = session.get('user', {}).get('uid')
    
    if not current_user_id:
        return jsonify({'success': False, 'error': 'Non authentifié'}), 401
    
    project = FirestoreService.get_project(project_id)
    if not project:
        return jsonify({'success': False, 'error': 'Projet non trouvé'}), 404
    
    # Remove from pending invites
    FirestoreService.decline_invitation(project_id, current_user_id)
    
    return jsonify({'success': True, 'message': 'Invitation refusée'})

def send_invitation_email(email, project_name, project_id):
    """Send invitation email"""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.environ.get('SMTP_EMAIL')
    sender_password = os.environ.get('SMTP_PASSWORD')
    
    if not sender_email or not sender_password:
        raise Exception("SMTP credentials not configured")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = f"Invitation au projet {project_name} - TaskFlow"
    
    body = f"""
    Vous avez été invité à rejoindre le projet "{project_name}" sur TaskFlow.
    
    Connectez-vous à votre compte TaskFlow pour accepter ou refuser cette invitation.
    
    ---
    TaskFlow - Gestion de Projets
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
@projects_bp.route('/join_project/<project_id>', methods=['POST'])
@login_required
def join_project_route(project_id):
    """ID-based password verification - prevents duplicate code conflicts"""
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
    """Rechercher et rejoindre un projet via son code d'accès uniquement"""
    from flask import session
    from datetime import datetime
    
    data = request.get_json()
    access_code = data.get('access_code', '').strip()
    
    # 1. Validation : On ne vérifie QUE le code d'accès
    if not access_code or len(access_code) < 4:
        return jsonify({'success': False, 'message': 'Code d\'accès invalide ou manquant'}), 400
    
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return jsonify({'success': False, 'message': 'Non authentifié'}), 401

    # 2. Chercher le projet qui correspond à ce code
    all_projects = FirestoreService.get_projects()
    target_project = None
    
    for p in all_projects:
        # Comparaison sensible à la casse
        if p.get('access_code') == access_code:
            target_project = p
            break
    
    if not target_project:
        return jsonify({'success': False, 'message': 'Aucun projet trouvé avec ce code'}), 404

    # 3. Vérifier si l'utilisateur est déjà membre
    if current_user_id in target_project.get('members', []) or target_project.get('created_by') == current_user_id:
        return jsonify({
            'success': True, 
            'message': 'Vous êtes déjà membre de ce projet', 
            'project_id': target_project['id'],
            'already_member': True
        })

    # 4. Ajouter l'utilisateur au projet
    try:
        from google.cloud.firestore import ArrayUnion
        db = FirestoreService._get_db()
        db.collection('projects').document(target_project['id']).update({
            'members': ArrayUnion([current_user_id]),
            'updated_at': datetime.utcnow()
        })
        
        return jsonify({
            'success': True, 
            'message': f'Bienvenue dans le projet "{target_project.get("name")}" !',
            'project_id': target_project['id']
        })
        
    except Exception as e:
        print(f"Error joining project: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur lors de l\'ajout'}), 500