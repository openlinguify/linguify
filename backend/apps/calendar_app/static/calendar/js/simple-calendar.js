/**
 * Simple Calendar Implementation
 * Fallback when FullCalendar fails to load
 */

class SimpleCalendar {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            initialView: 'dayGridMonth',
            locale: 'fr',
            events: [],
            ...options
        };
        this.currentDate = new Date();
        this.events = [];
        this.init();
    }
    
    init() {
        this.render();
        this.loadEvents();
    }
    
    render() {
        const html = `
            <div class="simple-calendar">
                <div class="calendar-header">
                    <button class="btn btn-sm btn-outline-secondary" id="prevMonth">
                        <i class="bi bi-chevron-left"></i>
                    </button>
                    <h4 class="month-title">${this.getMonthTitle()}</h4>
                    <button class="btn btn-sm btn-outline-secondary" id="nextMonth">
                        <i class="bi bi-chevron-right"></i>
                    </button>
                </div>
                <div class="calendar-grid">
                    ${this.renderWeekHeader()}
                    ${this.renderDays()}
                </div>
            </div>
        `;
        
        this.element.innerHTML = html;
        this.attachEvents();
    }
    
    renderWeekHeader() {
        const days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
        return `
            <div class="week-header">
                ${days.map(day => `<div class="day-header">${day}</div>`).join('')}
            </div>
        `;
    }
    
    renderDays() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        
        // Adjust to start on Monday
        const dayOfWeek = (firstDay.getDay() + 6) % 7;
        startDate.setDate(firstDay.getDate() - dayOfWeek);
        
        let html = '';
        let currentWeek = '';
        const today = new Date();
        
        for (let i = 0; i < 42; i++) {
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);
            
            const isCurrentMonth = date.getMonth() === month;
            const isToday = date.toDateString() === today.toDateString();
            
            let classes = 'calendar-day';
            if (!isCurrentMonth) classes += ' other-month';
            if (isToday) classes += ' today';
            
            const events = this.getEventsForDate(date);
            
            currentWeek += `
                <div class="${classes}" data-date="${date.toISOString().split('T')[0]}">
                    <div class="day-number">${date.getDate()}</div>
                    <div class="day-events">
                        ${events.map(event => `
                            <div class="event-dot" style="background-color: ${event.color || '#667eea'}" 
                                 title="${event.title}"></div>
                        `).join('')}
                    </div>
                </div>
            `;
            
            if ((i + 1) % 7 === 0) {
                html += `<div class="calendar-week">${currentWeek}</div>`;
                currentWeek = '';
            }
        }
        
        return html;
    }
    
    getMonthTitle() {
        const months = [
            'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ];
        return `${months[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
    }
    
    getEventsForDate(date) {
        const dateStr = date.toISOString().split('T')[0];
        return this.events.filter(event => {
            const eventDate = new Date(event.start).toISOString().split('T')[0];
            return eventDate === dateStr;
        });
    }
    
    attachEvents() {
        const prevBtn = this.element.querySelector('#prevMonth');
        const nextBtn = this.element.querySelector('#nextMonth');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prev());
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.next());
        }
        
        // Add click handlers for days
        this.element.querySelectorAll('.calendar-day').forEach(day => {
            day.addEventListener('click', (e) => {
                const date = e.currentTarget.dataset.date;
                this.onDateClick(date);
            });
        });
    }
    
    prev() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.render();
        this.updateTitle();
    }
    
    next() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.render();
        this.updateTitle();
    }
    
    today() {
        this.currentDate = new Date();
        this.render();
        this.updateTitle();
    }
    
    updateTitle() {
        // Update external title if it exists
        const titleElement = document.getElementById('calendarTitle');
        if (titleElement) {
            titleElement.textContent = this.getMonthTitle();
        }
    }
    
    onDateClick(date) {
        console.log('Date clicked:', date);
        // Trigger modal or event creation
        const modal = document.getElementById('createEventModal');
        if (modal) {
            const startInput = document.getElementById('eventStart');
            const endInput = document.getElementById('eventEnd');
            
            if (startInput && endInput) {
                startInput.value = date + 'T09:00';
                endInput.value = date + 'T10:00';
            }
            
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        }
    }
    
    async loadEvents() {
        try {
            const response = await fetch(this.options.events);
            if (response.ok) {
                this.events = await response.json();
                this.render();
            }
        } catch (error) {
            console.warn('Could not load events:', error);
        }
    }
    
    addEvent(event) {
        this.events.push(event);
        this.render();
    }
    
    refetchEvents() {
        this.loadEvents();
    }
    
    changeView(view) {
        console.log('View changed to:', view);
        // For now, only month view is supported
    }
}

// CSS for simple calendar
const calendarCSS = `
<style>
.simple-calendar {
    background: white;
    border-radius: 8px;
    overflow: hidden;
}

.calendar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
}

.month-title {
    margin: 0;
    font-weight: 600;
    color: #495057;
}

.calendar-grid {
    min-height: 400px;
}

.week-header {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    background: #e9ecef;
}

.day-header {
    padding: 0.75rem;
    text-align: center;
    font-weight: 600;
    color: #6c757d;
    border-right: 1px solid #dee2e6;
}

.calendar-week {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    border-bottom: 1px solid #dee2e6;
}

.calendar-day {
    min-height: 80px;
    padding: 0.5rem;
    border-right: 1px solid #dee2e6;
    cursor: pointer;
    transition: background-color 0.2s;
    position: relative;
}

.calendar-day:hover {
    background-color: #f8f9fa;
}

.calendar-day.today {
    background-color: rgba(102, 126, 234, 0.1);
    border: 2px solid #667eea;
}

.calendar-day.other-month {
    background-color: #fafafa;
    color: #adb5bd;
}

.day-number {
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.day-events {
    display: flex;
    flex-wrap: wrap;
    gap: 2px;
}

.event-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
</style>
`;

// Add CSS to head
if (!document.getElementById('simple-calendar-css')) {
    const styleElement = document.createElement('div');
    styleElement.id = 'simple-calendar-css';
    styleElement.innerHTML = calendarCSS;
    document.head.appendChild(styleElement);
}

// Export for global use
window.SimpleCalendar = SimpleCalendar;