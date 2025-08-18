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
            const response = await fetch('/todo/api/tasks/', {
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
            const response = await fetch('/todo/api/stages/', {
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
            const response = await fetch('/todo/api/tags/', {
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
        document.getElementById('taskDetails')?.classList.add('task-details-hidden');
        document.getElementById('kanbanView')?.classList.add('kanban-view-hidden');
        document.getElementById('welcomeState')?.classList.remove('empty-state-hidden');
        
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
        document.getElementById('welcomeState')?.classList.remove('empty-state-hidden');
        document.getElementById('taskDetails')?.classList.add('task-details-hidden');
        document.getElementById('kanbanView')?.classList.add('kanban-view-hidden');
        
        // Show sidebar on mobile
        document.getElementById('todoSidebar')?.classList.remove('d-none');
    }

    showKanbanView() {
        document.getElementById('welcomeState')?.classList.add('empty-state-hidden');
        document.getElementById('taskDetails')?.classList.add('task-details-hidden');
        document.getElementById('kanbanView')?.classList.remove('kanban-view-hidden');
        
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
            tasksEmpty?.classList.remove('empty-state-hidden');
            return;
        }
        
        tasksEmpty?.classList.add('empty-state-hidden');
        
        tasksList.innerHTML = this.tasks.map(task => this.renderTaskItem(task)).join('');
        
        // Add click listeners to tasks
        tasksList.querySelectorAll('.task-item').forEach((item, index) => {
            item.addEventListener('click', () => this.selectTask(this.tasks[index]));
        });
    }

    renderTaskItem(task) {
        const priorityIcon = task.priority === '1' ? '⭐' : '';
        const stateClass = task.state === '1_done' ? 'completed' : '';
        const progressPercent = task.progress_percentage || 0;
        
        return `
            <li class="task-item ${stateClass}" data-task-id="${task.id}" data-priority="${task.priority}" data-state="${task.state}">
                <div class="task-header">
                    <div class="d-flex align-items-center">
                        <div class="task-checkbox ${task.state === '1_done' ? 'checked' : ''}" 
                             onclick="todoApp.toggleTask('${task.id}', event)"></div>
                        <div>
                            <div class="task-name">${priorityIcon}${task.title || 'Untitled Task'}</div>
                            ${task.project_name ? `<small class="text-muted">${task.project_name}</small>` : ''}
                        </div>
                    </div>
                    <div class="task-stats">
                        ${task.subtask_count > 0 ? `<span class="task-badge">${task.completed_subtask_count}/${task.subtask_count}</span>` : ''}
                    </div>
                </div>
                ${task.description ? `<div class="task-description">${task.description.substring(0, 100)}${task.description.length > 100 ? '...' : ''}</div>` : ''}
                <div class="task-progress">
                    <div class="task-progress-bar" style="width: ${progressPercent}%"></div>
                </div>
                <div class="task-meta">
                    ${task.due_date ? `<span><i class="bi bi-calendar"></i> ${new Date(task.due_date).toLocaleDateString()}</span>` : ''}
                    ${task.is_overdue ? '<span class="text-danger"><i class="bi bi-exclamation-triangle"></i> Overdue</span>' : ''}
                    <span><i class="bi bi-clock"></i> ${new Date(task.created_at).toLocaleDateString()}</span>
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
                <div class="kanban-column">
                    <div class="kanban-header">
                        <h6 class="kanban-title">${stage.name}</h6>
                        <span class="kanban-count">${stageTasks.length}</span>
                    </div>
                    <div class="kanban-tasks">
                        ${stageTasks.map(task => this.renderKanbanTask(task)).join('')}
                    </div>
                </div>
            `;
        }).join('');
    }

    renderKanbanTask(task) {
        const priorityIcon = task.priority === '1' ? '⭐' : '';
        
        return `
            <div class="kanban-task" data-task-id="${task.id}" onclick="todoApp.selectTask(todoApp.getTaskById('${task.id}'))">
                <div class="d-flex align-items-center justify-content-between mb-2">
                    <span class="fw-bold">${priorityIcon}${task.title || 'Untitled Task'}</span>
                    <div class="task-checkbox ${task.state === '1_done' ? 'checked' : ''}" 
                         onclick="todoApp.toggleTask('${task.id}', event)"></div>
                </div>
                ${task.description ? `<p class="text-muted small mb-2">${task.description.substring(0, 80)}${task.description.length > 80 ? '...' : ''}</p>` : ''}
                ${task.due_date ? `<small class="text-muted"><i class="bi bi-calendar"></i> ${new Date(task.due_date).toLocaleDateString()}</small>` : ''}
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
        document.getElementById('welcomeState')?.classList.add('empty-state-hidden');
        document.getElementById('taskDetails')?.classList.remove('task-details-hidden');
        document.getElementById('kanbanView')?.classList.add('kanban-view-hidden');
        
        // Update task details
        document.getElementById('taskName').textContent = task.title || 'Untitled Task';
        document.getElementById('taskProject').textContent = task.project_name || 'No Project';
        
        const progressBadge = document.getElementById('taskProgress');
        if (progressBadge) {
            progressBadge.textContent = this.getStateLabel(task.state);
            progressBadge.className = `badge task-badge ${this.getStateBadgeClass(task.state)}`;
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
                        ${task.tags.map(tag => `<span class="task-tag-item">${tag.name}</span>`).join('')}
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
            '1_in_progress': 'bg-warning',
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
            const response = await fetch(`/todo/api/tasks/${taskId}/toggle_state/`, {
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
            const response = await fetch('/todo/api/tasks/quick_create/', {
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
            tasksEmpty?.classList.add('empty-state-hidden');
        } else {
            tasksEmpty?.classList.remove('empty-state-hidden');
        }
    }

    showSuccess(message) {
        // Simple success notification - can be enhanced with a proper toast system
        console.log('Success:', message);
        // TODO: Show toast notification
    }

    showError(message) {
        // Simple error notification - can be enhanced with a proper toast system
        console.error('Error:', message);
        // TODO: Show toast notification
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