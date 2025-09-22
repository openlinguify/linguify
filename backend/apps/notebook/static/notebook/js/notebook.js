// Notebook Application JavaScript

function notebookApp() {
    return {
        // État général
        isLoading: false,
        isSaving: false,
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

        // Modals
        showCreateModal: false,
        showEditModal: false,

        // Note vide pour création
        emptyNote: {
            title: '',
            content: '',
            language: '',
            translation: '',
            pronunciation: '',
            difficulty: '',
            is_pinned: false,
            is_archived: false
        },

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
                this.totalPages = Math.ceil(data.count / 50);
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

        async saveNote() {
            this.isSaving = true;
            try {
                const url = this.currentNote.id
                    ? `/notebook/api/notes/${this.currentNote.id}/`
                    : `/notebook/api/notes/`;
                const method = this.currentNote.id ? 'PUT' : 'POST';

                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(this.currentNote)
                });

                if (response.ok) {
                    await this.loadNotes();
                    this.closeModals();
                    this.showAlert('Note saved successfully!', 'success');
                } else {
                    throw new Error('Failed to save note');
                }
            } catch (error) {
                console.error('Error saving note:', error);
                this.showAlert('Error saving note', 'error');
            } finally {
                this.isSaving = false;
            }
        },

        editNote(note) {
            this.currentNote = { ...note };
            this.showEditModal = true;
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
                this.showAlert('Notes archived successfully!', 'success');
            } catch (error) {
                console.error('Error archiving notes:', error);
                this.showAlert('Error archiving notes', 'error');
            }
        },

        async bulkDelete() {
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
                this.showAlert('Notes deleted successfully!', 'success');
            } catch (error) {
                console.error('Error deleting notes:', error);
                this.showAlert('Error deleting notes', 'error');
            }
        },

        closeModals() {
            this.showCreateModal = false;
            this.showEditModal = false;
            this.currentNote = { ...this.emptyNote };
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