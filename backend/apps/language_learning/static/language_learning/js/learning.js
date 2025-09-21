// Language Learning Alpine.js Components

document.addEventListener('alpine:init', () => {

    // Main Learning Dashboard Component
    Alpine.data('learningDashboard', () => ({
        // State
        selectedLanguage: 'ES',
        selectedLanguageName: 'Español',
        courseUnits: [],
        userProgress: null,
        userStreak: 0,
        activeUnit: null,
        activeUnitModules: [],
        loading: false,
        apiUrls: {},

        // Initialize
        init() {
            console.log('🎯 Learning Dashboard initialized');
            this.loadConfig();
            this.loadDashboardData();
        },

        // Load configuration from the page
        loadConfig() {
            const configScript = document.getElementById('language-learning-config');
            if (configScript) {
                try {
                    const config = JSON.parse(configScript.textContent);
                    this.selectedLanguage = config.selectedLanguage || 'ES';
                    this.apiUrls = config.apiUrls || {};
                    console.log('✅ Config loaded:', config);
                } catch (error) {
                    console.error('❌ Error loading config:', error);
                }
            }
        },

        // Load dashboard data from API
        async loadDashboardData() {
            this.loading = true;
            try {
                const response = await fetch(`${this.apiUrls.dashboard}?lang=${this.selectedLanguage}`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        this.selectedLanguageName = data.selected_language_name;
                        this.courseUnits = data.course_units;
                        this.userProgress = data.user_progress;
                        this.userStreak = data.user_streak;
                        console.log('✅ Dashboard data loaded:', data);
                    } else {
                        console.error('❌ API error:', data.error);
                    }
                } else {
                    console.error('❌ HTTP error:', response.status);
                }
            } catch (error) {
                console.error('❌ Error loading dashboard data:', error);
            } finally {
                this.loading = false;
            }
        },

        // Language selection
        selectLanguage(langCode) {
            console.log('🌍 Language selected:', langCode);
            this.selectedLanguage = langCode;
            this.loadDashboardData();
        },

        // Load unit details
        async loadUnitDetails(unitId) {
            this.loading = true;
            try {
                const response = await fetch(`${this.apiUrls.unitDetail}${unitId}/`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        this.activeUnit = data.unit;
                        this.activeUnitModules = data.modules;
                        console.log('✅ Unit details loaded:', data);
                    } else {
                        console.error('❌ API error:', data.error);
                    }
                } else {
                    console.error('❌ HTTP error:', response.status);
                }
            } catch (error) {
                console.error('❌ Error loading unit details:', error);
            } finally {
                this.loading = false;
            }
        },

        // Go back to units list
        goBackToUnits() {
            this.activeUnit = null;
            this.activeUnitModules = [];
        },

        // Get language flag emoji
        getLanguageFlag(langCode) {
            const flags = {
                'EN': '🇬🇧',
                'FR': '🇫🇷',
                'ES': '🇪🇸',
                'DE': '🇩🇪',
                'IT': '🇮🇹'
            };
            return flags[langCode] || '🌍';
        },

        // Get streak icon based on count
        getStreakIcon(streak) {
            if (streak >= 30) return '🔥';
            if (streak >= 7) return '⚡';
            if (streak >= 3) return '✨';
            return '🌟';
        }
    }));

    // Unit Card Component
    Alpine.data('unitCard', (unit, dashboard) => ({
        unit: unit,

        // Get progress bar width
        get progressWidth() {
            return `${this.unit.progress_percentage || 0}%`;
        },

        // Get progress bar class
        get progressClass() {
            const percentage = this.unit.progress_percentage || 0;
            if (percentage === 100) return 'bg-success';
            if (percentage >= 50) return 'bg-primary';
            if (percentage > 0) return 'bg-warning';
            return 'bg-secondary';
        },

        // Handle unit click
        selectUnit() {
            console.log('📚 Unit selected:', this.unit.id);
            dashboard.loadUnitDetails(this.unit.id);
        }
    }));

    // Module Card Component
    Alpine.data('moduleCard', (module) => ({
        module: module,

        // Get module type badge class
        get badgeClass() {
            const type = this.module.module_type;
            const classes = {
                'vocabulary': 'module-badge vocabulary',
                'grammar': 'module-badge grammar',
                'listening': 'module-badge listening',
                'speaking': 'module-badge speaking',
                'reading': 'module-badge reading',
                'writing': 'module-badge writing',
                'culture': 'module-badge culture',
                'review': 'module-badge review'
            };
            return classes[type] || 'module-badge';
        },

        // Handle module click
        selectModule() {
            if (this.module.is_unlocked) {
                console.log('📖 Module selected:', this.module.id);
                // This will be handled by HTMX
            } else {
                alert('Ce module est verrouillé. Complétez les modules précédents pour y accéder.');
            }
        }
    }));

    // Progress Panel Component
    Alpine.data('progressPanel', (data) => ({
        userStreak: data.userStreak || 0,
        unitsCount: data.unitsCount || 0,
        completedUnitsCount: data.completedUnitsCount || 0,

        // Get completed units count
        get completedUnits() {
            return this.completedUnitsCount;
        },

        // Get streak icon
        get streakIcon() {
            if (this.userStreak >= 30) return '🔥';
            if (this.userStreak >= 7) return '⚡';
            if (this.userStreak >= 3) return '✨';
            return '🌟';
        }
    }));

    // Unit View Component
    Alpine.data('unitView', (unit, modules) => ({
        unit: unit,
        modules: modules || [],

        // Get progress bar width
        get progressWidth() {
            return `${this.unit.progress_percentage || 0}%`;
        },

        // Get progress bar class
        get progressClass() {
            const percentage = this.unit.progress_percentage || 0;
            if (percentage === 100) return 'bg-success';
            if (percentage >= 50) return 'bg-primary';
            if (percentage > 0) return 'bg-warning';
            return 'bg-secondary';
        },

        // Handle back click
        goBack() {
            console.log('🔙 Going back to units list');
            // This will be handled by HTMX
        }
    }));
});

// HTMX Configuration and Event Handlers
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Language Learning App loaded with HTMX + Alpine.js');

    // HTMX event handlers
    document.body.addEventListener('htmx:configRequest', function(evt) {
        // Add CSRF token to all HTMX requests
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            evt.detail.headers['X-CSRFToken'] = csrfToken;
        }
    });

    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        console.log('🔄 HTMX request starting:', evt.detail.xhr.url);
    });

    document.body.addEventListener('htmx:afterRequest', function(evt) {
        console.log('✅ HTMX request completed:', evt.detail.xhr.status);

        // Handle errors
        if (evt.detail.xhr.status >= 400) {
            console.error('❌ HTMX request failed:', evt.detail.xhr.status);
        }
    });

    document.body.addEventListener('htmx:afterSwap', function(evt) {
        console.log('🔄 HTMX content swapped');

        // Reinitialize Alpine components if needed
        if (window.Alpine) {
            Alpine.initTree(evt.target);
        }
    });
});

// Utility functions
window.LearningUtils = {
    // Format duration
    formatDuration(minutes) {
        if (minutes < 60) {
            return `${minutes} min`;
        }
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours}h ${mins}min`;
    },

    // Format XP
    formatXP(xp) {
        if (xp >= 1000) {
            return `${(xp / 1000).toFixed(1)}k XP`;
        }
        return `${xp} XP`;
    },

    // Show notification
    showNotification(message, type = 'success') {
        // Simple notification - could be enhanced with a toast library
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
};