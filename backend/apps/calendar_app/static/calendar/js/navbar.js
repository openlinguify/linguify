/**
 * Calendar App Navigation JavaScript
 * Gestion des navbars principale et contextuelle avec filtres avancés
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('[Calendar] Navbar functionality loading...');
    
    // App navbar functionality
    initAppNavbar();
    
    // Context navbar functionality  
    initContextNavbar();
    
    // Advanced filters functionality
    initCalendarFilters();
    
    console.log('[Calendar] Navbar functionality loaded');
});

/**
 * Initialize main app navbar functionality
 */
function initAppNavbar() {
    // Refresh button functionality
    const refreshBtn = document.getElementById('refreshCalendar');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            console.log('[Calendar] Refresh button clicked');
            
            // Add visual feedback
            const originalIcon = this.querySelector('i');
            const originalClass = originalIcon.className;
            
            // Animate refresh icon
            originalIcon.className = 'bi bi-arrow-clockwise me-1';
            originalIcon.classList.add('spinning');
            
            // Disable button during refresh
            this.disabled = true;
            
            // Perform refresh
            refreshCalendarData().then(() => {
                if (window.notificationService) {
                    window.notificationService.success('📅 Calendrier actualisé');
                } else {
                    console.log('Calendar refreshed successfully');
                }
            }).catch((error) => {
                console.error('Calendar refresh failed:', error);
                if (window.notificationService) {
                    window.notificationService.error('❌ Erreur lors de l\'actualisation');
                }
            }).finally(() => {
                // Reset icon and button state
                setTimeout(() => {
                    originalIcon.classList.remove('spinning');
                    originalIcon.className = originalClass;
                    this.disabled = false;
                }, 1000);
            });
        });
    }
}

/**
 * Refresh calendar data
 */
async function refreshCalendarData() {
    return new Promise((resolve, reject) => {
        if (window.calendar && window.calendar.refetchEvents) {
            window.calendar.refetchEvents();
            resolve();
        } else if (window.location.reload) {
            // Fallback to page reload
            setTimeout(() => {
                window.location.reload();
            }, 500);
            resolve();
        } else {
            reject(new Error('No refresh method available'));
        }
    });
}

/**
 * Initialize context navbar functionality (view switchers, navigation)
 */
function initContextNavbar() {
    // Navigation buttons
    const prevBtn = document.getElementById('prevPeriod');
    const nextBtn = document.getElementById('nextPeriod');
    const todayBtn = document.getElementById('todayBtn');
    
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            console.log('[Calendar] Previous period clicked');
            if (window.calendar && window.calendar.prev) {
                window.calendar.prev();
                updatePeriodTitle();
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            console.log('[Calendar] Next period clicked');
            if (window.calendar && window.calendar.next) {
                window.calendar.next();
                updatePeriodTitle();
            }
        });
    }
    
    if (todayBtn) {
        todayBtn.addEventListener('click', function() {
            console.log('[Calendar] Today button clicked');
            if (window.calendar && window.calendar.today) {
                window.calendar.today();
                updatePeriodTitle();
            }
        });
    }
    
    // View switcher buttons
    const viewBtns = document.querySelectorAll('[data-view]');
    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            console.log('[Calendar] View button clicked:', this.dataset.view);
            
            // Update active state
            viewBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Change calendar view
            const view = this.dataset.view;
            if (window.calendar && window.calendar.changeView) {
                changeCalendarView(view);
                updatePeriodTitle();
            }
        });
    });
}

/**
 * Change calendar view based on selected view type
 * @param {string} viewType - month, week, or day
 */
function changeCalendarView(viewType) {
    if (!window.calendar || !window.calendar.changeView) {
        console.warn('[Calendar] Calendar instance not available for view change');
        return;
    }
    
    switch (viewType) {
        case 'month':
            window.calendar.changeView('dayGridMonth');
            break;
        case 'week':
            window.calendar.changeView('timeGridWeek');
            break;
        case 'day':
            window.calendar.changeView('timeGridDay');
            break;
        default:
            console.warn('[Calendar] Unknown view type:', viewType);
    }
}

/**
 * Update the period title in the context navbar
 */
