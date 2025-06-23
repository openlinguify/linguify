/**
 * Modern Learning App Interface
 * Handles the course learning interface functionality
 */
class ModernLearningApp {
    constructor(config) {
        this.config = {
            units: [],
            currentUserId: null,
            csrfToken: '',
            apiBasePath: '/api/v1/course/',
            ...config
        };
        
        this.currentUnit = null;
        this.currentChapter = null;
        this.currentLesson = null;
        this.currentView = 'dashboard';
        
        console.log('🎓 ModernLearningApp initialized with config:', this.config);
    }
    
    init() {
        this.bindEvents();
        this.initializeMobileMenu();
        this.loadDashboard();
        console.log('✅ Learning app ready');
    }
    
    bindEvents() {
        // Mobile menu toggle
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => this.toggleMobileSidebar());
        }
        
        // Mobile overlay
        const mobileOverlay = document.getElementById('mobileOverlay');
        if (mobileOverlay) {
            mobileOverlay.addEventListener('click', () => this.toggleMobileSidebar());
        }
        
        // Unit selection
        document.addEventListener('click', (e) => {
            const unitCard = e.target.closest('[data-unit-id]');
            if (unitCard) {
                const unitId = parseInt(unitCard.dataset.unitId);
                this.selectUnit(unitId);
            }
        });
        
        // Navigation between views
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('back-to-dashboard')) {
                this.showDashboard();
            }
        });
    }
    
    initializeMobileMenu() {
        // Ensure mobile menu starts closed
        const sidebar = document.getElementById('learningSidebar');
        if (sidebar) {
            sidebar.classList.remove('mobile-open');
        }
    }
    
    toggleMobileSidebar() {
        const sidebar = document.getElementById('learningSidebar');
        const overlay = document.getElementById('mobileOverlay');
        
        if (sidebar && overlay) {
            const isOpen = sidebar.classList.contains('mobile-open');
            
            if (isOpen) {
                sidebar.classList.remove('mobile-open');
                overlay.classList.remove('active');
                document.body.classList.remove('mobile-menu-open');
            } else {
                sidebar.classList.add('mobile-open');
                overlay.classList.add('active');
                document.body.classList.add('mobile-menu-open');
            }
        }
    }
    
    loadDashboard() {
        this.showView('dashboard');
        this.currentView = 'dashboard';
    }
    
    showDashboard() {
        this.showView('dashboard');
        this.currentView = 'dashboard';
        this.currentUnit = null;
        this.currentChapter = null;
        this.currentLesson = null;
        
        // Update active unit in sidebar
        this.updateSidebarSelection(null);
    }
    
    selectUnit(unitId) {
        console.log('📚 Selecting unit:', unitId);
        
        const unit = this.config.units.find(u => u.id === unitId);
        if (!unit) {
            console.error('Unit not found:', unitId);
            return;
        }
        
        this.currentUnit = unit;
        this.currentView = 'unit';
        
        // Update sidebar selection
        this.updateSidebarSelection(unitId);
        
        // Show unit detail view
        this.showUnitDetail(unit);
    }
    
    showUnitDetail(unit) {
        const unitView = document.getElementById('unitView');
        if (!unitView) return;
        
        // Generate unit detail HTML
        unitView.innerHTML = this.generateUnitDetailHTML(unit);
        
        // Show the unit view
        this.showView('unit');
    }
    
    generateUnitDetailHTML(unit) {
        const chaptersHTML = unit.chapters.map(chapter => `
            <div class="chapter-card-modern" data-chapter-id="${chapter.id}" onclick="window.LearningApp.selectChapter(${chapter.id})">
                <div class="chapter-header">
                    <div class="chapter-number">${chapter.order}</div>
                    <div class="chapter-theme-badge ${chapter.theme}">${chapter.style}</div>
                </div>
                <div class="chapter-content">
                    <h5 class="chapter-title">${chapter.title}</h5>
                    <p class="chapter-description">${chapter.description}</p>
                    <div class="chapter-info">
                        <span><i class="bi bi-book"></i> ${chapter.lessons.length} leçon${chapter.lessons.length > 1 ? 's' : ''}</span>
                        <span><i class="bi bi-star"></i> ${chapter.points_reward} points</span>
                    </div>
                    <div class="chapter-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${chapter.progress_percentage || 0}%"></div>
                        </div>
                        <span class="progress-text">${chapter.progress_percentage || 0}% complété</span>
                    </div>
                </div>
            </div>
        `).join('');
        
        return `
            <div class="unit-detail-header">
                <button class="btn btn-outline-secondary back-to-dashboard">
                    <i class="bi bi-arrow-left me-2"></i>Retour au tableau de bord
                </button>
                <h2>${unit.title}</h2>
                <p class="unit-description">${unit.description}</p>
            </div>
            
            <div class="chapters-grid">
                ${chaptersHTML}
            </div>
        `;
    }
    
    selectChapter(chapterId) {
        console.log('📖 Selecting chapter:', chapterId);
        
        // Simple redirect to chapter page
        window.location.href = `/learning/chapter/${chapterId}/`;
    }
    
    showChapterDetail(chapter) {
        const chapterView = document.getElementById('chapterView');
        if (!chapterView) return;
        
        // Generate chapter detail HTML
        chapterView.innerHTML = this.generateChapterDetailHTML(chapter);
        
        // Show the chapter view
        this.showView('chapter');
    }
    
    generateChapterDetailHTML(chapter) {
        const lessonsHTML = chapter.lessons.map(lesson => `
            <div class="lesson-card-modern" data-lesson-id="${lesson.id}" onclick="window.LearningApp.selectLesson(${lesson.id})">
                <div class="lesson-status ${lesson.is_completed ? 'completed' : 'available'}">
                    <i class="bi bi-${lesson.is_completed ? 'check-circle-fill' : 'play-circle'}"></i>
                </div>
                <div class="lesson-content">
                    <h6 class="lesson-title">${lesson.title}</h6>
                    <p class="lesson-description">${lesson.description}</p>
                    <div class="lesson-meta">
                        <span><i class="bi bi-clock"></i> ${lesson.estimated_duration} min</span>
                        <span><i class="bi bi-star"></i> +${lesson.xp_reward} XP</span>
                    </div>
                </div>
            </div>
        `).join('');
        
        return `
            <div class="chapter-detail-header">
                <button class="btn btn-outline-secondary" onclick="window.LearningApp.selectUnit(${this.currentUnit.id})">
                    <i class="bi bi-arrow-left me-2"></i>Retour à l'unité
                </button>
                <h2>${chapter.title}</h2>
                <p class="chapter-description">${chapter.description}</p>
            </div>
            
            <div class="lessons-grid">
                ${lessonsHTML}
            </div>
        `;
    }
    
    selectLesson(lessonId) {
        console.log('📝 Selecting lesson:', lessonId);
        
        // Simple redirect to lesson page
        window.location.href = `/learning/lesson/${lessonId}/`;
    }
    
    showLessonDetail(lesson) {
        const lessonView = document.getElementById('lessonView');
        if (!lessonView) return;
        
        lessonView.innerHTML = `
            <div class="lesson-detail-header">
                <button class="btn btn-outline-secondary" onclick="window.LearningApp.selectChapter(${this.currentChapter.id})">
                    <i class="bi bi-arrow-left me-2"></i>Retour au chapitre
                </button>
                <h2>${lesson.title}</h2>
                <p class="lesson-description">${lesson.description}</p>
            </div>
            
            <div class="lesson-content-placeholder">
                <div class="text-center py-5">
                    <i class="bi bi-book display-1 text-muted"></i>
                    <h4 class="mt-3">Contenu de la leçon</h4>
                    <p class="text-muted">Le contenu de cette leçon sera bientôt disponible.</p>
                    <button class="btn btn-primary" onclick="window.LearningApp.selectChapter(${this.currentChapter.id})">
                        Retour au chapitre
                    </button>
                </div>
            </div>
        `;
        
        this.showView('lesson');
    }
    
    showView(viewName) {
        // Hide all views
        const views = document.querySelectorAll('.content-view');
        views.forEach(view => view.classList.remove('active'));
        
        // Show target view
        const targetView = document.getElementById(viewName + 'View');
        if (targetView) {
            targetView.classList.add('active');
        }
        
        console.log('👀 Showing view:', viewName);
    }
    
    updateSidebarSelection(unitId) {
        // Remove active class from all unit cards
        const unitCards = document.querySelectorAll('.unit-card-compact');
        unitCards.forEach(card => card.classList.remove('active'));
        
        // Add active class to selected unit
        if (unitId) {
            const selectedCard = document.querySelector(`[data-unit-id="${unitId}"]`);
            if (selectedCard) {
                selectedCard.classList.add('active');
            }
        }
    }
}

// Global functions for template compatibility
window.selectUnit = function(unitId) {
    if (window.LearningApp) {
        window.LearningApp.selectUnit(unitId);
    }
};

window.toggleMobileSidebar = function() {
    if (window.LearningApp) {
        window.LearningApp.toggleMobileSidebar();
    }
};

window.showProgressModal = function() {
    const modal = new bootstrap.Modal(document.getElementById('progressModal'));
    modal.show();
};

console.log('📚 Learning interface module loaded');