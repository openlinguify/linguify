/**
 * Todo & Productivity App JavaScript
 * Modern, feature-rich task management system
 */

class TodoApp {
    constructor() {
        this.currentView = 'dashboard';
        this.currentProject = null;
        this.filters = {
            status: 'all',
            priority: 'all',
            tags: [],
            search: ''
        };
        this.settings = {};
        this.initialize();
    }

    async initialize() {
        await this.loadSettings();
        this.setupEventListeners();
        this.loadDashboard();
        this.setupQuickAdd();
        this.initializeTheme();
    }

    // Settings Management
    async loadSettings() {
        try {
            const response = await fetch('/api/v1/todo/api/settings/');
            this.settings = await response.json();
        } catch (error) {
            console.error('Failed to load settings:', error);
            this.settings = this.getDefaultSettings();
        }
    }

    getDefaultSettings() {
        return {
            default_project_view: 'list',
            default_task_view: 'list',
            theme: 'auto',
            enable_reminders: true,
            show_completed_tasks: true,
            quick_add_shortcut: true
        };
    }

    // Theme Management
    initializeTheme() {
        const theme = this.settings.theme || 'auto';
        this.setTheme(theme);
    }

    setTheme(theme) {
        const app = document.querySelector('.todo-app');
        if (!app) return;

        app.classList.remove('light-theme', 'dark-theme');
        
        if (theme === 'auto') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            theme = prefersDark ? 'dark' : 'light';
        }
        
