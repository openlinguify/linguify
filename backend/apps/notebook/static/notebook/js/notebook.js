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

        // Filtres
        searchQuery: '',
        selectedLanguage: '',
        archiveStatus: 'active',
        sortBy: 'updated_desc',


        // Méthodes
        init() {
            this.loadNotes();
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



        async deleteNote(noteId) {
            if (!confirm('Are you sure you want to delete this note?')) return;

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
                for (let noteId of this.selectedNotes) {
                    await fetch(`/notebook/api/notes/${noteId}/`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCsrfToken()
                        },
                        credentials: 'same-origin',
                        body: JSON.stringify({ is_archived: true })
                    });
                }

                await this.loadNotes();
                this.selectedNotes = [];
            } catch (error) {
                console.error('Error archiving notes:', error);
                this.showAlert('Error archiving notes', 'error');
            }
        },

        async bulkDelete() {
            if (this.selectedNotes.length === 0) return;

            if (!confirm(`Are you sure you want to delete ${this.selectedNotes.length} notes?`)) return;

            try {
                for (let noteId of this.selectedNotes) {
                    await fetch(`/notebook/api/notes/${noteId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': this.getCsrfToken()
                        },
                        credentials: 'same-origin'
                    });
                }

                await this.loadNotes();
                this.selectedNotes = [];
            } catch (error) {
                console.error('Error deleting notes:', error);
                this.showAlert('Error deleting notes', 'error');
            }
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

        showAlert(message, type) {
            // Implémentation simple d'alert
            // TODO: Remplacer par un système de notification plus sophistiqué
            if (type === 'error') {
                alert('Error: ' + message);
            } else {
                alert(message);
            }
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

        openNote(note) {
            // Deep clone the note to avoid direct mutations
            this.currentNote = JSON.parse(JSON.stringify(note));
        },

        async updateNote() {
            if (!this.currentNote || !this.currentNote.id) return;

            try {
                const response = await fetch(`/notebook/api/notes/${this.currentNote.id}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(this.currentNote)
                });

                if (response.ok) {
                    const updatedNote = await response.json();
                    // Update the note in the list
                    const index = this.notes.findIndex(n => n.id === updatedNote.id);
                    if (index !== -1) {
                        this.notes[index] = updatedNote;
                    }
                } else {
                    console.error('Failed to update note');
                }
            } catch (error) {
                console.error('Error updating note:', error);
            }
        }
    }
}

// Editor.js notebook component
function notebookEditor() {
    return {
        editor: null,
        isReady: false,
        isLoading: false,

        init() {
            // Initialize when a note is opened
            this.$nextTick(() => {
                // Watch for changes to currentNote on the parent context
                this.$watch('currentNote', (note) => {
                    if (note) {
                        this.initEditor();
                    }
                });
            });
        },

        async initEditor() {
            if (this.editor) {
                this.editor.destroy();
            }

            this.isLoading = true;

            try {
                // Wait for Editor.js to be loaded
                await this.waitForEditorJS();

                console.log('🔧 Initializing Editor.js...');
                this.editor = new EditorJS({
                    holder: 'notebook-editor',
                    placeholder: 'Tapez "/" pour voir les commandes disponibles...',
                    autofocus: true,

                    tools: {
                        header: {
                            class: Header,
                            inlineToolbar: true,
                            config: {
                                placeholder: 'Titre...',
                                levels: [1, 2, 3, 4],
                                defaultLevel: 2
                            },
                            shortcut: 'CMD+SHIFT+H'
                        },

                        list: {
                            class: List,
                            inlineToolbar: true,
                            config: {
                                defaultStyle: 'unordered'
                            }
                        },

                        checklist: {
                            class: Checklist,
                            inlineToolbar: true
                        },

                        quote: {
                            class: Quote,
                            inlineToolbar: true,
                            config: {
                                quotePlaceholder: 'Citation...',
                                captionPlaceholder: 'Auteur...'
                            }
                        },

                        code: {
                            class: CodeTool,
                            config: {
                                placeholder: 'Entrez votre code...'
                            }
                        },

                        delimiter: Delimiter,

                        table: {
                            class: Table,
                            inlineToolbar: true
                        }
                    },

                    // Inline tools
                    inlineToolbar: ['marker', 'inlineCode'],

                    onChange: () => {
                        this.saveContent();
                    }
                });

                await this.editor.isReady;

                // Load existing content if available
                if (this.currentNote && this.currentNote.content) {
                    await this.loadContent();
                }

                this.isReady = true;
                this.isLoading = false;
                console.log('✅ Editor.js ready');

            } catch (error) {
                console.error('❌ Failed to init Editor.js:', error);
                this.isLoading = false;
                this.showFallback();
            }
        },

        async waitForEditorJS() {
            // Wait for all dependencies to load
            const maxWait = 10000; // 10 seconds
            const interval = 100; // Check every 100ms
            let elapsed = 0;

            while (elapsed < maxWait) {
                if (typeof EditorJS !== 'undefined' &&
                    typeof Header !== 'undefined' &&
                    typeof List !== 'undefined' &&
                    typeof Checklist !== 'undefined') {
                    return;
                }
                await new Promise(resolve => setTimeout(resolve, interval));
                elapsed += interval;
            }

            throw new Error('Editor.js dependencies failed to load');
        },

        async loadContent() {
            if (!this.editor || !this.currentNote || !this.currentNote.content) return;

            try {
                let content;
                if (typeof this.currentNote.content === 'string') {
                    content = JSON.parse(this.currentNote.content);
                } else {
                    content = this.currentNote.content;
                }

                await this.editor.render(content);
            } catch (e) {
                // If not valid JSON, treat as plain text
                await this.editor.render({
                    blocks: [{
                        type: 'paragraph',
                        data: { text: this.currentNote.content || '' }
                    }]
                });
            }
        },

        async saveContent() {
            if (!this.editor || !this.isReady || !this.currentNote) return;

            try {
                const data = await this.editor.save();
                this.currentNote.content = JSON.stringify(data);
                // Trigger save via the main app
                this.updateNote();
            } catch (error) {
                console.error('Error saving editor content:', error);
            }
        },

        showFallback() {
            document.getElementById('notebook-editor-fallback').style.display = 'block';
            document.getElementById('notebook-editor').style.display = 'none';
        }
    };
}