/**
 * Documents App - Comprehensive JavaScript Error Handling & Logging
 * Complements the Python backend error handling system
 */

// Global error handler configuration
window.DocumentsErrorHandler = {
    apiBaseUrl: '/documents/api/v1/',
    debugMode: document.documentElement.dataset.debug === 'True',
    userId: document.documentElement.dataset.userId,
    sessionId: this.generateSessionId(),
    
    // Error tracking
    errorCount: 0,
    errorHistory: [],
    maxErrorHistory: 50,
    
    // Performance tracking
    performanceMetrics: {},
    
    // Initialize error handling
    init() {
        this.setupGlobalErrorHandlers();
        this.setupUnhandledRejectionHandler();
        this.setupPerformanceMonitoring();
        this.setupUserActionTracking();
        this.startHeartbeat();
        
        console.log('🛡️ Documents Error Handler initialized');
    },
    
    // Generate unique session ID
    generateSessionId() {
        return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    },
    
    // Setup global error handlers
    setupGlobalErrorHandlers() {
        window.addEventListener('error', (event) => {
            this.logError({
                type: 'javascript_error',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                stack: event.error?.stack,
                url: window.location.href,
                userAgent: navigator.userAgent,
                timestamp: new Date().toISOString()
            });
        });
        
        // Console error override for better tracking
        const originalConsoleError = console.error;
        console.error = (...args) => {
            this.logError({
                type: 'console_error',
                message: args.join(' '),
                args: args,
                stack: new Error().stack,
                timestamp: new Date().toISOString()
            });
            originalConsoleError.apply(console, args);
        };
    },
    
    // Setup unhandled promise rejection handler
    setupUnhandledRejectionHandler() {
        window.addEventListener('unhandledrejection', (event) => {
            this.logError({
                type: 'unhandled_promise_rejection',
                reason: event.reason,
                promise: event.promise,
                stack: event.reason?.stack,
                timestamp: new Date().toISOString()
            });
        });
    },
    
    // Setup performance monitoring
    setupPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    this.logPerformance({
                        type: 'page_load',
                        loadTime: perfData.loadEventEnd - perfData.loadEventStart,
                        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                        responseTime: perfData.responseEnd - perfData.requestStart,
                        timestamp: new Date().toISOString()
                    });
                }
            }, 100);
        });
        
        // Monitor resource loading
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.duration > 1000) { // Log slow resources
                    this.logPerformance({
                        type: 'slow_resource',
                        name: entry.name,
                        duration: entry.duration,
                        size: entry.transferSize,
                        timestamp: new Date().toISOString()
                    });
                }
            }
        });
        
        try {
            observer.observe({entryTypes: ['resource']});
        } catch (e) {
            console.warn('Performance observer not supported');
        }
    },
    
    // Setup user action tracking
    setupUserActionTracking() {
        // Track clicks on important elements
        document.addEventListener('click', (event) => {
            const target = event.target.closest('[data-track-click]');
            if (target) {
                this.logUserAction({
                    type: 'click',
                    element: target.tagName.toLowerCase(),
                    action: target.dataset.trackClick,
                    text: target.textContent?.slice(0, 50),
                    timestamp: new Date().toISOString()
                });
            }
        });
        
        // Track form submissions
        document.addEventListener('submit', (event) => {
            const form = event.target;
            this.logUserAction({
                type: 'form_submit',
                formId: form.id,
                action: form.action,
                method: form.method,
                timestamp: new Date().toISOString()
            });
        });
        
        // Track navigation
        let currentPath = location.pathname;
        const trackNavigation = () => {
            if (location.pathname !== currentPath) {
                this.logUserAction({
                    type: 'navigation',
                    from: currentPath,
                    to: location.pathname,
                    timestamp: new Date().toISOString()
                });
                currentPath = location.pathname;
            }
        };
        
        window.addEventListener('popstate', trackNavigation);
        
        // Override history methods for SPA navigation tracking
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;
        
        history.pushState = function(...args) {
            originalPushState.apply(this, args);
            trackNavigation();
        };
        
        history.replaceState = function(...args) {
            originalReplaceState.apply(this, args);
            trackNavigation();
        };
    },
    
    // Log errors with context
    logError(errorData) {
        this.errorCount++;
        
        const enrichedError = {
            ...errorData,
            errorId: this.generateErrorId(),
            sessionId: this.sessionId,
            userId: this.userId,
            errorCount: this.errorCount,
            url: window.location.href,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            memory: this.getMemoryUsage(),
            connection: this.getConnectionInfo()
        };
        
        // Add to error history
        this.errorHistory.unshift(enrichedError);
        if (this.errorHistory.length > this.maxErrorHistory) {
            this.errorHistory.pop();
        }
        
        // Console logging for development
        if (this.debugMode) {
            console.group('🚨 Error Logged');
            console.error(enrichedError);
            console.groupEnd();
        }
        
        // Send to backend
        this.sendToBackend('error', enrichedError);
        
        // Show user notification for critical errors
        if (errorData.type === 'javascript_error' || errorData.type === 'unhandled_promise_rejection') {
            this.showErrorNotification(errorData);
        }
    },
    
    // Log performance metrics
    logPerformance(performanceData) {
        const enrichedPerformance = {
            ...performanceData,
            sessionId: this.sessionId,
            userId: this.userId,
            url: window.location.href
        };
        
        // Store metrics
        const metricKey = performanceData.type;
        if (!this.performanceMetrics[metricKey]) {
            this.performanceMetrics[metricKey] = [];
        }
        this.performanceMetrics[metricKey].push(enrichedPerformance);
        
        // Console logging for development
        if (this.debugMode) {
            console.log('⚡ Performance:', enrichedPerformance);
        }
        
        // Send to backend
        this.sendToBackend('performance', enrichedPerformance);
    },
    
    // Log user actions
    logUserAction(actionData) {
        const enrichedAction = {
            ...actionData,
            sessionId: this.sessionId,
            userId: this.userId,
            url: window.location.href
        };
        
        // Console logging for development
        if (this.debugMode) {
            console.log('👤 User Action:', enrichedAction);
        }
        
        // Send to backend
        this.sendToBackend('user_action', enrichedAction);
    },
    
    // Enhanced API request handler with error handling
    async apiRequest(endpoint, options = {}) {
        const startTime = performance.now();
        const requestId = this.generateRequestId();
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                'X-Request-ID': requestId
            },
            credentials: 'same-origin'
        };
        
        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            this.logUserAction({
                type: 'api_request_start',
                endpoint: endpoint,
                method: finalOptions.method || 'GET',
                requestId: requestId
            });
            
            const response = await fetch(this.apiBaseUrl + endpoint, finalOptions);
            const duration = performance.now() - startTime;
            
            // Log API performance
            this.logPerformance({
                type: 'api_request',
                endpoint: endpoint,
                method: finalOptions.method || 'GET',
                status: response.status,
                duration: duration,
                requestId: requestId
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new APIError(response.status, errorData, endpoint, requestId);
            }
            
            const data = await response.json();
            
            this.logUserAction({
                type: 'api_request_success',
                endpoint: endpoint,
                status: response.status,
                duration: duration,
                requestId: requestId
            });
            
            return data;
            
        } catch (error) {
            const duration = performance.now() - startTime;
            
            this.logError({
                type: 'api_request_error',
                endpoint: endpoint,
                method: finalOptions.method || 'GET',
                error: error.message,
                stack: error.stack,
                duration: duration,
                requestId: requestId
            });
            
            throw error;
        }
    },
    
    // Send data to backend
    async sendToBackend(type, data) {
        try {
            await fetch('/documents/api/v1/logging/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    type: type,
                    data: data,
                    timestamp: new Date().toISOString()
                }),
                credentials: 'same-origin'
            });
        } catch (error) {
            // Fail silently for logging endpoint errors to avoid infinite loops
            if (this.debugMode) {
                console.warn('Failed to send log to backend:', error);
            }
        }
    },
    
    // Show error notification to user
    showErrorNotification(errorData) {
        if (this.errorCount > 5) return; // Don't spam users
        
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Une erreur s'est produite</strong><br>
                ${this.debugMode ? errorData.message : 'Veuillez recharger la page si le problème persiste.'}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    },
    
    // Utility functions
    generateErrorId() {
        return 'err_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
    },
    
    generateRequestId() {
        return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
    },
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    },
    
    getMemoryUsage() {
        if (performance.memory) {
            return {
                used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
            };
        }
        return null;
    },
    
    getConnectionInfo() {
        if (navigator.connection) {
            return {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt
            };
        }
        return null;
    },
    
    // Heartbeat to track session activity
    startHeartbeat() {
        setInterval(() => {
            this.sendToBackend('heartbeat', {
                sessionId: this.sessionId,
                userId: this.userId,
                errorCount: this.errorCount,
                performanceMetrics: Object.keys(this.performanceMetrics).length
            });
        }, 60000); // Every minute
    },
    
    // Manual error reporting
    reportIssue(description, category = 'user_report') {
        this.logError({
            type: 'user_reported_issue',
            category: category,
            description: description,
            url: window.location.href,
            timestamp: new Date().toISOString()
        });
        
        alert('Merci pour votre signalement. Notre équipe va examiner le problème.');
    },
    
    // Get error summary for debugging
    getErrorSummary() {
        return {
            totalErrors: this.errorCount,
            recentErrors: this.errorHistory.slice(0, 10),
            performanceMetrics: this.performanceMetrics,
            sessionId: this.sessionId
        };
    }
};

// Custom API Error class
class APIError extends Error {
    constructor(status, data, endpoint, requestId) {
        super(data.message || `API Error ${status}`);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
        this.endpoint = endpoint;
        this.requestId = requestId;
    }
}

// Document ready initialization
document.addEventListener('DOMContentLoaded', function() {
    window.DocumentsErrorHandler.init();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.DocumentsErrorHandler;
}