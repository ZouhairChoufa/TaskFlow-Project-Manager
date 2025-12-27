from flask import Flask, render_template, session, redirect, url_for
from config import config
from firebase_setup import initialize_firebase
import os

# Initialize Firebase when app starts
initialize_firebase()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Custom Jinja2 filter for initials
    @app.template_filter('initials')
    def initials_filter(name):
        """Generate initials from a name"""
        if not name or not isinstance(name, str):
            return 'U'
        
        words = name.strip().split()
        if len(words) >= 2:
            return (words[0][0] + words[-1][0]).upper()
        elif len(words) == 1 and len(words[0]) >= 2:
            return words[0][:2].upper()
        elif len(words) == 1:
            return words[0][0].upper()
        return 'U'
    
    # Make Firebase config available to templates
    @app.context_processor
    def inject_firebase_config():
        return {
            'firebase_config': {
                'apiKey': app.config.get('FIREBASE_API_KEY'),
                'authDomain': app.config.get('FIREBASE_AUTH_DOMAIN'),
                'projectId': app.config.get('FIREBASE_PROJECT_ID'),
                'storageBucket': app.config.get('FIREBASE_STORAGE_BUCKET'),
                'messagingSenderId': app.config.get('FIREBASE_MESSAGING_SENDER_ID'),
                'appId': app.config.get('FIREBASE_APP_ID')
            }
        }
    
    # Home route
    @app.route('/')
    def home():
        if session.get('user'):
            return redirect(url_for('main.dashboard'))
        return render_template('home.html')
    
    # Register blueprints
    from routes.main import main_bp
    from routes.projects import projects_bp
    from routes.tasks import tasks_bp
    from routes.auth import auth_bp
    
    app.register_blueprint(main_bp, url_prefix='/dashboard')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(auth_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)