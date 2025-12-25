// Kanban Board Drag & Drop Functionality
class KanbanBoard {
    constructor() {
        this.draggedTask = null;
        this.init();
    }

    init() {
        this.setupDragAndDrop();
        this.setupTaskActions();
    }

    setupDragAndDrop() {
        // Make task cards draggable
        document.querySelectorAll('.task-card').forEach(card => {
            card.addEventListener('dragstart', this.handleDragStart.bind(this));
            card.addEventListener('dragend', this.handleDragEnd.bind(this));
        });

        // Setup drop zones
        document.querySelectorAll('.kanban-column').forEach(column => {
            column.addEventListener('dragover', this.handleDragOver.bind(this));
            column.addEventListener('dragleave', this.handleDragLeave.bind(this));
            column.addEventListener('drop', this.handleDrop.bind(this));
        });
    }

    handleDragStart(e) {
        this.draggedTask = e.target;
        e.target.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', e.target.outerHTML);
    }

    handleDragEnd(e) {
        e.target.classList.remove('dragging');
        this.draggedTask = null;
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        e.currentTarget.classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.currentTarget.classList.remove('drag-over');
    }

    async handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-over');
        
        if (this.draggedTask) {
            const newStatus = e.currentTarget.dataset.status;
            const taskId = this.draggedTask.dataset.taskId;
            
            // Move task visually
            e.currentTarget.appendChild(this.draggedTask);
            
            // Update task status in backend
            try {
                const response = await fetch(`/tasks/${taskId}/move`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ status: newStatus })
                });
                
                const result = await response.json();
                
                if (!result.success) {
                    // Revert if failed
                    this.showNotification('Failed to move task', 'error');
                    location.reload();
                } else {
                    this.showNotification('Task moved successfully', 'success');
                    this.updateColumnCounts();
                }
            } catch (error) {
                console.error('Error moving task:', error);
                this.showNotification('Error moving task', 'error');
                location.reload();
            }
        }
    }

    setupTaskActions() {
        // Add click handlers for task actions
        document.querySelectorAll('.task-card').forEach(card => {
            card.addEventListener('dblclick', this.editTask.bind(this));
        });
    }

    editTask(e) {
        const taskId = e.currentTarget.dataset.taskId;
        // Implement task editing modal
        console.log('Edit task:', taskId);
    }

    updateColumnCounts() {
        document.querySelectorAll('.kanban-column').forEach(column => {
            const count = column.querySelectorAll('.task-card').length;
            const badge = column.parentElement.querySelector('.column-count');
            if (badge) {
                badge.textContent = count;
            }
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-4 py-2 rounded-lg text-white z-50 transition-all duration-300 ${
            type === 'success' ? 'bg-emerald-600' : 
            type === 'error' ? 'bg-rose-600' : 'bg-indigo-600'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize Kanban Board when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.kanban-column')) {
        new KanbanBoard();
    }
});