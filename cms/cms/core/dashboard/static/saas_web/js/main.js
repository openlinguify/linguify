// SaaS Application Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Apply app icon gradients from data attributes
    const appIcons = document.querySelectorAll('.app-icon[data-gradient], .app-icon-simple[data-gradient]');
    appIcons.forEach(icon => {
        const gradient = icon.getAttribute('data-gradient');
        if (gradient) {
            icon.style.background = gradient;
        }
    });

    // Tab switching for dashboard (renamed to avoid conflicts)
    window.showDashboardTab = function(tabName) {
        // Hide all tabs
        document.querySelectorAll('.dashboard-tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Remove active class from all nav links
        document.querySelectorAll('.dashboard-nav .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Show selected tab
        const targetTab = document.getElementById(tabName);
        if (targetTab) {
            targetTab.classList.add('active');
        }
        
        // Add active class to clicked nav link
        if (event && event.target) {
            event.target.classList.add('active');
        }
    };

    // App installation function
    window.installApp = function(appId) {
        const button = event.target.closest('button');
        if (!button) return;
        
        const originalHtml = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Installation...';
        
        // API call to install app
        fetch(`/api/apps/${appId}/install/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                button.innerHTML = '<i class="bi bi-check-circle me-2"></i>Installé';
                button.classList.remove('btn-outline-primary');
                button.classList.add('btn-success');
                
                // Change to open button after a moment
                setTimeout(() => {
                    button.innerHTML = '<i class="bi bi-arrow-right me-2"></i>Ouvrir';
                    button.classList.remove('btn-success');
                    button.classList.add('btn-primary');
                    button.onclick = function() {
                        window.location.href = data.app_url || '#';
                    };
                }, 1000);
            } else {
                showMessage('Erreur lors de l\'installation: ' + (data.error || 'Erreur inconnue'), 'error');
                button.innerHTML = originalHtml;
                button.disabled = false;
            }
        })
        .catch(error => {
            console.error('Installation error:', error);
            showMessage('Erreur de connexion lors de l\'installation.', 'error');
            button.innerHTML = originalHtml;
            button.disabled = false;
        });
    };

    // Get CSRF token
    window.getCsrfToken = function() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.match(/csrftoken=([^;]+)/)?.[1];
    };

    // Show success/error messages
    window.showMessage = function(message, type = 'success') {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const iconClass = type === 'success' ? 'bi-check-circle' : 'bi-exclamation-triangle';
        
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" style="top: 100px; right: 20px; z-index: 9999; max-width: 350px;" role="alert">
                <i class="bi ${iconClass} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alert = document.querySelector('.alert:last-of-type');
            if (alert) alert.remove();
        }, 5000);
    };

    // Dashboard stats loading
    function loadUserStats() {
        fetch('/api/user/stats/')
            .then(response => response.json())
            .then(data => {
                // Update stats in the dashboard
                const statsElements = {
                    'lessons-completed': data.lessons_completed || 0,
                    'study-streak': data.study_streak || 0,
                    'words-learned': data.words_learned || 0,
                    'minutes-today': data.minutes_today || 0
                };
                
                Object.entries(statsElements).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = value.toLocaleString();
                    }
                });
            })
            .catch(error => {
                console.error('Error loading user stats:', error);
            });
    }

    // Load stats if on dashboard
    if (window.location.pathname.includes('/dashboard/')) {
        loadUserStats();
    }

    // Auto-refresh stats every 5 minutes
    setInterval(() => {
        if (window.location.pathname.includes('/dashboard/')) {
            loadUserStats();
        }
    }, 5 * 60 * 1000);

    // Theme switcher (if implemented)
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update toggle icon
            const icon = this.querySelector('i');
            if (icon) {
                icon.className = newTheme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
            }
        });
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    // App card hover effects
    document.querySelectorAll('.app-card-simple').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Initialize tooltips (Bootstrap)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers (Bootstrap)
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Progressive Web App functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}