/**
 * Careers Page JavaScript
 * Handles department filtering, modal interactions, and smooth scrolling
 */

class CareersManager {
    constructor() {
        this.filterButtons = document.querySelectorAll('[data-filter]');
        this.jobCards = document.querySelectorAll('.job-card');
        this.modal = document.getElementById('applicationModal');
        this.modalTitle = document.getElementById('modalTitle');
        this.closeModalBtn = document.getElementById('closeModal');
        
        this.init();
    }
    
    init() {
        this.setupFilters();
        this.setupModal();
        this.setupSmoothScroll();
        this.setupAnimations();
    }
    
    /**
     * Setup department filtering functionality
     */
    setupFilters() {
        if (this.filterButtons.length === 0) return;
        
        this.filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const filter = e.target.getAttribute('data-filter');
                this.filterJobs(filter);
                this.updateFilterButtons(e.target);
            });
        });
    }
    
    /**
     * Filter job positions by department
     */
    filterJobs(filter) {
        this.jobCards.forEach(card => {
            const department = card.getAttribute('data-department');
            const shouldShow = filter === 'all' || department === filter;
            
            if (shouldShow) {
                card.style.display = 'block';
                card.classList.add('animate-fade-in-up');
            } else {
                card.style.display = 'none';
                card.classList.remove('animate-fade-in-up');
            }
        });
    }
    
    /**
     * Update filter button styles
     */
    updateFilterButtons(activeButton) {
        this.filterButtons.forEach(btn => {
            btn.classList.remove('active');
        });
        activeButton.classList.add('active');
    }
    
    /**
     * Setup modal functionality
     */
    setupModal() {
        if (!this.modal) return;
        
        // Close modal on close button click
        if (this.closeModalBtn) {
            this.closeModalBtn.addEventListener('click', () => {
                this.closeModal();
            });
        }
        
        // Close modal on backdrop click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });
        
        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.closeModal();
            }
        });
    }
    
    /**
     * Open application modal
     */
    openModal(positionTitle) {
        if (!this.modal || !this.modalTitle) return;
        
        this.modalTitle.textContent = `Postuler - ${positionTitle}`;
        this.modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Focus trap
        const focusableElements = this.modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }
    
    /**
     * Close application modal
     */
    closeModal() {
        if (!this.modal) return;
        
        this.modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
    
    /**
     * Setup smooth scrolling for anchor links
     */
    setupSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    /**
     * Setup scroll animations
     */
    setupAnimations() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                }
            });
        }, observerOptions);
        
        // Observe position cards
        this.jobCards.forEach(card => {
            observer.observe(card);
        });
        
        // Observe value cards
        document.querySelectorAll('.value-card').forEach(card => {
            observer.observe(card);
        });
    }
}

/**
 * Global function to open application modal
 * Called from template onclick handlers
 */
window.openApplicationModal = function(element) {
    const positionTitle = element.getAttribute('data-position-title');
    if (window.careersManager) {
        window.careersManager.openModal(positionTitle);
    }
};

/**
 * Initialize careers page when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    window.careersManager = new CareersManager();
    
    // Add loading animation to page
    document.body.classList.add('careers-loaded');
});

/**
 * Utils for email functionality
 */
const CareersUtils = {
    /**
     * Open email client with pre-filled subject
     */
    openEmailClient(positionTitle) {
        const subject = encodeURIComponent(`Candidature - ${positionTitle}`);
        const body = encodeURIComponent(`Bonjour,\n\nJe souhaite postuler pour le poste de ${positionTitle}.\n\nCordialement,`);
        window.location.href = `mailto:careers@linguify.com?subject=${subject}&body=${body}`;
    },
    
    /**
     * Copy email to clipboard
     */
    copyEmailToClipboard() {
        const email = 'careers@linguify.com';
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(email).then(() => {
                this.showToast('Email copié dans le presse-papiers');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = email;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                this.showToast('Email copié dans le presse-papiers');
            } catch (err) {
                console.error('Erreur lors de la copie:', err);
            }
            
            document.body.removeChild(textArea);
        }
    },
    
    /**
     * Show toast notification
     */
    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg z-50';
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('opacity-0', 'transition-opacity');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 2000);
    }
};

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CareersManager, CareersUtils };
}