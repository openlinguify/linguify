/**
 * Revision Statistics Dashboard JavaScript
 * Handles all functionality for the statistics dashboard page
 */

// Global variables for statistics
let currentPeriod = 7;
let studyActivityChart = null;
let performanceChart = null;

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Stats dashboard DOM loaded, initializing...');
    
    // Test if DOM elements exist
    const testElement = document.getElementById('totalDecks');
    console.log('totalDecks element found:', !!testElement);
    
    // Initialize Chart.js
    initializeChartJS();
    
    // Load all statistics data
    loadCollectionOverview();
    loadStatistics();
    initializeCharts();
    loadDeckStats();
    loadRecentActivity();
    loadStudyGoals();
    
    // Set up event listeners
    setupEventListeners();
});

// ===== CHART.JS INITIALIZATION =====
/**
 * Try to load Chart.js from CDN, but continue without it if it fails
 */
function initializeChartJS() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    }).then(() => {
        console.log('✅ Chart.js loaded successfully');
    }).catch(() => {
        console.log('⚠️ Chart.js failed to load, continuing without charts');
    });
}

// ===== EVENT LISTENERS =====
/**
 * Set up all event listeners for the statistics dashboard
 */
function setupEventListeners() {
    // Period filter handlers
    document.querySelectorAll('.period-filter').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            currentPeriod = parseInt(this.dataset.period);
            const currentPeriodElement = document.getElementById('currentPeriod');
            if (currentPeriodElement) {
                currentPeriodElement.textContent = this.textContent;
            }
            loadStatistics();
        });
    });
    
    // Stats time range selector (navbar)
    const statsTimeRange = document.getElementById('statsTimeRange');
    if (statsTimeRange) {
        statsTimeRange.addEventListener('change', function(e) {
            currentPeriod = parseInt(e.target.value);
            console.log(`📊 Time period changed to: ${currentPeriod} days`);
            loadStatistics();
        });
    }
}

// ===== DATA LOADING FUNCTIONS =====
/**
 * Load basic collection overview statistics
 */
function loadCollectionOverview() {
    console.log('📊 Loading collection overview...');
    
    fetch('/api/v1/revision/decks/stats/')
        .then(response => response.json())
        .then(data => {
            console.log('Collection overview data:', data);
            
            // Update collection overview cards
            const totalDecks = data.total_decks || 0;
            const totalCards = data.total_cards || 0;
            const totalLearned = data.total_learned || 0;
            const completionPercentage = data.completion_percentage || 0;
            
            console.log('Parsed values:', { totalDecks, totalCards, totalLearned, completionPercentage });
            
            // Update DOM elements
            updateElement('totalDecks', totalDecks);
            updateElement('totalCards', totalCards);
            updateElement('totalLearned', totalLearned);
            updateElement('completionRate', completionPercentage + '%');
            
            // Update progress bar
            const progressBar = document.getElementById('completionProgress');
            if (progressBar) {
                progressBar.style.width = completionPercentage + '%';
            }
        })
        .catch(error => {
            console.error('❌ Error loading collection overview:', error);
            // Show error in UI
            updateElement('totalDecks', 'Error');
            updateElement('totalCards', 'Error');
            updateElement('totalLearned', 'Error');
            updateElement('completionRate', 'Error');
        });
}

/**
 * Load detailed statistics for the selected period
 */
function loadStatistics() {
    console.log(`📊 Loading statistics for ${currentPeriod} days...`);
    
    fetch(`/api/v1/revision/stats/?period=${currentPeriod}`)
        .then(response => response.json())
        .then(data => {
            console.log('Statistics data:', data);
            
            // Update overview cards
            updateElement('totalStudiedCards', data.total_studied_cards || 0);
            updateElement('accuracyRate', (data.accuracy_rate || 0) + '%');
            updateElement('studyTime', formatTime(data.total_study_time || 0));
            updateElement('currentStreak', data.current_streak || 0);
            
            // Update progress bars
            updateProgressBar('studiedCardsProgress', Math.min((data.total_studied_cards || 0) / 100 * 100, 100));
            updateProgressBar('accuracyProgress', data.accuracy_rate || 0);
            updateProgressBar('studyTimeProgress', Math.min((data.total_study_time || 0) / 600 * 100, 100));
            updateProgressBar('streakProgress', Math.min((data.current_streak || 0) / 30 * 100, 100));
            
            // Update charts
            updateStudyActivityChart(data.daily_activity || []);
            updatePerformanceChart(data.performance_breakdown || {});
        })
        .catch(error => {
            console.error('❌ Error loading statistics:', error);
            if (window.notificationService) {
                window.notificationService.error('Error loading statistics');
            }
        });
}

