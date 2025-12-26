from firebase_setup import get_firestore_client
from datetime import datetime
from typing import Dict, List, Optional

class FirestoreService:
    """Service class for Firestore operations"""
    
    @staticmethod
    def _get_db():
        """Get database connection"""
        db = get_firestore_client()
        if db is None:
            raise Exception("Firebase not configured. Please set FIREBASE_CREDENTIALS_PATH in .env")
        return db
    
    @staticmethod
    def create_project(data: Dict, current_user_id: str = 'anonymous') -> str:
        """Create a new project"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        data['members'] = [current_user_id]  # Creator is first member
        db = FirestoreService._get_db()
        doc_ref = db.collection('projects').add(data)
        return doc_ref[1].id
    
    @staticmethod
    def get_projects() -> List[Dict]:
        """Get all projects"""
        projects = []
        db = FirestoreService._get_db()
        docs = db.collection('projects').stream()
        for doc in docs:
            project = doc.to_dict()
            project['id'] = doc.id
            projects.append(project)
        return projects
    
    @staticmethod
    def get_project(project_id: str) -> Optional[Dict]:
        """Get a specific project"""
        db = FirestoreService._get_db()
        doc = db.collection('projects').document(project_id).get()
        if doc.exists:
            project = doc.to_dict()
            project['id'] = doc.id
            return project
        return None
    
    @staticmethod
    def update_project(project_id: str, data: Dict) -> bool:
        """Update a project"""
        data['updated_at'] = datetime.utcnow()
        db = FirestoreService._get_db()
        db.collection('projects').document(project_id).update(data)
        return True
    
    @staticmethod
    def delete_project(project_id: str) -> bool:
        """Delete a project and its tasks"""
        db = FirestoreService._get_db()
        tasks = db.collection('tasks').where('project_id', '==', project_id).stream()
        for task in tasks:
            task.reference.delete()
        db.collection('projects').document(project_id).delete()
        return True
    
    @staticmethod
    def create_task(data: Dict) -> str:
        """Create a new task"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        db = FirestoreService._get_db()
        doc_ref = db.collection('tasks').add(data)
        return doc_ref[1].id
    
    @staticmethod
    def get_tasks(project_id: str) -> List[Dict]:
        """Get all tasks for a project"""
        tasks = []
        db = FirestoreService._get_db()
        docs = db.collection('tasks').where('project_id', '==', project_id).stream()
        for doc in docs:
            task = doc.to_dict()
            task['id'] = doc.id
            tasks.append(task)
        return tasks
    
    @staticmethod
    def update_task(task_id: str, data: Dict) -> bool:
        """Update a task"""
        data['updated_at'] = datetime.utcnow()
        db = FirestoreService._get_db()
        db.collection('tasks').document(task_id).update(data)
        return True
    
    @staticmethod
    def delete_task(task_id: str) -> bool:
        """Delete a task"""
        db = FirestoreService._get_db()
        db.collection('tasks').document(task_id).delete()
        return True
    
    @staticmethod
    def find_project_by_access_code(access_code: str) -> Optional[Dict]:
        """Find project by access code"""
        db = FirestoreService._get_db()
        docs = db.collection('projects').where('access_code', '==', access_code).limit(1).stream()
        for doc in docs:
            project = doc.to_dict()
            project['id'] = doc.id
            return project
        return None
    
    @staticmethod
    def add_member_to_project(project_id: str, user_id: str) -> bool:
        """Add user to project members"""
        from google.cloud.firestore import ArrayUnion
        db = FirestoreService._get_db()
        db.collection('projects').document(project_id).update({
            'members': ArrayUnion([user_id]),
            'updated_at': datetime.utcnow()
        })
        return True
    
    @staticmethod
    def create_user_profile(uid: str, email: str, username: str) -> bool:
        """Create user profile in Firestore"""
        db = FirestoreService._get_db()
        user_data = {
            'uid': uid,
            'email': email,
            'username': username,
            'full_name': '',
            'phone': '',
            'bio': '',
            'location': '',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        db.collection('users').document(uid).set(user_data)
        return True
    
    @staticmethod
    def get_user_profile(uid: str) -> Optional[Dict]:
        """Get user profile from Firestore"""
        db = FirestoreService._get_db()
        doc = db.collection('users').document(uid).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    @staticmethod
    def update_user_profile(uid: str, data: Dict) -> bool:
        """Update user profile in Firestore"""
        db = FirestoreService._get_db()
        data['updated_at'] = datetime.utcnow()
        db.collection('users').document(uid).update(data)
        return True
    
    @staticmethod
    def add_invitation_to_project(project_id: str, email: str) -> bool:
        """Ajouter une invitation à un projet"""
        from google.cloud.firestore import ArrayUnion
        db = FirestoreService._get_db()
        db.collection('projects').document(project_id).update({
            'invitations': ArrayUnion([email]),
            'updated_at': datetime.utcnow()
        })
        return True
    
    @staticmethod
    def get_user_invitations(email: str) -> List[Dict]:
        """Récupérer les invitations d'un utilisateur"""
        db = FirestoreService._get_db()
        docs = db.collection('projects').where('invitations', 'array_contains', email).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @staticmethod
    def get_dashboard_stats() -> Dict:
        """Get dashboard statistics"""
        db = FirestoreService._get_db()
        projects = list(db.collection('projects').stream())
        tasks = list(db.collection('tasks').stream())
        
        total_projects = len(projects)
        total_tasks = len(tasks)
        
        # Task status distribution
        status_counts = {'todo': 0, 'in_progress': 0, 'done': 0}
        overdue_tasks = 0
        
        for task in tasks:
            task_data = task.to_dict()
            status = task_data.get('status', 'todo')
            status_counts[status] += 1
            
            # Check if task is overdue
            due_date = task_data.get('due_date')
            if due_date and status != 'done':
                # Handle timezone comparison
                now = datetime.utcnow()
                if hasattr(due_date, 'replace'):
                    due_date = due_date.replace(tzinfo=None) if due_date.tzinfo else due_date
                if due_date < now:
                    overdue_tasks += 1
        
        return {
            'total_projects': total_projects,
            'total_tasks': total_tasks,
            'overdue_tasks': overdue_tasks,
            'status_distribution': status_counts
        }