/**
 * Todo App Navbar JavaScript - Odoo Style
 * Handles navigation, filtering, and global interactions
 */

class TodoNavbar {
    constructor() {
        this.currentFilters = {
            search: '',
            priority: '',
            status: '',
            due: ''
        };
        this.searchTimeout = null;
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadSavedFilters();
        this.updateActiveView();
    }
    
    bindEvents() {
        // Search functionality
        const searchInput = document.getElementById('globalSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
        
        // Filter dropdown handlers
        document.addEventListener('click', (e) => {
            const filterItem = e.target.closest('[data-filter]');
            if (filterItem) {
                e.preventDefault();
                this.handleFilter(
                    filterItem.dataset.filter,
                    filterItem.dataset.value,
                    filterItem.textContent.trim()
                );
            }
        });
        
        // Refresh button
        document.addEventListener('click', (e) => {
            if (e.target.closest('[onclick="refreshData()"]')) {
                e.preventDefault();
                this.refreshData();
            }
        });
        
        // View change detection
        window.addEventListener('popstate', () => {
            this.updateActiveView();
        });
    }
    
    handleSearch(query) {
        clearTimeout(this.searchTimeout);
        
        this.searchTimeout = setTimeout(() => {
            this.currentFilters.search = query;
            this.applyFilters();
            this.saveFilters();
        }, 300); // Debounce search
    }
    
    handleFilter(filterType, value, label) {
        this.currentFilters[filterType] = value;
        this.updateFilterDisplay(filterType, label);
        this.applyFilters();
        this.saveFilters();
    }
    
    updateFilterDisplay(filterType, label) {
        // Update dropdown button text if needed
        const button = document.querySelector(`[data-bs-toggle="dropdown"][title*="${filterType}"]`);
        if (button) {
            const span = button.querySelector('span:not(.d-none)');
            if (span && label) {
                // Keep original text for "All" filters, otherwise show selected
                if (!label.includes('All') && !label.includes('Tous')) {
                    span.textContent = label;
                }
            }
        }
        
        // Show active filter indicator
        this.showActiveFilters();
    }
    
    showActiveFilters() {
        const activeFilters = Object.entries(this.currentFilters)
            .filter(([key, value]) => value !== '');
        
        // Create or update filter badges
        let filterBadges = document.querySelector('.active-filters');
        if (!filterBadges) {
            filterBadges = document.createElement('div');
            filterBadges.className = 'active-filters d-flex gap-1 flex-wrap';
            
            const searchSection = document.querySelector('.search-section');
            if (searchSection) {
                searchSection.after(filterBadges);
            }
        }
        
        if (activeFilters.length === 0) {
            filterBadges.remove();
            return;
        }
        
        filterBadges.innerHTML = activeFilters.map(([key, value]) => {
            const displayValue = this.getFilterDisplayValue(key, value);
            return `
                <span class="badge bg-primary filter-badge" data-filter="${key}">
                    ${displayValue}
                    <button class="btn-close btn-close-white ms-1" onclick="todoNavbar.removeFilter('${key}')" 
                            style="font-size: 0.6rem; width: 12px; height: 12px;"></button>
                </span>
            `;
        }).join('');
    }
    
    getFilterDisplayValue(key, value) {
        const mappings = {
            'search': `"${value}"`,
            'priority': {
                '1': '⭐ Starred',
                '0': 'Normal'
            },
            'status': {
                'open': 'Open',
                'closed': 'Closed'
            },
            'due': {
                'today': 'Due Today',
                'overdue': 'Overdue'
            }
        };
        
        if (key === 'search') {
            return mappings[key];
        }
        
        return mappings[key]?.[value] || value;
    }
    
    removeFilter(filterType) {
        this.currentFilters[filterType] = '';
        
        // Reset search input if it's search filter
        if (filterType === 'search') {
            const searchInput = document.getElementById('globalSearchInput');
            if (searchInput) {
                searchInput.value = '';
            }
        }
        
        this.applyFilters();
        this.saveFilters();
        this.showActiveFilters();
    }
    
    clearAllFilters() {
        this.currentFilters = {
            search: '',
            priority: '',
            status: '',
            due: ''
        };
        
        // Reset search input
        const searchInput = document.getElementById('globalSearchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        
        this.applyFilters();
        this.saveFilters();
        this.showActiveFilters();
        
        // Reset dropdown button texts
        document.querySelectorAll('.filters-section .dropdown-toggle span').forEach(span => {
            const button = span.closest('button');
            const title = button.getAttribute('title') || '';
            
            if (title.includes('Priority')) {
                span.textContent = 'Priority';
            } else if (title.includes('Status')) {
                span.textContent = 'Status';
            }
        });
    }
    
    applyFilters() {
        // Apply filters based on current view
        const currentView = this.getCurrentView();
        
        switch (currentView) {
            case 'kanban':
                this.applyKanbanFilters();
                break;
            case 'list':
                this.applyListFilters();
                break;
            case 'activity':
                this.applyActivityFilters();
                break;
            default:
                console.log('Applying filters:', this.currentFilters);
        }
    }
    
    applyKanbanFilters() {
        const kanbanCards = document.querySelectorAll('.kanban-card');
        
        kanbanCards.forEach(card => {
            let visible = true;
            
            // Search filter
            if (this.currentFilters.search) {
                const title = card.querySelector('.task-title')?.textContent?.toLowerCase() || '';
                visible = visible && title.includes(this.currentFilters.search.toLowerCase());
            }
            
            // Priority filter
            if (this.currentFilters.priority) {
                const isPriority = card.querySelector('.priority-indicator');
                const hasPriority = isPriority && !isPriority.classList.contains('d-none');
                
                if (this.currentFilters.priority === '1') {
                    visible = visible && hasPriority;
                } else if (this.currentFilters.priority === '0') {
                    visible = visible && !hasPriority;
                }
            }
            
            // Status filter
            if (this.currentFilters.status) {
                const isCompleted = card.querySelector('.bi-check-circle-fill');
                
                if (this.currentFilters.status === 'closed') {
                    visible = visible && isCompleted;
                } else if (this.currentFilters.status === 'open') {
                    visible = visible && !isCompleted;
                }
            }
            
            // Due date filter
            if (this.currentFilters.due) {
                const dueDateElement = card.querySelector('.due-date');
                const dueDateText = dueDateElement?.textContent?.toLowerCase() || '';
                
                if (this.currentFilters.due === 'today') {
                    visible = visible && dueDateText.includes('today');
                } else if (this.currentFilters.due === 'overdue') {
                    visible = visible && dueDateText.includes('overdue');
                }
            }
            
            // Apply visibility
            card.style.display = visible ? 'block' : 'none';
        });
        
        // Update column counts
        this.updateKanbanCounts();
    }
    
    applyListFilters() {
        // For list view, we'll reload with URL parameters
        const url = new URL(window.location);
        
        Object.entries(this.currentFilters).forEach(([key, value]) => {
            if (value) {
                url.searchParams.set(key, value);
            } else {
                url.searchParams.delete(key);
            }
        });
        
        // Only reload if URL changed
        if (url.toString() !== window.location.toString()) {
            window.location.href = url.toString();
        }
    }
    
    applyActivityFilters() {
        // Activity view filtering (basic search)
        if (this.currentFilters.search) {
            const activityItems = document.querySelectorAll('.activity-task-item, .activity-item');
            
            activityItems.forEach(item => {
                const title = item.querySelector('.task-title, .activity-title')?.textContent?.toLowerCase() || '';
                const visible = title.includes(this.currentFilters.search.toLowerCase());
                item.style.display = visible ? 'block' : 'none';
            });
        } else {
            // Show all items
            document.querySelectorAll('.activity-task-item, .activity-item').forEach(item => {
                item.style.display = 'block';
            });
        }
    }
    
    updateKanbanCounts() {
        document.querySelectorAll('.kanban-column').forEach(column => {
            const visibleCards = column.querySelectorAll('.kanban-card:not([style*="display: none"])');
            const countBadge = column.querySelector('.task-count');
            if (countBadge) {
                countBadge.textContent = visibleCards.length;
            }
        });
    }
    
    getCurrentView() {
        const path = window.location.pathname;
        if (path.includes('/kanban')) return 'kanban';
        if (path.includes('/list')) return 'list';
        if (path.includes('/activity')) return 'activity';
        return 'kanban'; // default
    }
    
    updateActiveView() {
        const currentView = this.getCurrentView();
        
        // Update navigation buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`.view-btn[href*="/${currentView}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }
    
    saveFilters() {
        try {
            localStorage.setItem('todoFilters', JSON.stringify(this.currentFilters));
        } catch (e) {
            console.warn('Could not save filters to localStorage:', e);
        }
    }
    
    loadSavedFilters() {
        try {
            const saved = localStorage.getItem('todoFilters');
            if (saved) {
                this.currentFilters = { ...this.currentFilters, ...JSON.parse(saved) };
                
                // Restore search input
                if (this.currentFilters.search) {
                    const searchInput = document.getElementById('globalSearchInput');
                    if (searchInput) {
                        searchInput.value = this.currentFilters.search;
                    }
                }
                
                this.applyFilters();
                this.showActiveFilters();
            }
        } catch (e) {
            console.warn('Could not load filters from localStorage:', e);
        }
    }
    
    refreshData() {
        // Show loading state
        document.querySelector('.todo-navbar')?.classList.add('navbar-loading');
        
        // Emit refresh event
        document.dispatchEvent(new CustomEvent('todoRefresh'));
        
        // For now, just reload the page
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }
}

// Global functions for button clicks
window.createNewTask = function() {
    // Check if we're in kanban view
    const currentView = todoNavbar ? todoNavbar.getCurrentView() : 'kanban';
    
    if (currentView === 'kanban') {
        // Use existing kanban functionality to add task directly to first column
        const firstColumn = document.querySelector('.kanban-column[data-stage-id]');
        if (firstColumn) {
            const stageId = firstColumn.getAttribute('data-stage-id');
            const addBtn = firstColumn.querySelector('.add-task-btn');
            
            // Use the existing TodoKanban showQuickAddForm method if available
            if (window.todoKanban && addBtn) {
                window.todoKanban.showQuickAddForm(stageId, addBtn);
            } else {
                // Fallback to the original addTaskToStage function
                window.addTaskToStage(stageId);
            }
        }
    } else if (currentView === 'list') {
        // For list view, redirect to create page or show modal
        window.location.href = '/todo/task/new/';
    } else {
        // For activity or other views, show the modal
        const modal = document.getElementById('quickTaskModal');
        if (modal) {
            new bootstrap.Modal(modal).show();
        }
    }
};

// Helper functions for other views

window.exportTasks = function() {
    console.log('Exporting tasks...');
    // Implementation would go here
};

window.importTasks = function() {
    console.log('Importing tasks...');
    // Implementation would go here
};

window.refreshData = function() {
    todoNavbar.refreshData();
};

// List view specific functions
window.selectProjectFilter = function(value, text) {
    document.getElementById('projectFilterText').textContent = text;
    // Apply project filter logic here
    console.log('Project filter:', value);
};

window.selectStageFilter = function(value, text) {
    document.getElementById('stageFilterText').textContent = text;
    // Apply stage filter logic here
    console.log('Stage filter:', value);
};

window.showBulkActionsMenu = function() {
    if (window.todoList && typeof window.todoList.showBulkActionsMenu === 'function') {
        window.todoList.showBulkActionsMenu();
    }
};

// Initialize navbar when DOM is loaded
let todoNavbar;
document.addEventListener('DOMContentLoaded', function() {
    todoNavbar = new TodoNavbar();
    
    // Make it globally accessible for onclick handlers
    window.todoNavbar = todoNavbar;
});