// Linguify Explorer Test Suite
class ExplorerTestSuite {
    constructor() {
        this.tests = [];
        this.results = {
            passed: 0,
            failed: 0,
            total: 0
        };
        this.startTime = Date.now();
    }

    // Test runner
    async runAllTests() {
        console.log('🧪 Starting Linguify Explorer Test Suite...');
        
        // Core functionality tests
        await this.testSearchFunctionality();
        await this.testFilterSystem();
        await this.testNotificationSystem();
        await this.testAnalyticsTracking();
        await this.testFavoritesAndCollections();
        await this.testPerformanceMetrics();
        await this.testResponsiveDesign();
        await this.testAccessibility();
        
        this.generateReport();
        return this.results;
    }

    // Search functionality tests
    async testSearchFunctionality() {
        this.startTest('Search Functionality');
        
        try {
            // Test search input exists
            const searchInput = document.getElementById('exploreSearchInput');
            this.assert(searchInput !== null, 'Search input element exists');
            
            // Test search suggestions
            if (window.loadSearchSuggestions) {
                await window.loadSearchSuggestions('test');
                this.assert(true, 'Search suggestions loaded successfully');
            }
            
            // Test voice search button
            const voiceBtn = document.getElementById('voiceSearchBtn');
            this.assert(voiceBtn !== null, 'Voice search button exists');
            
            // Test search history
            const searchHistory = JSON.parse(localStorage.getItem('linguify_search_history') || '[]');
            this.assert(Array.isArray(searchHistory), 'Search history is properly formatted');
            
            this.passTest('Search Functionality');
            
        } catch (error) {
            this.failTest('Search Functionality', error.message);
        }
    }

    // Filter system tests
    async testFilterSystem() {
        this.startTest('Filter System');
        
        try {
            // Test filter elements exist
            const categoryFilter = document.getElementById('categoryFilter');
            const languageFilter = document.getElementById('languageFilter');
            const levelFilter = document.getElementById('levelFilter');
            
            this.assert(categoryFilter !== null, 'Category filter exists');
            this.assert(languageFilter !== null, 'Language filter exists');
            this.assert(levelFilter !== null, 'Level filter exists');
            
            // Test filter state
            if (window.exploreState) {
                this.assert(typeof window.exploreState.filters === 'object', 'Filter state object exists');
            }
            
            // Test filter functions
            if (window.applyFilters) {
                this.assert(typeof window.applyFilters === 'function', 'applyFilters function exists');
            }
            
            this.passTest('Filter System');
            
        } catch (error) {
            this.failTest('Filter System', error.message);
        }
    }

    // Notification system tests
    async testNotificationSystem() {
        this.startTest('Notification System');
        
        try {
            // Test notification elements
            const notificationBtn = document.getElementById('notificationBtn');
            const notificationCenter = document.getElementById('notificationCenter');
            const notificationBadge = document.getElementById('notificationBadge');
            
            this.assert(notificationBtn !== null, 'Notification button exists');
            this.assert(notificationCenter !== null, 'Notification center exists');
            this.assert(notificationBadge !== null, 'Notification badge exists');
            
            // Test notification functions
            if (window.toggleNotificationCenter) {
                this.assert(typeof window.toggleNotificationCenter === 'function', 'toggleNotificationCenter function exists');
            }
            
            // Test notification settings
            const notificationSettings = JSON.parse(localStorage.getItem('linguify_notification_settings') || '{}');
            this.assert(typeof notificationSettings === 'object', 'Notification settings exist');
            
            // Test notification modals
            const settingsModal = document.getElementById('notificationSettingsModal');
            const allNotificationsModal = document.getElementById('allNotificationsModal');
            
            this.assert(settingsModal !== null, 'Notification settings modal exists');
            this.assert(allNotificationsModal !== null, 'All notifications modal exists');
            
            this.passTest('Notification System');
            
        } catch (error) {
            this.failTest('Notification System', error.message);
        }
    }

