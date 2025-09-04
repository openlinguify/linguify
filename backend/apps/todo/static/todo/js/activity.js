/**
 * Todo Activity View JavaScript
 * Handles activity timeline, statistics updates, and task interactions
 */

class TodoActivity {
    constructor() {
        this.refreshInterval = null;
        this.autoRefreshEnabled = true;
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.startAutoRefresh();
        this.loadRealtimeStats();
    }
    
    bindEvents() {
        // Task completion toggles
        document.addEventListener('click', (e) => {
            const completeBtn = e.target.closest('.complete-btn');
            if (completeBtn) {
                e.preventDefault();
                const activityItem = completeBtn.closest('.activity-task-item');
                const taskId = this.extractTaskId(completeBtn);
                if (taskId && activityItem) {
                    this.toggleTaskComplete(taskId, activityItem);
                }
            }
        });
        
        // Task title clicks for opening tasks
        document.addEventListener('click', (e) => {
            const taskTitle = e.target.closest('.task-title, .activity-title');
            if (taskTitle && taskTitle.hasAttribute('onclick')) {
                e.preventDefault();
                const taskId = this.extractTaskId(taskTitle);
                if (taskId) {
                    this.openTask(taskId);
                }
            }
        });
        
        // Edit task buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('[onclick*="editTask"]')) {
                e.preventDefault();
                const taskId = this.extractTaskId(e.target);
                if (taskId) {
                    this.editTask(taskId);
                }
            }
        });
        
        // View all buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('[onclick*="viewAllOverdue"]')) {
                e.preventDefault();
                this.viewAllOverdue();
            } else if (e.target.closest('[onclick*="viewAllWeek"]')) {
                e.preventDefault();
                this.viewAllWeek();
            }
        });
        
        // Auto-refresh toggle
        document.addEventListener('change', (e) => {
            if (e.target.id === 'autoRefreshToggle') {
                this.toggleAutoRefresh(e.target.checked);
            }
        });
        
        // Manual refresh
        document.addEventListener('click', (e) => {
            if (e.target.closest('.refresh-btn')) {
                e.preventDefault();
                this.refreshData();
            }
        });
    }
    
    extractTaskId(element) {
        // Try to extract task ID from onclick attribute or data attributes
        const onclick = element.getAttribute('onclick') || element.closest('[onclick]')?.getAttribute('onclick');
        if (onclick) {
            const match = onclick.match(/'([^']+)'/);
            return match ? match[1] : null;
        }
        
        // Try data attributes
        return element.dataset.taskId || 
               element.closest('[data-task-id]')?.dataset.taskId || 
               null;
    }
    
    async toggleTaskComplete(taskId, activityItem) {
        const completeBtn = activityItem.querySelector('.complete-btn i');
        const taskTitle = activityItem.querySelector('.task-title');
        const isCompleted = completeBtn.classList.contains('bi-check-circle-fill');
        
        // Show loading state
        activityItem.style.opacity = '0.6';
        completeBtn.style.pointerEvents = 'none';
        
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
                
                // Update UI based on new state
                if (data.state === '1_done') {
                    completeBtn.className = 'bi bi-check-circle-fill text-success';
                    taskTitle.classList.add('completed');
                    this.animateCompletion(activityItem);
                } else {
                    completeBtn.className = 'bi bi-circle text-muted';
                    taskTitle.classList.remove('completed');
                }
                
                this.showSuccess('Task updated successfully');
                
                // Update statistics
                this.updateStats();
                
                // Optionally move completed tasks to different section
                if (data.state === '1_done') {
                    setTimeout(() => {
                        this.moveToCompletedSection(activityItem, data);
                    }, 1000);
                }
                
            } else {
                throw new Error('Failed to toggle task');
            }
        } catch (error) {
            console.error('Error toggling task:', error);
            this.showError('Failed to update task');
        } finally {
            activityItem.style.opacity = '';
            completeBtn.style.pointerEvents = '';
        }
    }
    
    animateCompletion(activityItem) {
        // Add completion animation
        activityItem.classList.add('completing');
        
        // Create celebration effect
        this.createCelebrationEffect(activityItem);
        
        setTimeout(() => {
            activityItem.classList.remove('completing');
        }, 1000);
    }
    
    createCelebrationEffect(element) {
        // Create floating checkmark animation
        const celebration = document.createElement('div');
        celebration.className = 'completion-celebration';
        celebration.innerHTML = '<i class="bi bi-check-circle-fill"></i>';
        celebration.style.cssText = `
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            color: #28a745;
            font-size: 1.5rem;
            pointer-events: none;
            z-index: 1000;
            animation: celebrationFloat 1s ease-out forwards;
        `;
        
        element.style.position = 'relative';
        element.appendChild(celebration);
        
        setTimeout(() => celebration.remove(), 1000);
    }
    
    moveToCompletedSection(activityItem, taskData) {
        // Find or create completed section
        let completedSection = document.querySelector('.completed-tasks-section .section-content');
        
        if (!completedSection) {
            // Create completed section if it doesn't exist
            const completedSectionContainer = this.createCompletedSection();
            const rightColumn = document.querySelector('.col-lg-4');
            if (rightColumn) {
                rightColumn.appendChild(completedSectionContainer);
                completedSection = completedSectionContainer.querySelector('.section-content');
            }
        }
        
        if (completedSection) {
            // Clone the item and modify for completed section
            const completedItem = this.createCompletedActivityItem(taskData);
            
            // Add to beginning of completed section
            const firstChild = completedSection.firstElementChild;
            if (firstChild) {
                completedSection.insertBefore(completedItem, firstChild);
            } else {
                completedSection.appendChild(completedItem);
            }
            
            // Animate the new item
            completedItem.style.opacity = '0';
            completedItem.style.transform = 'translateY(-20px)';
            
            requestAnimationFrame(() => {
                completedItem.style.transition = 'all 0.3s ease';
                completedItem.style.opacity = '1';
                completedItem.style.transform = 'translateY(0)';
            });
        }
        
        // Remove from original section with animation
        activityItem.style.transition = 'all 0.3s ease';
        activityItem.style.opacity = '0';
        activityItem.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            activityItem.remove();
        }, 300);
    }
    
    createCompletedSection() {
        const section = document.createElement('div');
        section.className = 'activity-section mb-4 completed-tasks-section';
        section.innerHTML = `
            <div class="section-header">
                <h5 class="section-title text-success">
                    <i class="bi bi-check-circle"></i>
                    Recently Completed
                </h5>
            </div>
            <div class="section-content">
                <!-- Completed tasks will be added here -->
            </div>
        `;
        return section;
    }
    
    createCompletedActivityItem(taskData) {
        const item = document.createElement('div');
        item.className = 'activity-item completed-item';
        item.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="activity-icon me-2">
                    <i class="bi bi-check-circle-fill text-success"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="activity-title">${taskData.title}</div>
                    <small class="text-muted">
                        Completed just now
                        ${taskData.project ? `• ${taskData.project}` : ''}
                    </small>
                </div>
            </div>
        `;
        return item;
    }
    
    async updateStats() {
        try {
            const response = await fetch('/api/v1/todo/dashboard/');
            if (response.ok) {
                const data = await response.json();
                this.updateStatCards(data);
            }
        } catch (error) {
            console.warn('Could not update statistics:', error);
        }
    }
    
    updateStatCards(data) {
        // Update stat numbers with animation
        const statMappings = {
            'tasks_created_today': data.activity?.tasks_created_this_week || 0,
            'tasks_completed_today': data.activity?.tasks_completed_this_week || 0,
            'tasks_created_this_week': data.activity?.tasks_created_this_week || 0,
            'tasks_completed_this_week': data.activity?.tasks_completed_this_week || 0
        };
        
        Object.entries(statMappings).forEach(([elementClass, value]) => {
            const elements = document.querySelectorAll(`.activity-stats .stat-number`);
            elements.forEach((element, index) => {
                if (index < 4) { // We have 4 stat cards
                    this.animateNumberChange(element, value);
                }
            });
        });
    }
    
    animateNumberChange(element, newValue) {
        const currentValue = parseInt(element.textContent) || 0;
        
        if (currentValue === newValue) return;
        
        // Add pulse animation
        element.style.transform = 'scale(1.1)';
        element.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            element.textContent = newValue;
            element.style.transform = 'scale(1)';
        }, 100);
        
        // Highlight if increased
        if (newValue > currentValue) {
            element.style.color = '#28a745';
            setTimeout(() => {
                element.style.color = '';
            }, 1000);
        }
    }
    
    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            if (this.autoRefreshEnabled && document.visibilityState === 'visible') {
                this.loadRealtimeStats();
            }
        }, 30000);
    }
    
    toggleAutoRefresh(enabled) {
        this.autoRefreshEnabled = enabled;
        
        if (enabled) {
            this.startAutoRefresh();
            this.showInfo('Auto-refresh enabled');
        } else {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
            this.showInfo('Auto-refresh disabled');
        }
    }
    
    async loadRealtimeStats() {
        try {
            const response = await fetch('/api/v1/todo/dashboard/');
            if (response.ok) {
                const data = await response.json();
                this.updateStatCards(data);
                this.updateLastRefreshTime();
            }
        } catch (error) {
            console.warn('Could not load realtime stats:', error);
        }
    }
    
    updateLastRefreshTime() {
        let timeIndicator = document.querySelector('.last-refresh-time');
        if (!timeIndicator) {
            timeIndicator = document.createElement('small');
            timeIndicator.className = 'last-refresh-time text-muted';
            const activityControls = document.querySelector('.activity-controls');
            if (activityControls) {
                activityControls.appendChild(timeIndicator);
            }
        }
        
        const now = new Date();
        timeIndicator.textContent = `Last updated: ${now.toLocaleTimeString()}`;
        
        // Fade in effect
        timeIndicator.style.opacity = '0.5';
        setTimeout(() => {
            timeIndicator.style.opacity = '1';
        }, 100);
    }
    
    refreshData() {
        this.showInfo('Refreshing data...');
        this.loadRealtimeStats();
        
        // Simulate page refresh for demo
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }
    
    viewAllOverdue() {
        // Navigate to list view with overdue filter
        window.location.href = '/todo/list/?due=overdue';
    }
    
    viewAllWeek() {
        // Navigate to list view with week filter
        const today = new Date();
        const weekEnd = new Date(today);
        weekEnd.setDate(today.getDate() + 7);
        
        window.location.href = `/todo/list/?due_start=${today.toISOString().split('T')[0]}&due_end=${weekEnd.toISOString().split('T')[0]}`;
    }
    
    editTask(taskId) {
        window.open(`/todo/task/${taskId}/`, '_blank');
    }
    
    openTask(taskId) {
        window.location.href = `/todo/task/${taskId}/`;
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
    
    showInfo(message) {
        this.showToast(message, 'info');
    }
    
    showToast(message, type = 'info') {
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        const bgClass = type === 'error' ? 'bg-danger' : 
                       type === 'success' ? 'bg-success' : 
                       type === 'info' ? 'bg-info' : 'bg-primary';
        
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
    
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Add completion animation CSS
const style = document.createElement('style');
style.textContent = `
@keyframes celebrationFloat {
    0% {
        opacity: 1;
        transform: translateX(-50%) translateY(0) scale(1);
    }
    50% {
        opacity: 1;
        transform: translateX(-50%) translateY(-20px) scale(1.2);
    }
    100% {
        opacity: 0;
        transform: translateX(-50%) translateY(-40px) scale(1.5);
    }
}

.completing {
    background-color: rgba(40, 167, 69, 0.1) !important;
    transform: scale(1.02);
    transition: all 0.3s ease;
}

.activity-task-item {
    transition: all 0.3s ease;
}

.task-title.completed {
    text-decoration: line-through;
    color: #6c757d;
    opacity: 0.8;
}

.last-refresh-time {
    position: absolute;
    top: 100%;
    right: 0;
    font-size: 0.7rem;
    margin-top: 0.25rem;
}
`;
document.head.appendChild(style);

// Global functions
window.toggleTaskComplete = function(taskId) {
    if (todoActivity) {
        const activityItem = document.querySelector(`[onclick*="${taskId}"]`)?.closest('.activity-task-item');
        if (activityItem) {
            todoActivity.toggleTaskComplete(taskId, activityItem);
        }
    }
};

window.editTask = function(taskId) {
    if (todoActivity) {
        todoActivity.editTask(taskId);
    }
};

window.openTask = function(taskId) {
    if (todoActivity) {
        todoActivity.openTask(taskId);
    }
};

window.viewAllOverdue = function() {
    if (todoActivity) {
        todoActivity.viewAllOverdue();
    }
};

window.viewAllWeek = function() {
    if (todoActivity) {
        todoActivity.viewAllWeek();
    }
};

// Initialize Activity
let todoActivity;
function initializeActivity() {
    todoActivity = new TodoActivity();
    window.todoActivity = todoActivity;
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (todoActivity) {
        todoActivity.destroy();
    }
});