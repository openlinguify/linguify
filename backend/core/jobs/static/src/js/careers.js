// Careers Page JavaScript - Optimized for performance
(function() {
    'use strict';
    
    // Preload critical resources
    const prefetchLinks = [
        '/careers/apply/',  // Preconnect to API endpoint
    ];
    
    prefetchLinks.forEach(url => {
        const link = document.createElement('link');
        link.rel = 'preconnect';
        link.href = url;
        document.head.appendChild(link);
    });

    document.addEventListener('DOMContentLoaded', function() {
        // Use requestIdleCallback for non-critical initialization
        if (window.requestIdleCallback) {
            requestIdleCallback(() => {
                initializeFilters();
                initializeModal();
                initializePreloading();
            });
        } else {
            // Fallback for browsers without requestIdleCallback
            setTimeout(() => {
                initializeFilters();
                initializeModal();
                initializePreloading();
            }, 100);
        }
    });

    // Department Filter Functionality
    function initializeFilters() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        const jobCards = document.querySelectorAll('.position-card');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filterValue = this.getAttribute('data-filter');
                
                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Filter job cards
                jobCards.forEach(card => {
                    const cardDepartment = card.getAttribute('data-department');
                    
                    if (filterValue === 'all' || cardDepartment === filterValue) {
                        card.style.display = 'flex';
                        card.classList.add('animate-fade-in-up');
                    } else {
                        card.style.display = 'none';
                        card.classList.remove('animate-fade-in-up');
                    }
                });
            });
        });
    }

    // Modal Functionality
    function initializeModal() {
        const modal = document.getElementById('applicationModal');
        
        // Close modal when clicking outside
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeApplicationModal();
                }
            });
        }
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
                closeApplicationModal();
            }
        });
    }

    // Application Form Functionality
    function initializeApplicationForm() {
        initializeFileInput();
        initializeFormValidation();
        initializeDragAndDrop();
    }

    // Enhanced File Input
    function initializeFileInput() {
        const fileInput = document.querySelector('input[type="file"]');
        const fileInfo = document.querySelector('.file-input-info');
        const fileText = document.querySelector('.file-text');
        
        if (!fileInput || !fileInfo || !fileText) return;
        
        fileInput.addEventListener('change', function(e) {
            handleFileSelect(e.target.files[0]);
        });
    }

    // Drag and Drop Functionality
    function initializeDragAndDrop() {
        const fileInfo = document.querySelector('.file-input-info');
        const fileInput = document.querySelector('input[type="file"]');
        
        if (!fileInfo || !fileInput) return;
        
        fileInfo.addEventListener('dragover', function(e) {
            e.preventDefault();
            fileInfo.classList.add('dragover');
        });
        
        fileInfo.addEventListener('dragleave', function(e) {
            e.preventDefault();
            fileInfo.classList.remove('dragover');
        });
        
        fileInfo.addEventListener('drop', function(e) {
            e.preventDefault();
            fileInfo.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });
    }

    // Handle File Selection
    function handleFileSelect(file) {
        const fileInfo = document.querySelector('.file-input-info');
        const fileText = document.querySelector('.file-text');
        
        if (!file || !fileInfo || !fileText) return;
        
        // Update UI
        fileInfo.classList.add('file-selected');
        fileText.innerHTML = `
            <span class="file-name">📄 ${file.name}</span>
            <span class="file-size">(${formatFileSize(file.size)})</span>
            <span class="file-remove" onclick="removeFile()">🗑️ Supprimer</span>
        `;
        
        // Validate file
        if (!validateFile(file)) {
            showFileError(file);
        }
    }

    // Remove File
    window.removeFile = function() {
        const fileInput = document.querySelector('input[type="file"]');
        const fileInfo = document.querySelector('.file-input-info');
        const fileText = document.querySelector('.file-text');
        
        if (fileInput) fileInput.value = '';
        if (fileInfo) fileInfo.classList.remove('file-selected');
        if (fileText) fileText.textContent = 'Glisser votre CV ici ou cliquer pour parcourir';
    };

    // File Validation
    function validateFile(file) {
        const maxSize = 5 * 1024 * 1024; // 5MB
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        
        return file.size <= maxSize && (allowedTypes.includes(file.type) || file.name.toLowerCase().match(/\.(pdf|doc|docx)$/));
    }

    // Format File Size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    // Form Validation
    function initializeFormValidation() {
        const inputs = document.querySelectorAll('.form-control');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('error')) {
                    validateField(this);
                }
            });
        });
    }

    // Validate Individual Field
    function validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required') || field.closest('.form-group').querySelector('label').textContent.includes('*');
        
        // Clear previous states
        field.classList.remove('error', 'success');
        
        if (isRequired && !value) {
            field.classList.add('error');
            return false;
        }
        
        if (field.type === 'email' && value && !isValidEmail(value)) {
            field.classList.add('error');
            return false;
        }
        
        if (value) {
            field.classList.add('success');
        }
        
        return true;
    }

    // Email Validation
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Form cache for instant loading
    const formCache = new Map();
    
    // Preload form on hover with correct URL
    function preloadForm(positionId) {
        if (formCache.has(positionId)) return;
        
        const currentLang = document.documentElement.lang || 'fr';
        const applyUrl = `/${currentLang}/careers/apply/${positionId}/`;
        
        fetch(applyUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    formCache.set(positionId, {
                        html: data.html,
                        title: data.position_title,
                        cached: data.cached
                    });
                } else {
                    console.warn(`Failed to preload form for position ${positionId}:`, data.error);
                }
            })
            .catch(error => {
                console.error(`Error preloading form for position ${positionId}:`, error);
            });
    }
    
    // Initialize preloading with intersection observer for better performance
    function initializePreloading() {
        const applyButtons = document.querySelectorAll('[data-position-id]');
        
        // Use Intersection Observer for lazy preloading
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const button = entry.target;
                        const positionId = button.getAttribute('data-position-id');
                        
                        // Preload on scroll into view + add hover listener
                        preloadForm(positionId);
                        
                        button.addEventListener('mouseenter', function() {
                            preloadForm(positionId);
                        }, { once: true });
                        
                        observer.unobserve(button);
                    }
                });
            }, { rootMargin: '200px' });
            
            applyButtons.forEach(button => observer.observe(button));
        } else {
            // Fallback for older browsers
            applyButtons.forEach(button => {
                button.addEventListener('mouseenter', function() {
                    const positionId = this.getAttribute('data-position-id');
                    preloadForm(positionId);
                }, { once: true });
            });
        }
    }
    
    // Open Application Modal with instant loading
    function openApplicationModal(element) {
        const positionId = element.getAttribute('data-position-id');
        const positionTitle = element.getAttribute('data-position-title');
        const modal = document.getElementById('applicationModal');
        const modalTitle = document.querySelector('.modal-header h3');
        const modalBody = document.querySelector('.modal-body');
        
        if (modalTitle) {
            modalTitle.textContent = `Postuler pour ${positionTitle}`;
        }
        
        // Show modal immediately
        if (modal) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }
        
        // Load application form (instant if cached)
        if (modalBody) {
            const cachedForm = formCache.get(positionId);
            
            if (cachedForm) {
                // Instant loading from cache
                modalBody.innerHTML = cachedForm.html;
                initializeApplicationForm();
                attachFormSubmitHandler();
            } else {
                // Show loading state
                modalBody.innerHTML = `
                    <div class="loading-skeleton" style="text-align: center; padding: 2rem;">
                        <div class="skeleton-text"></div>
                        <div class="skeleton-text"></div>
                        <div class="skeleton-text"></div>
                    </div>`;
                
                // Utiliser l'URL correcte avec préfixe de langue
                const currentLang = document.documentElement.lang || 'fr';
                const applyUrl = `/${currentLang}/careers/apply/${positionId}/`;
                
                fetch(applyUrl)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            modalBody.innerHTML = data.html;
                            formCache.set(positionId, {
                                html: data.html,
                                title: data.position_title
                            });
                            initializeApplicationForm();
                            attachFormSubmitHandler();
                        } else {
                            modalBody.innerHTML = `
                                <div class="alert alert-error">
                                    <h4>Erreur de chargement</h4>
                                    <p>${data.error || 'Erreur lors du chargement du formulaire.'}</p>
                                    ${data.code ? `<small>Code d'erreur: ${data.code}</small>` : ''}
                                </div>
                            `;
                        }
                    })
                    .catch(error => {
                        modalBody.innerHTML = `
                            <div class="alert alert-error">
                                <h4>Erreur de connexion</h4>
                                <p>Impossible de charger le formulaire. Veuillez réessayer.</p>
                                <small>Détails: ${error.message}</small>
                            </div>
                        `;
                        console.error('Error loading form:', error);
                    });
            }
        }
    }

    // Close Application Modal
    function closeApplicationModal() {
        const modal = document.getElementById('applicationModal');
        
        if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = '';
            
            // Clear modal content
            const modalBody = document.querySelector('.modal-body');
            if (modalBody) {
                modalBody.innerHTML = '';
            }
        }
    }

    // Form Submission Handler
    function attachFormSubmitHandler() {
        const form = document.getElementById('applicationForm');
        if (!form) return;
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const submitText = submitBtn.querySelector('.submit-text');
            const submitLoading = submitBtn.querySelector('.submit-loading');
            
            // Show loading state
            submitBtn.disabled = true;
            submitText.style.display = 'none';
            submitLoading.style.display = 'flex';
            
            // Clear previous errors
            document.querySelectorAll('.error-message').forEach(el => {
                el.classList.remove('show');
            });
            document.querySelectorAll('.form-control').forEach(el => {
                el.classList.remove('error');
            });
            
            // Submit form with proper CSRF handling
            const formData = new FormData(form);
            const csrfToken = formData.get('csrfmiddlewaretoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const modalBody = document.querySelector('.modal-body');
                    modalBody.innerHTML = `
                        <div class="alert alert-success">
                            <h4>Candidature envoyée avec succès!</h4>
                            <p>${data.message}</p>
                        </div>
                        <div style="text-align: center; margin-top: 2rem;">
                            <button type="button" class="btn-primary" onclick="closeApplicationModal()">
                                Fermer
                            </button>
                        </div>
                    `;
                } else {
                    // Show validation errors
                    if (data.errors) {
                        Object.keys(data.errors).forEach(field => {
                            const errorElement = document.getElementById(`error-${field}`);
                            const inputElement = document.querySelector(`[name="${field}"]`);
                            
                            if (errorElement && data.errors[field]) {
                                errorElement.textContent = data.errors[field];
                                errorElement.classList.add('show');
                            }
                            
                            if (inputElement) {
                                inputElement.classList.add('error');
                            }
                        });
                    }
                    
                    // Show general error message
                    if (data.error) {
                        const modalBody = document.querySelector('.modal-body');
                        modalBody.insertAdjacentHTML('afterbegin', `
                            <div class="alert alert-error">
                                ${data.error}
                            </div>
                        `);
                    }
                    
                    // Reset button state
                    submitBtn.disabled = false;
                    submitText.style.display = 'inline';
                    submitLoading.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error submitting form:', error);
                
                // Show generic error
                const modalBody = document.querySelector('.modal-body');
                modalBody.insertAdjacentHTML('afterbegin', `
                    <div class="alert alert-error">
                        Une erreur s'est produite. Veuillez réessayer.
                    </div>
                `);
                
                // Reset button state
                submitBtn.disabled = false;
                submitText.style.display = 'inline';
                submitLoading.style.display = 'none';
            });
        });
    }

    // Scroll to positions function
    function scrollToPositions() {
        const positionsSection = document.getElementById('positions');
        if (positionsSection) {
            positionsSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    // Make functions global for template access
    window.openApplicationModal = openApplicationModal;
    window.closeApplicationModal = closeApplicationModal;
    window.scrollToPositions = scrollToPositions;

})();