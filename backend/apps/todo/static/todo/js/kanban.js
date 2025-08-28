/**
 * Todo Kanban View JavaScript
 * Handles drag & drop, task management, and kanban-specific interactions
 */

class TodoKanban {
    constructor() {
        this.draggedTask = null;
        this.isLoading = false;
        this.init();
    }
    
    init() {
        this.initDragDrop();
        this.bindEvents();
        this.initSortable();
    }
    
    initDragDrop() {
        // Make tasks draggable
        document.querySelectorAll('.kanban-card').forEach(card => {
            card.draggable = true;
            card.addEventListener('dragstart', this.handleDragStart.bind(this));
            card.addEventListener('dragend', this.handleDragEnd.bind(this));
        });
        
        // Make columns drop targets
        document.querySelectorAll('.kanban-tasks-container').forEach(container => {
            container.addEventListener('dragover', this.handleDragOver.bind(this));
            container.addEventListener('drop', this.handleDrop.bind(this));
            container.addEventListener('dragenter', this.handleDragEnter.bind(this));
            container.addEventListener('dragleave', this.handleDragLeave.bind(this));
        });
    }
    
    initSortable() {
        // Initialize sortable for each column if SortableJS is available
        if (typeof Sortable !== 'undefined') {
            document.querySelectorAll('.kanban-tasks-container').forEach(container => {
                new Sortable(container, {
                    group: 'kanban-tasks',
                    animation: 150,
                    ghostClass: 'kanban-card-ghost',
                    chosenClass: 'kanban-card-chosen',
                    dragClass: 'kanban-card-drag',
                    onEnd: this.handleSortableEnd.bind(this)
                });
            });
        }
    }
    
