/**
 * Application Notebook - Logique principale
 * Gestion des notes avec interface propre et fonctionnelle
 */

// Configuration du service notebook (pure Django)
const notebookService = {
    baseUrl: '/notebook/ajax',
    
    async getNotes(params = {}) {
        const searchParams = new URLSearchParams(params);
        return await window.apiService.request(`${this.baseUrl}/notes/?${searchParams}`);
    },
    
    async createNote(noteData) {
        return await window.apiService.request(`${this.baseUrl}/notes/create/`, {
            method: 'POST',
            body: JSON.stringify(noteData)
        });
    },
    
    async updateNote(id, noteData) {
        const url = `${this.baseUrl}/notes/${id}/update/`;
        console.log('UPDATE URL:', url);
        console.log('UPDATE Data:', noteData);
        return await window.apiService.request(url, {
            method: 'POST',
            body: JSON.stringify(noteData)
        });
    },
    
    async deleteNote(id) {
        const url = `${this.baseUrl}/notes/${id}/delete/`;
        console.log('DELETE URL:', url);
        return await window.apiService.request(url, {
            method: 'POST'
        });
    },
    
    async bulkDelete(noteIds) {
        return await window.apiService.request(`${this.baseUrl}/notes/bulk-delete/`, {
            method: 'POST',
            body: JSON.stringify({ note_ids: noteIds })
        });
    },
    
    async bulkUpdate(noteIds, updates) {
        return await window.apiService.request(`${this.baseUrl}/notes/bulk-update/`, {
            method: 'POST',
            body: JSON.stringify({ note_ids: noteIds, updates: updates })
        });
    }
};

// Variables globales
let currentNote = null;
let notes = [];
let searchTimeout = null;
let isMultiSelectMode = false;
let selectedNotes = new Set();

// Fonction de test pour vérifier l'API
async function testAPI() {
    try {
        console.log('Testing API connection...');
        const response = await notebookService.getNotes({page: 1});
        console.log('API Test successful:', response);
        return true;
    } catch (error) {
        console.error('API Test failed:', error);
        return false;
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    testAPI(); // Test API first
    loadNotes();
    setupKeyboardShortcuts();
    setupAutoSave();
});

// Chargement des notes
async function loadNotes() {
    try {
        showLoading();
        const archiveFilter = document.getElementById('archiveFilter')?.value || 'active';
        const params = {
            page: 1,
            search: document.getElementById('searchInput')?.value || '',
            language: document.getElementById('languageFilter')?.value || '',
            sort: document.getElementById('sortFilter')?.value || 'updated_desc',
            archive_status: archiveFilter
        };
        
        const response = await notebookService.getNotes(params);
        notes = response.results || [];
        displayNotes(notes);
        updateNotesCount(notes.length);
        
        // Sélectionner automatiquement la première note ou restaurer la note courante
        if (notes.length > 0) {
            if (currentNote) {
                // Vérifier si la note courante existe encore
                const stillExists = notes.find(n => n.id === currentNote.id);
                if (stillExists) {
                    selectNote(currentNote.id);
                } else {
                    // Note supprimée, sélectionner la première
                    selectNote(notes[0].id);
                }
            } else {
                selectNote(notes[0].id);
            }
        } else {
            currentNote = null;
            showEmpty();
        }
        
    } catch (error) {
        console.error('Error loading notes:', error);
        if (window.notificationService) {
            window.notificationService.error('Erreur lors du chargement des notes');
        }
        showEmpty();
    }
}