/**
 * Load deck performance statistics
 */
function loadDeckStats() {
    console.log('📊 Loading deck statistics...');
    
    fetch('/api/v1/revision/decks/performance/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('deckStatsTable');
            if (!tbody) return;
            
            tbody.innerHTML = '';
            
            if (data.results && data.results.length > 0) {
                data.results.forEach(deck => {
                    const accuracyClass = deck.accuracy >= 80 ? 'linguify-success-bg' : 
                                        deck.accuracy >= 60 ? 'linguify-warning-bg' : 'linguify-error-bg';
                    
                    tbody.innerHTML += `
                        <tr>
                            <td>
                                <strong>${deck.name}</strong>
                                <br><small class="text-muted">${deck.description || 'No description'}</small>
                            </td>
                            <td>${deck.cards_count}</td>
                            <td>
                                <div class="d-flex align-items-center">
                                    <span class="me-2">${deck.mastered_cards}/${deck.cards_count}</span>
                                    <div class="progress flex-grow-1" style="height: 4px;">
                                        <div class="progress-bar" style="width: ${deck.mastery_percentage}%"></div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <span class="badge ${accuracyClass} text-white">
                                    ${deck.accuracy}%
                                </span>
                            </td>
                        </tr>
                    `;
                });
            } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center py-3 text-muted">
                            No deck statistics available
                        </td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('❌ Error loading deck stats:', error);
            const tbody = document.getElementById('deckStatsTable');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center py-3 text-danger">
                            Error loading deck statistics
                        </td>
                    </tr>
                `;
            }
        });
}

/**
 * Load recent study activity
 */
function loadRecentActivity() {
    console.log('📊 Loading recent activity...');
    
    fetch('/api/v1/revision/sessions/recent/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('recentActivity');
            if (!container) return;
            
            container.innerHTML = '';
            
            if (data.results && data.results.length > 0) {
                data.results.forEach(session => {
                    const timeAgo = getTimeAgo(new Date(session.created_at));
                    container.innerHTML += `
                        <div class="list-group-item">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">${session.deck_name}</h6>
                                <small>${timeAgo}</small>
                            </div>
                            <p class="mb-1">${session.mode} - ${session.cards_studied} cards studied</p>
                            <small>Accuracy: ${session.accuracy}%</small>
                        </div>
                    `;
                });
            } else {
                container.innerHTML = `
                    <div class="list-group-item text-center py-3 text-muted">
                        No recent activity found
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('❌ Error loading recent activity:', error);
            const container = document.getElementById('recentActivity');
            if (container) {
                container.innerHTML = `
                    <div class="list-group-item text-center py-3 text-danger">
                        Error loading recent activity
                    </div>
                `;
            }
        });
}

/**
 * Load study goals progress
 */
function loadStudyGoals() {
    console.log('📊 Loading study goals...');
    
    fetch('/api/v1/revision/goals/')
        .then(response => response.json())
        .then(data => {
            // Update daily goal
            const dailyProgress = data.daily_cards_progress || { current: 0, target: 20 };
            const dailyPercentage = Math.round((dailyProgress.current / dailyProgress.target) * 100);
            updateElement('dailyGoalProgress', `${dailyProgress.current}/${dailyProgress.target}`);
            updateElement('dailyGoalPercentage', `${dailyPercentage}%`);
            updateProgressBar('dailyGoalBar', Math.min(dailyPercentage, 100));
            
            // Update weekly goal
            const weeklyProgress = data.weekly_time_progress || { current: 0, target: 300 };
            const weeklyPercentage = Math.round((weeklyProgress.current / weeklyProgress.target) * 100);
            updateElement('weeklyGoalProgress', `${weeklyProgress.current}/${weeklyProgress.target}min`);
            updateElement('weeklyGoalPercentage', `${weeklyPercentage}%`);
            updateProgressBar('weeklyGoalBar', Math.min(weeklyPercentage, 100));
            
            // Update accuracy goal
            const accuracyProgress = data.accuracy_progress || { current: 0, target: 85 };
            const accuracyPercentage = Math.round((accuracyProgress.current / accuracyProgress.target) * 100);
            updateElement('accuracyGoalProgress', `${accuracyProgress.current}%/${accuracyProgress.target}%`);
            updateElement('accuracyGoalStatus', 
                accuracyProgress.current >= accuracyProgress.target ? 'Achieved' : 'Target'
            );
            updateProgressBar('accuracyGoalBar', Math.min(accuracyPercentage, 100));
        })
        .catch(error => {
            console.error('❌ Error loading study goals:', error);
        });
}

