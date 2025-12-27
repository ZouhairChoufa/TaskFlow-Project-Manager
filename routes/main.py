from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, session
from services.firestore_service import FirestoreService
from routes.auth import login_required
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Dashboard with analytics"""
    stats = FirestoreService.get_dashboard_stats()
    
    # Get user's projects (owner or member only)
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
    
    return render_template('dashboard.html', stats=stats, projects=user_projects)

@main_bp.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    stats = FirestoreService.get_dashboard_stats()
    return jsonify(stats)

@main_bp.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    """Contact support page"""
    # Get current user data from Firestore
    current_user_id = session.get('user', {}).get('uid')
    user_data = FirestoreService.get_user_profile(current_user_id) if current_user_id else {}
    
    # Fallback to session data if Firestore profile doesn't exist
    if not user_data:
        user_data = {
            'email': session.get('user', {}).get('email', ''),
            'phone': '',
            'username': session.get('user', {}).get('email', '').split('@')[0]
        }
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # Send email
        try:
            send_contact_email(username, email, phone, message)
            flash('Votre message a été envoyé avec succès !', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            flash('Erreur lors de l\'envoi du message. Veuillez réessayer.', 'error')
    
    return render_template('contact.html', user_data=user_data)

def send_contact_email(username, email, phone, message):
    """Send contact form email using SMTP"""
    # Email configuration from environment variables
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.environ.get('SMTP_EMAIL')
    sender_password = os.environ.get('SMTP_PASSWORD')
    recipient_email = "zouhair.choufa3@gmail.com"
    
    if not sender_email or not sender_password:
        raise Exception("SMTP credentials not configured")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Nouveau message de {username} - TaskFlow Support"
    
    # Email body
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
    
    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)