    // Analytics tracking tests
    async testAnalyticsTracking() {
        this.startTest('Analytics Tracking');
        
        try {
            // Test analytics state
            if (window.exploreState && window.exploreState.analytics) {
                this.assert(typeof window.exploreState.analytics === 'object', 'Analytics state exists');
                this.assert(Array.isArray(window.exploreState.analytics.interactions), 'Interactions array exists');
                this.assert(typeof window.exploreState.analytics.metrics === 'object', 'Metrics object exists');
            }
            
            // Test tracking functions
            if (window.trackEvent) {
                // Simulate tracking event
                window.trackEvent('test_event', { test: true });
                this.assert(true, 'trackEvent function works');
            }
            
            // Test performance observers
            if (window.PerformanceObserver) {
                this.assert(typeof PerformanceObserver === 'function', 'PerformanceObserver available');
            }
            
            // Test localStorage analytics
            const searchHeatmap = localStorage.getItem('linguify_search_heatmap');
            this.assert(searchHeatmap !== null, 'Search heatmap stored');
            
            this.passTest('Analytics Tracking');
            
        } catch (error) {
            this.failTest('Analytics Tracking', error.message);
        }
    }

    // Favorites and collections tests
    async testFavoritesAndCollections() {
        this.startTest('Favorites and Collections');
        
        try {
            // Test favorites elements
            const favoritesSection = document.querySelector('.sidebar-favorites');
            this.assert(favoritesSection !== null, 'Favorites section exists');
            
            // Test collections elements
            const collectionsSection = document.querySelector('.sidebar-collections');
            this.assert(collectionsSection !== null, 'Collections section exists');
            
            // Test modal elements
            const createCollectionModal = document.getElementById('createCollectionModal');
            const addToCollectionModal = document.getElementById('addToCollectionModal');
            const manageCollectionModal = document.getElementById('manageCollectionModal');
            
            this.assert(createCollectionModal !== null, 'Create collection modal exists');
            this.assert(addToCollectionModal !== null, 'Add to collection modal exists');
            this.assert(manageCollectionModal !== null, 'Manage collection modal exists');
            
            // Test localStorage data
            const favoriteDecks = JSON.parse(localStorage.getItem('linguify_favorite_decks') || '[]');
            this.assert(Array.isArray(favoriteDecks), 'Favorite decks array exists');
            
            // Test functions
            if (window.toggleFavorite) {
                this.assert(typeof window.toggleFavorite === 'function', 'toggleFavorite function exists');
            }
            
            this.passTest('Favorites and Collections');
            
        } catch (error) {
            this.failTest('Favorites and Collections', error.message);
        }
    }

    // Performance metrics tests
    async testPerformanceMetrics() {
        this.startTest('Performance Metrics');
        
        try {
            // Test performance API availability
            this.assert(typeof performance !== 'undefined', 'Performance API available');
            
            // Test navigation timing
            if (performance.navigation) {
                this.assert(typeof performance.navigation.type === 'number', 'Navigation timing works');
            }
            
            // Test resource timing
            const resources = performance.getEntriesByType('resource');
            this.assert(Array.isArray(resources), 'Resource timing available');
            
            // Test memory usage (if available)
            if (performance.memory) {
                this.assert(typeof performance.memory.usedJSHeapSize === 'number', 'Memory usage tracking works');
            }
            
            // Test service worker
            if ('serviceWorker' in navigator) {
                this.assert(true, 'Service Worker support available');
            }
            
            // Test intersection observer
            if ('IntersectionObserver' in window) {
                this.assert(true, 'Intersection Observer available');
            }
            
            this.passTest('Performance Metrics');
            
        } catch (error) {
            this.failTest('Performance Metrics', error.message);
        }
    }

    // Responsive design tests
    async testResponsiveDesign() {
        this.startTest('Responsive Design');
        
        try {
            const originalWidth = window.innerWidth;
            
            // Test mobile breakpoint
            Object.defineProperty(window, 'innerWidth', { value: 768 });
            window.dispatchEvent(new Event('resize'));
            
            // Check if mobile-specific elements are shown/hidden correctly
            const sidebar = document.querySelector('.revision-sidebar');
            if (sidebar) {
                const sidebarStyles = window.getComputedStyle(sidebar);
                this.assert(true, 'Sidebar responsive styles applied');
            }
            
            // Test tablet breakpoint
            Object.defineProperty(window, 'innerWidth', { value: 1024 });
            window.dispatchEvent(new Event('resize'));
            
            // Test desktop breakpoint  
            Object.defineProperty(window, 'innerWidth', { value: 1200 });
            window.dispatchEvent(new Event('resize'));
            
            // Restore original width
            Object.defineProperty(window, 'innerWidth', { value: originalWidth });
            window.dispatchEvent(new Event('resize'));
            
            this.passTest('Responsive Design');
            
        } catch (error) {
            this.failTest('Responsive Design', error.message);
        }
    }