function updatePeriodTitle() {
    const titleElement = document.getElementById('currentPeriod');
    if (!titleElement) return;
    
    let currentDate;
    if (window.calendar && window.calendar.getDate) {
        currentDate = window.calendar.getDate();
    } else if (window.calendar && window.calendar.currentDate) {
        currentDate = window.calendar.currentDate;
    } else {
        currentDate = new Date();
    }
    
    // Format date based on current view
    const activeViewBtn = document.querySelector('[data-view].active');
    const viewType = activeViewBtn ? activeViewBtn.dataset.view : 'month';
    
    let formattedTitle;
    switch (viewType) {
        case 'day':
            formattedTitle = currentDate.toLocaleDateString('fr-FR', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
            break;
        case 'week':
            // Calculate week start and end
            const startOfWeek = new Date(currentDate);
            startOfWeek.setDate(currentDate.getDate() - currentDate.getDay() + 1);
            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(startOfWeek.getDate() + 6);
            
            formattedTitle = `${startOfWeek.getDate()} - ${endOfWeek.getDate()} ${endOfWeek.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}`;
            break;
        case 'month':
        default:
            formattedTitle = currentDate.toLocaleDateString('fr-FR', { 
                year: 'numeric', 
                month: 'long' 
            });
            break;
    }
    
    titleElement.textContent = formattedTitle;
}

/**
 * Initialize calendar filters functionality
 */
function initCalendarFilters() {
    console.log('[Calendar] Initializing filters...');
    
    // Search input
    const searchInput = document.getElementById('calendarSearchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterCalendarEvents();
            }, 300); // Debounce search
        });
    }
    
    // Calendar type filter
    const typeFilter = document.getElementById('calendarTypeFilter');
    if (typeFilter) {
        typeFilter.addEventListener('change', function() {
            filterCalendarEvents();
        });
    }
    
    // View filter with calendar view switching
    const viewFilter = document.getElementById('calendarViewFilter');
    if (viewFilter) {
        // Set current view on load
        const currentView = getCurrentCalendarView();
        if (currentView) {
            viewFilter.value = currentView;
        }
        
        viewFilter.addEventListener('change', function() {
            const selectedView = this.value;
            const viewType = this.options[this.selectedIndex].dataset.view;
            
            console.log('[Calendar] View changed to:', selectedView, 'Type:', viewType);
            
            if (viewType === 'agenda') {
                // Navigate to agenda page
                window.location.href = '/calendar/agenda/';
            } else if (viewType && window.calendar) {
                // Change calendar view
                changeCalendarView(viewType);
            }
        });
    }
}

/**
 * Filter calendar events based on current filter values
 */
function filterCalendarEvents() {
    const searchTerm = document.getElementById('calendarSearchInput')?.value.toLowerCase() || '';
    const typeFilter = document.getElementById('calendarTypeFilter')?.value || '';
    
    console.log('[Calendar] Filtering events:', { searchTerm, typeFilter });
    
    if (window.calendar && window.calendar.getEvents) {
        const events = window.calendar.getEvents();
        
        events.forEach(event => {
            let shouldShow = true;
            
            // Search filter
            if (searchTerm) {
                const title = event.title?.toLowerCase() || '';
                const description = event.extendedProps?.description?.toLowerCase() || '';
                shouldShow = shouldShow && (title.includes(searchTerm) || description.includes(searchTerm));
            }
            
            // Type filter
            if (typeFilter) {
                const eventType = event.extendedProps?.type || event.extendedProps?.calendar_type || 'personal';
                shouldShow = shouldShow && (eventType === typeFilter);
            }
            
            // Show/hide event
            if (shouldShow) {
                event.setProp('display', 'auto');
            } else {
                event.setProp('display', 'none');
            }
        });
        
        // Show filter status
        const filteredCount = events.filter(e => e.display !== 'none').length;
        const totalCount = events.length;
        
        if (window.notificationService && (searchTerm || typeFilter)) {
            window.notificationService.info(`📊 ${filteredCount}/${totalCount} événements affichés`);
        }
    }
}

/**
 * Get current calendar view type
 */
function getCurrentCalendarView() {
    if (window.calendar && window.calendar.view) {
        const view = window.calendar.view.type;
        if (view.includes('month')) return 'month';
        if (view.includes('week')) return 'week';
        if (view.includes('day')) return 'day';
    }
    
    // Check URL path
    const path = window.location.pathname;
    if (path.includes('/agenda/')) return 'agenda';
    if (path.includes('/week/')) return 'week';
    if (path.includes('/day/')) return 'day';
    
    return 'month'; // Default
}

/**
 * Reset all filters
 */
function resetCalendarFilters() {
    const searchInput = document.getElementById('calendarSearchInput');
    const typeFilter = document.getElementById('calendarTypeFilter');
    
    if (searchInput) searchInput.value = '';
    if (typeFilter) typeFilter.value = '';
    
    filterCalendarEvents();
    
    if (window.notificationService) {
        window.notificationService.info('🔄 Filtres réinitialisés');
    }
}

/**
 * Get filter status for display
 */
function getFilterStatus() {
    const searchTerm = document.getElementById('calendarSearchInput')?.value || '';
    const typeFilter = document.getElementById('calendarTypeFilter')?.value || '';
    
    const activeFilters = [];
    if (searchTerm) activeFilters.push(`recherche: "${searchTerm}"`);
    if (typeFilter) activeFilters.push(`type: ${typeFilter}`);
    
    return {
        hasFilters: activeFilters.length > 0,
        description: activeFilters.join(', ')
    };
}

// Export functions for potential external use
window.CalendarNavbar = {
    initAppNavbar,
    initContextNavbar,
    initCalendarFilters,
    changeCalendarView,
    updatePeriodTitle,
    filterCalendarEvents,
    resetCalendarFilters,
    getFilterStatus
};