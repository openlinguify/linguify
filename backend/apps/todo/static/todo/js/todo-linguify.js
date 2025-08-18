/**
 * Todo App - Linguify Design System
 * JavaScript functionality following Linguify patterns
 */

class TodoApp {
    constructor() {
        this.currentView = 'list';
        this.currentTask = null;
        this.tasks = [];
        this.projects = [];
        this.stages = [];
        this.tags = [];
        this.csrfToken = '';
        
        this.init();
    }

    init() {
        // Get CSRF token
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Initialize views
        this.initEventListeners();
        this.loadInitialData();
        
        // Set initial view
        this.setView('list');
        
        console.log('Todo App initialized with Linguify design');
    }

    initEventListeners() {
        // View switchers
        document.getElementById('listViewBtn')?.addEventListener('click', () => this.setView('list'));
        document.getElementById('kanbanViewBtn')?.addEventListener('click', () => this.setView('kanban'));
        document.getElementById('calendarViewBtn')?.addEventListener('click', () => this.setView('calendar'));
        
        // Search functionality
        document.getElementById('searchInput')?.addEventListener('keyup', () => this.debounceSearch());
        
        // Filters
        document.getElementById('stageFilter')?.addEventListener('change', () => this.filterTasks());
        document.getElementById('priorityFilter')?.addEventListener('change', () => this.filterTasks());
        
        // Create task buttons
        document.querySelectorAll('.create-task-btn').forEach(btn => {
            btn.addEventListener('click', () => this.createNewTask());
        });
        
        // Back to list button (mobile)
        document.getElementById('backToList')?.addEventListener('click', () => this.showTasksList());
        
        // Refresh button
        document.querySelector('button[onclick="refreshTasks()"]')?.addEventListener('click', () => this.refreshTasks());
        
        // Load more button
        document.getElementById('loadMoreBtn')?.addEventListener('click', () => this.loadMoreTasks());
        
        // Mobile sidebar controls
        document.getElementById('sidebarToggle')?.addEventListener('click', () => this.toggleSidebar());
        document.getElementById('sidebarClose')?.addEventListener('click', () => this.closeSidebar());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => this.handleOutsideClick(e));
    }

    async loadInitialData() {
        try {
            // Load tasks, stages, and other data
            await Promise.all([
                this.loadTasks(),
                this.loadStages(),
                this.loadTags()
            ]);
            
            this.renderTasks();
            this.renderStageFilter();
            this.updateUI();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load data');
        }
    }

    async loadTasks() {
        try {
            const response = await fetch('/api/v1/todo/tasks/', {
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.tasks = Array.isArray(data) ? data : data.results || [];
            }
        } catch (error) {
            console.error('Error loading tasks:', error);
        }
    }

    async loadStages() {
        try {
            const response = await fetch('/api/v1/todo/stages/', {
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.stages = Array.isArray(data) ? data : data.results || [];
            }
        } catch (error) {
            console.error('Error loading stages:', error);
        }
    }

    async loadTags() {
        try {
            const response = await fetch('/api/v1/todo/tags/', {
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.tags = Array.isArray(data) ? data : data.results || [];
            }
        } catch (error) {
            console.error('Error loading tags:', error);
        }
    }

    setView(viewType) {
        this.currentView = viewType;
        
        // Update view buttons
        document.querySelectorAll('.btn-outline-secondary').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Hide all views
        document.getElementById('taskDetails').style.display = 'none';
        document.getElementById('kanbanView').style.display = 'none';
        document.getElementById('welcomeState').style.display = 'block';
        
        switch (viewType) {
            case 'list':
                document.getElementById('listViewBtn')?.classList.add('active');
                this.showTasksList();
                break;
            case 'kanban':
                document.getElementById('kanbanViewBtn')?.classList.add('active');
                this.showKanbanView();
                break;
            case 'calendar':
                document.getElementById('calendarViewBtn')?.classList.add('active');
                this.showCalendarView();
                break;
        }
    }

    showTasksList() {
        document.getElementById('welcomeState').style.display = 'block';
        document.getElementById('taskDetails').style.display = 'none';
        document.getElementById('kanbanView').style.display = 'none';
        
        // Show sidebar on mobile
        document.getElementById('todoSidebar')?.classList.remove('d-none');
    }

    showKanbanView() {
        document.getElementById('welcomeState').style.display = 'none';
        document.getElementById('taskDetails').style.display = 'none';
        document.getElementById('kanbanView').style.display = 'block';
        
        this.renderKanbanBoard();
    }

    showCalendarView() {
        // TODO: Implement calendar view
        console.log('Calendar view not yet implemented');
    }

    renderTasks() {
        const tasksList = document.getElementById('tasksList');
        const tasksEmpty = document.getElementById('tasksEmpty');
        
        if (!tasksList) return;
        
        if (this.tasks.length === 0) {
            tasksList.innerHTML = '';
            tasksEmpty.style.display = 'block';
            return;
        }
        
        tasksEmpty.style.display = 'none';
        
        tasksList.innerHTML = this.tasks.map(task => this.renderTaskItem(task)).join('');
        
        // Add click listeners to tasks
        tasksList.querySelectorAll('.task-item').forEach((item, index) => {
            item.addEventListener('click', () => this.selectTask(this.tasks[index]));
        });
        
        // Update task counts
        this.updateTaskCounts();
    }

    renderTaskItem(task) {
        const priorityIcon = task.priority === '1' ? '⭐' : '';
        const stateClass = task.state === '1_done' ? 'text-muted' : '';
        const progressPercent = task.progress_percentage || 0;
        
        return `
            <li class="task-item list-group-item border-0 mb-2 rounded shadow-sm cursor-pointer ${stateClass}" data-task-id="${task.id}" data-priority="${task.priority}" data-state="${task.state}" style="cursor: pointer;">
                <div class="d-flex align-items-start">
                    <div class="form-check me-3">
                        <input class="form-check-input" type="checkbox" ${task.state === '1_done' ? 'checked' : ''} 
                               onclick="todoApp.toggleTask('${task.id}', event)" style="margin-top: 0.125rem;">
                    </div>
                    <div class="flex-fill">
                        <div class="d-flex align-items-center justify-content-between mb-1">
                            <h6 class="mb-0 fw-bold">${priorityIcon}${task.title || 'Untitled Task'}</h6>
                            ${task.subtask_count > 0 ? `<span class="badge bg-secondary">${task.completed_subtask_count}/${task.subtask_count}</span>` : ''}
                        </div>
                        ${task.project_name ? `<small class="text-muted d-block mb-1">${task.project_name}</small>` : ''}
                        ${task.description ? `<p class="text-muted small mb-2">${task.description.substring(0, 100)}${task.description.length > 100 ? '...' : ''}</p>` : ''}
                        ${progressPercent > 0 ? `
                            <div class="progress mb-2" style="height: 4px;">
                                <div class="progress-bar" style="width: ${progressPercent}%"></div>
                            </div>
                        ` : ''}
                        <div class="d-flex align-items-center text-muted small">
                            ${task.due_date ? `<span class="me-3"><i class="bi bi-calendar me-1"></i>${new Date(task.due_date).toLocaleDateString()}</span>` : ''}
                            ${task.is_overdue ? '<span class="text-danger me-3"><i class="bi bi-exclamation-triangle me-1"></i>Overdue</span>' : ''}
                            <span><i class="bi bi-clock me-1"></i>${new Date(task.created_at).toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>
            </li>
        `;
    }

    renderKanbanBoard() {
        const kanbanBoard = document.getElementById('kanbanBoard');
        if (!kanbanBoard) return;
        
        const tasksByStage = this.groupTasksByStage();
        
        kanbanBoard.innerHTML = this.stages.map(stage => {
            const stageTasks = tasksByStage[stage.id] || [];
            return `
                <div class="col-md-3">
                    <div class="card h-100">
                        <div class="card-header bg-primary text-white d-flex align-items-center justify-content-between">
                            <h6 class="mb-0">${stage.name}</h6>
                            <span class="badge bg-light text-dark">${stageTasks.length}</span>
                        </div>
                        <div class="card-body p-2">
                            ${stageTasks.map(task => this.renderKanbanTask(task)).join('')}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderKanbanTask(task) {
        const priorityIcon = task.priority === '1' ? '⭐' : '';
        
        return `
            <div class="card mb-2 shadow-sm" data-task-id="${task.id}" onclick="todoApp.selectTask(todoApp.getTaskById('${task.id}'))" style="cursor: pointer;">
                <div class="card-body p-2">
                    <div class="d-flex align-items-center justify-content-between mb-1">
                        <span class="fw-bold small">${priorityIcon}${task.title || 'Untitled Task'}</span>
                        <input class="form-check-input" type="checkbox" ${task.state === '1_done' ? 'checked' : ''} 
                               onclick="todoApp.toggleTask('${task.id}', event)">
                    </div>
                    ${task.description ? `<p class="text-muted small mb-1">${task.description.substring(0, 60)}${task.description.length > 60 ? '...' : ''}</p>` : ''}
                    ${task.due_date ? `<small class="text-muted"><i class="bi bi-calendar me-1"></i>${new Date(task.due_date).toLocaleDateString()}</small>` : ''}
                </div>
            </div>
        `;
    }

    renderStageFilter() {
        const stageFilter = document.getElementById('stageFilter');
        if (!stageFilter) return;
        
        const currentOptions = stageFilter.innerHTML;
        const stageOptions = this.stages.map(stage => 
            `<option value="${stage.id}">${stage.name}</option>`
        ).join('');
        
        stageFilter.innerHTML = `<option value="">All Stages</option>${stageOptions}`;
    }

    groupTasksByStage() {
        const grouped = {};
        this.stages.forEach(stage => {
            grouped[stage.id] = [];
        });
        
        this.tasks.forEach(task => {
            const stageId = task.personal_stage_type?.id;
            if (stageId && grouped[stageId]) {
                grouped[stageId].push(task);
            }
        });
        
        return grouped;
    }

    selectTask(task) {
        this.currentTask = task;
        
        // Update active state in sidebar
        document.querySelectorAll('.task-item').forEach(item => {
            item.classList.remove('active');
        });
        
        document.querySelector(`[data-task-id="${task.id}"]`)?.classList.add('active');
        
        // Show task details
        this.showTaskDetails(task);
        
        // Hide sidebar on mobile
        if (window.innerWidth <= 768) {
            document.getElementById('todoSidebar')?.classList.add('d-none');
        }
    }

    showTaskDetails(task) {
        document.getElementById('welcomeState').style.display = 'none';
        document.getElementById('taskDetails').style.display = 'block';
        document.getElementById('kanbanView').style.display = 'none';
        
        // Update task details
        document.getElementById('taskName').textContent = task.title || 'Untitled Task';
        document.getElementById('taskProject').textContent = task.project_name || 'No Project';
        
        const progressBadge = document.getElementById('taskProgress');
        if (progressBadge) {
            progressBadge.textContent = this.getStateLabel(task.state);
            progressBadge.className = `badge ${this.getStateBadgeClass(task.state)}`;
        }
        
        const priorityIndicator = document.getElementById('taskPriority');
        if (priorityIndicator) {
            priorityIndicator.style.display = task.priority === '1' ? 'block' : 'none';
        }
        
        // Update task content
        const taskContent = document.getElementById('taskContent');
        if (taskContent) {
            taskContent.innerHTML = `
                <div class="task-description-full">
                    ${task.description || '<p class="text-muted">No description provided.</p>'}
                </div>
                ${task.tags && task.tags.length > 0 ? `
                    <div class="task-tags-display mt-3">
                        ${task.tags.map(tag => `<span class="badge bg-secondary me-1">${tag.name}</span>`).join('')}
                    </div>
                ` : ''}
            `;
        }
        
        // Update toggle button
        const toggleBtn = document.getElementById('toggleCompleteBtn');
        if (toggleBtn) {
            const isCompleted = task.state === '1_done';
            toggleBtn.innerHTML = isCompleted ? '<i class="bi bi-check2-square"></i>' : '<i class="bi bi-check2"></i>';
            toggleBtn.title = isCompleted ? 'Mark as incomplete' : 'Mark as done';
        }
    }

    getStateLabel(state) {
        const stateLabels = {
            '1_draft': 'Draft',
            '1_todo': 'To Do',
            '1_in_progress': 'In Progress',
            '1_done': 'Done',
            '1_canceled': 'Canceled'
        };
        return stateLabels[state] || 'Unknown';
    }

    getStateBadgeClass(state) {
        const badgeClasses = {
            '1_draft': 'bg-secondary',
            '1_todo': 'bg-primary',
            '1_in_progress': 'bg-warning text-dark',
            '1_done': 'bg-success',
            '1_canceled': 'bg-danger'
        };
        return badgeClasses[state] || 'bg-secondary';
    }

    async toggleTask(taskId, event) {
        if (event) {
            event.stopPropagation();
        }
        
        try {
            const response = await fetch(`/api/v1/todo/tasks/${taskId}/toggle_state/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const updatedTask = await response.json();
                
                // Update task in local array
                const taskIndex = this.tasks.findIndex(t => t.id === taskId);
                if (taskIndex >= 0) {
                    this.tasks[taskIndex] = { ...this.tasks[taskIndex], ...updatedTask };
                }
                
                // Re-render views
                this.renderTasks();
                if (this.currentView === 'kanban') {
                    this.renderKanbanBoard();
                }
                
                // Update task details if currently selected
                if (this.currentTask && this.currentTask.id === taskId) {
                    this.currentTask = { ...this.currentTask, ...updatedTask };
                    this.showTaskDetails(this.currentTask);
                }
            }
        } catch (error) {
            console.error('Error toggling task:', error);
            this.showError('Failed to update task');
        }
    }

    getTaskById(taskId) {
        return this.tasks.find(task => task.id === taskId);
    }

    async createNewTask() {
        const title = prompt('Enter task title:');
        if (!title) return;
        
        try {
            const response = await fetch('/api/v1/todo/tasks/quick_create/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title
                })
            });
            
            if (response.ok) {
                const newTask = await response.json();
                this.tasks.unshift(newTask);
                this.renderTasks();
                
                if (this.currentView === 'kanban') {
                    this.renderKanbanBoard();
                }
                
                this.showSuccess('Task created successfully');
            }
        } catch (error) {
            console.error('Error creating task:', error);
            this.showError('Failed to create task');
        }
    }

    debounceSearch() {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.filterTasks();
        }, 300);
    }

    filterTasks() {
        const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
        const stageFilter = document.getElementById('stageFilter')?.value || '';
        const priorityFilter = document.getElementById('priorityFilter')?.value || '';
        
        // Filter tasks based on criteria
        const filteredTasks = this.tasks.filter(task => {
            const matchesSearch = !searchTerm || 
                task.title.toLowerCase().includes(searchTerm) ||
                (task.description && task.description.toLowerCase().includes(searchTerm));
            
            const matchesStage = !stageFilter || 
                (task.personal_stage_type && task.personal_stage_type.id === stageFilter);
            
            const matchesPriority = !priorityFilter || task.priority === priorityFilter;
            
            return matchesSearch && matchesStage && matchesPriority;
        });
        
        // Temporarily update tasks for rendering
        const originalTasks = this.tasks;
        this.tasks = filteredTasks;
        this.renderTasks();
        if (this.currentView === 'kanban') {
            this.renderKanbanBoard();
        }
        this.tasks = originalTasks;
    }

    async refreshTasks() {
        await this.loadTasks();
        this.renderTasks();
        if (this.currentView === 'kanban') {
            this.renderKanbanBoard();
        }
        this.showSuccess('Tasks refreshed');
    }

    loadMoreTasks() {
        // TODO: Implement pagination
        console.log('Load more tasks not yet implemented');
    }

    updateUI() {
        // Update empty states
        const hasAnyTasks = this.tasks.length > 0;
        const welcomeState = document.getElementById('welcomeState');
        const tasksEmpty = document.getElementById('tasksEmpty');
        
        if (hasAnyTasks) {
            tasksEmpty.style.display = 'none';
            welcomeState.style.display = 'block';
        } else {
            tasksEmpty.style.display = 'block';
            welcomeState.style.display = 'block';
        }
        
        // Update task counts
        this.updateTaskCounts();
    }

    updateTaskCounts() {
        const totalCount = this.tasks.length;
        const completedCount = this.tasks.filter(task => task.state === '1_done').length;
        
        const totalElement = document.getElementById('totalTasksCount');
        const completedElement = document.getElementById('completedTasksCount');
        
        if (totalElement) totalElement.textContent = totalCount;
        if (completedElement) completedElement.textContent = completedCount;
    }

    toggleSidebar() {
        const sidebar = document.getElementById('todoSidebar');
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    }

    closeSidebar() {
        const sidebar = document.getElementById('todoSidebar');
        if (sidebar) {
            sidebar.classList.remove('show');
        }
    }

    handleKeyboardShortcuts(event) {
        // Ctrl+N or Cmd+N for new task
        if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
            event.preventDefault();
            this.createNewTask();
            return;
        }
        
        // Escape to close sidebar on mobile
        if (event.key === 'Escape') {
            this.closeSidebar();
        }
        
        // F5 or Ctrl+R for refresh (allow default but also update our data)
        if (event.key === 'F5' || ((event.ctrlKey || event.metaKey) && event.key === 'r')) {
            setTimeout(() => this.refreshTasks(), 100);
        }
    }

    handleOutsideClick(event) {
        const sidebar = document.getElementById('todoSidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        
        if (window.innerWidth <= 991.98 && sidebar && sidebar.classList.contains('show')) {
            if (!sidebar.contains(event.target) && !sidebarToggle?.contains(event.target)) {
                this.closeSidebar();
            }
        }
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const iconClass = type === 'success' ? 'bi-check-circle' : 
                         type === 'error' ? 'bi-exclamation-triangle' : 'bi-info-circle';
        const bgClass = type === 'success' ? 'bg-success' : 
                       type === 'error' ? 'bg-danger' : 'bg-primary';

        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body d-flex align-items-center">
                        <i class="bi ${iconClass} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const bsToast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: type === 'error' ? 5000 : 3000
        });
        
        bsToast.show();
        
        // Remove toast element after hiding
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

// Global functions for template compatibility
function createNewTask() {
    todoApp.createNewTask();
}

function createNewProject() {
    // TODO: Implement project creation
    console.log('Project creation not yet implemented');
}

function setView(viewType) {
    todoApp.setView(viewType);
}

function filterTasks() {
    todoApp.filterTasks();
}

function debounceSearch() {
    todoApp.debounceSearch();
}

function refreshTasks() {
    todoApp.refreshTasks();
}

function editTask() {
    if (todoApp.currentTask) {
        // TODO: Implement task editing
        console.log('Task editing not yet implemented');
    }
}

function toggleTaskComplete() {
    if (todoApp.currentTask) {
        todoApp.toggleTask(todoApp.currentTask.id);
    }
}

function deleteTask() {
    if (todoApp.currentTask && confirm('Are you sure you want to delete this task?')) {
        // TODO: Implement task deletion
        console.log('Task deletion not yet implemented');
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.todoApp = new TodoApp();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TodoApp;
}