    bindEvents() {
        // Quick add task to stage
        document.addEventListener('click', (e) => {
            const addBtn = e.target.closest('.add-task-btn');
            if (addBtn) {
                e.preventDefault();
                const container = addBtn.closest('.kanban-tasks-container');
                const stageId = container?.closest('.kanban-column')?.dataset.stageId;
                this.showQuickAddForm(stageId, addBtn);
            }
        });
        
        // Toggle column fold
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="toggleStage"]')) {
                e.preventDefault();
                const stageId = e.target.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.toggleStage(stageId);
            }
        });
        
        // Add new stage
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-stage-btn')) {
                e.preventDefault();
                this.showAddStageForm();
            }
        });
        
        // Task actions
        document.addEventListener('click', (e) => {
            const taskCard = e.target.closest('.kanban-card');
            if (!taskCard) return;
            
            const taskId = taskCard.dataset.taskId;
            
            if (e.target.closest('[onclick*="toggleTaskComplete"]')) {
                e.preventDefault();
                this.toggleTaskComplete(taskId, taskCard);
            } else if (e.target.closest('[onclick*="editTask"]')) {
                e.preventDefault();
                this.editTask(taskId);
            } else if (e.target.closest('.task-title')) {
                e.preventDefault();
                this.openTask(taskId);
            }
        });
        
        // Escape key to close forms
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllForms();
            }
        });
    }
    
    handleDragStart(e) {
        this.draggedTask = {
            element: e.target,
            taskId: e.target.dataset.taskId,
            originalStageId: e.target.closest('.kanban-column').dataset.stageId
        };
        
        e.target.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', e.target.outerHTML);
    }
    
    handleDragEnd(e) {
        e.target.classList.remove('dragging');
        document.querySelectorAll('.kanban-column').forEach(col => {
            col.classList.remove('drag-over');
        });
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }
    
    handleDragEnter(e) {
        e.preventDefault();
        const column = e.target.closest('.kanban-column');
        if (column) {
            column.classList.add('drag-over');
        }
    }
    
    handleDragLeave(e) {
        const column = e.target.closest('.kanban-column');
        if (column && !column.contains(e.relatedTarget)) {
            column.classList.remove('drag-over');
        }
    }
    
    handleDrop(e) {
        e.preventDefault();
        
        const column = e.target.closest('.kanban-column');
        if (!column || !this.draggedTask) return;
        
        column.classList.remove('drag-over');
        
        const newStageId = column.dataset.stageId;
        const taskId = this.draggedTask.taskId;
        
        // Don't move if dropped in same stage
        if (newStageId === this.draggedTask.originalStageId) {
            return;
        }
        
        // Move task to new stage
        this.moveTaskToStage(taskId, newStageId, this.draggedTask.element);
    }
    
    handleSortableEnd(e) {
        const taskId = e.item.dataset.taskId;
        const newStageId = e.to.closest('.kanban-column').dataset.stageId;
        const oldStageId = e.from.closest('.kanban-column').dataset.stageId;
        
        if (newStageId !== oldStageId) {
            this.moveTaskToStage(taskId, newStageId, e.item);
        }
        
        // Update task sequence
        this.updateTaskSequence(newStageId);
    }
    
    async moveTaskToStage(taskId, newStageId, taskElement) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showTaskLoading(taskElement);
        
        try {
            const response = await fetch(`/api/todo/tasks/${taskId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    personal_stage_type: newStageId
                })
            });
            
            if (response.ok) {
                this.showSuccess('Task moved successfully');
                this.updateStageCounts();
            } else {
                throw new Error('Failed to move task');
            }
        } catch (error) {
            console.error('Error moving task:', error);
            this.showError('Failed to move task');
            
            // Revert the move
            const originalColumn = document.querySelector(`[data-stage-id="${this.draggedTask.originalStageId}"] .kanban-tasks-container`);
            if (originalColumn) {
                originalColumn.appendChild(taskElement);
            }
        } finally {
            this.hideTaskLoading(taskElement);
            this.isLoading = false;
        }
    }
    
    async toggleTaskComplete(taskId, taskCard) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showTaskLoading(taskCard);
        
        try {
            const response = await fetch(`/api/todo/tasks/${taskId}/toggle_completed/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateTaskCard(taskCard, data);
                this.showSuccess('Task updated successfully');
            } else {
                throw new Error('Failed to toggle task');
            }
        } catch (error) {
            console.error('Error toggling task:', error);
            this.showError('Failed to update task');
        } finally {
            this.hideTaskLoading(taskCard);
            this.isLoading = false;
        }
    }
    
    updateTaskCard(taskCard, taskData) {
        // Update completion button
        const completeBtn = taskCard.querySelector('[onclick*="toggleTaskComplete"] i');
        if (completeBtn) {
            if (taskData.state === '1_done') {
                completeBtn.className = 'bi bi-check-circle-fill';
                taskCard.classList.add('completed-task');
            } else {
                completeBtn.className = 'bi bi-circle';
                taskCard.classList.remove('completed-task');
            }
        }
        
        // Update task title appearance
        const taskTitle = taskCard.querySelector('.task-title');
        if (taskTitle) {
            if (taskData.state === '1_done') {
                taskTitle.classList.add('text-decoration-line-through', 'text-muted');
            } else {
                taskTitle.classList.remove('text-decoration-line-through', 'text-muted');
            }
        }
    }
    
    showQuickAddForm(stageId, addBtn) {
        // Hide existing forms
        this.closeAllForms();
        
        const form = document.createElement('div');
        form.className = 'quick-add-form';
        form.innerHTML = `
            <div class="card">
                <div class="card-body p-3">
                    <input type="text" class="form-control form-control-sm mb-2" 
                           placeholder="Task title..." id="quickTaskTitle" autofocus>
                    <div class="d-flex gap-2">
                        <button class="btn btn-primary btn-sm flex-fill" onclick="todoKanban.submitQuickTask('${stageId}')">
                            Add
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="todoKanban.closeAllForms()">
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        addBtn.style.display = 'none';
        addBtn.after(form);
        
        // Focus and enter key handling
        const input = form.querySelector('#quickTaskTitle');
        input.focus();
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.submitQuickTask(stageId);
            }
        });
    }
    
    async submitQuickTask(stageId) {
        const input = document.getElementById('quickTaskTitle');
        const title = input?.value?.trim();
        
        if (!title) {
            input?.focus();
            return;
        }
        
        try {
            const response = await fetch('/api/todo/tasks/quick_create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    title: title,
                    personal_stage_type: stageId
                })
            });
            
            if (response.ok) {
                const taskData = await response.json();
                this.addTaskToColumn(stageId, taskData);
                this.showSuccess('Task created successfully');
            } else {
                throw new Error('Failed to create task');
            }
        } catch (error) {
            console.error('Error creating task:', error);
            this.showError('Failed to create task');
        }
        
        this.closeAllForms();
    }
    
    addTaskToColumn(stageId, taskData) {
        const container = document.querySelector(`[data-stage-id="${stageId}"] .kanban-tasks-container`);
        if (!container) return;
        
        const addBtn = container.querySelector('.add-task-btn');
        const taskCard = this.createTaskCard(taskData);
        
        if (addBtn) {
            addBtn.before(taskCard);
        } else {
            container.appendChild(taskCard);
        }
        
        this.updateStageCounts();
        
        // Make new task draggable
        taskCard.draggable = true;
        taskCard.addEventListener('dragstart', this.handleDragStart.bind(this));
        taskCard.addEventListener('dragend', this.handleDragEnd.bind(this));
    }
    
    createTaskCard(taskData) {
        const card = document.createElement('div');
        card.className = 'kanban-card';
        card.dataset.taskId = taskData.id;
        card.dataset.stageId = taskData.personal_stage_type;
        
        const priorityIndicator = taskData.priority === '1' 
            ? '<div class="priority-indicator starred"><i class="bi bi-star-fill text-warning"></i></div>'
            : '';
        
        const colorBar = `<div class="task-color-bar color-${taskData.color || 0}"></div>`;
        
        const completeBtnIcon = taskData.state === '1_done' 
            ? 'bi-check-circle-fill' 
            : 'bi-circle';
        
        const titleClasses = taskData.state === '1_done' 
            ? 'task-title text-decoration-line-through text-muted'
            : 'task-title';
        
        card.innerHTML = `
            ${priorityIndicator}
            ${colorBar}
            <div class="kanban-card-body">
                <div class="task-title-container">
                    <h6 class="${titleClasses} mb-1" onclick="openTask('${taskData.id}')">
                        ${taskData.title}
                    </h6>
                </div>
                <div class="task-meta mb-2">
                    ${taskData.due_date ? `<small class="due-date"><i class="bi bi-calendar"></i> ${new Date(taskData.due_date).toLocaleDateString()}</small>` : ''}
                    ${taskData.project ? `<small class="project-name text-muted ms-2"><i class="bi bi-folder"></i> ${taskData.project}</small>` : ''}
                </div>
            </div>
            <div class="kanban-card-actions">
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">Just now</small>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-primary" onclick="editTask('${taskData.id}')" title="Edit">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="toggleTaskComplete('${taskData.id}')" title="Toggle Complete">
                            <i class="${completeBtnIcon}"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return card;
    }
    
    toggleStage(stageId) {
        const column = document.querySelector(`[data-stage-id="${stageId}"]`);
        const tasksContainer = column?.querySelector('.kanban-tasks-container');
        const toggleBtn = column?.querySelector('[onclick*="toggleStage"] i');
        
        if (!tasksContainer || !toggleBtn) return;
        
        const isHidden = tasksContainer.style.display === 'none';
        
        if (isHidden) {
            tasksContainer.style.display = 'block';
            toggleBtn.className = 'bi bi-chevron-down';
        } else {
            tasksContainer.style.display = 'none';
            toggleBtn.className = 'bi bi-chevron-up';
        }
        
        // Save column state
        this.saveColumnState(stageId, !isHidden);
    }
    
    saveColumnState(stageId, folded) {
        try {
            const states = JSON.parse(localStorage.getItem('kanbanColumnStates') || '{}');
            states[stageId] = { folded };
            localStorage.setItem('kanbanColumnStates', JSON.stringify(states));
        } catch (e) {
            console.warn('Could not save column state:', e);
        }
    }
    
    loadColumnStates() {
        try {
            const states = JSON.parse(localStorage.getItem('kanbanColumnStates') || '{}');
            Object.entries(states).forEach(([stageId, state]) => {
                if (state.folded) {
                    this.toggleStage(stageId);
                }
            });
        } catch (e) {
            console.warn('Could not load column states:', e);
        }
    }
    
    updateStageCounts() {
        document.querySelectorAll('.kanban-column').forEach(column => {
            const tasks = column.querySelectorAll('.kanban-card');
            const countBadge = column.querySelector('.task-count');
            if (countBadge) {
                countBadge.textContent = tasks.length;
            }
        });
    }
    
    updateTaskSequence(stageId) {
        const tasks = document.querySelectorAll(`[data-stage-id="${stageId}"] .kanban-card`);
        const taskIds = Array.from(tasks).map(task => task.dataset.taskId);
        
        // Send sequence update to server
        fetch(`/api/todo/stages/${stageId}/reorder_tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({ task_ids: taskIds })
        }).catch(error => {
            console.warn('Could not update task sequence:', error);
        });
    }
    
    closeAllForms() {
        document.querySelectorAll('.quick-add-form').forEach(form => form.remove());
        document.querySelectorAll('.add-task-btn').forEach(btn => btn.style.display = 'block');
    }
    
    showTaskLoading(taskCard) {
        taskCard.classList.add('loading');
        taskCard.style.opacity = '0.6';
        taskCard.style.pointerEvents = 'none';
    }
    
    hideTaskLoading(taskCard) {
        taskCard.classList.remove('loading');
        taskCard.style.opacity = '';
        taskCard.style.pointerEvents = '';
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'error');
    }
    
    showToast(message, type = 'info') {
        // Create toast if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
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
        
        // Remove after hide
        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.content || '';
    }
    
    editTask(taskId) {
        window.open(`/todo/task/${taskId}/`, '_blank');
    }
    
    openTask(taskId) {
        window.location.href = `/todo/task/${taskId}/`;
    }
    
    showAddStageForm() {
        console.log('Add new stage form - to be implemented');
    }
}

// Global functions
window.addTaskToStage = function(stageId) {
    const addBtn = document.querySelector(`[data-stage-id="${stageId}"] .add-task-btn`);
    if (addBtn) {
        todoKanban.showQuickAddForm(stageId, addBtn);
    }
};

window.toggleStage = function(stageId) {
    todoKanban.toggleStage(stageId);
};

window.toggleTaskComplete = function(taskId) {
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskCard) {
        todoKanban.toggleTaskComplete(taskId, taskCard);
    }
};

window.editTask = function(taskId) {
    todoKanban.editTask(taskId);
};

window.openTask = function(taskId) {
    todoKanban.openTask(taskId);
};

window.submitQuickTask = function() {
    const modal = document.getElementById('quickTaskModal');
    const form = modal.querySelector('#quickTaskForm');
    const formData = new FormData(form);
    
    const taskData = {
        title: formData.get('title'),
        personal_stage_type: formData.get('personal_stage_type'),
        project: formData.get('project') || null,
        due_date: formData.get('due_date') || null
    };
    
    todoKanban.submitQuickTask(taskData.personal_stage_type, taskData);
    bootstrap.Modal.getInstance(modal).hide();
};

// Initialize Kanban
let todoKanban;
function initializeKanban() {
    todoKanban = new TodoKanban();
    todoKanban.loadColumnStates();
    window.todoKanban = todoKanban;
}