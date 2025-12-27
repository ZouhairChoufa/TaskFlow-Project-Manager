/**
 * Professional UI Components for TaskFlow
 * Custom replacements for browser alerts and confirmations
 */

// Delete Confirmation Helper
function confirmDelete(elementId, title = 'Supprimer cet élément ?', message = 'Cette action ne peut pas être annulée.') {
    return new Promise((resolve) => {
        showDeleteConfirm(title, message, () => {
            resolve(true);
        });
        
        // Override cancel to resolve false
        const originalCancel = document.getElementById('deleteCancelBtn').onclick;
        document.getElementById('deleteCancelBtn').onclick = () => {
            resolve(false);
            hideDeleteModal();
        };
    });
}

// Form Delete Handler
function handleDeleteForm(formSelector, title, message) {
    const form = document.querySelector(formSelector);
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const confirmed = await confirmDelete(null, title, message);
        if (confirmed) {
            // Submit the form
            this.submit();
        }
    });
}

// Button Delete Handler
function handleDeleteButton(buttonSelector, action, title, message) {
    const button = document.querySelector(buttonSelector);
    if (!button) return;
    
    button.addEventListener('click', async function(e) {
        e.preventDefault();
        
        const confirmed = await confirmDelete(null, title, message);
        if (confirmed && typeof action === 'function') {
            action();
        }
    });
}

// Quick setup for common delete scenarios
function setupDeleteConfirmations() {
    // Project deletion
    handleDeleteForm('form[action*="/delete"]', 
        'Supprimer ce projet ?', 
        'Toutes les tâches et données du projet seront définitivement supprimées.');
    
    // Task deletion
    document.querySelectorAll('[data-delete-task]').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const taskTitle = this.dataset.taskTitle || 'cette tâche';
            
            const confirmed = await confirmDelete(null, 
                `Supprimer ${taskTitle} ?`, 
                'Cette tâche sera définitivement supprimée.');
            
            if (confirmed) {
                // Execute delete action
                const deleteUrl = this.dataset.deleteUrl || this.href;
                if (deleteUrl) {
                    window.location.href = deleteUrl;
                }
            }
        });
    });
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', setupDeleteConfirmations);