/**
 * Calendar App Navigation JavaScript
 * Gestion des navbars principale et contextuelle
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('[Calendar] Navbar functionality loading...');
    
    // App navbar functionality
    initAppNavbar();
    
    // Context navbar functionality  
    initContextNavbar();
    
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
            if (window.calendar && window.calendar.refetchEvents) {
                window.calendar.refetchEvents();
            } else {
                location.reload();
            }
            if (window.notificationService) {
                window.notificationService.info('Calendar refreshed');
            }
        });
    }
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

// Export functions for potential external use
window.CalendarNavbar = {
    initAppNavbar,
    initContextNavbar,
    changeCalendarView,
    updatePeriodTitle
};