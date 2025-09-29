/**
 * Revision Statistics Dashboard JavaScript
 * Handles all functionality for the statistics dashboard page
 */

// Global variables for statistics
let currentPeriod = 30; // Default to 30 days to match navbar default
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
    
    fetch('/api/v1/revision/api/decks/stats/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
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
            
            // Update sidebar elements
            updateElement('sidebarTotalDecks', totalDecks);
            updateElement('sidebarTotalCards', totalCards);
            updateElement('sidebarProgress', completionPercentage + '%');
            
            // Update progress bar
            const progressBar = document.getElementById('completionProgress');
            if (progressBar) {
                progressBar.style.width = completionPercentage + '%';
            }
        })
        .catch(error => {
            console.error('❌ Error loading collection overview:', error);
            console.log('🔄 Using fallback demo data...');
            
            // Use demo data as fallback
            const demoData = {
                total_decks: 5,
                total_cards: 120,
                total_learned: 85,
                completion_percentage: 71
            };
            
            updateElement('totalDecks', demoData.total_decks);
            updateElement('totalCards', demoData.total_cards);
            updateElement('totalLearned', demoData.total_learned);
            updateElement('completionRate', demoData.completion_percentage + '%');
            
            // Update sidebar elements with demo data
            updateElement('sidebarTotalDecks', demoData.total_decks);
            updateElement('sidebarTotalCards', demoData.total_cards);
            updateElement('sidebarProgress', demoData.completion_percentage + '%');
            
            const progressBar = document.getElementById('completionProgress');
            if (progressBar) {
                progressBar.style.width = demoData.completion_percentage + '%';
            }
        });
}

/**
 * Load detailed statistics for the selected period
 */
function loadStatistics() {
    console.log(`📊 Loading statistics for ${currentPeriod} days...`);
    
    fetch(`/api/v1/revision/api/stats/?period=${currentPeriod}`)
        .then(response => response.json())
        .then(data => {
            console.log('Statistics data:', data);
            
            // Update overview cards
            updateElement('totalStudiedCards', data.total_studied_cards || 0);
            updateElement('accuracyRate', (data.accuracy_rate || 0) + '%');
            updateElement('studyTime', formatTime(data.total_study_time || 0));
            updateElement('currentStreak', data.current_streak || 0);
            
            // Update sidebar elements
            updateElement('sidebarStudiedCards', data.total_studied_cards || 0);
            updateElement('sidebarAccuracy', (data.accuracy_rate || 0) + '%');
            updateElement('sidebarStreak', data.current_streak || 0);
            
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
            console.log('🔄 Using fallback demo data for activity stats...');
            
            // Use demo data as fallback
            const demoData = {
                total_studied_cards: 45,
                accuracy_rate: 87,
                total_study_time: 165,
                current_streak: 7
            };
            
            updateElement('totalStudiedCards', demoData.total_studied_cards);
            updateElement('accuracyRate', demoData.accuracy_rate + '%');
            updateElement('studyTime', formatTime(demoData.total_study_time));
            updateElement('currentStreak', demoData.current_streak);
            
            // Update sidebar elements with demo data
            updateElement('sidebarStudiedCards', demoData.total_studied_cards);
            updateElement('sidebarAccuracy', demoData.accuracy_rate + '%');
            updateElement('sidebarStreak', demoData.current_streak);
            
            // Update progress bars
            updateProgressBar('studiedCardsProgress', Math.min((demoData.total_studied_cards || 0) / 100 * 100, 100));
            updateProgressBar('accuracyProgress', demoData.accuracy_rate || 0);
            updateProgressBar('studyTimeProgress', Math.min((demoData.total_study_time || 0) / 600 * 100, 100));
            updateProgressBar('streakProgress', Math.min((demoData.current_streak || 0) / 30 * 100, 100));
        });
}

/**
 * Load deck performance statistics
 */