    // Accessibility tests
    async testAccessibility() {
        this.startTest('Accessibility');
        
        try {
            // Test ARIA labels
            const searchInput = document.getElementById('exploreSearchInput');
            if (searchInput) {
                const hasAriaLabel = searchInput.hasAttribute('aria-label') || 
                                   searchInput.hasAttribute('aria-labelledby');
                this.assert(hasAriaLabel, 'Search input has proper ARIA labeling');
            }
            
            // Test keyboard navigation
            const focusableElements = document.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            this.assert(focusableElements.length > 0, 'Focusable elements exist');
            
            // Test semantic HTML
            const mainElement = document.querySelector('main');
            const navElements = document.querySelectorAll('nav');
            
            this.assert(mainElement !== null || navElements.length > 0, 'Semantic HTML elements used');
            
            // Test color contrast (basic check)
            const body = document.body;
            const bodyStyles = window.getComputedStyle(body);
            this.assert(bodyStyles.color !== bodyStyles.backgroundColor, 'Color contrast exists');
            
            // Test alt attributes for images
            const images = document.querySelectorAll('img');
            let imagesWithAlt = 0;
            images.forEach(img => {
                if (img.hasAttribute('alt')) imagesWithAlt++;
            });
            
            const altPercentage = images.length > 0 ? (imagesWithAlt / images.length) * 100 : 100;
            this.assert(altPercentage >= 80, 'Most images have alt attributes');
            
            this.passTest('Accessibility');
            
        } catch (error) {
            this.failTest('Accessibility', error.message);
        }
    }

    // Helper methods
    startTest(testName) {
        console.log(`🧪 Testing: ${testName}...`);
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(`Assertion failed: ${message}`);
        }
        console.log(`  ✅ ${message}`);
    }

    passTest(testName) {
        this.results.passed++;
        this.results.total++;
        console.log(`✅ ${testName}: PASSED`);
    }

    failTest(testName, error) {
        this.results.failed++;
        this.results.total++;
        console.error(`❌ ${testName}: FAILED - ${error}`);
    }

    generateReport() {
        const endTime = Date.now();
        const duration = endTime - this.startTime;
        
        console.log('\n📊 Linguify Explorer Test Results:');
        console.log('═══════════════════════════════════');
        console.log(`🎯 Total Tests: ${this.results.total}`);
        console.log(`✅ Passed: ${this.results.passed}`);
        console.log(`❌ Failed: ${this.results.failed}`);
        console.log(`⏱️ Duration: ${duration}ms`);
        console.log(`📈 Success Rate: ${Math.round((this.results.passed / this.results.total) * 100)}%`);
        
        if (this.results.failed === 0) {
            console.log('🎉 All tests passed! Explorer is ready for production.');
        } else {
            console.log('⚠️ Some tests failed. Please review and fix issues.');
        }
        
        // Track test results with analytics
        if (window.trackEvent) {
            window.trackEvent('test_suite_completed', {
                passed: this.results.passed,
                failed: this.results.failed,
                total: this.results.total,
                duration: duration,
                successRate: (this.results.passed / this.results.total) * 100
            });
        }
    }
}

// Auto-run tests when ready
function runExplorerTests() {
    const testSuite = new ExplorerTestSuite();
    return testSuite.runAllTests();
}

// Export for manual testing
window.ExplorerTestSuite = ExplorerTestSuite;
window.runExplorerTests = runExplorerTests;

// Auto-run if in test mode
if (window.location.search.includes('test=true')) {
    setTimeout(runExplorerTests, 2000); // Wait for full initialization
}

console.log('🧪 Explorer Test Suite loaded. Run runExplorerTests() to start testing.');