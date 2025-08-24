// Advanced Statistics Module inspired by Anki
// Handles enhanced analytics with period analysis, forecasting, and detailed insights

class AdvancedStatsManager {
    constructor() {
        this.currentPeriod = 1; // PERIOD_MONTH by default
        this.cache = new Map();
        this.charts = {};
        
        // Period constants (matching backend)
        this.PERIODS = {
            WEEK: 0,
            MONTH: 1, 
            YEAR: 2,
            LIFETIME: 3
        };
        
        this.PERIOD_NAMES = {
            0: 'Last 7 days',
            1: 'Last 30 days',
            2: 'Last year', 
            3: 'All time'
        };
    }
    
    /**
     * Initialize the advanced stats dashboard
     */
    async init() {
        console.log('🚀 Initializing Advanced Statistics Manager');
        
        try {
            // Load initial data
            await this.loadAdvancedStats();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize charts
            this.initializeCharts();
            
            console.log('✅ Advanced Statistics Manager initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Advanced Statistics:', error);
            window.notificationService?.error('Failed to load advanced statistics');
        }
    }
    
    /**
     * Setup event listeners for period switching and controls
     */
    setupEventListeners() {
        // Period selector
        const periodSelector = document.getElementById('statsPeriodSelector');
        if (periodSelector) {
            periodSelector.addEventListener('change', (e) => {
                this.currentPeriod = parseInt(e.target.value);
                this.loadAdvancedStats();
            });
        }
        
        // Refresh button
        const refreshButton = document.getElementById('refreshAdvancedStats');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.cache.clear();
                this.loadAdvancedStats();
            });
        }
        
        // Export button
        const exportButton = document.getElementById('exportAdvancedStats');
        if (exportButton) {
            exportButton.addEventListener('click', () => {
                this.exportStatistics();
            });
        }
    }
    
    /**
     * Load advanced statistics data from API
     */
    async loadAdvancedStats() {
        const cacheKey = `advanced_stats_${this.currentPeriod}`;
        
        // Check cache first
        if (this.cache.has(cacheKey)) {
            console.log('📊 Using cached advanced stats data');
            this.renderAdvancedStats(this.cache.get(cacheKey));
            return;
        }
        
        try {
            console.log(`📡 Fetching advanced stats for period ${this.currentPeriod}`);
            
            const params = new URLSearchParams({
                period_type: this.currentPeriod.toString(),
                include_forecast: 'true',
                include_hourly: 'true',
                include_maturity: 'true'
            });
            
            const response = await window.apiService.request(
                `/api/v1/revision/stats/advanced/?${params}`,
                { method: 'GET' }
            );
            
            console.log('📊 Advanced stats data received:', response);
            
            // Cache the response
            this.cache.set(cacheKey, response);
            
            // Render the stats
            this.renderAdvancedStats(response);
            
        } catch (error) {
            console.error('❌ Error loading advanced stats:', error);
            window.notificationService?.handleApiError(error, 'Loading advanced statistics');
            this.showErrorState();
        }
    }
    
    /**
     * Render advanced statistics in the UI
     */
    renderAdvancedStats(data) {
        console.log('🎨 Rendering advanced statistics');
        
        // Update period info
        this.updatePeriodInfo(data.period_info);
        
        // Update enhanced basic stats
        this.updateEnhancedBasicStats(data.basic_stats);
        
        // Update card maturity breakdown
        this.updateCardMaturityStats(data.card_maturity);
        
        // Update forecast if available
        if (data.forecast) {
            this.updateForecastStats(data.forecast);
        }
        
        // Update hourly performance if available
        if (data.hourly_performance) {
            this.updateHourlyPerformance(data.hourly_performance);
        }
        
        // Update historical charts
        if (data.historical_data) {
            this.updateHistoricalCharts(data.historical_data);
        }
        
        // Show insights and recommendations
        this.showInsights(data);
    }
    
    /**
     * Update period information display
     */
    updatePeriodInfo(periodInfo) {
        const periodElement = document.getElementById('currentPeriodInfo');
        if (periodElement && periodInfo) {
            periodElement.innerHTML = `
                <div class="flex items-center gap-2 text-sm text-gray-600">
                    <i class="bi bi-calendar3"></i>
                    <span>${periodInfo.name}</span>
                    <span class="text-xs bg-gray-100 px-2 py-1 rounded">
                        ${periodInfo.days_covered} days, ${periodInfo.chunk_unit} chunks
                    </span>
                </div>
            `;
        }
    }
    
    /**
     * Update enhanced basic statistics with maturity metrics
     */
    updateEnhancedBasicStats(basicStats) {
        if (!basicStats) return;
        
        // Update existing basic stats
        const elements = {
            'stat-total-decks': basicStats.total_decks || 0,
            'stat-total-cards': basicStats.total_cards || 0,
            'stat-learned-cards': basicStats.total_learned || 0,
            'stat-completion-rate': `${basicStats.completion_percentage || 0}%`
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
        
        // Add new maturity metrics
        const maturityElement = document.getElementById('maturity-breakdown');
        if (maturityElement) {
            maturityElement.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-blue-50 p-3 rounded-lg">
                        <div class="text-2xl font-bold text-blue-600">${basicStats.total_mature || 0}</div>
                        <div class="text-sm text-blue-800">Mature Cards</div>
                        <div class="text-xs text-blue-600">${basicStats.maturity_percentage || 0}% of learned</div>
                    </div>
                    <div class="bg-green-50 p-3 rounded-lg">
                        <div class="text-2xl font-bold text-green-600">${basicStats.young_cards || 0}</div>
                        <div class="text-sm text-green-800">Young Cards</div>
                        <div class="text-xs text-green-600">Recently learned</div>
                    </div>
                </div>
            `;
        }
    }
    
    /**
     * Update card maturity breakdown
     */
    updateCardMaturityStats(maturityStats) {
        if (!maturityStats) return;
        
        const maturityChart = document.getElementById('maturity-chart');
        if (maturityChart) {
            const data = Object.entries(maturityStats).map(([level, info]) => ({
                label: level.charAt(0).toUpperCase() + level.slice(1),
                count: info.count,
                description: info.description,
                color: this.getMaturityColor(level)
            }));
            
            this.renderMaturityChart(maturityChart, data);
        }
        
        // Update detailed breakdown
        const maturityDetails = document.getElementById('maturity-details');
        if (maturityDetails) {
            maturityDetails.innerHTML = Object.entries(maturityStats).map(([level, info]) => `
                <div class="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div class="flex items-center gap-3">
                        <div class="w-3 h-3 rounded-full" style="background: ${this.getMaturityColor(level)}"></div>
                        <div>
                            <div class="font-medium">${level.charAt(0).toUpperCase() + level.slice(1)}</div>
                            <div class="text-sm text-gray-600">${info.description}</div>
                        </div>
                    </div>
                    <div class="font-bold">${info.count}</div>
                </div>
            `).join('');
        }
    }
    
    /**
     * Update forecast statistics
     */
    updateForecastStats(forecastData) {
        if (!forecastData) return;
        
        const forecastElement = document.getElementById('forecast-section');
        if (forecastElement) {
            const avgDaily = forecastData.avg_daily_base || 0;
            const nextWeekTotal = forecastData.forecast?.slice(0, 7)
                .reduce((sum, day) => sum + day.predicted_reviews, 0) || 0;
            
            forecastElement.innerHTML = `
                <div class="bg-purple-50 p-4 rounded-lg">
                    <h3 class="font-semibold text-purple-800 mb-3">📈 Review Forecast</h3>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <div class="text-2xl font-bold text-purple-600">${avgDaily}</div>
                            <div class="text-sm text-purple-800">Daily Average</div>
                        </div>
                        <div>
                            <div class="text-2xl font-bold text-purple-600">${nextWeekTotal}</div>
                            <div class="text-sm text-purple-800">Next 7 Days</div>
                        </div>
                    </div>
                    <div class="mt-3 text-xs text-purple-600">
                        Prediction based on your recent study patterns
                    </div>
                </div>
            `;
        }
        
        // Create forecast chart
        this.renderForecastChart(forecastData.forecast);
    }
    
    /**
     * Update hourly performance analysis
     */
    updateHourlyPerformance(hourlyData) {
        if (!hourlyData) return;
        
        const hourlyElement = document.getElementById('hourly-performance');
        if (hourlyElement) {
            const bestHour = hourlyData.best_performance_hour;
            
            if (bestHour) {
                hourlyElement.innerHTML = `
                    <div class="bg-yellow-50 p-4 rounded-lg">
                        <h3 class="font-semibold text-yellow-800 mb-3">⏰ Peak Performance</h3>
                        <div class="text-center">
                            <div class="text-3xl font-bold text-yellow-600">${bestHour.hour}:00</div>
                            <div class="text-sm text-yellow-800">Best Study Hour</div>
                            <div class="text-xs text-yellow-600">
                                ${bestHour.avg_success_rate}% success rate
                            </div>
                        </div>
                        <div class="mt-3 text-xs text-yellow-600 text-center">
                            Based on ${bestHour.session_count} study sessions
                        </div>
                    </div>
                `;
            } else {
                hourlyElement.innerHTML = `
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-semibold text-gray-600 mb-3">⏰ Hourly Analysis</h3>
                        <div class="text-center text-gray-500">
                            <i class="bi bi-clock text-2xl mb-2"></i>
                            <div class="text-sm">Study more to discover your peak hours!</div>
                        </div>
                    </div>
                `;
            }
        }
        
        // Create hourly performance chart
        this.renderHourlyChart(hourlyData.hourly_breakdown);
    }
    
    /**
     * Update historical data charts
     */
    updateHistoricalCharts(historicalData) {
        if (!historicalData || !historicalData.data_points) return;
        
        // Render activity chart
        this.renderActivityChart(historicalData.data_points);
        
        // Render performance trend chart
        this.renderPerformanceTrendChart(historicalData.data_points);
    }
    
    /**
     * Show insights and recommendations based on data
     */
    showInsights(data) {
        const insightsElement = document.getElementById('smart-insights');
        if (!insightsElement) return;
        
        const insights = this.generateInsights(data);
        
        insightsElement.innerHTML = `
            <div class="bg-blue-50 p-4 rounded-lg">
                <h3 class="font-semibold text-blue-800 mb-3">💡 Smart Insights</h3>
                <div class="space-y-2">
                    ${insights.map(insight => `
                        <div class="flex items-start gap-2">
                            <i class="${insight.icon} text-blue-600"></i>
                            <div class="text-sm text-blue-800">${insight.text}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    /**
     * Generate insights based on statistics
     */
    generateInsights(data) {
        const insights = [];
        const basicStats = data.basic_stats || {};
        const maturity = data.card_maturity || {};
        const forecast = data.forecast || {};
        const hourly = data.hourly_performance || {};
        
        // Learning progress insights
        if (basicStats.total_cards > 0) {
            const completionRate = basicStats.completion_percentage || 0;
            if (completionRate < 25) {
                insights.push({
                    icon: 'bi bi-rocket-takeoff',
                    text: 'You\'re just getting started! Focus on learning new cards consistently.'
                });
            } else if (completionRate < 75) {
                insights.push({
                    icon: 'bi bi-graph-up-arrow',
                    text: `Great progress! You've learned ${completionRate}% of your cards.`
                });
            } else {
                insights.push({
                    icon: 'bi bi-trophy',
                    text: 'Excellent! You\'ve mastered most of your cards. Time to add new content?'
                });
            }
        }
        
        // Maturity insights
        if (maturity.new && maturity.new.count > 10) {
            insights.push({
                icon: 'bi bi-lightbulb',
                text: `You have ${maturity.new.count} new cards waiting. Start with 5-10 per day.`
            });
        }
        
        if (maturity.mature && maturity.mature.count > 0) {
            const maturityRate = basicStats.maturity_percentage || 0;
            if (maturityRate > 50) {
                insights.push({
                    icon: 'bi bi-shield-check',
                    text: `${maturityRate}% of learned cards are mature. Excellent long-term retention!`
                });
            }
        }
        
        // Study schedule insights
        if (hourly.best_performance_hour) {
            insights.push({
                icon: 'bi bi-alarm',
                text: `Your peak performance is at ${hourly.best_performance_hour.hour}:00. Schedule important reviews then!`
            });
        } else {
            insights.push({
                icon: 'bi bi-calendar-plus',
                text: 'Complete more study sessions to discover your optimal study times.'
            });
        }
        
        // Forecast insights
        if (forecast.avg_daily_base > 0) {
            insights.push({
                icon: 'bi bi-calendar2-week',
                text: `You're averaging ${forecast.avg_daily_base.toFixed(1)} reviews per day. Keep it up!`
            });
        } else {
            insights.push({
                icon: 'bi bi-play-circle',
                text: 'Start your first study session to build your learning momentum!'
            });
        }
        
        return insights;
    }
    
    /**
     * Get color for maturity level
     */
    getMaturityColor(level) {
        const colors = {
            'new': '#e5e7eb',      // Gray
            'learning': '#fbbf24', // Yellow  
            'young': '#10b981',    // Green
            'mature': '#3b82f6'    // Blue
        };
        return colors[level] || '#6b7280';
    }
    
    /**
     * Show error state
     */
    showErrorState() {
        const container = document.getElementById('advanced-stats-container');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <i class="bi bi-exclamation-triangle text-4xl text-red-500 mb-4"></i>
                    <h3 class="text-lg font-semibold text-red-700 mb-2">Failed to Load Statistics</h3>
                    <p class="text-red-600 mb-4">Unable to fetch advanced statistics data.</p>
                    <button onclick="window.advancedStats.loadAdvancedStats()" 
                            class="btn btn-primary">
                        <i class="bi bi-arrow-clockwise"></i> Retry
                    </button>
                </div>
            `;
        }
    }
    
    /**
     * Chart rendering methods with basic implementations
     */
    renderMaturityChart(container, data) {
        console.log('📊 Rendering maturity chart:', data);
        
        // Create a simple visual representation using HTML/CSS
        const total = data.reduce((sum, item) => sum + item.count, 0);
        
        container.innerHTML = `
            <div class="space-y-2">
                ${data.map(item => {
                    const percentage = total > 0 ? (item.count / total * 100) : 0;
                    return `
                        <div class="flex items-center gap-2">
                            <div class="w-3 h-3 rounded-full" style="background: ${item.color}"></div>
                            <div class="flex-1 text-sm">${item.label}</div>
                            <div class="text-sm font-semibold">${item.count}</div>
                            <div class="text-xs text-gray-500">${percentage.toFixed(1)}%</div>
                        </div>
                        <div class="ml-5">
                            <div class="w-full bg-gray-200 rounded-full h-1">
                                <div class="rounded-full h-1 transition-all duration-300" 
                                     style="width: ${percentage}%; background: ${item.color}"></div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
    
    renderForecastChart(forecastData) {
        console.log('📊 Rendering forecast chart:', forecastData);
        
        // For now, just show a simple text representation
        const forecastContainer = document.getElementById('forecast-chart');
        if (forecastContainer && forecastData && forecastData.length > 0) {
            const nextWeek = forecastData.slice(0, 7);
            const maxReviews = Math.max(...nextWeek.map(d => d.predicted_reviews), 1);
            
            forecastContainer.innerHTML = `
                <div class="text-xs text-gray-600 mb-2">Next 7 days forecast:</div>
                <div class="space-y-1">
                    ${nextWeek.map((day, index) => {
                        const width = (day.predicted_reviews / maxReviews * 100);
                        const date = new Date(day.date).toLocaleDateString('fr-FR', { weekday: 'short' });
                        return `
                            <div class="flex items-center gap-2">
                                <div class="text-xs w-8">${date}</div>
                                <div class="flex-1 bg-gray-200 rounded h-2">
                                    <div class="bg-purple-500 rounded h-2 transition-all duration-300" 
                                         style="width: ${width}%"></div>
                                </div>
                                <div class="text-xs w-8 text-right">${day.predicted_reviews}</div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
        }
    }
    
    renderHourlyChart(hourlyData) {
        console.log('📊 Rendering hourly chart:', hourlyData);
        
        const hourlyContainer = document.getElementById('hourly-chart');
        if (hourlyContainer && hourlyData && hourlyData.length > 0) {
            const validHours = hourlyData.filter(h => h.avg_success_rate !== null && h.session_count > 0);
            
            if (validHours.length === 0) {
                hourlyContainer.innerHTML = '<div class="text-center text-gray-500 text-sm py-4">No hourly data available yet</div>';
                return;
            }
            
            const maxRate = Math.max(...validHours.map(h => h.avg_success_rate));
            
            hourlyContainer.innerHTML = `
                <div class="text-xs text-gray-600 mb-2">Performance by hour:</div>
                <div class="grid grid-cols-12 gap-1">
                    ${validHours.map(hour => {
                        const height = maxRate > 0 ? (hour.avg_success_rate / maxRate * 40) : 0;
                        return `
                            <div class="text-center">
                                <div class="bg-yellow-500 rounded-t mb-1 transition-all duration-300" 
                                     style="height: ${height}px; min-height: 2px;"
                                     title="${hour.hour}:00 - ${hour.avg_success_rate}%"></div>
                                <div class="text-xs">${hour.hour}</div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
        }
    }
    
    renderActivityChart(data) {
        console.log('📊 Rendering activity chart:', data);
        
        const activityContainer = document.getElementById('activityTrendChart');
        if (activityContainer && data && data.length > 0) {
            // Create a parent div to replace the canvas
            const parent = activityContainer.parentNode;
            const chartDiv = document.createElement('div');
            chartDiv.className = 'w-full h-64 flex items-end gap-1 p-4';
            chartDiv.id = 'activityTrendChart';
            
            const maxCards = Math.max(...data.map(d => d.cards_studied), 1);
            
            chartDiv.innerHTML = `
                <div class="text-sm text-gray-600 absolute top-2 left-4">Cards studied over time</div>
                ${data.map((point, index) => {
                    const height = (point.cards_studied / maxCards * 180);
                    return `
                        <div class="flex-1 flex flex-col items-center">
                            <div class="bg-linguify-primary rounded-t transition-all duration-300 w-full min-h-[2px]" 
                                 style="height: ${height}px"
                                 title="${point.label}: ${point.cards_studied} cards"></div>
                            <div class="text-xs mt-1 text-center transform -rotate-45 origin-left">${point.label}</div>
                        </div>
                    `;
                }).join('')}
            `;
            
            parent.replaceChild(chartDiv, activityContainer);
        }
    }
    
    renderPerformanceTrendChart(data) {
        console.log('📊 Rendering performance trend chart:', data);
        
        const performanceContainer = document.getElementById('performanceTrendChart');
        if (performanceContainer && data && data.length > 0) {
            // Create a parent div to replace the canvas
            const parent = performanceContainer.parentNode;
            const chartDiv = document.createElement('div');
            chartDiv.className = 'w-full h-64 flex items-end gap-1 p-4';
            chartDiv.id = 'performanceTrendChart';
            
            const maxRate = Math.max(...data.map(d => d.avg_success_rate), 1);
            
            chartDiv.innerHTML = `
                <div class="text-sm text-gray-600 absolute top-2 left-4">Success rate trend (%)</div>
                ${data.map((point, index) => {
                    const height = (point.avg_success_rate / maxRate * 180);
                    const color = point.avg_success_rate >= 80 ? 'bg-green-500' : 
                                 point.avg_success_rate >= 60 ? 'bg-yellow-500' : 'bg-red-500';
                    return `
                        <div class="flex-1 flex flex-col items-center">
                            <div class="${color} rounded-t transition-all duration-300 w-full min-h-[2px]" 
                                 style="height: ${height}px"
                                 title="${point.label}: ${point.avg_success_rate}% success"></div>
                            <div class="text-xs mt-1 text-center transform -rotate-45 origin-left">${point.label}</div>
                        </div>
                    `;
                }).join('')}
            `;
            
            parent.replaceChild(chartDiv, performanceContainer);
        }
    }
    
    initializeCharts() {
        console.log('📊 Initializing chart containers');
        
        // Add containers for charts that don't exist yet
        const forecastSection = document.getElementById('forecast-section');
        if (forecastSection) {
            const existingChart = document.getElementById('forecast-chart');
            if (!existingChart) {
                const chartContainer = document.createElement('div');
                chartContainer.id = 'forecast-chart';
                chartContainer.className = 'mt-4';
                forecastSection.appendChild(chartContainer);
            }
        }
        
        const hourlySection = document.getElementById('hourly-performance');
        if (hourlySection) {
            const existingChart = document.getElementById('hourly-chart');
            if (!existingChart) {
                const chartContainer = document.createElement('div');
                chartContainer.id = 'hourly-chart';
                chartContainer.className = 'mt-4';
                hourlySection.appendChild(chartContainer);
            }
        }
    }
    
    /**
     * Export statistics to CSV/JSON
     */
    exportStatistics() {
        const cacheKey = `advanced_stats_${this.currentPeriod}`;
        const data = this.cache.get(cacheKey);
        
        if (!data) {
            window.notificationService?.warning('No data to export. Please load statistics first.');
            return;
        }
        
        const exportData = {
            period: this.PERIOD_NAMES[this.currentPeriod],
            exported_at: new Date().toISOString(),
            basic_stats: data.basic_stats,
            card_maturity: data.card_maturity,
            historical_data: data.historical_data?.data_points || []
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
            type: 'application/json' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `linguify_advanced_stats_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        window.notificationService?.success('Statistics exported successfully!');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (window.REVISION_CONFIG) {
        window.advancedStats = new AdvancedStatsManager();
        
        // Initialize if we're on the stats page
        if (window.REVISION_CONFIG.viewType === 'stats') {
            window.advancedStats.init();
        }
    }
});

// Make available globally
window.AdvancedStatsManager = AdvancedStatsManager;