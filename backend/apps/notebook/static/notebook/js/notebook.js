// Notebook Application JavaScript

function notebookApp() {
    return {
        // État général
        isLoading: false,
        notes: [],
        currentNote: null,
        selectedNotes: [],
        totalNotes: 0,
        totalPages: 1,
        currentPage: 1,
        linguifyEditor: null, // Editor.js instance
        saveTimeout: null, // Pour le debouncing de la sauvegarde
        autoSaveInterval: null, // Pour la sauvegarde automatique
        isSaving: false, // Pour éviter les sauvegardes multiples

        // Filtres
        searchQuery: '',
        selectedLanguage: '',
        archiveStatus: 'active',
        sortBy: 'updated_desc',

        // Modal de confirmation de suppression
        showDeleteModal: false,
        deleteModalType: 'single', // 'single' ou 'bulk'
        deleteModalData: null, // Données de l'élément à supprimer
        deleteModalTitle: 'Delete Confirmation',
        deleteModalCallback: null, // Fonction à exécuter lors de la confirmation

        // Convert to Tasks modal
        showConvertModal: false,
        selectedProjectId: '',
        todoProjects: [],
        convertPreview: [],
        isConverting: false,


        // Méthodes
        init() {
            this.loadNotes();
            this.initEditor();

            // Auto-save every 5 seconds if there's an active note
            this.autoSaveInterval = setInterval(() => {
                if (this.currentNote && this.linguifyEditor && this.linguifyEditor.isReady) {
                    this.saveCurrentNote();
                }
            }, 5000); // 5 seconds

            // Save before page unload
            window.addEventListener('beforeunload', () => {
                if (this.currentNote) {
                    this.saveCurrentNote();
                }
            });
        },

        async saveCurrentNote() {
            if (!this.currentNote || !this.linguifyEditor || !this.linguifyEditor.isReady) {
                return;
            }

            // Prevent multiple saves at the same time
            if (this.isSaving) {
                return;
            }

            try {
                this.isSaving = true;
                const data = await this.linguifyEditor.save();

                if (data && data.blocks && Array.isArray(data.blocks)) {
                    // Don't save if there are no blocks (empty content)
                    if (data.blocks.length === 0) {
                        console.log('Skipping save - no content blocks');
                        return;
                    }

                    const newContent = JSON.stringify(data);

                    // Only save if content has changed significantly
                    if (newContent !== this.currentNote.content) {
                        this.currentNote.content = newContent;
                        console.log('Auto-saving note with', data.blocks.length, 'blocks');
                        await this.updateNote();
                    }
                } else {
                    console.log('No valid data to save');
                }
            } catch (error) {
                console.error('Error in auto-save:', error);
            } finally {
                this.isSaving = false;
            }
        },

        async initEditor() {
            // Initialize LinguifyEditor with Editor.js
            if (!this.linguifyEditor && document.getElementById('editorjs-container')) {
                this.linguifyEditor = new LinguifyEditor('editorjs-container', {
                    onChange: (data, api, event) => {
                        // Just log that content changed, the actual saving is handled by the interval
                        console.log('Editor content changed');
                    },
                    onReady: () => {
                        console.log('Editor.js is ready for notebook!');
                    }
                });

                await this.linguifyEditor.init();
            }
        },

        async loadNotes() {
            this.isLoading = true;
            try {
                // Map sort values to DRF ordering format
                const sortMapping = {
                    'updated_desc': '-updated_at',
                    'updated_asc': 'updated_at',
                    'title_asc': 'title',
                    'title_desc': '-title'
                };

                const params = new URLSearchParams({
                    page: this.currentPage,
                    search: this.searchQuery,
                    language: this.selectedLanguage,
                    archive_status: this.archiveStatus,
                    ordering: sortMapping[this.sortBy] || '-updated_at'
                });

                // Use the DRF API endpoint
                const response = await fetch(`/notebook/api/notes/?${params}`, {
                    headers: {
                        'Accept': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    credentials: 'same-origin'
                });

                const data = await response.json();
                this.notes = data.results;
                this.totalPages = Math.ceil(data.count / 20);  // Mis à jour pour page_size=20
                this.totalNotes = data.count;
            } catch (error) {
                console.error('Error loading notes:', error);
                this.showAlert('Error loading notes', 'error');
            } finally {
                this.isLoading = false;
            }
        },

        changePage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
                this.loadNotes();
            }
        },



        deleteNote(noteId) {
            // Trouver la note dans la liste pour afficher ses informations dans le modal
            const note = this.notes.find(n => n.id === noteId);

            this.showDeleteConfirmation(
                'single',
                note,
                async () => {
                    try {
                        const response = await fetch(`/notebook/api/notes/${noteId}/`, {
                            method: 'DELETE',
                            headers: {
                                'X-CSRFToken': this.getCsrfToken()
                            },
                            credentials: 'same-origin'
                        });

                        if (response.ok) {
                            await this.loadNotes();
                            if (this.currentNote && this.currentNote.id === noteId) {
                                this.currentNote = null;
                            }
                            this.showAlert('Note supprimée avec succès ! 🗑️', 'success');
                        } else {
                            throw new Error('Failed to delete note');
                        }
                    } catch (error) {
                        console.error('Error deleting note:', error);
                        this.showAlert('Error deleting note', 'error');
                        throw error; // Re-throw pour que le modal gère l'erreur
                    }
                },
                'Delete Note'
            );
        },

        async _performDeleteNote(noteId) {
            // Fonction helper pour la logique de suppression (gardée pour référence si nécessaire)
            try {
                const response = await fetch(`/notebook/api/notes/${noteId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    credentials: 'same-origin'
                });

                if (response.ok) {
                    await this.loadNotes();
                    if (this.currentNote && this.currentNote.id === noteId) {
                        this.currentNote = null;
                    }
                    this.showAlert('Note deleted successfully!', 'success');
                } else {
                    throw new Error('Failed to delete note');
                }
            } catch (error) {
                console.error('Error deleting note:', error);
                this.showAlert('Error deleting note', 'error');
            }
        },

        async togglePin(note) {
            try {
                const updatedNote = { ...note, is_pinned: !note.is_pinned };

                const response = await fetch(`/notebook/api/notes/${note.id}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ is_pinned: !note.is_pinned })
                });

                if (response.ok) {
                    await this.loadNotes();
                    if (this.currentNote && this.currentNote.id === note.id) {
                        this.currentNote.is_pinned = !note.is_pinned;
                    }
                } else {
                    throw new Error('Failed to update pin status');
                }
            } catch (error) {
                console.error('Error toggling pin:', error);
                this.showAlert('Error updating pin status', 'error');
            }
        },

        toggleSelection(noteId) {
            const index = this.selectedNotes.indexOf(noteId);
            if (index === -1) {
                this.selectedNotes.push(noteId);
            } else {
                this.selectedNotes.splice(index, 1);
            }
        },

        async bulkArchive() {
            if (this.selectedNotes.length === 0) return;

            try {
                // Execute all archive requests in parallel for better performance
                await Promise.all(
                    this.selectedNotes.map(noteId =>
                        fetch(`/notebook/api/notes/${noteId}/`, {
                            method: 'PATCH',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': this.getCsrfToken()
                            },
                            credentials: 'same-origin',
                            body: JSON.stringify({ is_archived: true })
                        })
                    )
                );

                await this.loadNotes();
                this.selectedNotes = [];
            } catch (error) {
                console.error('Error archiving notes:', error);
                this.showAlert('Error archiving notes', 'error');
            }
        },

        async bulkUnarchive() {
            if (this.selectedNotes.length === 0) return;

            try {
                // Execute all unarchive requests in parallel for better performance
                await Promise.all(
                    this.selectedNotes.map(noteId =>
                        fetch(`/notebook/api/notes/${noteId}/`, {
                            method: 'PATCH',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': this.getCsrfToken()
                            },
                            credentials: 'same-origin',
                            body: JSON.stringify({ is_archived: false })
                        })
                    )
                );

                await this.loadNotes();
                this.selectedNotes = [];
            } catch (error) {
                console.error('Error unarchiving notes:', error);
                this.showAlert('Error unarchiving notes', 'error');
            }
        },

        bulkDelete() {
            if (this.selectedNotes.length === 0) return;

            this.showDeleteConfirmation(
                'bulk',
                { count: this.selectedNotes.length },
                async () => {
                    try {
                        const deletedCount = this.selectedNotes.length;
                        // Execute all delete requests in parallel for better performance
                        await Promise.all(
                            this.selectedNotes.map(noteId =>
                                fetch(`/notebook/api/notes/${noteId}/`, {
                                    method: 'DELETE',
                                    headers: {
                                        'X-CSRFToken': this.getCsrfToken()
                                    },
                                    credentials: 'same-origin'
                                })
                            )
                        );

                        await this.loadNotes();
                        this.selectedNotes = [];
                        this.showAlert(`${deletedCount} notes supprimées avec succès ! 🎉`, 'success');
                    } catch (error) {
                        console.error('Error deleting notes:', error);
                        this.showAlert('Error deleting notes', 'error');
                        throw error; // Re-throw pour que le modal gère l'erreur
                    }
                },
                'Delete Multiple Notes'
            );
        },

        async createNewNote() {
            try {
                // Créer une nouvelle note avec titre par défaut
                const newNote = {
                    title: 'Nouvelle note',
                    content: '',
                    language: '',
                    is_pinned: false,
                    is_archived: false
                };

                const response = await fetch('/notebook/api/notes/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(newNote)
                });

                if (response.ok) {
                    const createdNote = await response.json();
                    // Recharger les notes et ouvrir la nouvelle
                    await this.loadNotes();
                    this.openNote(createdNote);
                } else {
                    throw new Error('Failed to create note');
                }
            } catch (error) {
                console.error('Error creating note:', error);
                this.showAlert('Erreur lors de la création de la note', 'error');
            }
        },


        getCsrfToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        },

        showAlert(message, type = 'success', duration = 5000) {
            // No alerts or notifications - silent operation
        },

        // Helper functions for the notes display
        timeAgo(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(diff / 3600000);
            const days = Math.floor(diff / 86400000);

            if (minutes < 1) return 'just now';
            if (minutes < 60) return `${minutes}m ago`;
            if (hours < 24) return `${hours}h ago`;
            if (days < 30) return `${days}d ago`;
            return date.toLocaleDateString();
        },

        selectNote(noteId, event) {
            // Handle note selection (could be used for detailed view)
            if (!event.target.closest('input') && !event.target.closest('button')) {
                console.log('Selected note:', noteId);
                // Future: show note details or edit mode
            }
        },

        clearSelection() {
            this.selectedNotes = [];
        },

        selectAll() {
            this.selectedNotes = this.notes.map(note => note.id);
        },

        async openNote(note) {
            console.log('Opening note:', note.id, 'Content length:', note.content?.length || 0);

            // Deep clone the note to avoid direct mutations
            this.currentNote = JSON.parse(JSON.stringify(note));

            // Load content in Editor.js
            if (this.linguifyEditor && this.linguifyEditor.isReady) {
                try {
                    // Clear current editor content
                    await this.linguifyEditor.clear();

                    // Load note content
                    if (this.currentNote.content && this.currentNote.content.trim() !== '') {
                        let contentData;
                        try {
                            // Try to parse as JSON (Editor.js format)
                            contentData = JSON.parse(this.currentNote.content);
                            console.log('Parsed content data:', contentData);

                            // Ensure we have valid blocks
                            if (!contentData.blocks || !Array.isArray(contentData.blocks) || contentData.blocks.length === 0) {
                                console.log('No valid blocks found, creating empty paragraph');
                                contentData = {
                                    blocks: [{
                                        type: 'paragraph',
                                        data: { text: '' }
                                    }]
                                };
                            }
                        } catch (e) {
                            console.log('Content is not JSON, treating as plain text');
                            // If not JSON, convert plain text to Editor.js format
                            contentData = {
                                blocks: [{
                                    type: 'paragraph',
                                    data: {
                                        text: this.currentNote.content
                                    }
                                }]
                            };
                        }

                        console.log('Rendering content with', contentData.blocks.length, 'blocks');
                        await this.linguifyEditor.render(contentData);
                    } else {
                        console.log('No content to load, loading empty editor');
                        // Load empty content
                        await this.linguifyEditor.render({
                            blocks: [{
                                type: 'paragraph',
                                data: { text: '' }
                            }]
                        });
                    }
                } catch (error) {
                    console.error('Error loading note in editor:', error);
                }
            } else {
                console.log('Editor not ready, cannot load note');
            }
        },

        // Debounced auto-save function
        debouncedSave() {
            if (this.saveTimeout) {
                clearTimeout(this.saveTimeout);
            }
            this.saveTimeout = setTimeout(() => {
                this.updateNote();
            }, 2000); // Save after 2 seconds of inactivity
        },

        async updateNote() {
            if (!this.currentNote || !this.currentNote.id) return;

            try {
                // Prepare the data to send
                const updateData = {
                    title: this.currentNote.title,
                    content: this.currentNote.content,
                    language: this.currentNote.language,
                    is_pinned: this.currentNote.is_pinned,
                    is_archived: this.currentNote.is_archived
                };

                const response = await fetch(`/notebook/api/notes/${this.currentNote.id}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(updateData)
                });

                if (response.ok) {
                    const updatedNote = await response.json();
                    // Update the note in the list
                    const index = this.notes.findIndex(n => n.id === updatedNote.id);
                    if (index !== -1) {
                        this.notes[index] = updatedNote;
                    }
                    // Update current note with server response
                    this.currentNote = { ...this.currentNote, ...updatedNote };
                    console.log('Note updated successfully');
                } else {
                    console.error('Failed to update note:', response.status, response.statusText);
                    this.showAlert('Failed to save note', 'error');
                }
            } catch (error) {
                console.error('Error updating note:', error);
                this.showAlert('Error saving note', 'error');
            }
        },

        async copyNoteContent() {
            if (!this.linguifyEditor || !this.currentNote) return;

            try {
                const data = await this.linguifyEditor.save();
                const textContent = this.extractTextFromEditorData(data);
                await navigator.clipboard.writeText(textContent);
                this.showAlert('Contenu copié dans le presse-papiers ! 📋', 'success');
            } catch (error) {
                console.error('Error copying content:', error);
                this.showAlert('Erreur lors de la copie', 'error');
            }
        },

        extractTextFromEditorData(data) {
            if (!data || !data.blocks) return '';

            return data.blocks.map(block => {
                switch (block.type) {
                    case 'paragraph':
                        return block.data.text || '';
                    case 'header':
                        return block.data.text || '';
                    case 'list':
                        return block.data.items.join('\n');
                    case 'quote':
                        return `"${block.data.text}" - ${block.data.caption}`;
                    case 'code':
                        return block.data.code || '';
                    default:
                        return '';
                }
            }).join('\n\n');
        },

        async exportNote() {
            if (!this.linguifyEditor || !this.currentNote) return;

            try {
                const data = await this.linguifyEditor.save();
                const exportData = {
                    title: this.currentNote.title,
                    content: data,
                    language: this.currentNote.language,
                    created_at: this.currentNote.created_at,
                    updated_at: this.currentNote.updated_at
                };

                const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                    type: 'application/json'
                });

                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${this.currentNote.title || 'note'}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);

                this.showAlert('Note exportée avec succès ! 💾', 'success');
            } catch (error) {
                console.error('Error exporting note:', error);
                this.showAlert('Erreur lors de l\'export', 'error');
            }
        },

        // === MODAL FUNCTIONS ===
        showDeleteConfirmation(type, data, callback, title = 'Delete Confirmation') {
            this.deleteModalType = type;
            this.deleteModalData = data;
            this.deleteModalCallback = callback;
            this.deleteModalTitle = title;
            this.showDeleteModal = true;
        },

        async confirmDelete() {
            if (this.deleteModalCallback) {
                try {
                    await this.deleteModalCallback();
                } catch (error) {
                    console.error('Error in delete callback:', error);
                    this.showAlert('Error during deletion', 'error');
                }
            }
            this.showDeleteModal = false;
            this.deleteModalData = null;
            this.deleteModalCallback = null;
        },

        // Convert to Tasks functionality
        async showConvertToTasksModal() {
            if (!this.currentNote) {
                this.showAlert('No note selected', 'error');
                return;
            }

            // Load TODO projects
            await this.loadTodoProjects();

            // Generate preview
            this.convertPreview = this.parseNoteForTasks();

            // Show modal
            this.showConvertModal = true;
        },

        async loadTodoProjects() {
            try {
                const response = await fetch('/api/v1/todo/projects/', {
                    headers: {
                        'X-CSRFToken': this.getCsrfToken()
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    this.todoProjects = data.results || data;
                } else {
                    this.todoProjects = [];
                }
            } catch (error) {
                console.error('Error loading projects:', error);
                this.todoProjects = [];
            }
        },

        parseNoteForTasks() {
            if (!this.currentNote || !this.currentNote.content) {
                return [];
            }

            const tasks = [];
            let contentData;

            try {
                contentData = JSON.parse(this.currentNote.content);
            } catch (e) {
                // If content is not JSON, treat as plain text
                contentData = { blocks: [{ type: 'paragraph', data: { text: this.currentNote.content } }] };
            }

            if (!contentData.blocks) {
                return [];
            }

            // Parse blocks for tasks
            contentData.blocks.forEach(block => {
                if (block.type === 'checklist' && block.data && block.data.items) {
                    // Checklist blocks
                    block.data.items.forEach(item => {
                        tasks.push({
                            title: this.stripHtml(item.text),
                            completed: item.checked || false
                        });
                    });
                } else if (block.type === 'list' && block.data && block.data.items) {
                    // List blocks (ordered or unordered)
                    block.data.items.forEach(item => {
                        const text = this.stripHtml(item);
                        if (text.trim()) {
                            tasks.push({
                                title: text,
                                completed: false
                            });
                        }
                    });
                } else if (block.type === 'paragraph' && block.data && block.data.text) {
                    // Check for checkbox patterns in paragraph text
                    const text = block.data.text;
                    const checkboxRegex = /\[([ xX])\]\s*(.+)/g;
                    let match;

                    while ((match = checkboxRegex.exec(text)) !== null) {
                        tasks.push({
                            title: this.stripHtml(match[2]),
                            completed: match[1].toLowerCase() === 'x'
                        });
                    }
                }
            });

            return tasks;
        },

        stripHtml(html) {
            const tmp = document.createElement('div');
            tmp.innerHTML = html;
            return tmp.textContent || tmp.innerText || '';
        },

        async convertNoteToTasks() {
            if (!this.currentNote || this.convertPreview.length === 0) {
                return;
            }

            this.isConverting = true;

            try {
                const response = await fetch(`/notebook/api/notes/${this.currentNote.id}/convert_to_tasks/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify({
                        project_id: this.selectedProjectId || null
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    this.showAlert(`${data.message}`, 'success');
                    this.showConvertModal = false;
                    this.selectedProjectId = '';
                    this.convertPreview = [];

                    // Optional: redirect to todo app
                    setTimeout(() => {
                        if (confirm('Tasks created! Do you want to view them in the Todo app?')) {
                            window.location.href = '/todo/';
                        }
                    }, 1000);
                } else {
                    const error = await response.json();
                    this.showAlert(error.error || 'Failed to convert note to tasks', 'error');
                }
            } catch (error) {
                console.error('Error converting note to tasks:', error);
                this.showAlert('An error occurred while converting the note', 'error');
            } finally {
                this.isConverting = false;
            }
        },

        showAlert(message, type = 'info') {
            // Simple alert for now - you can enhance this with a toast notification
            if (type === 'error') {
                alert('Error: ' + message);
            } else {
                alert(message);
            }
        }
    }
}
