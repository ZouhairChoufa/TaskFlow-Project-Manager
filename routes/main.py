from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, session
from services.firestore_service import FirestoreService
from routes.auth import login_required
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime, timezone

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Dashboard with user-specific analytics"""
    
    # 1. Get Current User
    current_user_id = session.get('user', {}).get('uid')
    if not current_user_id:
        return redirect(url_for('auth.login'))

    # 2. Get User's Projects (Owner or Member)
    all_projects = FirestoreService.get_projects()
    user_projects = []
    
    # Filter projects
    for project in all_projects:
        is_owner = project.get('created_by') == current_user_id
        is_member = current_user_id in project.get('members', [])
        if is_owner or is_member:
            user_projects.append(project)

    # 3. Calculate Stats Dynamically based on these projects
    total_tasks = 0
    overdue_tasks = 0
    status_counts = {'todo': 0, 'in_progress': 0, 'done': 0}
    
    now = datetime.now(timezone.utc)

    for project in user_projects:
        # Get tasks for this specific project
        tasks = FirestoreService.get_tasks(project['id'])
        
        # Check if we should count ALL tasks in the project or ONLY tasks assigned to the user
        # Option A: Count ALL tasks in the project (Dashboard view of project health)
        # Option B: Filter by assignee (Personal workload view)
        
        # We will use Option A (Project Health) to match the "Total Projects" context
        total_tasks += len(tasks)
        
        for task in tasks:
            # Count Status
            status = task.get('status', 'todo')
            if status in status_counts:
                status_counts[status] += 1
            
            # Count Overdue
            # Check if task has a deadline, isn't done, and deadline is passed
            if task.get('due_date') and status != 'done':
                # Handle Firestore timestamp or ISO string
                due_date = task.get('due_date')
                # (Assuming due_date is offset-aware from previous fixes)
                if due_date < now:
                    overdue_tasks += 1

    # Construct the stats dictionary
    stats = {
        'total_projects': len(user_projects),
        'total_tasks': total_tasks,
        'overdue_tasks': overdue_tasks,
        'status_distribution': status_counts
    }
    
    return render_template('dashboard.html', stats=stats, projects=user_projects)

@main_bp.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint to get the same dynamic stats (for refresh)"""
    # ... You would copy the same logic here if you want the API to be dynamic too ...
    # For now, simplistic return
    return jsonify({'message': 'Use page reload for updated stats'})

@main_bp.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    """Contact support page"""
    current_user_id = session.get('user', {}).get('uid')
    user_data = FirestoreService.get_user_profile(current_user_id) if current_user_id else {}
    
    if not user_data:
        user_data = {
            'email': session.get('user', {}).get('email', ''),
            'phone': '',
            'username': session.get('user', {}).get('email', '').split('@')[0]
        }
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        try:
            send_contact_email(username, email, phone, message)
            flash('Votre message a été envoyé avec succès !', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            flash('Erreur lors de l\'envoi du message. Veuillez réessayer.', 'error')
    
    return render_template('contact.html', user_data=user_data)

def send_contact_email(username, email, phone, message):
    """Send contact form email using SMTP"""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.environ.get('SMTP_EMAIL')
    sender_password = os.environ.get('SMTP_PASSWORD')
    recipient_email = "zouhair.choufa3@gmail.com"
    
    if not sender_email or not sender_password:
        # Log error in production, don't crash
        print("SMTP Credentials missing")
        return
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Nouveau message de {username} - TaskFlow Support"
    
    body = f"""
    Nouveau message de support TaskFlow
    
    Utilisateur: {username}
    Email: {email}
    Téléphone: {phone}
    
    Message:
    {message}
    
    ---
    Envoyé depuis TaskFlow Support
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        
@main_bp.route('/demo')
def demo():
    """Page de démonstration et documentation"""
    return render_template('demo.html')