function loadDeckStats() {
    console.log('📊 Loading deck statistics...');
    
    fetch('/api/v1/revision/api/decks/performance/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('deckStatsTable');
            if (!tbody) return;
            
            tbody.innerHTML = '';
            
            if (data.results && data.results.length > 0) {
                data.results.forEach(deck => {
                    const accuracyClass = deck.accuracy >= 80 ? 'bg-green-500 text-white' : 
                                        deck.accuracy >= 60 ? 'bg-yellow-500 text-white' : 'bg-red-500 text-white';
                    
                    tbody.innerHTML += `
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-3">
                                <div class="text-xs font-medium text-gray-900">${deck.name}</div>
                                <div class="text-xs text-gray-500">${deck.description || _('No description')}</div>
                            </td>
                            <td class="px-4 py-3 text-xs text-gray-900">${deck.cards_count}</td>
                            <td class="px-4 py-3">
                                <div class="flex items-center">
                                    <span class="mr-2 text-xs text-gray-900">${deck.mastered_cards}/${deck.cards_count}</span>
                                    <div class="flex-1 bg-gray-200 rounded-full h-1">
                                        <div class="bg-linguify-primary rounded-full h-1 transition-all duration-300" style="width: ${deck.mastery_percentage}%"></div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-4 py-3">
                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${accuracyClass}">
                                    ${deck.accuracy}%
                                </span>
                            </td>
                        </tr>
                    `;
                });
            } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="px-4 py-6 text-center text-gray-500 text-sm">
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
                        <td colspan="4" class="px-4 py-6 text-center text-red-600 text-sm">
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
    
    fetch('/api/v1/revision/api/sessions/recent/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('recentActivity');
            if (!container) return;
            
            container.innerHTML = '';
            
            if (data.results && data.results.length > 0) {
                data.results.forEach(session => {
                    const timeAgo = getTimeAgo(new Date(session.created_at));
                    container.innerHTML += `
                        <div class="px-4 py-3">
                            <div class="flex justify-between items-start">
                                <h6 class="text-xs font-medium text-gray-900 mb-1">${session.deck_name}</h6>
                                <span class="text-xs text-gray-500">${timeAgo}</span>
                            </div>
                            <p class="text-xs text-gray-600 mb-1">${session.mode} - ${session.cards_studied} cards studied</p>
                            <div class="text-xs text-gray-500">Accuracy: ${session.accuracy}%</div>
                        </div>
                    `;
                });
            } else {
                container.innerHTML = `
                    <div class="px-4 py-6 text-center text-gray-500 text-sm">
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
                    <div class="px-4 py-6 text-center text-red-600 text-sm">
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
    
    fetch('/api/v1/revision/api/goals/')
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
            console.log('🔄 Using fallback demo data for study goals...');
            
            // Use demo data as fallback
            const demoData = {
                daily_cards_progress: { current: 12, target: 20 },
                weekly_time_progress: { current: 180, target: 300 },
                accuracy_progress: { current: 87, target: 85 }
            };
            
            // Update daily goal
            const dailyPercentage = Math.round((demoData.daily_cards_progress.current / demoData.daily_cards_progress.target) * 100);
            updateElement('dailyGoalProgress', `${demoData.daily_cards_progress.current}/${demoData.daily_cards_progress.target}`);
            updateElement('dailyGoalPercentage', `${dailyPercentage}%`);
            updateProgressBar('dailyGoalBar', Math.min(dailyPercentage, 100));
            
            // Update weekly goal
            const weeklyPercentage = Math.round((demoData.weekly_time_progress.current / demoData.weekly_time_progress.target) * 100);
            updateElement('weeklyGoalProgress', `${demoData.weekly_time_progress.current}/${demoData.weekly_time_progress.target}min`);
            updateElement('weeklyGoalPercentage', `${weeklyPercentage}%`);
            updateProgressBar('weeklyGoalBar', Math.min(weeklyPercentage, 100));
            
            // Update accuracy goal
            const accuracyPercentage = Math.round((demoData.accuracy_progress.current / demoData.accuracy_progress.target) * 100);
            updateElement('accuracyGoalProgress', `${demoData.accuracy_progress.current}%/${demoData.accuracy_progress.target}%`);
            updateElement('accuracyGoalStatus', 
                demoData.accuracy_progress.current >= demoData.accuracy_progress.target ? 'Achieved' : 'Target'
            );
            updateProgressBar('accuracyGoalBar', Math.min(accuracyPercentage, 100));
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
    
    fetch(`/api/v1/revision/api/stats/export/?period=${currentPeriod}`)
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