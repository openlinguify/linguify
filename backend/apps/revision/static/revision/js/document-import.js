// Document Import - NLP Flashcard Generation
// Handles PDF/Image document upload and automatic flashcard generation

(function() {
    'use strict';

    // State
    let selectedDocument = null;
    let currentImportType = 'excel';

    // Initialize when DOM is ready
    function initDocumentImport() {
        console.log('📄 Document Import Module Initialized');
        console.log('📄 Current import type on init:', currentImportType);

        // Setup event listeners
        setupImportTypeSwitch();
        setupDocumentFileInput();
        setupDocumentDropZone();

        // Check if document radio is already selected on init
        const documentRadio = document.getElementById('importTypeDocument');
        if (documentRadio && documentRadio.checked) {
            console.log('📄 Document radio is already checked, switching to document mode');
            switchToDocumentMode();
        }
    }

    // Switch between Excel and Document import
    function setupImportTypeSwitch() {
        const excelRadio = document.getElementById('importTypeExcel');
        const documentRadio = document.getElementById('importTypeDocument');

        console.log('📄 Setting up import type switch', { excelRadio, documentRadio });

        if (excelRadio) {
            excelRadio.addEventListener('change', function() {
                console.log('📊 Excel radio changed, checked:', this.checked);
                if (this.checked) {
                    switchToExcelMode();
                }
            });
        }

        if (documentRadio) {
            documentRadio.addEventListener('change', function() {
                console.log('📄 Document radio changed, checked:', this.checked);
                if (this.checked) {
                    switchToDocumentMode();
                }
            });
        }
    }

    function switchToExcelMode() {
        console.log('📊 Switched to Excel/CSV mode');
        currentImportType = 'excel';

        const excelSection = document.getElementById('excelImportSection');
        const documentSection = document.getElementById('documentImportSection');
        const submitBtn = document.getElementById('submitImport');

        if (excelSection) excelSection.classList.remove('d-none');
        if (documentSection) documentSection.classList.add('d-none');

        if (submitBtn) {
            submitBtn.innerHTML = '<i class="bi bi-arrow-right me-2"></i>' + _('Next - Preview', 'Suivant - Aperçu');
            submitBtn.disabled = false;
        }

        // Clear document selection
        selectedDocument = null;
        clearSelectedDocument();
    }

    function switchToDocumentMode() {
        console.log('📄 Switched to Document/PDF mode');
        currentImportType = 'document';

        const excelSection = document.getElementById('excelImportSection');
        const documentSection = document.getElementById('documentImportSection');
        const submitBtn = document.getElementById('submitImport');

        if (excelSection) excelSection.classList.add('d-none');
        if (documentSection) documentSection.classList.remove('d-none');

        if (submitBtn) {
            submitBtn.innerHTML = '<i class="bi bi-cpu me-2"></i>' + _('Generate Flashcards', 'Générer les flashcards');
            submitBtn.disabled = !selectedDocument;
        }
    }

    // Setup document file input
    function setupDocumentFileInput() {
        const fileInput = document.getElementById('documentFile');

        if (fileInput) {
            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    handleDocumentSelection(file);
                }
            });
        }
    }

    // Setup drag & drop for documents
    function setupDocumentDropZone() {
        const dropZone = document.getElementById('documentDropZone');

        if (!dropZone) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, function() {
                dropZone.classList.add('border-success', 'bg-success', 'bg-opacity-10');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, function() {
                dropZone.classList.remove('border-success', 'bg-success', 'bg-opacity-10');
            }, false);
        });

        // Handle dropped files
        dropZone.addEventListener('drop', function(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                handleDocumentSelection(files[0]);
            }
        }, false);

        // Click to select file
        dropZone.addEventListener('click', function(e) {
            if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'INPUT') {
                document.getElementById('documentFile')?.click();
            }
        });
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Handle document file selection
    function handleDocumentSelection(file) {
        console.log('📎 Document selected:', file.name, file.size, 'bytes');

        // Validate file type
        const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'text/plain'];
        const allowedExtensions = ['.pdf', '.png', '.jpg', '.jpeg', '.txt'];

        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
            window.showToast?.('error', _('Invalid file type. Please select PDF, Image or Text file.', 'Type de fichier invalide. Veuillez sélectionner un PDF, une image ou un fichier texte.'));
            return;
        }

        // Validate file size (max 10MB)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            window.showToast?.('error', _('File too large. Maximum size is 10MB.', 'Fichier trop volumineux. Taille maximum 10MB.'));
            return;
        }

        selectedDocument = file;
        displaySelectedDocument(file);

        // Enable submit button
        const submitBtn = document.getElementById('submitImport');
        if (submitBtn) {
            submitBtn.disabled = false;
        }
    }

    // Display selected document info
    function displaySelectedDocument(file) {
        const fileInfo = document.getElementById('selectedDocumentInfo');
        const fileName = document.getElementById('selectedDocumentName');
        const fileSize = document.getElementById('selectedDocumentSize');

        if (fileInfo) fileInfo.classList.remove('d-none');
        if (fileName) fileName.textContent = file.name;
        if (fileSize) {
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            fileSize.textContent = `${sizeMB} MB`;
        }
    }

    // Clear selected document
    window.clearSelectedDocument = function() {
        selectedDocument = null;

        const fileInfo = document.getElementById('selectedDocumentInfo');
        const fileInput = document.getElementById('documentFile');
        const submitBtn = document.getElementById('submitImport');

        if (fileInfo) fileInfo.classList.add('d-none');
        if (fileInput) fileInput.value = '';
        if (submitBtn && currentImportType === 'document') {
            submitBtn.disabled = true;
        }
    };

    // Process document and generate flashcards
    async function processDocumentImport(deckId) {
        if (!selectedDocument) {
            window.showToast?.('error', _('Please select a document first', 'Veuillez d\'abord sélectionner un document'));
            return null;
        }

        const maxCards = parseInt(document.getElementById('maxCardsInput')?.value || 10);

        // Get selected generation mode
        const generationModeRadio = document.querySelector('input[name="generationMode"]:checked');
        const generationMode = generationModeRadio ? generationModeRadio.value : 'comprehension';

        console.log('🚀 Processing document import:', {
            file: selectedDocument.name,
            deckId: deckId,
            maxCards: maxCards,
            generationMode: generationMode
        });

        const formData = new FormData();
        formData.append('document', selectedDocument);
        formData.append('max_cards', maxCards);
        formData.append('generation_mode', generationMode);

        try {
            // Show loading
            showDocumentProcessingState(true);

            const csrfToken = window.apiService?.getCSRFToken() ||
                            document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            const response = await fetch(`/api/v1/revision/api/decks/${deckId}/import-document/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            if (data.success) {
                console.log('✅ Flashcards generated successfully:', data);

                window.showToast?.('success',
                    `${data.cards_created} ${_('flashcards generated successfully!', 'flashcards générées avec succès !')}`
                );

                // Show preview if available
                if (data.preview && data.preview.length > 0) {
                    showGeneratedCardsPreview(data.preview, data);
                }

                return data;
            } else {
                throw new Error(data.error || 'Generation failed');
            }

        } catch (error) {
            console.error('❌ Document import error:', error);
            window.showToast?.('error',
                _('Error generating flashcards', 'Erreur lors de la génération') + ': ' + error.message
            );
            throw error;
        } finally {
            showDocumentProcessingState(false);
        }
    }

    // Show/hide processing state
    function showDocumentProcessingState(isProcessing) {
        const submitBtn = document.getElementById('submitImport');

        if (submitBtn) {
            submitBtn.disabled = isProcessing;
            if (isProcessing) {
                submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    ${_('Generating...', 'Génération...')}
                `;
            } else {
                submitBtn.innerHTML = '<i class="bi bi-cpu me-2"></i>' + _('Generate Flashcards', 'Générer les flashcards');
            }
        }
    }

    // Show preview of generated cards
    function showGeneratedCardsPreview(cards, metadata) {
        const previewHtml = `
            <div class="card-linguify p-4 mb-3">
                <div class="d-flex align-items-center justify-content-between mb-3">
                    <h6 class="mb-0">
                        <i class="bi bi-check-circle-fill text-success me-2"></i>
                        ${cards.length} ${_('flashcards generated', 'flashcards générées')}
                    </h6>
                    <span class="badge bg-success">${metadata.extraction_method || 'NLP'}</span>
                </div>

                ${cards.map((card, index) => `
                    <div class="card mb-2">
                        <div class="card-body p-3">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <span class="badge bg-${getDifficultyColor(card.difficulty)}">${card.difficulty}</span>
                                ${card.relevance_score ? `<span class="badge bg-secondary">${(card.relevance_score * 100).toFixed(0)}%</span>` : ''}
                            </div>
                            <p class="mb-2 small"><strong>❓ ${_('Question', 'Question')}:</strong> ${escapeHtml(card.front_text)}</p>
                            <p class="mb-0 small text-muted"><strong>✅ ${_('Answer', 'Réponse')}:</strong> ${escapeHtml(card.back_text)}</p>
                        </div>
                    </div>
                `).join('')}

                ${metadata.detected_language ? `
                    <div class="alert alert-info mt-3 mb-0">
                        <i class="bi bi-info-circle me-2"></i>
                        ${_('Detected language', 'Langue détectée')}: <strong>${metadata.detected_language}</strong>
                    </div>
                ` : ''}
            </div>
        `;

        // Insert preview before the bottom actions
        const importContent = document.querySelector('.import-content-scrollable');
        if (importContent) {
            const previewContainer = document.createElement('div');
            previewContainer.id = 'documentPreviewContainer';
            previewContainer.innerHTML = previewHtml;

            // Remove old preview if exists
            const oldPreview = document.getElementById('documentPreviewContainer');
            if (oldPreview) oldPreview.remove();

            importContent.appendChild(previewContainer);

            // Scroll to preview
            previewContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    function getDifficultyColor(difficulty) {
        const colors = {
            'easy': 'success',
            'medium': 'warning',
            'hard': 'danger'
        };
        return colors[difficulty] || 'secondary';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Get current import type
    window.getCurrentImportType = function() {
        return currentImportType;
    };

    // Process document import (exposed globally)
    window.processDocumentImport = processDocumentImport;

    // Expose init function to be called when modal opens
    window.initDocumentImport = initDocumentImport;

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDocumentImport);
    } else {
        initDocumentImport();
    }

})();
