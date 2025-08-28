/**
 * Todo List View JavaScript
 * Handles list interactions, filtering, sorting, and bulk actions
 */

class TodoList {
    constructor() {
        this.selectedTasks = new Set();
        this.currentSort = {
            field: 'state',
            direction: 'asc'
        };
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.restoreState();
    }
    
    bindEvents() {
        // Select all checkbox
        const selectAllCheckbox = document.getElementById('selectAll');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.handleSelectAll(e.target.checked);
            });
        }
        
        // Individual task checkboxes
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('task-select')) {
                this.handleTaskSelect(e.target.value, e.target.checked);
            }
        });
        
        // Sort headers
        document.addEventListener('click', (e) => {
            const sortHeader = e.target.closest('.sort-header');
            if (sortHeader) {
                e.preventDefault();
                const sortField = sortHeader.dataset.sort;
                this.handleSort(sortField);
            }
        });
        
        // Filter controls
        document.addEventListener('change', (e) => {
            if (e.target.matches('#projectFilter, #stageFilter, #statusFilter, #priorityFilter')) {
                this.applyFilters();
            }
        });
        
        // Search
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
        
        // Task actions
        document.addEventListener('click', (e) => {
            const taskRow = e.target.closest('.task-row');
            if (!taskRow) return;
            
            const taskId = taskRow.dataset.taskId;
            
            if (e.target.closest('.priority-btn')) {
                e.preventDefault();
                this.togglePriority(taskId, taskRow);
            } else if (e.target.closest('.complete-btn')) {
                e.preventDefault();
                this.toggleComplete(taskId, taskRow);
            } else if (e.target.closest('[onclick*="editTask"]')) {
                e.preventDefault();
                this.editTask(taskId);
            } else if (e.target.closest('[onclick*="deleteTask"]')) {
                e.preventDefault();
                this.deleteTask(taskId, taskRow);
            } else if (e.target.closest('.task-title')) {
                e.preventDefault();
                this.openTask(taskId);
            }
        });
        
        // Bulk actions
        document.addEventListener('click', (e) => {
            if (e.target.closest('#bulkActionsBtn')) {
                e.preventDefault();
                this.showBulkActionsMenu();
            }
        });
    }
    
    handleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('.task-select');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
            if (checked) {
                this.selectedTasks.add(checkbox.value);
            } else {
                this.selectedTasks.delete(checkbox.value);
            }
        });
        
        this.updateSelectionUI();
    }
    
    handleTaskSelect(taskId, checked) {
        if (checked) {
            this.selectedTasks.add(taskId);
        } else {
            this.selectedTasks.delete(taskId);
        }
        
        // Update select all checkbox
        const selectAllCheckbox = document.getElementById('selectAll');
        const allCheckboxes = document.querySelectorAll('.task-select');
        const checkedBoxes = document.querySelectorAll('.task-select:checked');
        
        if (selectAllCheckbox) {
            selectAllCheckbox.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < allCheckboxes.length;
            selectAllCheckbox.checked = checkedBoxes.length === allCheckboxes.length && allCheckboxes.length > 0;
        }
        
        this.updateSelectionUI();
    }
    
    updateSelectionUI() {
        const selectedCount = this.selectedTasks.size;
        
        // Update bulk actions button
        const bulkActionsBtn = document.getElementById('bulkActionsBtn');
        if (bulkActionsBtn) {
            if (selectedCount > 0) {
                bulkActionsBtn.disabled = false;
                bulkActionsBtn.classList.add('btn-linguify-primary');
                bulkActionsBtn.classList.remove('btn-linguify-secondary');
                const textSpan = bulkActionsBtn.querySelector('span');
                if (textSpan) {
                    textSpan.textContent = `Actions (${selectedCount})`;
                }
            } else {
                bulkActionsBtn.disabled = true;
                bulkActionsBtn.classList.remove('btn-linguify-primary');
                bulkActionsBtn.classList.add('btn-linguify-secondary');
                const textSpan = bulkActionsBtn.querySelector('span');
                if (textSpan) {
                    textSpan.textContent = 'Bulk Actions';
                }
            }
        }
        
        // Highlight selected task cards
        document.querySelectorAll('.task-item-linguify').forEach(card => {
            const taskId = card.dataset.taskId;
            if (this.selectedTasks.has(taskId)) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
    }
    
    handleSort(field) {
        if (this.currentSort.field === field) {
            this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.field = field;
            this.currentSort.direction = 'asc';
        }
        
        this.applySorting();
        this.updateSortUI();
    }
    
    applySorting() {
        // For list view, we'll use URL parameters to handle sorting server-side
        const url = new URL(window.location);
        url.searchParams.set('order_by', this.currentSort.field);
        url.searchParams.set('order_dir', this.currentSort.direction);
        
        // Add a small delay to show the sorting change
        this.showSortingIndicator();
        setTimeout(() => {
            window.location.href = url.toString();
        }, 200);
    }
    
    updateSortUI() {
        // Remove all sort indicators
        document.querySelectorAll('.sort-header i').forEach(icon => {
            icon.remove();
        });
        
        // Add indicator to current sort column
        const currentHeader = document.querySelector(`[data-sort="${this.currentSort.field}"]`);
        if (currentHeader) {
            const icon = document.createElement('i');
            icon.className = this.currentSort.direction === 'asc' ? 'bi bi-chevron-up' : 'bi bi-chevron-down';
            currentHeader.appendChild(icon);
        }
    }
    
    showSortingIndicator() {
        const table = document.getElementById('tasksTable');
        if (table) {
            table.classList.add('sorting');
            setTimeout(() => table.classList.remove('sorting'), 1000);
        }
    }
    
    applyFilters() {
        const filters = {
            project: document.getElementById('projectFilter')?.value || '',
            stage: document.getElementById('stageFilter')?.value || '',
            status: document.getElementById('statusFilter')?.value || '',
            priority: document.getElementById('priorityFilter')?.value || ''
        };
        
        const url = new URL(window.location);
        
        Object.entries(filters).forEach(([key, value]) => {
            if (value) {
                url.searchParams.set(key, value);
            } else {
                url.searchParams.delete(key);
            }
        });
        
        window.location.href = url.toString();
    }
    
    handleSearch(query) {
        // Debounce search
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            const url = new URL(window.location);
            
            if (query.trim()) {
                url.searchParams.set('search', query);
            } else {
                url.searchParams.delete('search');
            }
            
            window.location.href = url.toString();
        }, 500);
    }
    
    async togglePriority(taskId, taskRow) {
        const priorityBtn = taskRow.querySelector('.priority-btn i');
        const isStarred = priorityBtn.classList.contains('bi-star-fill');
        
        try {
            const response = await fetch(`/api/v1/todo/tasks/${taskId}/toggle_important/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                // Toggle star visual
                if (isStarred) {
                    priorityBtn.className = 'bi bi-star text-muted';
                } else {
                    priorityBtn.className = 'bi bi-star-fill text-warning';
                }
                
                this.showSuccess('Priority updated');
            } else {
                throw new Error('Failed to toggle priority');
            }
        } catch (error) {
            console.error('Error toggling priority:', error);
            this.showError('Failed to update priority');
        }
    }
    
    async toggleComplete(taskId, taskRow) {
        const completeBtn = taskRow.querySelector('.complete-btn i');
        const isCompleted = completeBtn.classList.contains('bi-check-circle-fill');
        
        try {
            const response = await fetch(`/api/v1/todo/tasks/${taskId}/toggle_completed/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateTaskRowCompletion(taskRow, data);
                this.showSuccess('Task updated');
            } else {
                throw new Error('Failed to toggle completion');
            }
        } catch (error) {
            console.error('Error toggling completion:', error);
            this.showError('Failed to update task');
        }
    }
    
    updateTaskRowCompletion(taskRow, taskData) {
        const completeBtn = taskRow.querySelector('.complete-btn i');
        const taskTitle = taskRow.querySelector('.task-title');
        
        if (taskData.state === '1_done') {
            completeBtn.className = 'bi bi-check-circle-fill text-success';
            taskTitle.classList.add('text-decoration-line-through', 'text-muted');
            taskRow.classList.add('completed-task');
        } else {
            completeBtn.className = 'bi bi-circle text-muted';
            taskTitle.classList.remove('text-decoration-line-through', 'text-muted');
            taskRow.classList.remove('completed-task');
        }
    }
    
    showBulkActionsMenu() {
        if (this.selectedTasks.size === 0) {
            this.showWarning('Please select tasks first');
            return;
        }
        
        // Create context menu
        const menu = document.createElement('div');
        menu.className = 'bulk-actions-menu dropdown-menu show';
        menu.style.position = 'fixed';
        menu.style.zIndex = '1050';
        
        menu.innerHTML = `
            <h6 class="dropdown-header">${this.selectedTasks.size} tasks selected</h6>
            <a class="dropdown-item" href="#" onclick="todoList.bulkMarkComplete()">
                <i class="bi bi-check-circle"></i> Mark as Complete
            </a>
            <a class="dropdown-item" href="#" onclick="todoList.bulkMarkIncomplete()">
                <i class="bi bi-circle"></i> Mark as Incomplete
            </a>
            <div class="dropdown-divider"></div>
            <a class="dropdown-item" href="#" onclick="todoList.bulkSetPriority('1')">
                <i class="bi bi-star-fill text-warning"></i> Add Star
            </a>
            <a class="dropdown-item" href="#" onclick="todoList.bulkSetPriority('0')">
                <i class="bi bi-star text-muted"></i> Remove Star
            </a>
            <div class="dropdown-divider"></div>
            <a class="dropdown-item text-danger" href="#" onclick="todoList.bulkDelete()">
                <i class="bi bi-trash"></i> Delete Tasks
            </a>
        `;
        
        // Position menu near bulk actions button
        const bulkBtn = document.getElementById('bulkActions');
        if (bulkBtn) {
            const rect = bulkBtn.getBoundingClientRect();
            menu.style.left = rect.left + 'px';
            menu.style.top = (rect.bottom + 5) + 'px';
        }
        
        document.body.appendChild(menu);
        
        // Close menu when clicking outside
        const closeMenu = (e) => {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        };
        
        setTimeout(() => {
            document.addEventListener('click', closeMenu);
        }, 100);
    }
    
    async bulkMarkComplete() {
        await this.bulkUpdateTasks({ state: '1_done' }, 'Tasks marked as complete');
    }
    
    async bulkMarkIncomplete() {
        await this.bulkUpdateTasks({ state: '1_todo' }, 'Tasks marked as incomplete');
    }
    
    async bulkSetPriority(priority) {
        const message = priority === '1' ? 'Stars added to tasks' : 'Stars removed from tasks';
        await this.bulkUpdateTasks({ priority }, message);
    }
    
    async bulkDelete() {
        if (!confirm(`Are you sure you want to delete ${this.selectedTasks.size} tasks?`)) {
            return;
        }
        
        const taskIds = Array.from(this.selectedTasks);
        
        try {
            const promises = taskIds.map(taskId =>
                fetch(`/api/v1/todo/tasks/${taskId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                })
            );
            
            await Promise.all(promises);
            
            // Remove rows from table
            taskIds.forEach(taskId => {
                const row = document.querySelector(`[data-task-id="${taskId}"]`);
                if (row) {
                    row.remove();
                }
            });
            
            this.selectedTasks.clear();
            this.updateSelectionUI();
            this.showSuccess(`${taskIds.length} tasks deleted`);
            
        } catch (error) {
            console.error('Error deleting tasks:', error);
            this.showError('Failed to delete some tasks');
        }
    }
    
    async bulkUpdateTasks(updates, successMessage) {
        const taskIds = Array.from(this.selectedTasks);
        
        try {
            const promises = taskIds.map(taskId =>
                fetch(`/api/v1/todo/tasks/${taskId}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(updates)
                })
            );
            
            const responses = await Promise.all(promises);
            const successful = responses.filter(r => r.ok).length;
            
            if (successful === taskIds.length) {
                this.showSuccess(successMessage);
                setTimeout(() => window.location.reload(), 1000);
            } else {
                this.showWarning(`Updated ${successful} of ${taskIds.length} tasks`);
            }
            
        } catch (error) {
            console.error('Error updating tasks:', error);
            this.showError('Failed to update tasks');
        }
    }
    
    clearSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
            this.handleSearch('');
        }
    }
    
    editTask(taskId) {
        window.open(`/todo/task/${taskId}/`, '_blank');
    }
    
    openTask(taskId) {
        window.location.href = `/todo/task/${taskId}/`;
    }
    
    async deleteTask(taskId, taskRow) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/v1/todo/tasks/${taskId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                taskRow.remove();
                this.selectedTasks.delete(taskId);
                this.updateSelectionUI();
                this.showSuccess('Task deleted');
            } else {
                throw new Error('Failed to delete task');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            this.showError('Failed to delete task');
        }
    }
    
    restoreState() {
        // Restore current sort from URL
        const urlParams = new URLSearchParams(window.location.search);
        const orderBy = urlParams.get('order_by');
        const orderDir = urlParams.get('order_dir') || 'asc';
        
        if (orderBy) {
            this.currentSort.field = orderBy;
            this.currentSort.direction = orderDir;
            this.updateSortUI();
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.content || '';
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'error');
    }
    
    showWarning(message) {
        this.showToast(message, 'warning');
    }
    
    showToast(message, type = 'info') {
        // Reuse toast system from kanban.js
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        const bgClass = type === 'error' ? 'bg-danger' : 
                       type === 'warning' ? 'bg-warning' : 
                       type === 'success' ? 'bg-success' : 'bg-primary';
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white ${bgClass} border-0`;
        toast.setAttribute('role', 'alert');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    }
}

// Global functions
window.togglePriority = function(taskId) {
    const taskRow = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskRow && todoList) {
        todoList.togglePriority(taskId, taskRow);
    }
};

window.toggleComplete = function(taskId) {
    const taskRow = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskRow && todoList) {
        todoList.toggleComplete(taskId, taskRow);
    }
};

window.editTask = function(taskId) {
    if (todoList) {
        todoList.editTask(taskId);
    }
};

window.deleteTask = function(taskId) {
    const taskRow = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskRow && todoList) {
        todoList.deleteTask(taskId, taskRow);
    }
};

window.openTask = function(taskId) {
    if (todoList) {
        todoList.openTask(taskId);
    }
};

window.clearSearch = function() {
    if (todoList) {
        todoList.clearSearch();
    }
};

// Missing table functions
window.togglePriority = function(taskId) {
    const taskRow = document.querySelector(`[data-task-id="${taskId}"]`);
    if (todoList && taskRow) {
        todoList.togglePriority(taskId, taskRow);
    }
};

window.toggleComplete = function(taskId) {
    const taskRow = document.querySelector(`[data-task-id="${taskId}"]`);
    if (todoList && taskRow) {
        todoList.toggleComplete(taskId, taskRow);
    }
};

window.duplicateTask = function(taskId) {
    console.log('Duplicating task:', taskId);
    // This would typically make an API call to duplicate the task
    if (confirm('Are you sure you want to duplicate this task?')) {
        // API call would go here
        fetch(`/todo/api/tasks/${taskId}/duplicate/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': todoList ? todoList.getCSRFToken() : '',
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                todoList.showSuccess('Task duplicated successfully');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                todoList.showError('Failed to duplicate task');
            }
        })
        .catch(error => {
            console.error('Error duplicating task:', error);
            todoList.showError('Failed to duplicate task');
        });
    }
};

// Initialize List
let todoList;
function initializeList() {
    todoList = new TodoList();
    window.todoList = todoList;
}