        if (theme === 'dark') {
            app.classList.add('dark-theme');
        }
    }

    // Event Listeners
    setupEventListeners() {
        // Navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-nav]')) {
                this.handleNavigation(e.target.dataset.nav);
            }
        });

        // Task actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-task-action]')) {
                this.handleTaskAction(e.target.dataset.taskAction, e.target);
            }
        });

        // Project actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-project-action]')) {
                this.handleProjectAction(e.target.dataset.projectAction, e.target);
            }
        });

        // Filters
        document.addEventListener('change', (e) => {
            if (e.target.matches('[data-filter]')) {
                this.handleFilterChange(e.target.dataset.filter, e.target.value);
            }
        });

        // Search
        const searchInput = document.querySelector('[data-search]');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }

        // Keyboard shortcuts
        if (this.settings.quick_add_shortcut) {
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'Enter') {
                    this.showQuickAdd();
                }
            });
        }
    }

    // Navigation
    handleNavigation(view) {
        this.currentView = view;
        this.updateActiveNav(view);
        
        switch (view) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'tasks':
                this.loadTasks();
                break;
            case 'projects':
                this.loadProjects();
                break;
            case 'notes':
                this.loadNotes();
                break;
            case 'calendar':
                this.loadCalendar();
                break;
            case 'kanban':
                this.loadKanban();
                break;
            default:
                this.loadDashboard();
        }
    }

    updateActiveNav(activeView) {
        document.querySelectorAll('.todo-nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeItem = document.querySelector(`[data-nav="${activeView}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    // Dashboard
    async loadDashboard() {
        const mainContent = document.querySelector('.todo-main');
        mainContent.innerHTML = '<div class="todo-loading"><div class="todo-spinner"></div></div>';

        try {
            const response = await fetch('/api/v1/todo/api/dashboard/');
            const data = await response.json();
            
            mainContent.innerHTML = this.renderDashboard(data);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            mainContent.innerHTML = '<div class="alert alert-danger">Failed to load dashboard</div>';
        }
    }

    renderDashboard(data) {
        const stats = data.stats || {};
        const activity = data.activity || {};
        const quickAccess = data.quick_access || {};

        return `
            <div class="todo-dashboard">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1>Dashboard</h1>
                    <button class="todo-btn todo-btn-primary" onclick="todoApp.showQuickAdd()">
                        <i class="bi bi-plus"></i> Quick Add
                    </button>
                </div>

                <div class="todo-dashboard-grid">
                    <div class="todo-stat-card">
                        <div class="todo-stat-number">${stats.total_tasks || 0}</div>
                        <div class="todo-stat-label">Total Tasks</div>
                    </div>
                    <div class="todo-stat-card">
                        <div class="todo-stat-number">${stats.completed_tasks || 0}</div>
                        <div class="todo-stat-label">Completed</div>
                    </div>
                    <div class="todo-stat-card">
                        <div class="todo-stat-number">${stats.today_tasks || 0}</div>
                        <div class="todo-stat-label">Due Today</div>
                    </div>
                    <div class="todo-stat-card">
                        <div class="todo-stat-number" style="color: var(--todo-danger)">${stats.overdue_tasks || 0}</div>
                        <div class="todo-stat-label">Overdue</div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-8">
                        <div class="todo-card">
                            <div class="todo-card-header">
                                <h3>Recent Activity</h3>
                            </div>
                            <div class="todo-card-body">
                                <p>Tasks created this week: ${activity.tasks_created_this_week || 0}</p>
                                <p>Tasks completed this week: ${activity.tasks_completed_this_week || 0}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="todo-card">
                            <div class="todo-card-header">
                                <h4>Quick Access</h4>
                            </div>
                            <div class="todo-card-body">
                                <h6>Recent Projects</h6>
                                ${this.renderQuickAccessProjects(quickAccess.recent_projects || [])}
                                
                                <h6 class="mt-3">Important Tasks</h6>
                                ${this.renderQuickAccessTasks(quickAccess.important_tasks || [])}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderQuickAccessProjects(projects) {
        if (!projects.length) return '<p class="text-muted">No recent projects</p>';
        
        return projects.map(project => `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span>${project.name}</span>
                <button class="btn btn-sm btn-outline-primary" onclick="todoApp.openProject('${project.id}')">
                    Open
                </button>
            </div>
        `).join('');
    }

    renderQuickAccessTasks(tasks) {
        if (!tasks.length) return '<p class="text-muted">No important tasks</p>';
        
        return tasks.map(task => `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span>${task.title}</span>
                <span class="badge bg-warning">${this.formatDate(task.due_date)}</span>
            </div>
        `).join('');
    }

    // Tasks
    async loadTasks() {
        const mainContent = document.querySelector('.todo-main');
        mainContent.innerHTML = '<div class="todo-loading"><div class="todo-spinner"></div></div>';

        try {
            const params = new URLSearchParams(this.filters);
            const response = await fetch(`/api/v1/todo/api/tasks/?${params}`);
            const tasks = await response.json();
            
            mainContent.innerHTML = this.renderTasks(tasks);
        } catch (error) {
            console.error('Failed to load tasks:', error);
            mainContent.innerHTML = '<div class="alert alert-danger">Failed to load tasks</div>';
        }
    }

    renderTasks(tasks) {
        return `
            <div class="todo-tasks">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1>Tasks</h1>
                    <button class="todo-btn todo-btn-primary" onclick="todoApp.showTaskForm()">
                        <i class="bi bi-plus"></i> New Task
                    </button>
                </div>

                <div class="row mb-4">
                    <div class="col-md-3">
                        <select class="todo-form-control" data-filter="status">
                            <option value="all">All Status</option>
                            <option value="todo">To Do</option>
                            <option value="in_progress">In Progress</option>
                            <option value="completed">Completed</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <select class="todo-form-control" data-filter="priority">
                            <option value="all">All Priorities</option>
                            <option value="urgent">Urgent</option>
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <input type="text" class="todo-form-control" placeholder="Search tasks..." data-search>
                    </div>
                </div>

                <div class="todo-task-list">
                    ${tasks.map(task => this.renderTaskItem(task)).join('')}
                </div>
            </div>
        `;
    }

    renderTaskItem(task) {
        const priorityClass = `todo-task-priority ${task.priority}`;
        const completedClass = task.status === 'completed' ? 'completed' : '';
        const overdueClass = task.is_overdue ? 'overdue' : '';

        return `
            <div class="todo-task-item ${completedClass}" data-task-id="${task.id}">
                <input type="checkbox" class="todo-task-checkbox" 
                       ${task.status === 'completed' ? 'checked' : ''}
                       data-task-action="toggle-completed">
                
                <div class="todo-task-content">
                    <div class="todo-task-title">${task.title}</div>
                    <div class="todo-task-meta">
                        <span class="${priorityClass}">${task.priority}</span>
                        ${task.due_date ? `<span class="todo-task-due ${overdueClass}">
                            <i class="bi bi-calendar"></i> ${this.formatDate(task.due_date)}
                        </span>` : ''}
                        ${task.project_name ? `<span class="text-muted">${task.project_name}</span>` : ''}
                    </div>
                    ${task.tags && task.tags.length ? `
                        <div class="todo-task-tags">
                            ${task.tags.map(tag => `<span class="todo-tag">#${tag.name}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>

                <div class="todo-task-actions">
                    <button class="btn btn-sm btn-outline-primary" data-task-action="edit">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" 
                            data-task-action="toggle-important"
                            title="${task.is_important ? 'Remove from important' : 'Mark as important'}">
                        <i class="bi ${task.is_important ? 'bi-star-fill' : 'bi-star'}"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // Projects
    async loadProjects() {
        const mainContent = document.querySelector('.todo-main');
        mainContent.innerHTML = '<div class="todo-loading"><div class="todo-spinner"></div></div>';

        try {
            const response = await fetch('/api/v1/todo/api/projects/');
            const projects = await response.json();
            
            mainContent.innerHTML = this.renderProjects(projects);
        } catch (error) {
            console.error('Failed to load projects:', error);
            mainContent.innerHTML = '<div class="alert alert-danger">Failed to load projects</div>';
        }
    }

    renderProjects(projects) {
        return `
            <div class="todo-projects">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1>Projects</h1>
                    <button class="todo-btn todo-btn-primary" onclick="todoApp.showProjectForm()">
                        <i class="bi bi-plus"></i> New Project
                    </button>
                </div>

                <div class="row">
                    ${projects.map(project => this.renderProjectCard(project)).join('')}
                </div>
            </div>
        `;
    }

    renderProjectCard(project) {
        return `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="todo-project-item" data-project-id="${project.id}">
                    <div class="todo-project-header">
                        <h3 class="todo-project-title">${project.name}</h3>
                        <button class="btn btn-sm btn-outline-secondary" 
                                data-project-action="toggle-favorite"
                                title="${project.is_favorite ? 'Remove from favorites' : 'Add to favorites'}">
                            <i class="bi ${project.is_favorite ? 'bi-heart-fill' : 'bi-heart'}"></i>
                        </button>
                    </div>
                    
                    ${project.description ? `<p class="todo-project-description">${project.description}</p>` : ''}
                    
                    <div class="todo-project-progress">
                        <div class="todo-project-progress-bar" style="width: ${project.progress_percentage}%"></div>
                    </div>
                    
                    <div class="todo-project-stats">
                        <span>${project.completed_task_count}/${project.task_count} tasks</span>
                        <span class="badge bg-primary">${project.status}</span>
                    </div>
                </div>
            </div>
        `;
    }

    // Task Actions
    async handleTaskAction(action, element) {
        const taskItem = element.closest('.todo-task-item');
        const taskId = taskItem.dataset.taskId;

        switch (action) {
            case 'toggle-completed':
                await this.toggleTaskCompleted(taskId);
                break;
            case 'toggle-important':
                await this.toggleTaskImportant(taskId);
                break;
            case 'edit':
                this.showTaskForm(taskId);
                break;
        }
    }

    async toggleTaskCompleted(taskId) {
        try {
            const response = await fetch(`/api/v1/todo/api/tasks/${taskId}/toggle_completed/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.loadTasks(); // Refresh tasks
            }
        } catch (error) {
            console.error('Failed to toggle task:', error);
        }
    }

    async toggleTaskImportant(taskId) {
        try {
            const response = await fetch(`/api/v1/todo/api/tasks/${taskId}/toggle_important/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.loadTasks(); // Refresh tasks
            }
        } catch (error) {
            console.error('Failed to toggle importance:', error);
        }
    }

    // Project Actions
    async handleProjectAction(action, element) {
        const projectItem = element.closest('.todo-project-item');
        const projectId = projectItem.dataset.projectId;

        switch (action) {
            case 'toggle-favorite':
                await this.toggleProjectFavorite(projectId);
                break;
        }
    }

    async toggleProjectFavorite(projectId) {
        try {
            const response = await fetch(`/api/v1/todo/api/projects/${projectId}/toggle_favorite/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.loadProjects(); // Refresh projects
            }
        } catch (error) {
            console.error('Failed to toggle favorite:', error);
        }
    }

    // Filters
    handleFilterChange(filterType, value) {
        this.filters[filterType] = value;
        
        if (this.currentView === 'tasks') {
            this.loadTasks();
        }
    }

    handleSearch(query) {
        this.filters.search = query;
        
        // Debounce search
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            if (this.currentView === 'tasks') {
                this.loadTasks();
            }
        }, 300);
    }

    // Quick Add
    setupQuickAdd() {
        const quickAddBtn = document.querySelector('.todo-quick-add');
        if (quickAddBtn) {
            quickAddBtn.addEventListener('click', () => this.showQuickAdd());
        }
    }

    showQuickAdd() {
        // Simple prompt for now - in a real app this would be a modal
        const title = prompt('Enter task title:');
        if (title) {
            this.createTask({ title });
        }
    }

    async createTask(taskData) {
        try {
            const response = await fetch('/api/v1/todo/api/tasks/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(taskData)
            });

            if (response.ok) {
                if (this.currentView === 'tasks') {
                    this.loadTasks();
                }
                this.showNotification('Task created successfully!', 'success');
            }
        } catch (error) {
            console.error('Failed to create task:', error);
            this.showNotification('Failed to create task', 'error');
        }
    }

    // Utility methods
    formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const taskDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
        
        const diffTime = taskDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Tomorrow';
        if (diffDays === -1) return 'Yesterday';
        if (diffDays < 0) return `${Math.abs(diffDays)} days ago`;
        if (diffDays < 7) return `In ${diffDays} days`;
        
        return date.toLocaleDateString();
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    showNotification(message, type = 'info') {
        // Simple notification - in a real app this would be a toast notification
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'error' ? 'alert-danger' : 'alert-info';
        
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Placeholder methods for forms
    showTaskForm(taskId = null) {
        console.log('Show task form for:', taskId);
        // This would open a modal or navigate to a form page
    }

    showProjectForm(projectId = null) {
        console.log('Show project form for:', projectId);
        // This would open a modal or navigate to a form page
    }

    openProject(projectId) {
        console.log('Open project:', projectId);
        this.currentProject = projectId;
        this.handleNavigation('tasks');
    }

    // Placeholder methods for other views
    loadNotes() {
        const mainContent = document.querySelector('.todo-main');
        mainContent.innerHTML = '<h1>Notes</h1><p>Notes feature coming soon...</p>';
    }

    loadCalendar() {
        const mainContent = document.querySelector('.todo-main');
        mainContent.innerHTML = '<h1>Calendar</h1><p>Calendar view coming soon...</p>';
    }

    loadKanban() {
        const mainContent = document.querySelector('.todo-main');
        mainContent.innerHTML = '<h1>Kanban Board</h1><p>Kanban view coming soon...</p>';
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.todoApp = new TodoApp();
});