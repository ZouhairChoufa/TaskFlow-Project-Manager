from flask import Blueprint, request, jsonify
from services.firestore_service import FirestoreService
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/create', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json()
    
    # Check for unique task name within project
    project_id = data.get('project_id')
    task_title = data.get('title', '').strip()
    
    if project_id and task_title:
        existing_tasks = FirestoreService.get_tasks(project_id)
        for task in existing_tasks:
            if task.get('title', '').strip().lower() == task_title.lower():
                return jsonify({'success': False, 'error': 'Le nom de la tâche doit être unique dans ce projet.'}), 400
    
    # Convert due_date string to datetime if provided
    if data.get('due_date'):
        data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
    
    # Set default status if not provided
    if 'status' not in data:
        data['status'] = 'todo'
    
    task_id = FirestoreService.create_task(data)
    return jsonify({'success': True, 'id': task_id})

@tasks_bp.route('/<task_id>/update', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    data = request.get_json()
    
    if data.get('due_date'):
        data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
    
    FirestoreService.update_task(task_id, data)
    return jsonify({'success': True})

@tasks_bp.route('/<task_id>/move', methods=['PUT'])
def move_task(task_id):
    """Move task to different status (for drag & drop)"""
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['todo', 'in_progress', 'done']:
        return jsonify({'error': 'Invalid status'}), 400
    
    FirestoreService.update_task(task_id, {'status': new_status})
    return jsonify({'success': True})

@tasks_bp.route('/<task_id>/delete', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    FirestoreService.delete_task(task_id)
    return jsonify({'success': True})