// Learning Dashboard JavaScript

class LearningDashboard {
    constructor() {
        this.currentTab = 'my-learning';
        this.filters = {
            status: 'all',
            level: '',
            language: ''
        };
        this.searchTimeout = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSearch();
        this.setupAnimations();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('[data-bs-toggle="pill"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                this.onTabSwitch(e.target.id);
            });
        });

        // Course filter
        const courseFilter = document.getElementById('courseFilter');
        if (courseFilter) {
            courseFilter.addEventListener('change', (e) => {
                this.filterMyCourses(e.target.value);
            });
        }

        // Search functionality
        const searchInput = document.getElementById('searchCourses');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    setupSearch() {
        const searchInput = document.getElementById('searchCourses');
        if (!searchInput) return;

        searchInput.addEventListener('focus', () => {
            searchInput.parentElement.classList.add('focused');
        });

        searchInput.addEventListener('blur', () => {
            searchInput.parentElement.classList.remove('focused');
        });
    }

    setupAnimations() {
        // Intersection Observer for fade-in animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, { threshold: 0.1 });

        // Observe course cards
        document.querySelectorAll('.course-card, .marketplace-course-card, .continue-card').forEach(card => {
            observer.observe(card);
        });
    }

    loadInitialData() {
        // Check for URL parameters to set initial state
        const urlParams = new URLSearchParams(window.location.search);
        const tab = urlParams.get('tab');
        
        if (tab && tab !== 'my-learning') {
            const tabElement = document.getElementById(`${tab}-tab`);
            if (tabElement) {
                setTimeout(() => {
                    tabElement.click();
                }, 100);
            }
        }

        // Log dashboard data if available
        if (window.dashboardData) {
            console.log('Dashboard initialized with data:', window.dashboardData);
        }
    }

    onTabSwitch(tabId) {
        // Update current tab
        this.currentTab = tabId.replace('-tab', '');
        
        // Update URL without page reload
        const newUrl = new URL(window.location);
        newUrl.searchParams.set('tab', this.currentTab);
        history.replaceState(null, '', newUrl);

        // Log tab switch
        console.log('Switched to tab:', this.currentTab);

        // Tab-specific initialization
        switch (this.currentTab) {
            case 'my-learning':
                this.initMyLearningTab();
                break;
            case 'marketplace':
                this.initMarketplaceTab();
                break;
            case 'browse':
                this.initBrowseTab();
                break;
        }
    }

    initMyLearningTab() {
        console.log('Initializing My Learning tab');
        // Add any specific initialization for my learning tab
    }

    initMarketplaceTab() {
        console.log('Initializing Marketplace tab');
        // Add any specific initialization for marketplace tab
    }

    initBrowseTab() {
        console.log('Initializing Browse tab');
        // Add any specific initialization for browse tab
    }

    filterMyCourses(status) {
        const courseItems = document.querySelectorAll('.course-item');
        
        courseItems.forEach(item => {
            const itemStatus = item.dataset.status;
            const shouldShow = status === 'all' || itemStatus === status;
            
            item.style.display = shouldShow ? 'block' : 'none';
            
            if (shouldShow) {
                item.classList.add('slide-in-left');
            }
        });

        // Update course count
        const visibleCourses = document.querySelectorAll('.course-item:not([style*="display: none"])').length;
        console.log(`Filtered courses: ${visibleCourses} visible with status: ${status}`);
    }

    handleSearch(query) {
        clearTimeout(this.searchTimeout);
        
        this.searchTimeout = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }

    performSearch(query) {
        if (!query.trim()) {
            this.clearSearchResults();
            return;
        }

        console.log('Searching for:', query);

        switch (this.currentTab) {
            case 'my-learning':
                this.searchMyCourses(query);
                break;
            case 'marketplace':
                this.searchMarketplace(query);
                break;
            case 'browse':
                this.searchCategories(query);
                break;
        }
    }

    searchMyCourses(query) {
        const courseItems = document.querySelectorAll('.course-item');
        let matchCount = 0;

        courseItems.forEach(item => {
            const title = item.querySelector('.course-title')?.textContent.toLowerCase() || '';
            const instructor = item.querySelector('.course-instructor')?.textContent.toLowerCase() || '';
            const searchTerm = query.toLowerCase();

            const matches = title.includes(searchTerm) || instructor.includes(searchTerm);
            item.style.display = matches ? 'block' : 'none';
            
            if (matches) {
                matchCount++;
                this.highlightSearchTerm(item, query);
            }
        });

        console.log(`Found ${matchCount} matching courses in My Learning`);
    }

    searchMarketplace(query) {
        const courseCards = document.querySelectorAll('.marketplace-course-card');
        let matchCount = 0;

        courseCards.forEach(card => {
            const title = card.querySelector('.course-title')?.textContent.toLowerCase() || '';
            const instructor = card.querySelector('.course-instructor')?.textContent.toLowerCase() || '';
            const description = card.querySelector('.course-description')?.textContent.toLowerCase() || '';
            const searchTerm = query.toLowerCase();

            const matches = title.includes(searchTerm) || 
                           instructor.includes(searchTerm) || 
                           description.includes(searchTerm);

            const parentCol = card.closest('.col-md-6, .col-lg-4, .col-xl-3');
            if (parentCol) {
                parentCol.style.display = matches ? 'block' : 'none';
                if (matches) {
                    matchCount++;
                    this.highlightSearchTerm(card, query);
                }
            }
        });

        console.log(`Found ${matchCount} matching courses in Marketplace`);
    }

    searchCategories(query) {
        const categoryCards = document.querySelectorAll('.category-card');
        let matchCount = 0;

        categoryCards.forEach(card => {
            const title = card.querySelector('h5')?.textContent.toLowerCase() || '';
            const searchTerm = query.toLowerCase();

            const matches = title.includes(searchTerm);
            card.closest('.col-md-3').style.display = matches ? 'block' : 'none';
            
            if (matches) {
                matchCount++;
            }
        });

        console.log(`Found ${matchCount} matching categories`);
    }

    highlightSearchTerm(element, term) {
        // Simple highlighting - remove existing highlights first
        element.querySelectorAll('.search-highlight').forEach(el => {
            el.outerHTML = el.innerHTML;
        });

        // Add new highlights (simplified version)
        const textElements = element.querySelectorAll('.course-title, .course-instructor, .course-description');
        textElements.forEach(el => {
            const regex = new RegExp(`(${term})`, 'gi');
            if (regex.test(el.textContent)) {
                el.innerHTML = el.textContent.replace(regex, '<span class="search-highlight">$1</span>');
            }
        });
    }

    clearSearchResults() {
        // Show all items
        document.querySelectorAll('.course-item, .col-md-6, .col-lg-4, .col-xl-3, .col-md-3').forEach(item => {
            item.style.display = 'block';
        });

        // Remove highlights
        document.querySelectorAll('.search-highlight').forEach(el => {
            el.outerHTML = el.innerHTML;
        });

        console.log('Search results cleared');
    }

    handleKeyboardShortcuts(e) {
        // Cmd/Ctrl + K for search focus
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('searchCourses')?.focus();
        }

        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.getElementById('searchCourses');
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                this.clearSearchResults();
            }
        }

        // Arrow keys for tab navigation
        if ((e.ctrlKey || e.metaKey) && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
            const tabs = document.querySelectorAll('[data-bs-toggle="pill"]');
            const activeTab = document.querySelector('.nav-link.active');
            const currentIndex = Array.from(tabs).indexOf(activeTab);
            
            let newIndex;
            if (e.key === 'ArrowLeft') {
                newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
            } else {
                newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
            }
            
            e.preventDefault();
            tabs[newIndex].click();
        }
    }

    // Utility methods
    animateNumber(element, targetValue) {
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            element.textContent = currentValue;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    formatDuration(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        
        if (hours > 0) {
            return `${hours}h ${mins}min`;
        }
        return `${mins}min`;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.learningDashboard = new LearningDashboard();
    console.log('Learning Dashboard initialized');
});

// Global functions for template compatibility
function switchToMarketplace() {
    const marketplaceTab = document.getElementById('marketplace-tab');
    if (marketplaceTab) {
        marketplaceTab.click();
    }
}

function continueLesson(lessonId) {
    console.log('Continue lesson:', lessonId);
    // Implementation will be added when lesson pages are created
}

function startCourse(courseId) {
    console.log('Start course:', courseId);
    // Implementation will be added when enrollment system is created
}

function continueCourse(courseId) {
    console.log('Continue course:', courseId);
    // Implementation will be added when course pages are created
}

function enrollCourse(courseId) {
    console.log('Enroll in course:', courseId);
    // Implementation will be added when enrollment system is created
}

function buyCourse(courseId) {
    console.log('Buy course:', courseId);
    // Implementation will be added when payment system is integrated
}

function filterByLanguage(language) {
    switchToMarketplace();
    setTimeout(() => {
        console.log('Filter by language:', language);
        // Implementation will be added when marketplace filters are enhanced
    }, 100);
}