// Affichage des notes
function displayNotes(notesList) {
    const container = document.getElementById('notesList');
    const emptyDiv = document.getElementById('emptyNotes');
    const loadingDiv = document.getElementById('loadingNotes');
    
    if (loadingDiv) loadingDiv.style.display = 'none';
    
    if (notesList.length === 0) {
        if (container) container.innerHTML = '';
        if (emptyDiv) emptyDiv.style.display = 'block';
        return;
    }
    
    if (emptyDiv) emptyDiv.style.display = 'none';
    if (container) {
        container.innerHTML = notesList.map(note => {
            const isSelected = selectedNotes.has(note.id);
            return `
                <div class="note-item ${isSelected ? 'selected' : ''} ${note.is_archived ? 'archived' : ''}" 
                     onclick="${isMultiSelectMode ? `toggleNoteSelection(${note.id})` : `selectNote(${note.id})`}" 
                     data-note-id="${note.id}">
                    ${isMultiSelectMode ? `
                        <div class="note-checkbox">
                            <input type="checkbox" ${isSelected ? 'checked' : ''} onclick="event.stopPropagation(); toggleNoteSelection(${note.id})">
                        </div>
                    ` : ''}
                    <div class="note-content">
                        <div class="note-title">
                            ${escapeHtml(note.title || 'Sans titre')}
                            ${note.is_archived ? '<span class="badge bg-secondary ms-2">Archivée</span>' : ''}
                            ${note.is_pinned ? '<i class="bi bi-pin-angle text-primary ms-1"></i>' : ''}
                        </div>
                        <div class="note-preview">${escapeHtml(note.content || '').substring(0, 100)}...</div>
                        <div class="note-meta">
                            ${note.language ? `<span class="note-language">${note.language.toUpperCase()}</span>` : ''}
                            <span>${formatDate(note.updated_at)}</span>
                            ${note.is_archived ? `
                                <button class="btn btn-sm btn-outline-success ms-2" onclick="event.stopPropagation(); unarchiveNote(${note.id})" title="Désarchiver">
                                    <i class="bi bi-arrow-up-circle"></i>
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
}

// Sélection d'une note
async function selectNote(noteId) {
    try {
        console.log('Selecting note with ID:', noteId);
        const note = notes.find(n => n.id === noteId);
        if (!note) {
            console.error('Note not found with ID:', noteId);
            return;
        }
        
        console.log('Found note:', note);
        currentNote = note;
        showEditor();
        loadNoteInEditor(note);
        
        // Marquer la note comme active
        document.querySelectorAll('.note-item').forEach(item => {
            item.classList.remove('active');
        });
        const activeItem = document.querySelector(`[data-note-id="${noteId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
            console.log('Note marked as active in sidebar');
        }
        
    } catch (error) {
        console.error('Error selecting note:', error);
        window.notificationService.error('Erreur lors de la sélection de la note');
    }
}

// Charger une note dans l'éditeur
function loadNoteInEditor(note) {
    console.log('Loading note in editor:', note);
    
    // Éléments principaux (obligatoires)
    const noteTitle = document.getElementById('noteTitle');
    const noteLanguage = document.getElementById('noteLanguage');
    const noteContent = document.getElementById('noteContent');
    
    // Remplir les champs principaux
    if (noteTitle) {
        noteTitle.value = note.title || '';
        console.log('Title loaded:', note.title);
    }
    if (noteLanguage) {
        noteLanguage.value = note.language || '';
        console.log('Language loaded:', note.language);
    }
    if (noteContent) {
        noteContent.value = note.content || '';
        console.log('Content loaded, length:', (note.content || '').length);
    }
    
    // Éléments optionnels (peuvent ne pas exister)
    const optionalElements = [
        { id: 'noteTranslation', value: note.translation || '' },
        { id: 'notePronunciation', value: note.pronunciation || '' },
        { id: 'noteDifficulty', value: note.difficulty || '' },
        { id: 'noteExamples', value: (note.example_sentences || []).join('\n') },
        { id: 'noteRelatedWords', value: (note.related_words || []).join(', ') },
        { id: 'noteType', value: note.note_type || 'NOTE' },
        { id: 'notePriority', value: note.priority || 'MEDIUM' }
    ];
    
    optionalElements.forEach(({ id, value }) => {
        const element = document.getElementById(id);
        if (element) element.value = value;
    });
    
    // Checkboxes
    const notePinned = document.getElementById('notePinned');
    const noteArchived = document.getElementById('noteArchived');
    if (notePinned) notePinned.checked = note.is_pinned || false;
    if (noteArchived) noteArchived.checked = note.is_archived || false;
    
    // Statistiques (texte uniquement)
    const noteCreatedAt = document.getElementById('noteCreatedAt');
    const noteUpdatedAt = document.getElementById('noteUpdatedAt');
    const noteReviewCount = document.getElementById('noteReviewCount');
    if (noteCreatedAt) noteCreatedAt.textContent = formatDate(note.created_at);
    if (noteUpdatedAt) noteUpdatedAt.textContent = formatDate(note.updated_at);
    if (noteReviewCount) noteReviewCount.textContent = note.review_count || 0;
    
    // Mettre à jour le bouton d'archivage
    const archiveToggleBtn = document.getElementById('archiveToggleBtn');
    if (archiveToggleBtn) {
        if (note.is_archived) {
            archiveToggleBtn.className = 'btn btn-outline-success btn-sm';
            archiveToggleBtn.innerHTML = '<i class="bi bi-arrow-up-circle"></i>';
            archiveToggleBtn.title = 'Désarchiver cette note';
        } else {
            archiveToggleBtn.className = 'btn btn-outline-warning btn-sm';
            archiveToggleBtn.innerHTML = '<i class="bi bi-archive"></i>';
            archiveToggleBtn.title = 'Archiver cette note';
        }
    }
}

// Créer une nouvelle note
async function createNewNote() {
    try {
        const newNoteData = {
            title: 'Nouvelle note',
            language: 'fr',
            content: '',
            translation: '',
            example_sentences: [],
            related_words: []
        };
        
        const createdNote = await notebookService.createNote(newNoteData);
        notes.unshift(createdNote);
        displayNotes(notes);
        selectNote(createdNote.id);
        updateNotesCount(notes.length);
        
        window.notificationService.success('Note créée avec succès');
        
    } catch (error) {
        console.error('Error creating note:', error);
        window.notificationService.error('Erreur lors de la création de la note');
    }
}

// Sauvegarder la note actuelle
async function saveCurrentNote(showFeedback = false) {
    if (!currentNote) {
        if (showFeedback && window.notificationService) {
            window.notificationService.error('Aucune note sélectionnée');
        }
        return;
    }
    
    try {
        const noteData = {
            title: document.getElementById('noteTitle')?.value || '',
            language: document.getElementById('noteLanguage')?.value || '',
            content: document.getElementById('noteContent')?.value || '',
            translation: document.getElementById('noteTranslation')?.value || '',
            pronunciation: document.getElementById('notePronunciation')?.value || '',
            difficulty: document.getElementById('noteDifficulty')?.value || '',
            example_sentences: (document.getElementById('noteExamples')?.value || '').split('\n').filter(s => s.trim()),
            related_words: (document.getElementById('noteRelatedWords')?.value || '').split(',').map(s => s.trim()).filter(s => s),
            note_type: document.getElementById('noteType')?.value || 'NOTE',
            priority: document.getElementById('notePriority')?.value || 'MEDIUM',
            is_pinned: document.getElementById('notePinned')?.checked || false,
            is_archived: document.getElementById('noteArchived')?.checked || false
        };
        
        const updatedNote = await notebookService.updateNote(currentNote.id, noteData);
        
        // Mettre à jour la note dans la liste
        const index = notes.findIndex(n => n.id === currentNote.id);
        if (index !== -1) {
            notes[index] = updatedNote;
            currentNote = updatedNote;
            displayNotes(notes);
            
            // Marquer la note comme active sans recharger tout l'éditeur
            document.querySelectorAll('.note-item').forEach(item => {
                item.classList.remove('active');
            });
            const activeItem = document.querySelector(`[data-note-id="${updatedNote.id}"]`);
            if (activeItem) activeItem.classList.add('active');
            
            // Mettre à jour les statistiques
            const updatedAtElement = document.getElementById('noteUpdatedAt');
            if (updatedAtElement) updatedAtElement.textContent = formatDate(updatedNote.updated_at);
        }
        
        // Feedback de succès
        if (showFeedback) {
            showSaveAlert();
        } else {
            console.log('Note sauvegardée automatiquement');
        }
        
    } catch (error) {
        console.error('Error saving note:', error);
        if (window.notificationService) {
            window.notificationService.error('Erreur lors de la sauvegarde');
        } else if (showFeedback) {
            alert('Erreur lors de la sauvegarde');
        }
    }
}

// Afficher une alert de sauvegarde réussie
function showSaveAlert() {
    // Supprimer les alertes existantes
    const existingAlerts = document.querySelectorAll('.save-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Créer l'alert Bootstrap
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show save-alert';
    alertDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        <i class="bi bi-check-circle-fill me-2"></i>
        <strong>Note sauvegardée avec succès!</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Ajouter à la page
    document.body.appendChild(alertDiv);
    
    // Supprimer automatiquement après 3 secondes
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

// Supprimer la note actuelle
async function deleteCurrentNote() {
    console.log('=== DELETE FUNCTION CALLED ===');
    console.log('currentNote:', currentNote);
    
    if (!currentNote) {
        console.log('Pas de note sélectionnée');
        if (window.notificationService) {
            window.notificationService.error('Aucune note sélectionnée');
        }
        return;
    }
    
    const confirmed = confirm('Êtes-vous sûr de vouloir supprimer cette note ?');
    console.log('User confirmed deletion:', confirmed);
    
    if (!confirmed) {
        console.log('Suppression annulée par l\'utilisateur');
        return;
    }
    
    try {
        console.log('Tentative de suppression de la note ID:', currentNote.id);
        const deleteUrl = `${notebookService.baseUrl}/notes/${currentNote.id}/`;
        console.log('URL de suppression:', deleteUrl);
        
        const result = await notebookService.deleteNote(currentNote.id);
        console.log('Résultat de la suppression:', result);
        
        // Supprimer de la liste
        notes = notes.filter(n => n.id !== currentNote.id);
        displayNotes(notes);
        updateNotesCount(notes.length);
        
        // Sélectionner une autre note si possible
        if (notes.length > 0) {
            selectNote(notes[0].id);
        } else {
            showEmpty();
            currentNote = null;
        }
        
        if (window.notificationService) {
            window.notificationService.success('Note supprimée avec succès');
        }
        
    } catch (error) {
        console.error('Erreur détaillée lors de la suppression:', error);
        console.error('Stack trace:', error.stack);
        
        let errorMessage = 'Erreur lors de la suppression';
        if (error.message) {
            errorMessage += ': ' + error.message;
        }
        
        if (window.notificationService) {
            window.notificationService.error(errorMessage);
        } else {
            alert(errorMessage);
        }
    }
}

// Recherche avec délai
function debounceSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(filterNotes, 300);
}

// Filtrer les notes
function filterNotes() {
    const currentNoteId = currentNote?.id;
    loadNotes().then(() => {
        // Appliquer les filtres selon la vue courante
        const filteredNotes = applyViewFilters();
        displayNotes(filteredNotes);
        
        // Si la note courante existe encore après filtrage, la maintenir sélectionnée
        if (currentNoteId && filteredNotes.find(n => n.id === currentNoteId)) {
            selectNote(currentNoteId);
        }
    });
}

// Actualiser les notes
function refreshNotes() {
    const currentNoteId = currentNote?.id;
    loadNotes().then(() => {
        // Appliquer les filtres selon la vue courante
        const filteredNotes = applyViewFilters();
        displayNotes(filteredNotes);
        
        // Essayer de restaurer la note sélectionnée
        if (currentNoteId && filteredNotes.find(n => n.id === currentNoteId)) {
            selectNote(currentNoteId);
        }
    });
}

// Basculer la sidebar sur mobile
function toggleSidebar() {
    const sidebar = document.getElementById('notebookSidebar');
    const isVisible = sidebar.classList.contains('show');
    
    // Toggle sidebar visibility
    sidebar.classList.toggle('show');
    
    // Update button icon and accessibility attributes based on new state
    const toggleBtn = document.getElementById('toggleSidebar');
    const icon = toggleBtn?.querySelector('i');
    if (icon && toggleBtn) {
        if (isVisible) {
            // Sidebar will be hidden - show "expand" icon
            icon.className = 'bi bi-layout-sidebar-inset-reverse';
            toggleBtn.title = 'Afficher la barre latérale';
            toggleBtn.setAttribute('aria-expanded', 'false');
        } else {
            // Sidebar will be shown - show "collapse" icon
            icon.className = 'bi bi-layout-sidebar-inset';
            toggleBtn.title = 'Masquer la barre latérale';
            toggleBtn.setAttribute('aria-expanded', 'true');
        }
    }
}

// États d'affichage
function showLoading() {
    const loadingDiv = document.getElementById('loadingNotes');
    const emptyDiv = document.getElementById('emptyNotes');
    if (loadingDiv) loadingDiv.style.display = 'block';
    if (emptyDiv) emptyDiv.style.display = 'none';
}

function showEmpty() {
    const noteEditor = document.getElementById('noteEditor');
    if (noteEditor) noteEditor.style.display = 'none';
}

function showEditor() {
    const noteEditor = document.getElementById('noteEditor');
    if (noteEditor) noteEditor.style.display = 'flex';
}

// Utilitaires
function updateNotesCount(count) {
    const notesCountElement = document.getElementById('notesCount');
    if (notesCountElement) {
        notesCountElement.textContent = `${count} note${count !== 1 ? 's' : ''}`;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Hier';
    if (diffDays <= 7) return `Il y a ${diffDays} jours`;
    return date.toLocaleDateString('fr-FR');
}

// Configuration des raccourcis clavier
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+S pour sauvegarder
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            saveCurrentNote();
        }
        
        // Ctrl+N pour nouvelle note
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            createNewNote();
        }
        
        // Échap pour fermer la sidebar mobile
        if (e.key === 'Escape') {
            const sidebar = document.getElementById('sidebar');
            if (sidebar && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
            }
        }
    });
}

// Configuration de l'auto-sauvegarde
function setupAutoSave() {
    let autoSaveTimeout = null;
    
    function scheduleAutoSave() {
        if (autoSaveTimeout) {
            clearTimeout(autoSaveTimeout);
        }
        
        autoSaveTimeout = setTimeout(() => {
            if (currentNote) {
                saveCurrentNote();
            }
        }, 2000); // Auto-save après 2 secondes d'inactivité
    }
    
    // Attacher les événements d'auto-sauvegarde aux champs d'édition
    const autoSaveFields = [
        'noteTitle', 'noteContent', 'noteTranslation', 'notePronunciation',
        'noteExamples', 'noteRelatedWords', 'noteLanguage', 'noteDifficulty',
        'noteType', 'notePriority', 'notePinned', 'noteArchived'
    ];
    
    autoSaveFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', scheduleAutoSave);
            field.addEventListener('change', scheduleAutoSave);
        }
    });
}

// === FONCTIONS DE SÉLECTION MULTIPLE ===

// Basculer le mode sélection multiple
function toggleMultiSelect() {
    isMultiSelectMode = !isMultiSelectMode;
    selectedNotes.clear();
    
    const multiSelectControls = document.getElementById('multiSelectControls');
    const normalControls = document.getElementById('normalControls');
    
    if (isMultiSelectMode) {
        // Transition fluide vers mode sélection
        normalControls.classList.remove('show');
        normalControls.classList.add('fade-out');
        
        setTimeout(() => {
            normalControls.style.display = 'none';
            multiSelectControls.style.display = 'flex';
            multiSelectControls.classList.remove('fade-out');
            multiSelectControls.classList.add('show');
        }, 200);
    } else {
        // Transition fluide vers mode normal  
        multiSelectControls.classList.remove('show');
        multiSelectControls.classList.add('fade-out');
        
        setTimeout(() => {
            multiSelectControls.style.display = 'none';
            normalControls.style.display = 'flex';
            normalControls.classList.remove('fade-out');
            normalControls.classList.add('show');
        }, 200);
    }
    
    displayNotes(notes);
    updateSelectedCounts();
}

// Annuler la sélection multiple
function cancelMultiSelect() {
    isMultiSelectMode = false;
    selectedNotes.clear();
    
    const multiSelectControls = document.getElementById('multiSelectControls');
    const normalControls = document.getElementById('normalControls');
    
    // Transition fluide vers mode normal
    multiSelectControls.classList.remove('show');
    multiSelectControls.classList.add('fade-out');
    
    setTimeout(() => {
        multiSelectControls.style.display = 'none';
        normalControls.style.display = 'flex';
        normalControls.classList.remove('fade-out');
        normalControls.classList.add('show');
    }, 200);
    
    displayNotes(notes);
}

// Basculer la sélection d'une note
function toggleNoteSelection(noteId) {
    if (selectedNotes.has(noteId)) {
        selectedNotes.delete(noteId);
    } else {
        selectedNotes.add(noteId);
    }
    
    // Mettre à jour l'affichage de la note
    const noteElement = document.querySelector(`[data-note-id="${noteId}"]`);
    if (noteElement) {
        const checkbox = noteElement.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.checked = selectedNotes.has(noteId);
        }
        
        if (selectedNotes.has(noteId)) {
            noteElement.classList.add('selected');
        } else {
            noteElement.classList.remove('selected');
        }
    }
    
    updateSelectedCounts();
}

// Mettre à jour les compteurs
function updateSelectedCounts() {
    const count = selectedNotes.size;
    const selectedCountElement = document.getElementById('selectedCount');
    const selectedCountArchiveElement = document.getElementById('selectedCountArchive');
    const selectedCountUnarchiveElement = document.getElementById('selectedCountUnarchive');
    
    // Fonction pour animer les badges
    const animateBadge = (element) => {
        if (element) {
            element.classList.remove('updated');
            void element.offsetWidth; // Force reflow
            element.classList.add('updated');
        }
    };
    
    if (selectedCountElement) {
        selectedCountElement.textContent = count;
        animateBadge(selectedCountElement);
    }
    if (selectedCountArchiveElement) {
        selectedCountArchiveElement.textContent = count;
        animateBadge(selectedCountArchiveElement);
    }
    if (selectedCountUnarchiveElement) {
        selectedCountUnarchiveElement.textContent = count;
        animateBadge(selectedCountUnarchiveElement);
    }
    
    // Activer/désactiver les boutons selon la sélection
    const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
    if (bulkDeleteBtn) {
        bulkDeleteBtn.disabled = count === 0;
        if (count === 0) {
            bulkDeleteBtn.classList.add('disabled');
        } else {
            bulkDeleteBtn.classList.remove('disabled');
        }
    }
}

// Suppression en lot
async function bulkDelete() {
    if (selectedNotes.size === 0) {
        window.notificationService?.error('Aucune note sélectionnée');
        return;
    }
    
    const confirmed = confirm(`Êtes-vous sûr de vouloir supprimer ${selectedNotes.size} note(s) ?`);
    if (!confirmed) return;
    
    try {
        const noteIds = Array.from(selectedNotes);
        await notebookService.bulkDelete(noteIds);
        
        // Supprimer les notes de la liste locale
        notes = notes.filter(note => !selectedNotes.has(note.id));
        selectedNotes.clear();
        
        displayNotes(notes);
        updateNotesCount(notes.length);
        updateSelectedCounts();
        
        // Si plus aucune note, cacher l'éditeur
        if (notes.length === 0) {
            showEmpty();
            currentNote = null;
        } else if (currentNote && selectedNotes.has(currentNote.id)) {
            // Si la note actuelle était supprimée, sélectionner la première disponible
            selectNote(notes[0].id);
        }
        
        window.notificationService?.success(`${noteIds.length} note(s) supprimée(s)`);
        
    } catch (error) {
        console.error('Error bulk deleting notes:', error);
        window.notificationService?.error('Erreur lors de la suppression en lot');
    }
}

// Archivage en lot
async function bulkArchive() {
    if (selectedNotes.size === 0) {
        window.notificationService?.error('Aucune note sélectionnée');
        return;
    }
    
    const confirmed = confirm(`Êtes-vous sûr de vouloir archiver ${selectedNotes.size} note(s) ?`);
    if (!confirmed) return;
    
    try {
        const noteIds = Array.from(selectedNotes);
        await notebookService.bulkUpdate(noteIds, { is_archived: true });
        
        // Mettre à jour les notes localement
        notes = notes.map(note => {
            if (selectedNotes.has(note.id)) {
                return { ...note, is_archived: true };
            }
            return note;
        });
        
        selectedNotes.clear();
        displayNotes(notes);
        updateSelectedCounts();
        
        window.notificationService?.success(`${noteIds.length} note(s) archivée(s)`);
        
    } catch (error) {
        console.error('Error bulk archiving notes:', error);
        window.notificationService?.error('Erreur lors de l\'archivage en lot');
    }
}

// Désarchiver une note individuelle
async function unarchiveNote(noteId) {
    try {
        const note = notes.find(n => n.id === noteId);
        if (!note) return;
        
        const updatedNote = await notebookService.updateNote(noteId, {
            ...note,
            is_archived: false
        });
        
        // Mettre à jour la note localement
        const index = notes.findIndex(n => n.id === noteId);
        if (index !== -1) {
            notes[index] = updatedNote;
        }
        
        // Rafraîchir l'affichage
        displayNotes(notes);
        
        // Si on était en mode "notes archivées", recharger pour la faire disparaître
        const archiveFilter = document.getElementById('archiveFilter')?.value;
        if (archiveFilter === 'archived') {
            loadNotes();
        }
        
        window.notificationService?.success('Note désarchivée');
        
    } catch (error) {
        console.error('Error unarchiving note:', error);
        window.notificationService?.error('Erreur lors du désarchivage');
    }
}

// Fonction pour basculer l'archivage d'une note depuis l'éditeur
async function toggleArchiveCurrentNote() {
    if (!currentNote) return;
    
    try {
        const newArchivedState = !currentNote.is_archived;
        const updatedNote = await notebookService.updateNote(currentNote.id, {
            ...currentNote,
            is_archived: newArchivedState
        });
        
        // Mettre à jour la note courante et la liste
        currentNote = updatedNote;
        const index = notes.findIndex(n => n.id === currentNote.id);
        if (index !== -1) {
            notes[index] = updatedNote;
        }
        
        // Mettre à jour l'interface
        displayNotes(notes);
        loadNoteInEditor(updatedNote);
        
        const action = newArchivedState ? 'archivée' : 'désarchivée';
        window.notificationService?.success(`Note ${action}`);
        
    } catch (error) {
        console.error('Error toggling archive status:', error);
        window.notificationService?.error('Erreur lors du changement de statut');
    }
}

// Désarchivage en lot
async function bulkUnarchive() {
    if (selectedNotes.size === 0) {
        window.notificationService?.error('Aucune note sélectionnée');
        return;
    }
    
    const confirmed = confirm(`Êtes-vous sûr de vouloir désarchiver ${selectedNotes.size} note(s) ?`);
    if (!confirmed) return;
    
    try {
        const noteIds = Array.from(selectedNotes);
        await notebookService.bulkUpdate(noteIds, { is_archived: false });
        
        // Mettre à jour les notes localement
        notes = notes.map(note => {
            if (selectedNotes.has(note.id)) {
                return { ...note, is_archived: false };
            }
            return note;
        });
        
        selectedNotes.clear();
        displayNotes(notes);
        updateSelectedCounts();
        
        window.notificationService?.success(`${noteIds.length} note(s) désarchivée(s)`);
        
    } catch (error) {
        console.error('Error bulk unarchiving notes:', error);
        window.notificationService?.error('Erreur lors du désarchivage en lot');
    }
}

// === FONCTIONS DE NAVIGATION ===

// Variables globales pour la navigation
let currentView = 'notes'; // 'notes', 'archived', 'tags'

// Afficher la vue des notes
function showNotesView() {
    currentView = 'notes';
    
    // Mettre à jour les onglets
    updateActiveTab('notes');
    
    // Créer ou mettre à jour l'élément archiveFilter pour les notes actives
    let archiveFilter = document.getElementById('archiveFilter');
    if (!archiveFilter) {
        archiveFilter = document.createElement('input');
        archiveFilter.type = 'hidden';
        archiveFilter.id = 'archiveFilter';
        document.body.appendChild(archiveFilter);
    }
    archiveFilter.value = 'active';
    
    // Recharger les notes avec le bon filtre
    loadNotes();
    
    console.log('📝 Vue "Mes notes" activée');
}

// Afficher la vue des archives
function showArchivedView() {
    currentView = 'archived';
    
    // Mettre à jour les onglets
    updateActiveTab('archived');
    
    // Créer ou mettre à jour l'élément archiveFilter pour les notes archivées
    let archiveFilter = document.getElementById('archiveFilter');
    if (!archiveFilter) {
        archiveFilter = document.createElement('input');
        archiveFilter.type = 'hidden';
        archiveFilter.id = 'archiveFilter';
        document.body.appendChild(archiveFilter);
    }
    archiveFilter.value = 'archived';
    
    // Recharger les notes avec le bon filtre
    loadNotes();
    
    console.log('📦 Vue "Archives" activée');
}

// Afficher la vue des étiquettes
function showTagsView() {
    currentView = 'tags';
    
    // Mettre à jour les onglets
    updateActiveTab('tags');
    
    // Créer ou mettre à jour l'élément archiveFilter pour toutes les notes
    let archiveFilter = document.getElementById('archiveFilter');
    if (!archiveFilter) {
        archiveFilter = document.createElement('input');
        archiveFilter.type = 'hidden';
        archiveFilter.id = 'archiveFilter';
        document.body.appendChild(archiveFilter);
    }
    archiveFilter.value = 'all';
    
    // Recharger les notes avec le bon filtre
    loadNotes();
    
    // Ouvrir le modal de gestion des étiquettes
    if (window.notebookTagsManagement) {
        window.notebookTagsManagement.showTagsManagement();
    }
    
    console.log('🏷️ Vue "Étiquettes" activée');
}

// === FONCTIONS DE FILTRAGE ===
function selectLanguageFilter(value, label) {
    const button = document.getElementById('languageFilterToggle');
    const text = document.getElementById('languageFilterText');
    
    if (button && text) {
        text.textContent = label;
        // Mettre à jour un input caché ou une variable pour le filtrage
        const hiddenInput = document.getElementById('languageFilter') || document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.id = 'languageFilter';
        hiddenInput.value = value;
        if (!document.getElementById('languageFilter')) {
            document.body.appendChild(hiddenInput);
        }
        
        // Rafraîchir les notes avec le nouveau filtre
        refreshNotes();
    }
    console.log(`🌐 Filtre langue: ${label} (${value})`);
}

function selectSortFilter(value, label) {
    const button = document.getElementById('sortFilterToggle');
    const text = document.getElementById('sortFilterText');
    
    if (button && text) {
        text.textContent = label;
        // Mettre à jour un input caché ou une variable pour le tri
        const hiddenInput = document.getElementById('sortFilter') || document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.id = 'sortFilter';
        hiddenInput.value = value;
        if (!document.getElementById('sortFilter')) {
            document.body.appendChild(hiddenInput);
        }
        
        // Rafraîchir les notes avec le nouveau tri
        refreshNotes();
    }
    console.log(`🔄 Tri: ${label} (${value})`);
}

function selectTagsFilter(value, label) {
    const button = document.getElementById('tagsFilterToggle');
    const text = document.getElementById('tagsFilterText');
    
    if (button && text) {
        text.textContent = label;
        // Mettre à jour un input caché ou une variable pour le filtrage
        const hiddenInput = document.getElementById('tagsFilter') || document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.id = 'tagsFilter';
        hiddenInput.value = value;
        if (!document.getElementById('tagsFilter')) {
            document.body.appendChild(hiddenInput);
        }
        
        // Rafraîchir les notes avec le nouveau filtre
        refreshNotes();
    }
    console.log(`🏷️ Filtre tags: ${label} (${value})`);
}

// Exposer les fonctions de navigation globalement pour les onclick handlers
window.showNotesView = showNotesView;
window.showArchivedView = showArchivedView;
window.showTagsView = showTagsView;
window.refreshNotes = refreshNotes;
window.toggleSidebar = toggleSidebar;
window.createNewNote = createNewNote;
window.saveCurrentNote = saveCurrentNote;
window.selectLanguageFilter = selectLanguageFilter;
window.selectSortFilter = selectSortFilter;
window.selectTagsFilter = selectTagsFilter;
window.debounceSearch = debounceSearch;

// Mettre à jour l'onglet actif
function updateActiveTab(activeTab) {
    // Supprimer la classe active de tous les onglets
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Ajouter la classe active au bon onglet
    const tabs = document.querySelectorAll('.nav-tab');
    if (activeTab === 'notes' && tabs[0]) {
        tabs[0].classList.add('active');
    } else if (activeTab === 'archived' && tabs[1]) {
        tabs[1].classList.add('active');
    } else if (activeTab === 'tags' && tabs[2]) {
        tabs[2].classList.add('active');
    }
}

// Mettre à jour l'interface selon la vue
function updateViewInterface() {
    const notesContainer = document.getElementById('notesContainer');
    const editor = document.getElementById('editor');
    
    if (currentView === 'notes') {
        // Vue normale des notes
        if (notesContainer) notesContainer.style.display = 'block';
        if (editor) editor.style.display = 'block';
    } else if (currentView === 'archived') {
        // Vue des archives
        if (notesContainer) notesContainer.style.display = 'block';
        if (editor) editor.style.display = 'block';
    } else if (currentView === 'tags') {
        // Vue des étiquettes - garder l'interface normale
        if (notesContainer) notesContainer.style.display = 'block';
        if (editor) editor.style.display = 'block';
    }
    
    // Mettre à jour le compteur
    updateSelectedCounts();
}

// Appliquer les filtres selon la vue courante
function applyViewFilters() {
    let filteredNotes = [];
    
    if (currentView === 'notes') {
        filteredNotes = notes.filter(note => !note.is_archived);
    } else if (currentView === 'archived') {
        filteredNotes = notes.filter(note => note.is_archived);
    } else {
        filteredNotes = notes; // Pour la vue étiquettes, on garde toutes les notes
    }
    
    return filteredNotes;
}

// Initialiser la vue au chargement
document.addEventListener('DOMContentLoaded', () => {
    // S'assurer que la vue "Mes notes" est active par défaut
    setTimeout(() => {
        showNotesView();
    }, 100);
});