// ===== CHART FUNCTIONS =====
/**
 * Initialize all charts
 */
function initializeCharts() {
    // Skip chart initialization if Chart.js is not available
    if (typeof Chart === 'undefined') {
        console.log('⚠️ Chart.js not available, skipping chart initialization');
        // Replace charts with simple placeholders
        const activityChart = document.getElementById('studyActivityChart');
        const performanceChart = document.getElementById('performanceChart');
        
        if (activityChart) {
            activityChart.parentElement.innerHTML = '<p class="text-center text-muted p-4">Chart unavailable (offline mode)</p>';
        }
        if (performanceChart) {
            performanceChart.parentElement.innerHTML = '<p class="text-center text-muted p-4">Chart unavailable (offline mode)</p>';
        }
        return;
    }
    
    // Study Activity Chart
    const activityCtx = document.getElementById('studyActivityChart');
    if (activityCtx) {
        studyActivityChart = new Chart(activityCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Cards Studied',
                    data: [],
                    borderColor: '#2D5BBA',
                    backgroundColor: 'rgba(45, 91, 186, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Performance Chart
    const performanceCtx = document.getElementById('performanceChart');
    if (performanceCtx) {
        performanceChart = new Chart(performanceCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Correct', 'Incorrect', 'Skipped'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#10B981', '#EF4444', '#6B7280']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

/**
 * Update study activity chart with new data
 */
function updateStudyActivityChart(data) {
    if (studyActivityChart && data) {
        studyActivityChart.data.labels = data.map(item => item.date);
        studyActivityChart.data.datasets[0].data = data.map(item => item.cards_studied);
        studyActivityChart.update();
    }
}

/**
 * Update performance chart with new data
 */
function updatePerformanceChart(data) {
    if (performanceChart && data) {
        performanceChart.data.datasets[0].data = [
            data.correct || 0,
            data.incorrect || 0,
            data.skipped || 0
        ];
        performanceChart.update();
    }
}

// ===== ACTION FUNCTIONS =====
/**
 * Export statistics data
 */
function exportStats() {
    console.log('📥 Exporting statistics...');
    
    fetch(`/api/v1/revision/stats/export/?period=${currentPeriod}`)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `revision_stats_${currentPeriod}days.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            if (window.notificationService) {
                window.notificationService.success('Statistics exported successfully');
            }
        })
        .catch(error => {
            console.error('❌ Error exporting stats:', error);
            if (window.notificationService) {
                window.notificationService.error('Error exporting statistics');
            }
        });
}

/**
 * Set study goal (placeholder)
 */
function setStudyGoal() {
    console.log('🎯 Setting study goal...');
    // This would open a modal to set study goals
    if (window.notificationService) {
        window.notificationService.info('Study goal setting coming soon!');
    } else {
        alert('Study goal setting coming soon!');
    }
}

// ===== UTILITY FUNCTIONS =====
/**
 * Update DOM element text content safely
 */
function updateElement(elementId, content) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = content;
    } else {
        console.warn(`⚠️ Element with ID '${elementId}' not found`);
    }
}

/**
 * Update progress bar width safely
 */
function updateProgressBar(elementId, percentage) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.width = percentage + '%';
    } else {
        console.warn(`⚠️ Progress bar with ID '${elementId}' not found`);
    }
}

/**
 * Format time in minutes to readable format
 */
function formatTime(minutes) {
    if (minutes < 60) {
        return minutes + 'min';
    } else {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return hours + 'h' + (mins > 0 ? ' ' + mins + 'min' : '');
    }
}

/**
 * Get human-readable time ago string
 */
function getTimeAgo(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 60) {
        return minutes + ' min ago';
    } else if (minutes < 1440) {
        return Math.floor(minutes / 60) + ' hours ago';
    } else {
        return Math.floor(minutes / 1440) + ' days ago';
    }
}

// ===== GLOBAL EXPORTS =====
// Make functions globally available for inline event handlers
window.exportStats = exportStats;
window.setStudyGoal = setStudyGoal;
window.loadDeckStats = loadDeckStats;

console.log('📊 Revision statistics module loaded successfully');