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
            // Apply SortableJS directly to tasks-list containers where tasks actually are
            document.querySelectorAll('.tasks-list').forEach(tasksList => {
                new Sortable(tasksList, {
                    group: 'kanban-tasks',
                    animation: 150,
                    ghostClass: 'kanban-card-ghost',
                    chosenClass: 'kanban-card-chosen',
                    dragClass: 'kanban-card-drag',
                    draggable: '.kanban-card', // Only individual task cards are draggable
                    onEnd: this.handleSortableEnd.bind(this),
                    onMove: function(evt) {
                        // Allow all moves
                        return true;
                    }
                });
            });
            
            // Also handle the kanban-tasks-container for new tasks added dynamically
            document.querySelectorAll('.kanban-tasks-container').forEach(container => {
                // Find the tasks-list inside
                const tasksList = container.querySelector('.tasks-list');
                if (!tasksList) {
                    // If no tasks-list, apply directly to container
                    new Sortable(container, {
                        group: 'kanban-tasks',
                        animation: 150,
                        ghostClass: 'kanban-card-ghost',
                        chosenClass: 'kanban-card-chosen',
                        dragClass: 'kanban-card-drag',
                        draggable: '.kanban-card',
                        filter: '.add-task-container',
                        onEnd: this.handleSortableEnd.bind(this)
                    });
                }
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
        
        // Double-click to edit stage names
        document.addEventListener('dblclick', (e) => {
            const stageTitle = e.target.closest('.column-title-linguify');
            if (stageTitle) {
                e.preventDefault();
                const stageColumn = stageTitle.closest('.kanban-column');
                const stageId = stageColumn?.dataset.stageId;
                if (stageId) {
                    this.editStageName(stageId);
                }
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
        
        // Only move if dropped in different stage (SortableJS handles same-stage reordering)
        if (newStageId !== this.draggedTask.originalStageId) {
            // Move task to new stage
            this.moveTaskToStage(taskId, newStageId, this.draggedTask.element);
        }
    }
    
    handleSortableEnd(e) {
        const taskId = e.item.dataset.taskId;
        const newStageId = e.to.closest('.kanban-column').dataset.stageId;
        const oldStageId = e.from.closest('.kanban-column').dataset.stageId;
        
        if (newStageId !== oldStageId) {
            // Move task to different stage
            this.moveTaskToStage(taskId, newStageId, e.item, oldStageId);
        } else {
            // Just reorder within the same stage
            this.updateTaskSequence(newStageId);
        }
    }
    
    async moveTaskToStage(taskId, newStageId, taskElement, oldStageId = null) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showTaskLoading(taskElement);
        
        try {
            const response = await fetch(`/api/v1/todo/tasks/${taskId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    personal_stage_type_id: newStageId
                })
            });
            
            if (response.ok) {
                this.showSuccess('Tâche déplacée avec succès');
                this.updateStageCounts();
                // Update task's stage ID in DOM
                taskElement.dataset.stageId = newStageId;
            } else {
                const errorData = await response.json();
                console.error('API Error:', errorData);
                throw new Error(`Failed to move task: ${response.status}`);
            }
        } catch (error) {
            console.error('Error moving task:', error);
            this.showError('Erreur lors du déplacement de la tâche');
            
            // Revert the move - find the original tasks list
            const originalColumn = document.querySelector(`[data-stage-id="${oldStageId || taskElement.dataset.stageId || 'unknown'}"]`);
            if (originalColumn) {
                const originalTasksList = originalColumn.querySelector('.tasks-list');
                if (originalTasksList) {
                    originalTasksList.appendChild(taskElement);
                } else {
                    // Fallback to kanban-tasks-container
                    const container = originalColumn.querySelector('.kanban-tasks-container');
                    if (container) {
                        container.appendChild(taskElement);
                    }
                }
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
            const response = await fetch(`/api/v1/todo/tasks/${taskId}/toggle_completed/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Check if task moved to a different stage
                const currentStageId = taskCard.dataset.stageId;
                const newStageId = data.personal_stage_type?.id;
                
                if (newStageId && newStageId !== currentStageId) {
                    // Task moved to a different stage - move it visually
                    const newStageColumn = document.querySelector(`[data-stage-id="${newStageId}"]`);
                    const newTasksList = newStageColumn?.querySelector('.tasks-list');
                    
                    if (newTasksList) {
                        // Update task's stage ID
                        taskCard.dataset.stageId = newStageId;
                        
                        // Move task to new stage
                        newTasksList.appendChild(taskCard);
                        
                        // Update task card content
                        this.updateTaskCard(taskCard, data);
                        
                        // Update stage counts
                        this.updateStageCounts();
                        
                        this.showSuccess('Tâche déplacée automatiquement vers ' + (data.personal_stage_type.name || 'Done'));
                    } else {
                        // Fallback: reload page if stage not found
                        this.showSuccess('Tâche mise à jour');
                        setTimeout(() => window.location.reload(), 1000);
                    }
                } else {
                    // Just update the task card in place
                    this.updateTaskCard(taskCard, data);
                    this.showSuccess('Tâche mise à jour');
                }
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
                taskTitle.classList.add('line-through', 'text-gray-400');
            } else {
                taskTitle.classList.remove('line-through', 'text-gray-400');
            }
        }
    }
    
    showQuickAddForm(stageId, referenceElement) {
        // Hide existing forms
        this.closeAllForms();
        
        // Find the tasks container for this stage
        const tasksContainer = document.querySelector(`[data-stage-id="${stageId}"] .kanban-tasks-container`);
        if (!tasksContainer) return;
        
        // Create Linguify-style inline form
        const form = document.createElement('div');
        form.className = 'task-card-linguify quick-add-form';
        form.dataset.stageId = stageId;
        form.innerHTML = `
            <input type="text" 
                   placeholder="Tapez le titre de la tâche..." 
                   id="quickTaskTitle_${stageId}" 
                   class="form-control mb-3"
                   style="border: 1px solid var(--linguify-primary); font-size: 14px; width: 100%;"
                   autofocus>
            <div class="d-flex gap-2">
                <button class="btn-linguify-secondary submit-task-btn" type="button">
                    <i class="bi bi-check me-1"></i>Ajouter
                </button>
                <button class="btn-linguify-secondary cancel-task-btn" type="button">
                    <i class="bi bi-x me-1"></i>Annuler
                </button>
            </div>
        `;
        
        // Insert at the top of the tasks container (Odoo behavior)
        tasksContainer.insertBefore(form, tasksContainer.firstChild);
        
        // Add event listeners to the buttons
        const submitBtn = form.querySelector('.submit-task-btn');
        const cancelBtn = form.querySelector('.cancel-task-btn');
        
        if (submitBtn) {
            submitBtn.addEventListener('click', () => {
                this.submitQuickTask(stageId);
            });
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.closeAllForms();
            });
        }
        
        // Focus and keyboard handling
        const input = form.querySelector(`#quickTaskTitle_${stageId}`);
        if (input) {
            input.focus();
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.submitQuickTask(stageId);
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    this.closeAllForms();
                }
            });
        }
        
        // Hide the reference button if it's an add button
        if (referenceElement && referenceElement.classList.contains('add-task-btn-linguify')) {
            referenceElement.style.display = 'none';
        }
    }
    
    async submitQuickTask(stageId) {
        // Look for the input in the specific stage form
        const input = document.getElementById(`quickTaskTitle_${stageId}`) || document.getElementById('quickTaskTitle');
        const title = input?.value?.trim();
        
        if (!title) {
            input?.focus();
            return;
        }
        
        try {
            const response = await fetch('/api/v1/todo/tasks/quick_create/', {
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
        card.className = 'card mb-3 kanban-task-card kanban-card';
        card.dataset.taskId = taskData.id;
        card.dataset.stageId = taskData.personal_stage_type;
        card.onclick = () => window.openTask(taskData.id);
        card.style.cursor = 'pointer';
        card.style.border = '1px solid var(--linguify-gray-200, #e5e7eb)';
        card.style.transition = 'all 0.2s ease';
        
        const priorityIcon = taskData.priority === '1' 
            ? '<i class="bi bi-star-fill text-warning ms-2"></i>'
            : '';
        
        const completeBtnIcon = taskData.state === '1_done' 
            ? 'bi-check-circle-fill text-success' 
            : 'bi-circle';
        
        const titleClasses = taskData.state === '1_done' 
            ? 'card-title mb-0 flex-grow-1 text-decoration-line-through'
            : 'card-title mb-0 flex-grow-1';
        
        const titleStyle = 'color: var(--linguify-primary-dark, #1E4A8C);';
        
        card.innerHTML = `
            <div class="card-body p-3">
                <!-- Task Header -->
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="${titleClasses}" style="${titleStyle}">${taskData.title}</h6>
                    ${priorityIcon}
                </div>

                <!-- Task Meta Information -->
                ${(taskData.due_date || taskData.project) ? `
                <div class="d-flex align-items-center gap-3 mb-2 small text-muted">
                    ${taskData.due_date ? `
                    <span class="d-flex align-items-center gap-1">
                        <i class="bi bi-calendar"></i>
                        ${new Date(taskData.due_date).toLocaleDateString()}
                    </span>` : ''}
                    ${taskData.project ? `
                    <span class="d-flex align-items-center gap-1">
                        <i class="bi bi-folder"></i>
                        ${taskData.project}
                    </span>` : ''}
                </div>` : ''}

                <!-- Task Footer -->
                <div class="d-flex justify-content-between align-items-center pt-2" 
                     style="border-top: 1px solid var(--linguify-gray-100, #f3f4f6);">
                    <small class="text-muted">Just now</small>
                    <div class="d-flex align-items-center gap-1">
                        <button class="btn btn-sm btn-outline-primary p-1" 
                                onclick="event.stopPropagation(); editTask('${taskData.id}')" 
                                title="Edit"
                                style="border-color: var(--linguify-primary, #2D5BBA); color: var(--linguify-primary, #2D5BBA);">
                            <i class="bi bi-pencil" style="font-size: 0.8rem;"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success p-1" 
                                onclick="event.stopPropagation(); toggleTaskComplete('${taskData.id}')" 
                                title="Toggle Complete">
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
            const countBadge = column.querySelector('.badge-linguify');
            if (countBadge) {
                countBadge.textContent = tasks.length;
            }
        });
    }
    
    async updateTaskSequence(stageId) {
        const tasks = document.querySelectorAll(`[data-stage-id="${stageId}"] .kanban-card`);
        const taskIds = Array.from(tasks)
            .map(task => task.dataset.taskId)
            .filter(id => id); // Filter out empty IDs
        
        if (taskIds.length === 0) return;
        
        try {
            const response = await fetch(`/api/v1/todo/stages/${stageId}/reorder_tasks/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ task_ids: taskIds })
            });
            
            if (response.ok) {
                // Optional: show subtle success feedback
                console.log('Tasks reordered successfully');
            } else {
                throw new Error('Failed to reorder tasks');
            }
        } catch (error) {
            console.error('Could not update task sequence:', error);
            this.showError('Impossible de sauvegarder l\'ordre des tâches');
        }
    }
    
    closeAllForms() {
        // Remove all quick add forms
        document.querySelectorAll('.quick-add-form').forEach(form => form.remove());
        
        // Restore any hidden add buttons
        document.querySelectorAll('.add-task-btn-linguify').forEach(btn => {
            btn.style.display = 'block';
        });
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
    
    showInfo(message) {
        this.showToast(message, 'info');
    }
    
    showWarning(message) {
        this.showToast(message, 'warning');
    }
    
    handleStageDeleteError(errorData) {
        const errorType = errorData.type;
        const errorMessage = errorData.error;
        
        switch (errorType) {
            case 'CRITICAL_STAGE_ERROR':
                this.showCriticalStageError(errorData);
                break;
            case 'LAST_STAGE_ERROR':
                this.showError('⚠️ ' + errorMessage);
                break;
            case 'LAST_CLOSED_STAGE_ERROR':
                this.showError('⚠️ ' + errorMessage + '\n💡 Créez un autre stage fermé avant de supprimer celui-ci.');
                break;
            case 'LAST_OPEN_STAGE_ERROR':
                this.showError('⚠️ ' + errorMessage + '\n💡 Créez un autre stage ouvert avant de supprimer celui-ci.');
                break;
            default:
                this.showError(errorMessage || 'Impossible de supprimer ce stage');
        }
    }
    
    showCriticalStageError(errorData) {
        // Special handling for critical system stages
        const stageName = errorData.stage_name;
        const reason = errorData.reason;
        
        this.showToast(
            `🚫 Stage "${stageName}" protégé\n\n${reason}\n\n💡 Ce stage est essentiel au fonctionnement de l'application.`,
            'error',
            8000 // Show longer for important message
        );
    }
    
    showToast(message, type = 'info', duration = 5000) {
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
        
        const bsToast = new bootstrap.Toast(toast, {
            delay: duration
        });
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
    
    async createNewStage(stageName = null) {
        // If no name provided, create a default name
        if (!stageName) {
            const existingStages = document.querySelectorAll('.kanban-column').length - 1; // -1 for the "Add Stage" column
            stageName = `Nouveau Stage ${existingStages + 1}`;
        }
        
        try {
            const response = await fetch('/api/v1/todo/stages/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    name: stageName
                })
            });
            
            if (response.ok) {
                this.showSuccess('Stage créé avec succès');
                // Reload the page to show the new stage
                window.location.reload();
            } else {
                throw new Error('Failed to create stage');
            }
        } catch (error) {
            console.error('Error creating stage:', error);
            this.showError('Erreur lors de la création du stage');
        }
    }
    
    showDeleteStageModal(stageId) {
        // Find stage name and task count
        const stageColumn = document.querySelector(`[data-stage-id="${stageId}"]`);
        const stageName = stageColumn?.querySelector('.column-title-linguify')?.textContent || 'ce stage';
        const taskCount = stageColumn?.querySelectorAll('.kanban-card').length || 0;
        
        // Check if this is a critical stage
        const isCriticalStage = ['To Do', 'Done'].includes(stageName);
        
        // Update modal content
        const modal = document.getElementById('deleteStageModal');
        const stageNameElement = document.getElementById('stageNameToDelete');
        const tasksWarning = document.getElementById('tasksWarning');
        const confirmButton = document.getElementById('confirmDeleteStage');
        
        if (stageNameElement) {
            stageNameElement.textContent = stageName;
        }
        
        // Add critical stage warning
        let criticalWarning = modal.querySelector('#criticalStageWarning');
        if (isCriticalStage) {
            if (!criticalWarning) {
                criticalWarning = document.createElement('div');
                criticalWarning.id = 'criticalStageWarning';
                criticalWarning.className = 'alert alert-danger border-0 mb-3';
                criticalWarning.style.background = '#f8d7da';
                
                const warningContainer = modal.querySelector('.modal-body');
                const firstAlert = warningContainer.querySelector('.alert');
                warningContainer.insertBefore(criticalWarning, firstAlert);
            }
            
            criticalWarning.innerHTML = `
                <div class="d-flex">
                    <i class="bi bi-shield-exclamation text-danger me-3 mt-1 flex-shrink-0"></i>
                    <div>
                        <p class="mb-2"><strong>🚫 Stage système protégé</strong></p>
                        <p class="mb-0">Le stage "<strong>${stageName}</strong>" est essentiel au fonctionnement de l'application et ne peut pas être supprimé.</p>
                    </div>
                </div>
            `;
            criticalWarning.style.display = 'block';
            
            // Disable the delete button for critical stages
            if (confirmButton) {
                confirmButton.disabled = true;
                confirmButton.textContent = '🔒 Suppression impossible';
                confirmButton.className = 'btn btn-secondary';
            }
        } else {
            // Remove critical warning if exists
            if (criticalWarning) {
                criticalWarning.style.display = 'none';
            }
            
            // Re-enable delete button for non-critical stages
            if (confirmButton) {
                confirmButton.disabled = false;
                confirmButton.innerHTML = '<i class="bi bi-trash me-2"></i>Supprimer définitivement';
                confirmButton.className = 'btn btn-danger';
            }
        }
        
        // Show/hide tasks warning based on task count
        if (tasksWarning) {
            if (taskCount > 0 && !isCriticalStage) {
                tasksWarning.style.display = 'block';
                // Update the text to show task count
                const strongElement = tasksWarning.querySelector('p strong');
                if (strongElement) {
                    const taskText = taskCount === 1 
                        ? 'Que se passe-t-il avec la tâche ?' 
                        : `Que se passe-t-il avec les ${taskCount} tâches ?`;
                    strongElement.textContent = taskText;
                }
            } else {
                tasksWarning.style.display = 'none';
            }
        }
        
        // Store stageId for the confirm button
        this.pendingDeleteStageId = stageId;
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    async deleteStage(stageId) {
        const stageColumn = document.querySelector(`[data-stage-id="${stageId}"]`);
        const taskCount = stageColumn?.querySelectorAll('.kanban-card').length || 0;
        
        try {
            const response = await fetch(`/api/v1/todo/stages/${stageId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                this.showSuccess('Stage supprimé avec succès');
                // Remove the stage column from the UI
                stageColumn?.remove();
                
                // If there were tasks, show a message about orphaned tasks
                if (taskCount > 0) {
                    setTimeout(() => {
                        this.showInfo(`${taskCount} tâche(s) ont été déplacées vers aucun stage. Vous pouvez les réassigner depuis la vue Liste.`);
                    }, 2000);
                }
            } else if (response.status === 404) {
                this.showError('Stage non trouvé');
            } else if (response.status === 400) {
                // Handle various protection errors
                const errorData = await response.json();
                this.handleStageDeleteError(errorData);
            } else {
                throw new Error('Failed to delete stage');
            }
        } catch (error) {
            console.error('Error deleting stage:', error);
            this.showError('Erreur lors de la suppression du stage');
        }
    }
    
    showAddStageForm() {
        console.log('Add new stage form - to be implemented');
    }
    
    editStageName(stageId) {
        const stageColumn = document.querySelector(`[data-stage-id="${stageId}"]`);
        const titleElement = stageColumn?.querySelector('.column-title-linguify');
        
        if (!titleElement) return;
        
        const currentName = titleElement.textContent.trim();
        
        // Create input element
        const input = document.createElement('input');
        input.type = 'text';
        input.value = currentName;
        input.className = 'form-control form-control-sm';
        input.style.cssText = `
            width: auto;
            min-width: 120px;
            background: transparent;
            border: 1px solid var(--linguify-primary);
            color: var(--linguify-primary-dark);
            font-weight: 600;
            font-size: inherit;
        `;
        
        // Replace title with input
        titleElement.style.display = 'none';
        titleElement.parentNode.insertBefore(input, titleElement.nextSibling);
        
        // Focus and select
        input.focus();
        input.select();
        
        // Handle save/cancel
        const saveStage = async () => {
            const newName = input.value.trim();
            
            if (!newName || newName === currentName) {
                cancelEdit();
                return;
            }
            
            try {
                const response = await fetch(`/api/v1/todo/stages/${stageId}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({ name: newName })
                });
                
                if (response.ok) {
                    titleElement.textContent = newName;
                    this.showSuccess('Nom du stage modifié');
                } else {
                    throw new Error('Failed to update stage name');
                }
            } catch (error) {
                console.error('Error updating stage name:', error);
                this.showError('Erreur lors de la modification du nom');
            }
            
            cancelEdit();
        };
        
        const cancelEdit = () => {
            input.remove();
            titleElement.style.display = '';
        };
        
        // Events
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveStage();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelEdit();
            }
        });
        
        input.addEventListener('blur', saveStage);
    }
}

// Global functions
window.addTaskToStage = function(stageId) {
    // Look for the kanban-quick-add button first (Odoo style)
    let addBtn = document.querySelector(`[data-stage-id="${stageId}"] .kanban-quick-add`);
    
    // If not found, look for the bottom add button
    if (!addBtn) {
        addBtn = document.querySelector(`[data-stage-id="${stageId}"] .add-task-btn-linguify`);
    }
    
    // If still not found, create a reference from the column header
    if (!addBtn) {
        const column = document.querySelector(`[data-stage-id="${stageId}"]`);
        if (column) {
            addBtn = column.querySelector('.kanban-column-header');
        }
    }
    
    if (window.todoKanban) {
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

window.addNewStage = function() {
    if (todoKanban) {
        todoKanban.createNewStage();
    }
};

window.deleteStage = function(stageId) {
    if (todoKanban) {
        todoKanban.showDeleteStageModal(stageId);
    }
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