# TaskFlow - Professional Project Management Application

A modern, professional Project Management Application built with Flask and Firebase, featuring a sleek Kanban board interface and comprehensive analytics dashboard.

## 🚀 Features

- **Modern UI/UX**: Glassmorphism design with Tailwind CSS
- **Kanban Board**: Drag & drop task management
- **Project Management**: Create, edit, and manage projects
- **Analytics Dashboard**: Real-time project and task statistics
- **Firebase Integration**: Secure authentication and cloud database
- **Responsive Design**: Works on all devices

## 🛠️ Tech Stack

- **Backend**: Flask (Python 3.10+)
- **Database**: Firebase Firestore
- **Authentication**: Firebase Auth
- **Frontend**: Jinja2 Templates + Tailwind CSS
- **Charts**: Chart.js
- **Icons**: Font Awesome

## 📁 Project Structure

```
TaskFlow/
├── app.py                 # Flask application factory
├── config.py             # Configuration settings
├── firebase_setup.py     # Firebase initialization
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── routes/              # Flask blueprints
│   ├── __init__.py
│   ├── main.py         # Dashboard routes
│   ├── projects.py     # Project management routes
│   └── tasks.py        # Task management routes
├── services/           # Business logic layer
│   ├── __init__.py
│   └── firestore_service.py
├── templates/          # Jinja2 templates
│   ├── base.html      # Base layout
│   ├── dashboard.html # Analytics dashboard
│   ├── board.html     # Kanban board
│   └── projects.html  # Projects listing
└── static/            # Static assets
    ├── css/
    │   └── custom.css
    └── js/
        └── kanban.js
```

## 🔧 Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd TaskFlow
pip install -r requirements.txt
```

### 2. Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Enable Authentication (optional for this version)
4. Download service account key JSON file
5. Place the JSON file in your project directory

### 3. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` file:
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-credentials.json
```

### 4. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` to access TaskFlow.

## 🎨 Design System

### Color Palette
- **Background**: Slate (900, 800, 700)
- **Primary**: Indigo (600, 500, 400)
- **Success**: Emerald (600, 500, 400)
- **Warning**: Amber (600, 500, 400)
- **Danger**: Rose (600, 500, 400)

### Components
- **Glassmorphism Cards**: Semi-transparent backgrounds with blur effects
- **Smooth Animations**: CSS transitions and hover effects
- **Priority Badges**: Color-coded task priorities
- **Drag & Drop**: Intuitive task movement

## 📊 Features Overview

### Dashboard
- Project and task statistics
- Task distribution charts
- Recent projects overview
- Completion rate tracking

### Project Management
- Create/edit/delete projects
- Set project deadlines
- Project overview cards
- Quick access to Kanban boards

### Kanban Board
- Three-column layout (To Do, In Progress, Done)
- Drag & drop task movement
- Task priority indicators
- Real-time status updates

### Task Management
- Create tasks with priorities
- Assign tasks to team members
- Set due dates
- Task descriptions and details

## 🔒 Security Features

- Firebase Admin SDK for secure server-side operations
- Environment-based configuration
- Input validation and sanitization
- CSRF protection (Flask built-in)

## 🚀 Deployment

### Production Setup
1. Set `FLASK_ENV=production` in environment
2. Use a production WSGI server (Gunicorn included)
3. Configure Firebase production credentials
4. Set up proper domain and SSL

### Docker Deployment (Optional)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please open an issue in the repository.

---

Built with ❤️ using Flask and Firebase