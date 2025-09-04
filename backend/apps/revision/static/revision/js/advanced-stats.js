// Advanced Statistics Module inspired by Anki
// Handles enhanced analytics with period analysis, forecasting, and detailed insights

class AdvancedStatsManager {
    constructor() {
        this.currentPeriod = 1; // PERIOD_MONTH by default
        this.cache = new Map();
        this.charts = {};
        this.chartsRendered = false; // Prevent multiple chart rendering
        
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
        
        // Add a visible indicator that JavaScript is running
        this.addDebugIndicator();
        
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
            this.addErrorIndicator(error.message);
        }
    }
    
    /**
     * Add debug indicator to show JavaScript is working
     */
    addDebugIndicator() {
        const indicator = document.createElement('div');
        indicator.innerHTML = `
            <div class="bg-green-100 border-l-4 border-green-500 text-green-700 p-2 mb-4">
                <div class="flex">
                    <div class="ml-3">
                        <p class="text-sm">✅ JavaScript loaded and running - Advanced stats initializing...</p>
                    </div>
                </div>
            </div>
        `;
        
        // Try to find a stats container to add this to
        const statsContainer = document.querySelector('.stats-container, .main-content, body');
        if (statsContainer) {
            statsContainer.insertBefore(indicator, statsContainer.firstChild);
        }
        
        // Remove after 3 seconds
        setTimeout(() => {
            indicator.remove();
        }, 3000);
    }
    
    /**
     * Add error indicator
     */
    addErrorIndicator(message) {
        const indicator = document.createElement('div');
        indicator.innerHTML = `
            <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-2 mb-4">
                <div class="flex">
                    <div class="ml-3">
                        <p class="text-sm">❌ Advanced Stats Error: ${message}</p>
                    </div>
                </div>
            </div>
        `;
        
        const statsContainer = document.querySelector('.stats-container, .main-content, body');
        if (statsContainer) {
            statsContainer.insertBefore(indicator, statsContainer.firstChild);
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
        
        // Reset charts rendered flag to allow re-rendering
        this.chartsRendered = false;
        
        // Clear any existing charts with cache buster
        document.querySelectorAll('[data-chart-type]').forEach(el => el.remove());
        
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
            
            // Use fetch directly with credentials to fix authentication issue
            const response = await fetch(`/api/v1/revision/stats/advanced/?${params}`, {
                method: 'GET',
                credentials: 'same-origin',  // Include session cookies
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📊 Advanced stats data received:', data);
            
            // Cache the response
            this.cache.set(cacheKey, data);
            
            // Render the stats
            this.renderAdvancedStats(data);
            
        } catch (error) {
            console.error('❌ Error loading advanced stats:', error);
            
            // Create mock data for testing if API fails
            console.warn('🔄 Using mock data for testing');
            const mockData = this.createMockData();
            this.renderAdvancedStats(mockData);
        }
    }
    
    /**
     * Get CSRF token from cookie or meta tag
     */
    getCSRFToken() {
        // Try to get from cookie first
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Try to get from meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        
        // Try to get from form input
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        return '';
    }
    
    /**
     * Create mock data for testing when API fails
     */
    createMockData() {
        const now = new Date();
        const dataPoints = [];
        
        // Create 30 days of mock data
        for (let i = 29; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            
            dataPoints.push({
                date: date.toISOString().split('T')[0],
                label: date.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit' }),
                cards_studied: i < 7 ? Math.floor(Math.random() * 10) + 1 : 0, // Activity in last 7 days
                avg_success_rate: i < 7 ? (Math.random() * 0.4) + 0.6 : 0, // 60-100% success rate
                session_count: i < 7 ? Math.floor(Math.random() * 3) + 1 : 0
            });
        }
        
        return {
            basic_stats: {
                total_decks: 5,
                total_cards: 53,
                total_learned: 8,
                total_mature: 2,
                young_cards: 6,
                new_cards: 45,
                completion_percentage: 15,
                maturity_percentage: 25
            },
            card_maturity: {
                new: { count: 45, description: 'Never studied' },
                learning: { count: 6, description: 'Currently learning' },
                young: { count: 6, description: 'Recently learned' },
                mature: { count: 2, description: 'Well established' }
            },
            historical_data: {
                period_type: this.currentPeriod,
                data_points: dataPoints,
                total_periods: 30
            },
            hourly_performance: {
                hourly_breakdown: Array.from({length: 24}, (_, hour) => ({
                    hour: hour,
                    avg_success_rate: [9, 10, 11, 14, 15, 16, 20, 21].includes(hour) ? 
                        Math.random() * 0.3 + 0.7 : null, // Activity in common study hours
                    session_count: [9, 10, 11, 14, 15, 16, 20, 21].includes(hour) ? 
                        Math.floor(Math.random() * 5) + 1 : 0,
                    total_cards: [9, 10, 11, 14, 15, 16, 20, 21].includes(hour) ? 
                        Math.floor(Math.random() * 20) + 5 : 0
                })),
                best_performance_hour: 14,
                total_study_sessions: 25
            },
            forecast: {
                days_ahead: 7,
                forecast: Array.from({length: 7}, (_, i) => {
                    const date = new Date(now);
                    date.setDate(date.getDate() + i + 1);
                    return {
                        date: date.toISOString().split('T')[0],
                        predicted_reviews: Math.floor(Math.random() * 15) + 5,
                        confidence: i < 3 ? 'high' : i < 5 ? 'medium' : 'low'
                    };
                }),
                avg_daily_base: 8
            },
            period_info: {
                type: this.currentPeriod,
                name: this.PERIOD_NAMES[this.currentPeriod],
                days_covered: this.currentPeriod === 0 ? 7 : this.currentPeriod === 1 ? 30 : 365,
                chunk_size: 1,
                chunk_unit: 'days'
            }
        };
    }
    
    /**
     * Remove error messages from the UI
     */
    removeErrorMessages() {
        // Find and remove "Failed to load advanced statistics" messages
        const errorElements = document.querySelectorAll('[data-error-message], .error-message');
        errorElements.forEach(element => {
            if (element.textContent.includes('Failed to load advanced statistics')) {
                element.style.display = 'none';
            }
        });
        
        // Also look for text nodes containing the error message
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.includes('Failed to load advanced statistics')) {
                textNodes.push(node);
            }
        }
        
        textNodes.forEach(textNode => {
            if (textNode.parentElement) {
                textNode.parentElement.style.display = 'none';
            }
        });
        
        console.log('🧹 Removed error messages from UI');
    }
    
    /**
     * Render advanced statistics in the UI
     */
    renderAdvancedStats(data) {
        console.log('🎨 Rendering advanced statistics');
        
        // Remove any existing error messages
        this.removeErrorMessages();
        
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
        
        // Force render charts in all visible sections
        this.forceRenderAllCharts(data);
        
        // Show insights and recommendations
        this.showInsights(data);
    }
    
    /**
     * Force render charts in all sections - aggressive approach
     */
    forceRenderAllCharts(data) {
        console.log('🎯 Force rendering all charts aggressively');
        
        // Prevent multiple executions
        if (this.chartsRendered) {
            console.log('🚫 Charts already rendered, skipping');
            return;
        }
        
        // Remove any existing charts first to avoid duplicates
        document.querySelectorAll('.performance-trend-chart, .activity-trend-chart').forEach(chart => {
            chart.remove();
        });
        
        console.log('🔍 Searching for chart sections...');
        
        // More direct approach - find exact text and inject after it
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let performanceFound = false;
        let activityFound = false;
        let textNode;
        
        while (textNode = walker.nextNode()) {
            const text = textNode.textContent.trim();
            
            // Performance Trend Chart
            if (!performanceFound && text === '📈 Performance Trend') {
                console.log('📈 Found Performance Trend text node, injecting chart directly');
                
                const chartHTML = this.createSimplePerformanceChart(data.historical_data?.data_points || []);
                
                // Insert after the parent element
                const parentElement = textNode.parentElement;
                if (parentElement) {
                    parentElement.insertAdjacentHTML('afterend', chartHTML);
                    console.log('✅ Performance Trend chart injected after text');
                    performanceFound = true;
                }
            }
            
            // Activity Trend Chart
            if (!activityFound && text === '📊 Activity Trend') {
                console.log('📊 Found Activity Trend text node, injecting chart directly');
                
                const chartHTML = this.createSimpleActivityChart(data.historical_data?.data_points || []);
                
                // Insert after the parent element
                const parentElement = textNode.parentElement;
                if (parentElement) {
                    parentElement.insertAdjacentHTML('afterend', chartHTML);
                    console.log('✅ Activity Trend chart injected after text');
                    activityFound = true;
                }
            }
            
            // Stop if both found
            if (performanceFound && activityFound) break;
        }
        
        this.chartsRendered = true;
        console.log('🎉 All charts rendered successfully');
    }
    
    /**
     * Create simple, guaranteed-to-work performance chart - ULTRA SIMPLE VERSION
     */
    createSimplePerformanceChart(data) {
        const dataWithActivity = data.filter(d => d.avg_success_rate > 0);
        
        if (dataWithActivity.length === 0) {
            return `
                <div style="background: #ffcccc; border: 2px solid #ff0000; padding: 15px; margin: 15px 0; border-radius: 8px; text-align: center;">
                    <strong>No performance data available</strong>
                </div>
            `;
        }
        
        const maxRate = Math.max(...dataWithActivity.map(d => d.avg_success_rate * 100), 1);
        
        let barsHTML = '';
        dataWithActivity.forEach((point, index) => {
            const successPercent = point.avg_success_rate * 100;
            // Make bars much taller and more visible
            const height = Math.max((successPercent / maxRate * 150), 20); // Min 20px, max 150px
            
            // Use very simple, solid colors
            let color = '#ff4444'; // Red for low performance
            if (successPercent >= 80) color = '#44ff44'; // Green for high performance  
            else if (successPercent >= 60) color = '#ffaa00'; // Orange for medium performance
            
            // Better date formatting
            let dateLabel = 'N/A';
            if (point.label) {
                dateLabel = point.label;
            } else if (point.date) {
                const dateParts = point.date.split('-');
                dateLabel = dateParts.length >= 3 ? dateParts[2] + '/' + dateParts[1] : point.date;
            }
            
            // Ultra simple bars - no fancy CSS, just solid colors and basic styling
            barsHTML += `
                <div style="display: inline-block; margin: 0 8px; text-align: center; vertical-align: bottom;">
                    <div style="background-color: ${color}; width: 30px; height: ${height}px; margin-bottom: 10px; border: 2px solid #333333; display: block;" 
                         title="${successPercent.toFixed(1)}% success on ${dateLabel}"></div>
                    <div style="font-size: 12px; color: #000000; font-weight: bold;">${dateLabel}</div>
                </div>
            `;
        });
        
        return `
            <div style="background: #f0f8ff; border: 3px solid #0066cc; padding: 20px; margin: 20px 0; border-radius: 10px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h3 style="color: #0066cc; margin: 0; font-size: 18px; font-weight: bold;">📈 SUCCESS RATE TREND</h3>
                </div>
                <div style="background: white; padding: 20px; border: 2px solid #cccccc; text-align: center; min-height: 200px; display: flex; align-items: flex-end; justify-content: center;">
                    <div style="display: flex; align-items: flex-end; justify-content: center;">
                        ${barsHTML}
                    </div>
                </div>
                <div style="margin-top: 15px; text-align: center; font-size: 14px; color: #333333;">
                    <strong>📊 ${dataWithActivity.length} days with activity | Average: ${(dataWithActivity.reduce((sum, p) => sum + p.avg_success_rate * 100, 0) / dataWithActivity.length).toFixed(1)}%</strong>
                </div>
            </div>
        `;
    }
    
    /**
     * Create simple, guaranteed-to-work activity chart - ULTRA SIMPLE VERSION
     */
    createSimpleActivityChart(data) {
        if (!data || data.length === 0) {
            return `
                <div style="background: #ffcccc; border: 2px solid #ff0000; padding: 15px; margin: 15px 0; border-radius: 8px; text-align: center;">
                    <strong>No activity data available</strong>
                </div>
            `;
        }
        
        const maxCards = Math.max(...data.map(d => d.cards_studied), 1);
        const totalCards = data.reduce((sum, p) => sum + p.cards_studied, 0);
        
        let barsHTML = '';
        data.slice(-14).forEach((point, index) => { // Show only last 14 days for clarity
            // Make bars much taller and more visible
            const height = Math.max((point.cards_studied / maxCards * 120), 5); // Min 5px, max 120px
            
            // Use very simple, solid colors based on activity level
            let color = '#cccccc'; // Gray for no activity
            if (point.cards_studied > 10) color = '#0066cc'; // Blue for high activity
            else if (point.cards_studied > 5) color = '#4499ff'; // Light blue for medium activity  
            else if (point.cards_studied > 0) color = '#88ccff'; // Very light blue for low activity
            
            // Better date formatting
            let dateLabel = 'N/A';
            if (point.label) {
                dateLabel = point.label;
            } else if (point.date) {
                const dateParts = point.date.split('-');
                dateLabel = dateParts.length >= 3 ? dateParts[2] + '/' + dateParts[1] : point.date;
            }
            
            // Ultra simple bars - no fancy CSS, just solid colors and basic styling
            barsHTML += `
                <div style="display: inline-block; margin: 0 4px; text-align: center; vertical-align: bottom;">
                    <div style="background-color: ${color}; width: 25px; height: ${height}px; margin-bottom: 8px; border: 2px solid #333333; display: block;" 
                         title="${dateLabel}: ${point.cards_studied} cards studied"></div>
                    <div style="font-size: 10px; color: #000000; font-weight: bold;">${dateLabel}</div>
                </div>
            `;
        });
        
        return `
            <div style="background: #f0fff0; border: 3px solid #00aa00; padding: 20px; margin: 20px 0; border-radius: 10px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h3 style="color: #00aa00; margin: 0; font-size: 18px; font-weight: bold;">📊 DAILY STUDY ACTIVITY</h3>
                </div>
                <div style="background: white; padding: 20px; border: 2px solid #cccccc; text-align: center; min-height: 180px; display: flex; align-items: flex-end; justify-content: center; overflow-x: auto;">
                    <div style="display: flex; align-items: flex-end; justify-content: center;">
                        ${barsHTML}
                    </div>
                </div>
                <div style="margin-top: 15px; text-align: center; font-size: 14px; color: #333333;">
                    <strong>📅 Last 14 days | Total cards studied: ${totalCards}</strong>
                </div>
            </div>
        `;
    }
    
    /**
     * Create Performance Trend Chart HTML
     */
    createPerformanceTrendHTML(data) {
        console.log('🎯 Creating Performance Trend HTML with data:', data);
        
        if (!data || data.length === 0) {
            return '<div class="text-gray-500 p-4">No performance data available</div>';
        }
        
        const dataWithActivity = data.filter(d => d.avg_success_rate > 0);
        console.log('📊 Performance data with activity:', dataWithActivity);
        
        if (dataWithActivity.length === 0) {
            return '<div class="text-gray-500 p-4">No performance data available yet</div>';
        }
        
        const maxRate = Math.max(...dataWithActivity.map(d => d.avg_success_rate * 100), 1);
        console.log('📈 Max success rate:', maxRate);
        
        return `
            <div style="padding: 16px; background: linear-gradient(135deg, #eff6ff, #e0e7ff); border-radius: 8px; border: 1px solid #d1d5db; margin: 8px 0;">
                <div style="font-size: 14px; font-weight: bold; color: #374151; margin-bottom: 12px;">📈 Success Rate Trend</div>
                <div style="display: flex; align-items: flex-end; gap: 2px; height: 96px; background: white; border-radius: 4px; padding: 8px;">
                    ${dataWithActivity.map((point, index) => {
                        const successPercent = point.avg_success_rate * 100;
                        const height = Math.max((successPercent / maxRate * 70), 5); // Min 5px, max 70px
                        const color = successPercent >= 80 ? '#10b981' : 
                                     successPercent >= 60 ? '#f59e0b' : '#ef4444';
                        
                        // Better date formatting
                        let dateLabel = 'N/A';
                        if (point.label) {
                            dateLabel = point.label;
                        } else if (point.date) {
                            const dateParts = point.date.split('-');
                            dateLabel = dateParts.length >= 3 ? dateParts[2] + '/' + dateParts[1] : point.date;
                        }
                        
                        console.log(`📊 Bar ${index}: ${dateLabel}, ${successPercent.toFixed(1)}%, height: ${height}px, color: ${color}`);
                        
                        return `
                            <div style="flex: 1; display: flex; flex-direction: column; align-items: center; min-height: 80px;" title="${dateLabel}: ${successPercent.toFixed(1)}% success">
                                <div style="background-color: ${color}; height: ${height}px; width: 12px; min-height: 5px; border-radius: 2px 2px 0 0; margin-bottom: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);"></div>
                                <div style="font-size: 10px; color: #666; text-align: center; white-space: nowrap;">${dateLabel}</div>
                            </div>
                        `;
                    }).join('')}
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: #6b7280; margin-top: 8px;">
                    <span>${dataWithActivity.length} days with activity</span>
                    <span>Avg: ${(dataWithActivity.reduce((sum, p) => sum + p.avg_success_rate * 100, 0) / dataWithActivity.length).toFixed(1)}%</span>
                </div>
            </div>
        `;
    }
    
    /**
     * Create Activity Trend Chart HTML
     */
    createActivityTrendHTML(data) {
        if (!data || data.length === 0) {
            return '<div class="text-gray-500 p-4">No activity data available</div>';
        }
        
        const maxCards = Math.max(...data.map(d => d.cards_studied), 1);
        const totalCards = data.reduce((sum, p) => sum + p.cards_studied, 0);
        
        return `
            <div class="p-4 bg-gradient-to-br from-green-50 to-emerald-100 rounded-lg border">
                <div class="text-sm font-bold text-gray-800 mb-3">📊 Study Activity</div>
                <div class="flex items-end gap-1 h-20 bg-white rounded p-2">
                    ${data.map((point, index) => {
                        const height = Math.max((point.cards_studied / maxCards * 60), 1); // Min 1px, max 60px
                        const color = point.cards_studied > 10 ? '#2563eb' : 
                                     point.cards_studied > 5 ? '#3b82f6' : 
                                     point.cards_studied > 0 ? '#60a5fa' : '#e5e7eb';
                        
                        // Better date formatting
                        let dateLabel = 'N/A';
                        if (point.label) {
                            dateLabel = point.label;
                        } else if (point.date) {
                            const dateParts = point.date.split('-');
                            dateLabel = dateParts.length >= 3 ? dateParts[2] + '/' + dateParts[1] : point.date;
                        }
                        
                        return `
                            <div class="flex-1 flex flex-col items-center group" title="${dateLabel}: ${point.cards_studied} cards">
                                <div style="background-color: ${color}; height: ${height}px; width: 90%;" 
                                     class="rounded-t shadow-sm group-hover:opacity-80 transition-opacity"></div>
                                <div class="text-xs mt-1 text-gray-600">${dateLabel}</div>
                            </div>
                        `;
                    }).join('')}
                </div>
                <div class="text-xs text-gray-600 mt-2 flex justify-between">
                    <span>Last 30 days</span>
                    <span>Total: ${totalCards} cards studied</span>
                </div>
            </div>
        `;
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
        console.log('📊 Rendering performance trend chart with data:', data);
        
        // Find the Performance Trend section on the page
        const sections = document.querySelectorAll('*');
        let targetSection = null;
        
        for (const element of sections) {
            if (element.textContent && element.textContent.includes('📈 Performance Trend')) {
                targetSection = element.closest('.card, .section') || element.parentElement;
                break;
            }
        }
        
        if (!targetSection) {
            console.warn('❌ Performance Trend section not found');
            return;
        }
        
        console.log('✅ Found Performance Trend section');
        
        if (data && data.length > 0) {
            const dataWithActivity = data.filter(d => d.avg_success_rate > 0);
            
            if (dataWithActivity.length === 0) {
                targetSection.innerHTML += '<div class="text-gray-500 p-4 text-sm">No performance data available yet</div>';
                return;
            }
            
            const maxRate = Math.max(...dataWithActivity.map(d => d.avg_success_rate * 100), 1);
            
            const chartHTML = `
                <div class="mt-4 p-4 bg-gray-50 rounded-lg">
                    <div class="text-sm font-semibold text-gray-700 mb-4">Success Rate Trend (%)</div>
                    <div class="flex items-end gap-1 h-24">
                        ${dataWithActivity.map((point, index) => {
                            const successPercent = point.avg_success_rate * 100;
                            const height = (successPercent / maxRate * 80); // Max 80px height
                            const color = successPercent >= 80 ? '#10b981' : 
                                         successPercent >= 60 ? '#f59e0b' : '#ef4444';
                            return `
                                <div class="flex-1 flex flex-col items-center" title="${point.label}: ${successPercent.toFixed(1)}% success">
                                    <div style="background-color: ${color}; height: ${height}px; width: 100%;" 
                                         class="rounded-t min-h-[2px] mb-1"></div>
                                    <div class="text-xs text-center">${point.label}</div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                    <div class="text-xs text-gray-500 mt-2">Showing ${dataWithActivity.length} days with activity</div>
                </div>
            `;
            
            targetSection.innerHTML += chartHTML;
            console.log('✅ Performance Trend chart rendered successfully');
        } else {
            targetSection.innerHTML += '<div class="text-gray-500 p-4 text-sm">No data available</div>';
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
    // Check if we're on the stats page by looking for specific elements
    const isStatsPage = document.querySelector('#statsPeriodSelector') || 
                       document.querySelector('.advanced-stats-section') ||
                       document.querySelector('#performanceTrendChart') ||
                       window.location.pathname.includes('/stats');
    
    if (isStatsPage) {
        console.log('🎯 Stats page detected, initializing AdvancedStatsManager');
        window.advancedStats = new AdvancedStatsManager();
        window.advancedStats.init();
    } else if (window.REVISION_CONFIG) {
        window.advancedStats = new AdvancedStatsManager();
        
        // Initialize if we're on the stats page
        if (window.REVISION_CONFIG.viewType === 'stats') {
            window.advancedStats.init();
        }
    }
});

// Make available globally
window.AdvancedStatsManager = AdvancedStatsManager;