/**
 * Calendar Month View JavaScript
 * Fonctionnalités spécifiques à la vue mensuelle du calendrier
 */

console.log('[Calendar] Month view script loaded');

// Variable globale pour l'instance du calendrier
let calendarInstance = null;

/**
 * Force initialize calendar when DOM is ready
 */
function forceInitializeCalendar() {
    console.log('[Calendar] FORCE Initialize starting...');
    
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) {
        console.error('[Calendar] Calendar element not found!');
        return;
    }
    
    console.log('[Calendar] Calendar element found, creating simple calendar...');
    
    // Update debug info
    const typeEl = document.getElementById('calendar-type');
    if (typeEl) typeEl.textContent = 'SimpleCalendar (Inline)';
    
    const timeEl = document.getElementById('debug-time');
    if (timeEl) timeEl.textContent = new Date().toLocaleString();
    
    // Simple calendar implementation inline
    const currentDate = new Date();
    
    function renderSimpleCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        const today = new Date();
        
        const monthNames = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                           'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
        
        const firstDay = new Date(year, month, 1);
        const startDate = new Date(firstDay);
        
        // Adjust to start on Monday
        const dayOfWeek = (firstDay.getDay() + 6) % 7;
        startDate.setDate(firstDay.getDate() - dayOfWeek);
        
        let html = `
            <div style="background: white; border-radius: 8px; overflow: hidden;">
                <div style="display: grid; grid-template-columns: repeat(7, 1fr); background: #e9ecef;">
                    <div style="padding: 0.75rem; text-align: center; font-weight: 600; color: #6c757d; border-right: 1px solid #dee2e6;">Lun</div>
                    <div style="padding: 0.75rem; text-align: center; font-weight: 600; color: #6c757d; border-right: 1px solid #dee2e6;">Mar</div>
                    <div style="padding: 0.75rem; text-align: center; font-weight: 600; color: #6c757d; border-right: 1px solid #dee2e6;">Mer</div>
                    <div style="padding: 0.75rem; text-align: center; font-weight: 600; color: #6c757d; border-right: 1px solid #dee2e6;">Jeu</div>
                    <div style="padding: 0.75rem; text-align: center; font-weight: 600; color: #6c757d; border-right: 1px solid #dee2e6;">Ven</div>
                    <div style="padding: 0.75rem; text-align: center; font-weight: 600; color: #6c757d; border-right: 1px solid #dee2e6;">Sam</div>
                    <div style="padding: 0.75rem; text-align: center; font-weight: 600; color: #6c757d;">Dim</div>
                </div>
        `;
        
        for (let week = 0; week < 6; week++) {
            html += '<div style="display: grid; grid-template-columns: repeat(7, 1fr); border-bottom: 1px solid #dee2e6;">';
            for (let day = 0; day < 7; day++) {
                const date = new Date(startDate);
                date.setDate(startDate.getDate() + (week * 7) + day);
                
                const isCurrentMonth = date.getMonth() === month;
                const isToday = date.toDateString() === today.toDateString();
                
                let style = 'min-height: 80px; padding: 0.5rem; border-right: 1px solid #dee2e6; cursor: pointer; transition: background-color 0.2s;';
                if (!isCurrentMonth) style += ' background-color: #fafafa; color: #adb5bd;';
                if (isToday) style += ' background-color: rgba(102, 126, 234, 0.1); border: 2px solid #667eea;';
                
                // Format date correctly for local timezone
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const localDateString = `${year}-${month}-${day}`;
                
                html += `
                    <div style="${style}" onmouseover="this.style.backgroundColor='#f8f9fa'" onmouseout="this.style.backgroundColor='${isToday ? 'rgba(102, 126, 234, 0.1)' : (isCurrentMonth ? 'white' : '#fafafa')}'" onclick="handleDateClick('${localDateString}')">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">${date.getDate()}</div>
                    </div>
                `;
            }
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    }
    
    // Remove debug content
    const debugElements = calendarEl.parentElement.querySelectorAll('.calendar-header-debug, .calendar-debug-info');
    debugElements.forEach(el => el.remove());
    
    // Render calendar
    calendarEl.innerHTML = renderSimpleCalendar();
    
    // Create global calendar object
    window.calendar = {
        currentDate: currentDate,
        prev: function() {
            currentDate.setMonth(currentDate.getMonth() - 1);
            calendarEl.innerHTML = renderSimpleCalendar();
            updateCalendarTitle();
        },
        next: function() {
            currentDate.setMonth(currentDate.getMonth() + 1);
            calendarEl.innerHTML = renderSimpleCalendar();
            updateCalendarTitle();
        },
        today: function() {
            currentDate.setTime(new Date().getTime());
            calendarEl.innerHTML = renderSimpleCalendar();
            updateCalendarTitle();
        },
        refetchEvents: function() {
            console.log('[Calendar] Refresh requested');
            // Could implement actual event fetching here
        }
    };
    
    calendarInstance = window.calendar;
    console.log('[Calendar] Simple calendar initialized successfully!');
    
    // Update the period title in navbar
    updateCalendarTitle();
}

/**
 * Update calendar title in the context navbar
 */
function updateCalendarTitle() {
    const titleElement = document.getElementById('currentPeriod');
    if (titleElement && window.calendar && window.calendar.currentDate) {
        const monthNames = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                           'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
        const title = monthNames[window.calendar.currentDate.getMonth()] + ' ' + window.calendar.currentDate.getFullYear();
        titleElement.textContent = title;
    }
}

/**
 * Handle date click events
 * @param {string} date - Date in YYYY-MM-DD format (local timezone)
 */
function handleDateClick(date) {
    console.log('[Calendar] Date clicked:', date);
    
    const modal = document.getElementById('createEventModal');
    if (modal) {
        const startInput = document.getElementById('eventStart');
        const endInput = document.getElementById('eventEnd');
        
        if (startInput && endInput) {
            // Date is already in YYYY-MM-DD format, just add time
            startInput.value = date + 'T09:00';
            endInput.value = date + 'T10:00';
            console.log('[Calendar] Form dates set:', startInput.value, endInput.value);
        }
        
        if (typeof bootstrap !== 'undefined') {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Force execution immediately if DOM is already loaded
    if (document.readyState !== 'loading') {
        forceInitializeCalendar();
    } else {
        setTimeout(forceInitializeCalendar, 100);
    }
});

// Backup execution
setTimeout(() => {
    if (!window.calendar) {
        console.log('[Calendar] Backup initialization...');
        forceInitializeCalendar();
    }
}, 1000);

// Export functions for global use
window.CalendarMonth = {
    forceInitializeCalendar,
    updateCalendarTitle,
    handleDateClick
};