# TaskFlow

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0.0-black)
![Firebase](https://img.shields.io/badge/firebase-11.6.1-orange)
![Tailwind](https://img.shields.io/badge/tailwind-3.x-38bdf8)

TaskFlow is a professional project management application that provides teams with an intuitive Kanban board interface for task organization and collaboration. Built with modern web technologies, it offers real-time project tracking, team collaboration features, and comprehensive analytics to streamline workflow management.

## Description

TaskFlow solves the challenge of distributed team coordination by providing a centralized platform where teams can create projects, manage tasks through visual Kanban boards, and collaborate effectively. The application features secure access controls, real-time updates, and French localization, making it suitable for professional environments requiring structured project management workflows.

## Tech Stack

### Backend
- **Python 3.10+** - Core programming language
- **Flask 3.0.0** - Web application framework
- **Firebase Admin SDK 6.2.0** - Backend authentication and database
- **Google Cloud Firestore** - NoSQL document database
- **python-dotenv 1.0.0** - Environment variable management
- **Gunicorn 20.1.0** - WSGI HTTP Server for production

### Frontend
- **Jinja2** - Server-side templating engine
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript (ES6+)** - Client-side interactivity
- **Chart.js** - Data visualization library
- **FontAwesome 6.4.0** - Icon library

### Infrastructure
- **Firebase Authentication** - User authentication system
- **Firebase Firestore** - Real-time database
- **SMTP Integration** - Email notifications and contact forms

## Architecture

TaskFlow follows a **Model-View-Controller (MVC)** architecture pattern with Flask blueprints for modular organization:

- **Models**: Firestore collections (projects, tasks, users) managed through FirestoreService
- **Views**: Jinja2 templates with French localization and glassmorphism design
- **Controllers**: Flask blueprints (auth, main, projects, tasks) handling business logic
- **Services**: Abstraction layer for Firebase operations and external integrations

The application uses the **Application Factory Pattern** for Flask initialization and **Blueprint Registration** for route organization, ensuring scalable and maintainable code structure.

## Key Features

- **Kanban Board Management**: Drag-and-drop task organization across customizable columns
- **Project Access Control**: Secure project creation with access codes and member management
- **Real-time Collaboration**: Live updates and team member notifications
- **User Authentication**: Firebase-based secure login and registration system
- **Analytics Dashboard**: Project statistics and task distribution visualization
- **French Localization**: Complete French interface with professional terminology
- **Responsive Design**: Mobile-first approach with glassmorphism UI effects
- **Task Management**: Priority levels, due dates, assignee tracking, and status updates
- **Team Invitations**: Email-based project invitations with notification system
- **Profile Management**: User profile customization and account settings
- **Contact Support**: Integrated SMTP-based contact form system
- **Advanced Filtering**: Real-time task filtering by name and assignee
- **Unique Validation**: Prevents duplicate task names within projects
- **Smart Sorting**: Automatic task ordering by creation date

## Installation

### Prerequisites
- Python 3.10 or higher
- Firebase project with Firestore enabled
- Gmail account for SMTP (optional, for contact forms)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TaskFlow
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Firebase Configuration**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Enable Firestore Database (Native mode)
   - Enable Authentication with Email/Password provider
   - Generate service account key (Project Settings → Service Accounts)
   - Download web app configuration

5. **Environment Setup**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your Firebase credentials:
   ```env
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-generated-secret-key
   FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
   
   # Firebase Web Config
   FIREBASE_API_KEY=your-api-key
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   FIREBASE_APP_ID=your-app-id
   
   # SMTP Configuration (Optional)
   SMTP_EMAIL=your-gmail@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

6. **Generate Secret Key**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

## Usage

### Development Server
```bash
python app.py
```
The application will be available at `http://localhost:5000`

### Production Deployment
```bash
gunicorn app:create_app()
```

### Basic Workflow
1. **Registration**: Create an account using email/password
2. **Project Creation**: Create a new project with a unique access code
3. **Team Collaboration**: Share access codes to invite team members
4. **Task Management**: Use the Kanban board to create, assign, and track tasks
5. **Analytics**: Monitor project progress through the dashboard

### API Endpoints
- `GET /` - Landing page or redirect to dashboard
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `GET /dashboard/` - Analytics dashboard
- `GET /projects/` - Project listing
- `POST /projects/create` - Project creation
- `GET /projects/<id>/board` - Kanban board interface
- `POST /tasks/create` - Task creation
- `PUT /tasks/<id>/move` - Task status updates

## Development

### Project Structure
```
TaskFlow/
├── app.py                    # Application factory and configuration
├── config.py                 # Environment-based settings
├── firebase_setup.py         # Firebase initialization
├── routes/                   # Flask blueprints
│   ├── auth.py              # Authentication logic
│   ├── main.py              # Dashboard and utilities
│   ├── projects.py          # Project management
│   └── tasks.py             # Task operations
├── services/                 # Business logic layer
│   └── firestore_service.py # Database operations
├── templates/                # Jinja2 templates
└── static/                   # CSS, JavaScript, images
```

### Code Style
- Follow PEP 8 for Python code formatting
- Use descriptive variable and function names
- Implement proper error handling and logging
- Maintain consistent indentation (4 spaces)
- Add docstrings for all functions and classes

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.