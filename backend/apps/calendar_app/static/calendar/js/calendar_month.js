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
                
                // Get events for this date
                const dayEvents = getDayEvents(date);
                let eventsHtml = '';
                
                if (dayEvents.length > 0) {
                    dayEvents.slice(0, 3).forEach(event => { // Show max 3 events
                        const eventColor = event.backgroundColor || '#007bff';
                        const eventTitle = event.title.length > 15 ? event.title.substring(0, 15) + '...' : event.title;
                        eventsHtml += `
                            <div style="
                                background: ${eventColor}; 
                                color: white; 
                                font-size: 0.7rem; 
                                padding: 1px 4px; 
                                margin-bottom: 1px; 
                                border-radius: 2px; 
                                cursor: pointer;
                                overflow: hidden;
                                white-space: nowrap;
                                text-overflow: ellipsis;
                            " onclick="event.stopPropagation(); showEventDetails('${event.id}')" title="${event.title}">
                                ${eventTitle}
                            </div>
                        `;
                    });
                    
                    if (dayEvents.length > 3) {
                        eventsHtml += `
                            <div style="
                                font-size: 0.6rem; 
                                color: #6c757d; 
                                text-align: center;
                                margin-top: 2px;
                            ">
                                +${dayEvents.length - 3} plus
                            </div>
                        `;
                    }
                }
                
                html += `
                    <div style="${style}" onmouseover="this.style.backgroundColor='#f8f9fa'" onmouseout="this.style.backgroundColor='${isToday ? 'rgba(102, 126, 234, 0.1)' : (isCurrentMonth ? 'white' : '#fafafa')}'" onclick="handleDateClick('${localDateString}')">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">${date.getDate()}</div>
                        ${eventsHtml}
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
        events: [],
        prev: function() {
            currentDate.setMonth(currentDate.getMonth() - 1);
            loadAndRenderCalendar();
            updateCalendarTitle();
        },
        next: function() {
            currentDate.setMonth(currentDate.getMonth() + 1);
            loadAndRenderCalendar();
            updateCalendarTitle();
        },
        today: function() {
            currentDate.setTime(new Date().getTime());
            loadAndRenderCalendar();
            updateCalendarTitle();
        },
        refetchEvents: function() {
            console.log('[Calendar] Refresh requested');
            loadAndRenderCalendar();
        },
        getEvents: function() {
            return this.events;
        }
    };
    
    // Load events and render calendar
    async function loadAndRenderCalendar() {
        try {
            const events = await loadCalendarEvents();
            window.calendar.events = events;
            calendarEl.innerHTML = renderSimpleCalendar();
        } catch (error) {
            console.error('[Calendar] Error loading events:', error);
            calendarEl.innerHTML = renderSimpleCalendar(); // Render without events
        }
    }
    
    calendarInstance = window.calendar;
    console.log('[Calendar] Simple calendar initialized successfully!');
    
    // Update the period title in navbar
    updateCalendarTitle();
    
    // Load events initially
    loadAndRenderCalendar();
}

/**
 * Load calendar events from the API
 */
async function loadCalendarEvents() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // Calculate date range for the month view (including prev/next month days)
    const startDate = new Date(year, month, 1);
    startDate.setDate(startDate.getDate() - startDate.getDay() - 7); // Start from week before
    
    const endDate = new Date(year, month + 1, 0);
    endDate.setDate(endDate.getDate() + (7 - endDate.getDay()) + 7); // End week after
    
    const start = startDate.toISOString();
    const end = endDate.toISOString();
    
    console.log('[Calendar] Loading events for range:', start, 'to', end);
    
    try {
        const response = await fetch(`/calendar/json/?start=${start}&end=${end}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const events = await response.json();
        console.log('[Calendar] Loaded events:', events);
        return events;
        
    } catch (error) {
        console.error('[Calendar] Error loading events:', error);
        return [];
    }
}

/**
 * Get CSRF token for API requests
 */
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.querySelector('meta[name="csrf-token"]')?.content ||
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
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

/**
 * Get events for a specific date
 * @param {Date} date - The date to get events for
 */
function getDayEvents(date) {
    if (!window.calendar.events) return [];
    
    const targetDate = date.toISOString().split('T')[0];
    
    return window.calendar.events.filter(event => {
        const eventStart = new Date(event.start).toISOString().split('T')[0];
        const eventEnd = new Date(event.end).toISOString().split('T')[0];
        
        // Check if event starts on this date or spans across this date
        return eventStart === targetDate || (eventStart <= targetDate && eventEnd >= targetDate);
    });
}

/**
 * Show event details modal or popup
 * @param {string} eventId - ID of the event to show
 */
function showEventDetails(eventId) {
    const event = window.calendar.events.find(e => e.id === eventId);
    if (!event) return;
    
    console.log('[Calendar] Showing event details for:', event);
    
    // Create a simple modal or alert for now
    const details = `
📅 ${event.title}
⏰ ${formatEventTime(event)}
${event.extendedProps.location ? '📍 ' + event.extendedProps.location : ''}
${event.extendedProps.description ? '📝 ' + event.extendedProps.description : ''}
👤 ${event.extendedProps.organizer || 'Vous'}
    `.trim();
    
    if (window.notificationService) {
        window.notificationService.info(details.replace(/\n/g, '<br>'));
    } else {
        alert(details);
    }
}

/**
 * Format event time for display
 * @param {Object} event - Event object
 */
function formatEventTime(event) {
    const start = new Date(event.start);
    const end = new Date(event.end);
    
    if (event.allDay) {
        return 'Toute la journée';
    }
    
    const startTime = start.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    const endTime = end.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    
    if (start.toDateString() === end.toDateString()) {
        return `${startTime} - ${endTime}`;
    } else {
        return `${start.toLocaleDateString('fr-FR')} ${startTime} - ${end.toLocaleDateString('fr-FR')} ${endTime}`;
    }
}

// Export functions for global use
window.CalendarMonth = {
    forceInitializeCalendar,
    updateCalendarTitle,
    handleDateClick,
    getDayEvents,
    showEventDetails,
    formatEventTime
};