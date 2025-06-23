/**
 * Simple Learning App - Direct Django views
 */

class SimpleLearningApp {
    constructor() {
        this.init();
    }

    init() {
        console.log('🎓 Simple Learning App initialized');
        this.bindEvents();
        this.animateProgress();
    }

    bindEvents() {
        // Chapter selection
        document.addEventListener('click', (e) => {
            const chapterCard = e.target.closest('.chapter-card:not(.locked)');
            if (chapterCard) {
                const chapterId = chapterCard.dataset.chapterId;
                if (chapterId) {
                    this.selectChapter(chapterId);
                }
            }
        });

        // Continue lesson button
        const continueBtn = document.querySelector('[onclick*="continueLesson"]');
        if (continueBtn) {
            continueBtn.onclick = (e) => {
                e.preventDefault();
                this.continueLesson();
            };
        }
    }

    animateProgress() {
        // Animate circular progress on load
        const circles = document.querySelectorAll('.circular-progress');
        circles.forEach(circle => {
            const progress = circle.dataset.progress || 0;
            const progressBar = circle.querySelector('.progress-bar');
            if (progressBar) {
                setTimeout(() => {
                    const circumference = 2 * Math.PI * 50; // radius = 50
                    const strokeDasharray = (progress / 100) * circumference;
                    progressBar.style.strokeDasharray = `${strokeDasharray} ${circumference}`;
                }, 100);
            }
        });

        // Animate progress bars
        const progressBars = document.querySelectorAll('.progress .progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    }

    selectChapter(chapterId) {
        console.log('📘 Selecting chapter:', chapterId);
        // Simple redirect to chapter page
        window.location.href = `/learning/chapter/${chapterId}/`;
    }

    continueLesson() {
        console.log('📝 Continuing lesson');
        // Get the current lesson from the template data
        const continueBtn = document.querySelector('[onclick*="continueLesson"]');
        if (continueBtn && continueBtn.dataset.lessonId) {
            window.location.href = `/learning/lesson/${continueBtn.dataset.lessonId}/`;
        } else {
            // Fallback to first available chapter
            const firstChapter = document.querySelector('.chapter-card:not(.locked)');
            if (firstChapter) {
                const chapterId = firstChapter.dataset.chapterId;
                this.selectChapter(chapterId);
            }
        }
    }

    showProfile() {
        window.location.href = '/profile/';
    }
}

// Global functions for template compatibility
window.selectChapter = function(chapterId) {
    if (window.simpleLearningApp) {
        window.simpleLearningApp.selectChapter(chapterId);
    }
};

window.continueLesson = function() {
    if (window.simpleLearningApp) {
        window.simpleLearningApp.continueLesson();
    }
};

window.showProfile = function() {
    if (window.simpleLearningApp) {
        window.simpleLearningApp.showProfile();
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    window.simpleLearningApp = new SimpleLearningApp();
});

console.log('📚 Simple learning interface module loaded');