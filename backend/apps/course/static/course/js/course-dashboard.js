// Course Dashboard JavaScript - Modern interactions and functionality

class CourseDashboard {
    constructor() {
        this.currentView = 'grid';
        this.filters = {
            level: '',
            price: '',
            language: '',
            status: 'all'
        };
        this.searchTimeout = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSearch();
        this.setupFilters();
        this.setupAnimations();
        this.loadUserProgress();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('[data-bs-toggle="pill"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                this.onTabSwitch(e.target.id);
            });
        });

        // View toggle
        document.querySelectorAll('.view-toggle .btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.toggleView(e.target.dataset.view);
            });
        });

        // Course filter
        document.getElementById('courseFilter')?.addEventListener('change', (e) => {
            this.filterMyCourses(e.target.value);
        });

        // Marketplace filters
        ['levelFilter', 'priceFilter', 'languageFilter'].forEach(id => {
            document.getElementById(id)?.addEventListener('change', (e) => {
                this.filters[id.replace('Filter', '')] = e.target.value;
                this.filterMarketplaceCourses();
            });
        });

        // Search functionality
        document.getElementById('courseSearch')?.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    setupSearch() {
        const searchInput = document.getElementById('courseSearch');
        if (!searchInput) return;

        // Add search suggestions dropdown
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'search-suggestions';
        suggestionsContainer.style.display = 'none';
        searchInput.parentNode.appendChild(suggestionsContainer);

        searchInput.addEventListener('focus', () => {
            this.showSearchSuggestions();
        });

        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                suggestionsContainer.style.display = 'none';
            }, 200);
        });
    }

    setupFilters() {
        // Initialize filter state from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        Object.keys(this.filters).forEach(key => {
            const value = urlParams.get(key);
            if (value) {
                this.filters[key] = value;
                const filterElement = document.getElementById(key + 'Filter');
                if (filterElement) {
                    filterElement.value = value;
                }
            }
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
        document.querySelectorAll('.course-card, .marketplace-course-card').forEach(card => {
            observer.observe(card);
        });
    }

    onTabSwitch(tabId) {
        // Update URL without page reload
        const tabName = tabId.replace('-tab', '');
        const newUrl = new URL(window.location);
        newUrl.searchParams.set('tab', tabName);
        history.replaceState(null, '', newUrl);

        // Load tab-specific data
        switch (tabName) {
            case 'my-learning':
                this.loadMyLearningData();
                break;
            case 'marketplace':
                this.loadMarketplaceData();
                break;
            case 'browse':
                this.loadBrowseData();
                break;
        }

        // Analytics
        this.trackEvent('tab_switch', { tab: tabName });
    }

    toggleView(view) {
        this.currentView = view;
        
        // Update button states
        document.querySelectorAll('.view-toggle .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`).classList.add('active');

        // Update course grid layout
        const coursesContainer = document.querySelector('.marketplace-courses');
        if (coursesContainer) {
            coursesContainer.className = `marketplace-courses view-${view}`;
        }

        // Save preference
        localStorage.setItem('preferredView', view);
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
        this.updateCourseCount(visibleCourses, 'my-courses');
    }

    filterMarketplaceCourses() {
        const courseCards = document.querySelectorAll('.marketplace-course-card');
        let visibleCount = 0;

        courseCards.forEach(card => {
            const courseData = this.getCourseDataFromCard(card);
            const shouldShow = this.shouldShowCourse(courseData);
            
            const parentCol = card.closest('.col-md-6, .col-lg-4, .col-xl-3');
            if (parentCol) {
                parentCol.style.display = shouldShow ? 'block' : 'none';
                if (shouldShow) {
                    visibleCount++;
                    card.classList.add('fade-in');
                }
            }
        });

        this.updateCourseCount(visibleCount, 'marketplace');
        this.updateURL();
    }

    getCourseDataFromCard(card) {
        return {
            level: card.querySelector('.course-level-badge')?.textContent || '',
            price: card.querySelector('.price')?.textContent || '',
            title: card.querySelector('.course-title')?.textContent || '',
            instructor: card.querySelector('.course-instructor')?.textContent || '',
            isFree: card.querySelector('.free-badge') !== null
        };
    }

    shouldShowCourse(courseData) {
        // Level filter
        if (this.filters.level && !courseData.level.includes(this.filters.level)) {
            return false;
        }

        // Price filter
        if (this.filters.price) {
            if (this.filters.price === 'free' && !courseData.isFree) {
                return false;
            }
            if (this.filters.price === 'paid' && courseData.isFree) {
                return false;
            }
        }

        // Language filter (would need language data in course cards)
        if (this.filters.language) {
            // Implementation depends on how language data is stored
        }

        return true;
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

        const activeTab = document.querySelector('.nav-link.active').id;
        
        if (activeTab === 'my-learning-tab') {
            this.searchMyCourses(query);
        } else if (activeTab === 'marketplace-tab') {
            this.searchMarketplace(query);
        }

        this.trackEvent('search', { query, tab: activeTab });
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

        this.updateSearchResults(matchCount, query);
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

        this.updateSearchResults(matchCount, query);
    }

    highlightSearchTerm(element, term) {
        // Remove existing highlights
        element.querySelectorAll('.search-highlight').forEach(el => {
            el.outerHTML = el.innerHTML;
        });

        // Add new highlights
        const textNodes = this.getTextNodes(element);
        textNodes.forEach(node => {
            const regex = new RegExp(`(${term})`, 'gi');
            if (regex.test(node.textContent)) {
                const highlightedText = node.textContent.replace(regex, '<span class="search-highlight">$1</span>');
                const wrapper = document.createElement('div');
                wrapper.innerHTML = highlightedText;
                node.parentNode.replaceChild(wrapper.firstChild, node);
            }
        });
    }

    getTextNodes(element) {
        const textNodes = [];
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim()) {
                textNodes.push(node);
            }
        }

        return textNodes;
    }

    showSearchSuggestions() {
        const suggestions = [
            'Français débutant',
            'Anglais conversation',
            'Grammaire espagnole',
            'Vocabulaire business',
            'Prononciation anglaise'
        ];

        const container = document.querySelector('.search-suggestions');
        container.innerHTML = suggestions.map(suggestion => 
            `<div class="suggestion-item" onclick="courseDashboard.selectSuggestion('${suggestion}')">${suggestion}</div>`
        ).join('');
        container.style.display = 'block';
    }

    selectSuggestion(suggestion) {
        document.getElementById('courseSearch').value = suggestion;
        this.performSearch(suggestion);
        document.querySelector('.search-suggestions').style.display = 'none';
    }

    clearSearchResults() {
        // Show all items
        document.querySelectorAll('.course-item, .col-md-6, .col-lg-4, .col-xl-3').forEach(item => {
            item.style.display = 'block';
        });

        // Remove highlights
        document.querySelectorAll('.search-highlight').forEach(el => {
            el.outerHTML = el.innerHTML;
        });

        // Clear search results message
        const resultsMessage = document.querySelector('.search-results-message');
        if (resultsMessage) {
            resultsMessage.remove();
        }
    }

    updateSearchResults(count, query) {
        // Remove existing message
        const existingMessage = document.querySelector('.search-results-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Add new message
        const message = document.createElement('div');
        message.className = 'search-results-message alert alert-info';
        message.innerHTML = `
            <i class="fas fa-search me-2"></i>
            ${count} résultat${count !== 1 ? 's' : ''} pour "${query}"
            <button type="button" class="btn-close" onclick="courseDashboard.clearSearchResults()"></button>
        `;

        const activeTabContent = document.querySelector('.tab-pane.active');
        if (activeTabContent) {
            activeTabContent.insertBefore(message, activeTabContent.firstElementChild.nextSibling);
        }
    }

    updateCourseCount(count, context) {
        const countElement = document.querySelector(`.${context}-count`);
        if (countElement) {
            countElement.textContent = count;
        }
    }

    updateURL() {
        const url = new URL(window.location);
        Object.keys(this.filters).forEach(key => {
            if (this.filters[key]) {
                url.searchParams.set(key, this.filters[key]);
            } else {
                url.searchParams.delete(key);
            }
        });
        history.replaceState(null, '', url);
    }

    handleKeyboardShortcuts(e) {
        // Cmd/Ctrl + K for search focus
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('courseSearch')?.focus();
        }

        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.getElementById('courseSearch');
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                this.clearSearchResults();
            }
        }

        // Arrow keys for tab navigation
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            const tabs = document.querySelectorAll('[data-bs-toggle="pill"]');
            const activeTab = document.querySelector('.nav-link.active');
            const currentIndex = Array.from(tabs).indexOf(activeTab);
            
            let newIndex;
            if (e.key === 'ArrowLeft') {
                newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
            } else {
                newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
            }
            
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                tabs[newIndex].click();
            }
        }
    }

    loadMyLearningData() {
        // Load user's enrolled courses and progress
        this.showLoadingState('.my-courses-section');
        
        fetch('/api/v1/course/progress/dashboard/')
            .then(response => response.json())
            .then(data => {
                this.updateMyLearningContent(data);
            })
            .catch(error => {
                console.error('Error loading my learning data:', error);
                this.showErrorState('.my-courses-section');
            });
    }

    loadMarketplaceData() {
        if (document.querySelector('.marketplace-courses .course-card')) {
            return; // Already loaded
        }

        this.showLoadingState('.marketplace-courses');
        
        fetch('/api/v1/course/units/')
            .then(response => response.json())
            .then(data => {
                this.updateMarketplaceContent(data);
            })
            .catch(error => {
                console.error('Error loading marketplace data:', error);
                this.showErrorState('.marketplace-courses');
            });
    }

    loadBrowseData() {
        // Load category statistics and featured content
        console.log('Loading browse data...');
    }

    loadUserProgress() {
        // Load overall user progress and statistics
        fetch('/api/v1/course/progress/statistics/')
            .then(response => response.json())
            .then(data => {
                this.updateUserStats(data);
            })
            .catch(error => {
                console.error('Error loading user progress:', error);
            });
    }

    updateMyLearningContent(data) {
        // Update continue learning section
        if (data.recommended_lessons && data.recommended_lessons.length > 0) {
            this.renderContinueLearning(data.recommended_lessons);
        }

        // Update user stats
        if (data.user_progress) {
            this.updateUserStats(data.user_progress);
        }

        this.hideLoadingState('.my-courses-section');
    }

    updateMarketplaceContent(data) {
        // Render marketplace courses
        this.renderMarketplaceCourses(data);
        this.hideLoadingState('.marketplace-courses');
    }

    updateUserStats(stats) {
        // Update streak days
        const streakElement = document.querySelector('.stat-number');
        if (streakElement) {
            this.animateNumber(streakElement, stats.streak_days || 0);
        }

        // Update XP
        const xpElements = document.querySelectorAll('.stat-number');
        if (xpElements[1]) {
            this.animateNumber(xpElements[1], stats.total_xp || 0);
        }

        // Update level
        const levelElements = document.querySelectorAll('.stat-number');
        if (levelElements[2]) {
            levelElements[2].textContent = stats.level || 'A1';
        }
    }

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

    showLoadingState(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.classList.add('loading');
            element.innerHTML = '<div class="loading-skeleton"></div>'.repeat(3);
        }
    }

    hideLoadingState(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.classList.remove('loading');
        }
    }

    showErrorState(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.innerHTML = `
                <div class="error-state text-center py-4">
                    <i class="fas fa-exclamation-triangle text-warning mb-3" style="font-size: 2rem;"></i>
                    <h5>Erreur de chargement</h5>
                    <p class="text-muted">Une erreur est survenue lors du chargement des données.</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        <i class="fas fa-refresh me-2"></i>Réessayer
                    </button>
                </div>
            `;
        }
    }

    trackEvent(eventName, data) {
        // Analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, {
                'custom_parameter': JSON.stringify(data)
            });
        }
        console.log('Event tracked:', eventName, data);
    }
}

// Initialize dashboard when DOM is loaded
function initializeDashboard() {
    window.courseDashboard = new CourseDashboard();
    
    // Check for URL parameters to set initial state
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    if (tab) {
        const tabElement = document.getElementById(`${tab}-tab`);
        if (tabElement) {
            tabElement.click();
        }
    }

    // Restore preferred view
    const preferredView = localStorage.getItem('preferredView');
    if (preferredView) {
        courseDashboard.toggleView(preferredView);
    }
}

// Utility functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours > 0) {
        return `${hours}h ${mins}min`;
    }
    return `${mins}min`;
}