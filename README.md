# TaskFlow - Professional Project Management Application

A modern, enterprise-grade Project Management Application built with Flask and Firebase, featuring secure authentication, professional landing page, Kanban board interface, and comprehensive analytics dashboard.

---

## Table of Contents
1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Setup Instructions](#setup-instructions)
5. [Design System](#design-system)
6. [Features Overview](#features-overview)
7. [Security Features](#security-features)
8. [User Experience](#user-experience)
9. [Deployment](#deployment)
10. [Development](#development)
11. [Contributing](#contributing)
12. [License](#license)
13. [Acknowledgments](#acknowledgments)

---

## Features

- **Professional Landing Page**: Hero section with compelling CTAs and feature highlights
- **Secure Authentication**: Firebase Auth + Flask sessions with login/register system
- **Dark/Light Mode**: Professional theme switching with system preference detection
- **Kanban Board**: Drag & drop task management with real-time updates
- **Project Access Control**: Secure project joining with access codes
- **Analytics Dashboard**: Real-time statistics with Chart.js visualizations
- **Responsive Design**: Mobile-first approach with glassmorphism effects
- **User Profile**: Account management and session handling
- **French Interface**: Complete French localization with dynamic navigation
- **Contact Support**: Built-in contact form with SMTP email integration
- **Member Management**: Real user data integration with initials avatar system
- **Role-Based Access**: Owner/member permissions with secure project visibility

## Tech Stack

- **Backend**: Flask (Python 3.10+) with Application Factory pattern
- **Database**: Firebase Firestore with Admin SDK
- **Authentication**: Hybrid Firebase Client Auth + Flask Server Sessions
- **Frontend**: Jinja2 Templates + Tailwind CSS (CDN)
- **Charts**: Chart.js for analytics visualization
- **Icons**: FontAwesome 6.4.0
- **Styling**: Glassmorphism effects with backdrop-filter
- **Email**: SMTP integration with Gmail for contact forms
- **Localization**: French interface with dynamic navigation system

---

## Project Structure

```text
TaskFlow/
├── app.py                    # Flask application factory with Firebase init
├── config.py                 # Environment-based configuration
├── firebase_setup.py         # Firebase Admin SDK initialization
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore patterns
├── routes/                   # Flask blueprints (modular architecture)
│   ├── __init__.py
│   ├── auth.py              # Authentication routes & login_required decorator
│   ├── main.py              # Dashboard & contact routes (protected)
│   ├── projects.py          # Project management & access control
│   └── tasks.py             # Task CRUD operations
├── services/                 # Business logic layer
│   ├── __init__.py
│   └── firestore_service.py  # Firestore operations & data access
├── templates/                # Jinja2 templates with dark mode support
│   ├── auth/                # Authentication templates
│   │   ├── login.html       # Login page with Firebase integration
│   │   ├── register.html    # Registration with client-side validation
│   │   └── profile.html     # User profile management
│   ├── base_fr.html         # French base layout with dynamic navigation
│   ├── home.html            # Professional landing page
│   ├── dashboard.html       # Analytics dashboard with charts
│   ├── board.html           # Kanban board with drag & drop
│   ├── projects.html        # Projects listing with access control
│   ├── contact.html         # Contact support form
│   └── project_overview.html # Project dashboard with team info
└── static/                  # Static assets
    ├── css/
    │   └── custom.css       # Custom styles & animations
    └── js/
        └── kanban.js        # Drag & drop functionality
```

---

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd TaskFlow
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Firebase Setup

1. **Create Firebase Project**: Go to [Firebase Console](https://console.firebase.google.com/).
2. **Enable Services**:
   - Firestore Database (Native mode)
   - Authentication → Email/Password provider
3. **Get Credentials**:
   - **Service Account**: Project Settings → Service Accounts → Generate new private key
   - **Web Config**: Project Settings → Your apps → Web app config
4. **Place Files**: Put service account JSON in project root.

### 3. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` file with your Firebase credentials:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-generated-secret-key
FIREBASE_CREDENTIALS_PATH=your-service-account-key.json

# Firebase Web Config (from Firebase Console)
FIREBASE_API_KEY=your-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id

# SMTP Configuration for Contact Form
SMTP_EMAIL=your-gmail@gmail.com
SMTP_PASSWORD=your-app-password
```

### 4. Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` to access TaskFlow.

---

## Design System

### Color Palette

- **Light Mode**: Slate-50 backgrounds, white surfaces, slate-900 text
- **Dark Mode**: Slate-900 backgrounds, slate-800 surfaces, white text
- **Primary**: Indigo (600, 500, 400) for actions and branding
- **Success**: Emerald (600, 500, 400) for completed states
- **Warning**: Amber (600, 500, 400) for pending/overdue
- **Danger**: Rose (600, 500, 400) for errors and deletion

### Components

- **Glassmorphism Cards**: Semi-transparent with backdrop-blur effects
- **Smooth Animations**: CSS transitions with cubic-bezier easing
- **Priority Badges**: Color-coded task priorities with gradients
- **Theme Toggle**: Moon/Sun icons with smooth transitions
- **Drag & Drop**: Visual feedback with hover states

---

## Features Overview

### Landing Page

- Professional hero section with value proposition
- Feature highlights with check icons
- Dual CTAs (Register/Login) with hover effects
- Mock Kanban board preview
- Responsive design with fade-in animations

### Authentication System

- **Hybrid Security**: Firebase client auth + Flask server sessions
- **Registration**: Email/password with validation
- **Login**: Secure token exchange with error handling
- **Session Management**: Server-side user state
- **Route Protection**: Login required decorator
- **Profile Management**: User account information

### Dashboard

- **Analytics Cards**: Project/task statistics with icons
- **Chart Visualization**: Task distribution donut chart
- **Recent Projects**: Scrollable list with member access control
- **Quick Actions**: Create project and join project modals
- **Real-time Data**: Live statistics from Firestore

### Project Management

- **Access Control**: Projects with secure access codes
- **Member System**: Creator automatically added as member
- **Join Flow**: Modal-based project joining with validation
- **Visual Indicators**: Lock icons for private projects
- **CRUD Operations**: Full project lifecycle management

### Kanban Board

- **Three Columns**: To Do, In Progress, Done with status counts
- **Drag & Drop**: Smooth task movement between columns
- **Task Cards**: Priority badges, assignee info, due dates
- **Real-time Updates**: Instant status synchronization
- **Member Protection**: Only project members can access

### Task Management

- **Priority System**: High/Medium/Low with color coding
- **Assignment**: Task assignee with user icons
- **Due Dates**: Calendar integration with overdue detection
- **Status Tracking**: Automatic status updates via drag & drop
- **Rich Information**: Title, description, metadata

---

## Security Features

- **Firebase Admin SDK**: Server-side token verification
- **Environment Variables**: Secure credential management
- **Route Protection**: Login required for sensitive areas
- **Access Codes**: Project-level security with member verification
- **Session Management**: Secure Flask sessions with user data
- **Input Validation**: Client and server-side validation
- **CSRF Protection**: Flask built-in security measures

---

## User Experience

### Navigation Flow

1. **Landing Page** → Professional introduction with CTAs
2. **Authentication** → Secure login/register with Firebase
3. **Dashboard** → Analytics overview with project access
4. **Projects** → List view with join/create options
5. **Kanban Board** → Task management with drag & drop
6. **Profile** → Account management and logout
7. **Contact Support** → Built-in support form with email integration

### French Interface

- **Complete Localization**: All interface elements in French
- **Dynamic Navigation**: Context-aware sidebar (global vs project-specific)
- **Professional Styling**: Enterprise SaaS design patterns
- **Responsive Layout**: Mobile-first French interface

### Responsive Design

- **Mobile First**: Optimized for all screen sizes
- **Touch Friendly**: Large touch targets and gestures
- **Progressive Enhancement**: Works without JavaScript
- **Fast Loading**: Optimized assets and lazy loading

---

## Deployment

### Production Setup

1. Set `FLASK_ENV=production` in environment.
2. Use production WSGI server: `gunicorn app:create_app()`.
3. Configure Firebase production credentials.
4. Set up proper domain with SSL/TLS.
5. Configure environment variables on hosting platform.

### Docker Deployment

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]
```

### Environment Variables for Production

```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
FIREBASE_CREDENTIALS_PATH=/path/to/production/credentials.json
FIREBASE_API_KEY=your-production-api-key
# ... other Firebase config
```

---

## Development

### Local Development

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### Code Structure

- **Blueprints**: Modular route organization
- **Service Layer**: Business logic separation
- **Template Inheritance**: DRY template structure
- **Environment Config**: Flexible configuration management

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the existing code style
4. Add tests if applicable
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Open an issue in the repository
- Check the documentation in the code comments
- Review the Firebase and Flask documentation

## Acknowledgments

- **Flask**: Micro web framework for Python
- **Firebase**: Backend-as-a-Service platform
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js**: Simple yet flexible JavaScript charting
- **FontAwesome**: Icon library and toolkit

---

Built with Flask, Firebase, and modern web technologies