# Contributing to TaskFlow

We welcome contributions to TaskFlow! This document provides guidelines for contributing to the project.

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Enforcement

Project maintainers are responsible for clarifying the standards of acceptable behavior and are expected to take appropriate and fair corrective action in response to any instances of unacceptable behavior.

## How to Report Bugs

### Before Submitting a Bug Report

- Check the existing issues to avoid duplicates
- Ensure you're using the latest version of TaskFlow
- Verify the bug is reproducible in a clean environment

### Submitting a Bug Report

Create an issue with the following information:

1. **Bug Description**: Clear and concise description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the behavior
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: 
   - Operating System and version
   - Python version
   - Browser and version (for frontend issues)
   - Firebase project configuration (without sensitive data)
6. **Screenshots**: If applicable, add screenshots to help explain the problem
7. **Additional Context**: Any other context about the problem

### Bug Report Template

```markdown
## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Screenshots
If applicable, add screenshots to help explain your problem.

## Environment
- OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
- Python Version: [e.g. 3.10.5]
- Browser: [e.g. Chrome 96.0, Firefox 95.0]
- TaskFlow Version: [e.g. 1.0.0]

## Additional Context
Add any other context about the problem here.
```

## Setting Up the Development Environment

### Prerequisites

- Python 3.10 or higher
- Git
- Firebase project with Firestore enabled
- Code editor (VS Code recommended)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/TaskFlow.git
   cd TaskFlow
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase credentials
   ```

5. **Firebase Setup**
   - Create a Firebase project for development
   - Enable Firestore and Authentication
   - Download service account key
   - Configure environment variables

6. **Run Development Server**
   ```bash
   python app.py
   ```

### Development Tools

- **Linting**: Use `flake8` for Python code linting
- **Formatting**: Use `black` for code formatting
- **Testing**: Use `pytest` for unit testing (when implemented)

## Style Guide

### Python Code Style

Follow PEP 8 guidelines with these specific requirements:

#### General Guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 88 characters (Black formatter standard)
- Use descriptive variable and function names
- Add docstrings for all public functions and classes

#### Naming Conventions
```python
# Variables and functions: snake_case
user_profile = get_user_profile()

# Classes: PascalCase
class FirestoreService:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3

# Private methods: _leading_underscore
def _internal_method(self):
    pass
```

#### Function Documentation
```python
def create_project(data: Dict, current_user_id: str = 'anonymous') -> str:
    """Create a new project in Firestore.
    
    Args:
        data: Project data dictionary containing name, description, etc.
        current_user_id: ID of the user creating the project
        
    Returns:
        str: The ID of the created project
        
    Raises:
        Exception: If Firebase is not configured properly
    """
    pass
```

#### Import Organization
```python
# Standard library imports
import os
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
from flask import Blueprint, render_template
from firebase_admin import firestore

# Local imports
from services.firestore_service import FirestoreService
```

### HTML/Template Style

#### Jinja2 Templates
- Use consistent indentation (2 spaces)
- Keep template logic minimal
- Use descriptive variable names
- Add comments for complex template sections

```html
<!-- Good -->
{% if user.is_authenticated %}
    <div class="user-menu">
        <span>{{ user.username }}</span>
    </div>
{% endif %}

<!-- Avoid complex logic in templates -->
{% if user.projects|length > 0 and user.is_premium and not user.is_suspended %}
    <!-- This should be handled in the view -->
{% endif %}
```

#### CSS Classes
- Use Tailwind CSS utility classes
- Follow consistent naming for custom classes
- Group related classes logically

```html
<!-- Good: Logical grouping -->
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
    <h3 class="text-lg font-semibold text-gray-900">Project Title</h3>
</div>
```

### JavaScript Style

#### General Guidelines
- Use ES6+ features (const/let, arrow functions, template literals)
- Use descriptive function and variable names
- Add JSDoc comments for complex functions
- Handle errors gracefully

```javascript
// Good
const fetchProjectData = async (projectId) => {
    try {
        const response = await fetch(`/api/projects/${projectId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch project data:', error);
        showToast('Error loading project data', 'error');
    }
};
```

### Flask Route Style

```python
@projects_bp.route('/<project_id>/board')
@login_required
def project_board(project_id):
    """Display Kanban board for a specific project.
    
    Args:
        project_id: The ID of the project to display
        
    Returns:
        Rendered template or redirect if access denied
    """
    # Validate project access
    project = FirestoreService.get_project(project_id)
    if not project:
        return "Project not found", 404
    
    # Check user permissions
    current_user_id = session.get('user', {}).get('uid')
    if not _user_has_access(project, current_user_id):
        return render_template('join_project.html', project=project)
    
    # Fetch and organize data
    tasks = FirestoreService.get_tasks(project_id)
    board = _organize_tasks_by_status(tasks)
    
    return render_template('board.html', project=project, board=board)
```

## Submitting Pull Requests

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow the style guide
   - Add tests if applicable
   - Update documentation

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

4. **Push Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use the pull request template
   - Provide clear description of changes
   - Link related issues

### Pull Request Guidelines

#### Title Format
```
Type: Brief description

Examples:
- Feature: Add task filtering by assignee
- Fix: Resolve authentication redirect loop
- Docs: Update installation instructions
- Refactor: Improve Firestore service error handling
```

#### Description Template
```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have tested these changes locally
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
```

### Review Process

1. **Automated Checks**: Ensure all CI checks pass
2. **Code Review**: Address reviewer feedback promptly
3. **Testing**: Verify changes work as expected
4. **Documentation**: Update relevant documentation
5. **Merge**: Maintainer will merge after approval

### Commit Message Guidelines

Use conventional commit format:

```
type(scope): description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes (formatting, etc.)
- refactor: Code refactoring
- test: Adding or updating tests
- chore: Maintenance tasks

Examples:
- feat(auth): add password reset functionality
- fix(kanban): resolve drag and drop issue on mobile
- docs(readme): update installation instructions
```

## Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature development
- `hotfix/*`: Critical bug fixes

### Testing Guidelines

When testing is implemented:

- Write unit tests for new functions
- Test edge cases and error conditions
- Ensure tests pass before submitting PR
- Maintain test coverage above 80%

### Database Changes

When modifying Firestore structure:

1. Document schema changes
2. Provide migration instructions
3. Test with existing data
4. Update service layer accordingly

## Getting Help

- **Documentation**: Check existing documentation first
- **Issues**: Search existing issues for similar problems
- **Discussions**: Use GitHub Discussions for questions
- **Contact**: Reach out to maintainers for urgent matters

Thank you for contributing to TaskFlow!