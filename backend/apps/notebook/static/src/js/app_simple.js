/**
 * Version simplifiée pour tester l'intégration OWL
 */

// Application simple sans imports externes
class SimpleNotebookApp extends owl.Component {
    static template = owl.xml`
        <div class="notebook-app d-flex h-100">
            <!-- Sidebar -->
            <div class="notebook-sidebar">
                <div class="p-3 border-bottom">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0">Mes Notes</h5>
                        <button class="btn btn-sm btn-primary" t-on-click="createNote">
                            <i class="bi bi-plus"></i>
                        </button>
                    </div>
                    
                    <div class="input-group">
                        <span class="input-group-text">
                            <i class="bi bi-search"></i>
                        </span>
                        <input 
                            type="text" 
                            class="form-control" 
                            placeholder="Rechercher..."
                            t-model="state.searchQuery"
                        />
                    </div>
                </div>
                
                <div class="p-0">
                    <t t-if="filteredNotes.length === 0">
                        <div class="text-center text-muted p-4">
                            <i class="bi bi-inbox display-4"></i>
                            <p class="mt-2">Aucune note</p>
                        </div>
                    </t>
                    
                    <t t-foreach="filteredNotes" t-as="note" t-key="note.id">
                        <div 
                            class="note-item p-3 border-bottom cursor-pointer"
                            t-att-class="{ 'active': note.id === state.selectedNoteId }"
                            t-on-click="() => this.selectNote(note.id)"
                        >
                            <h6 class="mb-1 text-truncate">
                                <t t-esc="note.title || 'Sans titre'"/>
                            </h6>
                            <p class="mb-1 small text-muted text-truncate">
                                <t t-esc="note.content || 'Aucun contenu'"/>
                            </p>
                            <small class="text-muted">
                                <t t-esc="formatDate(note.updated_at)"/>
                            </small>
                        </div>
                    </t>
                </div>
            </div>
            
            <!-- Zone principale -->
            <div class="notebook-main flex-grow-1">
                <t t-if="state.loading">
                    <div class="d-flex justify-content-center align-items-center h-100">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Chargement...</span>
                        </div>
                    </div>
                </t>
                
                <t t-elif="selectedNote">
                    <div class="h-100 d-flex flex-column">
                        <!-- Barre d'outils -->
                        <div class="border-bottom p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <input 
                                    type="text" 
                                    class="form-control form-control-lg border-0 flex-grow-1"
                                    placeholder="Titre de la note"
                                    t-model="selectedNote.title"
                                    t-on-blur="saveNote"
                                />
                                
                                <button 
                                    class="btn btn-sm btn-outline-danger ms-2"
                                    t-on-click="() => this.deleteNote(selectedNote.id)"
                                >
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                        
                        <!-- Zone d'édition -->
                        <div class="flex-grow-1 p-4">
                            <textarea 
                                class="form-control h-100 border-0"
                                placeholder="Commencez à écrire..."
                                t-model="selectedNote.content"
                                t-on-blur="saveNote"
                            ></textarea>
                        </div>
                        
                        <!-- Barre de statut -->
                        <div class="border-top px-3 py-2 bg-light">
                            <small class="text-muted">
                                Dernière modification: <t t-esc="formatDate(selectedNote.updated_at)"/>
                            </small>
                        </div>
                    </div>
                </t>
                
                <t t-else="">
                    <div class="empty-state text-center p-5">
                        <i class="bi bi-journal-text display-1 text-muted mb-3"></i>
                        <h3 class="text-muted">Aucune note sélectionnée</h3>
                        <p class="text-muted">
                            Sélectionnez une note dans la liste ou créez-en une nouvelle
                        </p>
                        <button class="btn btn-primary" t-on-click="createNote">
                            <i class="bi bi-plus-circle me-2"></i>
                            Nouvelle note
                        </button>
                    </div>
                </t>
            </div>
        </div>
    `;

    setup() {
        this.state = owl.useState({
            selectedNoteId: null,
            notes: [
                {
                    id: 1,
                    title: "Note d'exemple",
                    content: "Ceci est une note d'exemple pour tester l'interface OWL.",
                    updated_at: new Date().toISOString(),
                    tags: ['exemple', 'test']
                },
                {
                    id: 2,
                    title: "Deuxième note",
                    content: "Une autre note pour voir comment l'interface gère plusieurs notes.",
                    updated_at: new Date(Date.now() - 86400000).toISOString(), // Hier
                    tags: ['demo']
                }
            ],
            loading: false,
            searchQuery: "",
        });

        // Sélectionner la première note par défaut
        if (this.state.notes.length > 0) {
            this.state.selectedNoteId = this.state.notes[0].id;
        }
    }

    get filteredNotes() {
        let notes = [...this.state.notes];
        
        if (this.state.searchQuery) {
            const query = this.state.searchQuery.toLowerCase();
            notes = notes.filter(note => 
                note.title.toLowerCase().includes(query) ||
                note.content.toLowerCase().includes(query)
            );
        }
        
        return notes;
    }

    get selectedNote() {
        return this.state.notes.find(
            note => note.id === this.state.selectedNoteId
        );
    }

    selectNote(noteId) {
        this.state.selectedNoteId = noteId;
    }

    createNote() {
        const newNote = {
            id: Date.now(),
            title: "Nouvelle note",
            content: "",
            updated_at: new Date().toISOString(),
            tags: []
        };
        
        this.state.notes.unshift(newNote);
        this.state.selectedNoteId = newNote.id;
        
        console.log('Note créée:', newNote);
    }

    saveNote() {
        if (this.selectedNote) {
            this.selectedNote.updated_at = new Date().toISOString();
            console.log('Note sauvegardée:', this.selectedNote);
            
            // Ici, on ferait un appel API
            // await this.notebookService.updateNote(this.selectedNote.id, this.selectedNote);
        }
    }

    deleteNote(noteId) {
        if (confirm('Êtes-vous sûr de vouloir supprimer cette note ?')) {
            this.state.notes = this.state.notes.filter(note => note.id !== noteId);
            if (this.state.selectedNoteId === noteId) {
                this.state.selectedNoteId = this.state.notes.length > 0 ? this.state.notes[0].id : null;
            }
            console.log('Note supprimée:', noteId);
        }
    }

    formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) {
            return "Aujourd'hui";
        } else if (diffDays === 1) {
            return "Hier";
        } else if (diffDays < 7) {
            return `Il y a ${diffDays} jours`;
        } else {
            return date.toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'short'
            });
        }
    }
}

// Démarrer l'application quand la page est chargée
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const { mount } = owl;
        const app = new SimpleNotebookApp();
        
        // Monter l'application sur l'élément #notebook-app
        await mount(app, document.getElementById('notebook-app'));
        
        console.log('✅ Application Notebook OWL démarrée avec succès !');
    } catch (error) {
        console.error('❌ Erreur lors du démarrage de l\'application:', error);
        
        // Afficher l'erreur dans l'interface
        const appElement = document.getElementById('notebook-app');
        if (appElement) {
            appElement.innerHTML = `
                <div class="d-flex justify-content-center align-items-center h-100">
                    <div class="text-center">
                        <i class="bi bi-exclamation-triangle display-1 text-danger mb-3"></i>
                        <h3 class="text-danger">Erreur de chargement</h3>
                        <p class="text-muted">Impossible de charger l'application Notebook.</p>
                        <p class="small text-muted">Vérifiez la console pour plus de détails.</p>
                    </div>
                </div>
            `;
        }
    }
});