/**
 * Explorer Utilities - Performance monitoring et error tracking
 */

// ===== SERVICE WORKER REGISTRATION =====
/**
 * Enregistrement du Service Worker pour la mise en cache
 */
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            const swPath = window.REVISION_CONFIG?.staticUrl ? 
                `${window.REVISION_CONFIG.staticUrl}revision/js/explorer/sw.js` :
                '/static/revision/js/explorer/sw.js';
                
            const scope = window.REVISION_CONFIG?.staticUrl ?
                `${window.REVISION_CONFIG.staticUrl}revision/` :
                '/static/revision/';
                
            navigator.serviceWorker.register(swPath, { scope })
                .then(function(registration) {
                    console.log('🚀 Service Worker registered successfully:', registration.scope);
                })
                .catch(function(error) {
                    console.warn('⚠️ Service Worker registration failed:', error);
                });
        });
    }
}

// ===== PERFORMANCE MONITORING =====
/**
 * Critical Web Vitals monitoring
 * Mesure les métriques de performance et les envoie au tracking
 */
function measureWebVitals() {
    if ('web-vital' in window) return;
    
    // First Contentful Paint
    if ('PerformanceObserver' in window) {
        try {
            new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    if (entry.name === 'first-contentful-paint') {
                        console.log('🎨 FCP:', entry.startTime);
                        if (window.trackEvent) {
                            window.trackEvent('web_vital_fcp', { value: entry.startTime });
                        }
                    }
                }
            }).observe({ entryTypes: ['paint'] });
        } catch (e) {
            console.warn('⚠️ FCP monitoring failed:', e);
        }
        
        // Largest Contentful Paint
        try {
            new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log('🖼️ LCP:', lastEntry.startTime);
                if (window.trackEvent) {
                    window.trackEvent('web_vital_lcp', { value: lastEntry.startTime });
                }
            }).observe({ entryTypes: ['largest-contentful-paint'] });
        } catch (e) {
            console.warn('⚠️ LCP monitoring failed:', e);
        }
        
        // Cumulative Layout Shift
        try {
            let clsValue = 0;
            new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                    }
                }
                console.log('📏 CLS:', clsValue);
                if (window.trackEvent) {
                    window.trackEvent('web_vital_cls', { value: clsValue });
                }
            }).observe({ entryTypes: ['layout-shift'] });
        } catch (e) {
            console.warn('⚠️ CLS monitoring failed:', e);
        }
    }
    
    // First Input Delay (FID) simulation via click event
    document.addEventListener('click', function measureFID() {
        const startTime = performance.now();
        requestAnimationFrame(() => {
            const endTime = performance.now();
            const fid = endTime - startTime;
            console.log('⚡ FID (estimated):', fid);
            if (window.trackEvent) {
                window.trackEvent('web_vital_fid', { value: fid });
            }
        });
        document.removeEventListener('click', measureFID, { once: true });
    }, { once: true });
    
    // Mark as initialized
    window['web-vital'] = true;
}

// ===== ERROR TRACKING =====
/**
 * Gestionnaire d'erreurs JavaScript global
 * Capture les erreurs et les envoie au service de tracking
 */
function setupErrorTracking() {
    // JavaScript Errors
    window.addEventListener('error', function(event) {
        console.error('🚨 JavaScript Error:', event.error);
        if (window.trackEvent) {
            window.trackEvent('javascript_error', {
                message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno,
                stack: event.error ? event.error.stack : null,
                userAgent: navigator.userAgent,
                url: window.location.href,
                timestamp: new Date().toISOString()
            });
        }
    });

    // Unhandled Promise Rejections
    window.addEventListener('unhandledrejection', function(event) {
        console.error('🚨 Unhandled Promise Rejection:', event.reason);
        if (window.trackEvent) {
            window.trackEvent('promise_rejection', {
                reason: event.reason?.toString() || 'Unknown rejection',
                stack: event.reason?.stack || null,
                userAgent: navigator.userAgent,
                url: window.location.href,
                timestamp: new Date().toISOString()
            });
        }
    });
}

// ===== INITIALIZATION =====
/**
 * Initialise tous les utilitaires
 */
function initializeUtilities() {
    // Service Worker
    registerServiceWorker();
    
    // Error tracking
    setupErrorTracking();
    
    // Performance monitoring
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', measureWebVitals);
    } else {
        measureWebVitals();
    }
    
    console.log('🛠️ Explorer utilities initialized');
}

// Auto-initialize when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeUtilities);
} else {
    initializeUtilities();
}

// Export for manual initialization if needed
window.explorerUtils = {
    registerServiceWorker,
    measureWebVitals,
    setupErrorTracking,
    initializeUtilities
};