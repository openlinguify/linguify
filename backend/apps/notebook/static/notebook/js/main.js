// Simple Owl import sans Odoo module
const { mount, Component, xml, useState } = owl;

// Définir directement les composants ici
class Navbar extends Component {
  static template = xml`
    <div class="navbar-linguify">
      <!-- Gauche: Navigation + Actions principales -->
      <div class="navbar-section">
        <!-- Bouton toggle sidebar -->
        <button class="btn-navbar-outline" title="Masquer/Afficher la barre latérale" t-on-click="toggleSidebar">
          <i class="bi bi-layout-sidebar-inset"></i>
        </button>

        <!-- Navigation tabs -->
        <div class="nav-tabs-group">
          <a href="#" class="nav-tab" t-att-class="{ active: state.currentView === 'notes' }" t-on-click="() => this.switchView('notes')">
            <i class="bi bi-journal-text"></i>
            Mes notes
          </a>
          <a href="#" class="nav-tab" t-att-class="{ active: state.currentView === 'archives' }" t-on-click="() => this.switchView('archives')">
            <i class="bi bi-archive"></i>
            Archives
          </a>
          <div class="container-extra">
            <button class="btn-sb" title="Sauvegarder la note" t-on-click="saveCurrentNote">
              <i class="bi bi-cloud-check"></i>
            </button>
            <button class="btn-sb" title="Actualiser les notes" t-on-click="refreshNotes">
              <i class="bi bi-arrow-clockwise"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Droite: Actions et filtres -->
      <div class="navbar-section-right" style="display: flex; align-items: center; gap: 10px; margin-left: auto;">
        <input type="text" class="form-control-linguify" placeholder="Rechercher..." style="width: 140px;"
               t-model="state.searchQuery" t-on-input="onSearchInput" />

        <!-- Bouton nouvelle note -->
        <button class="btn-navbar btn-navbar-primary" t-on-click="createNewNote">
          <i class="bi bi-plus-lg"></i>
          <span class="d-none d-xxl-inline">Nouvelle</span>
        </button>
      </div>
    </div>
  `;

  setup() {
    // Utiliser le store passé en props
    this.store = this.props.store;
    this.state = this.store.state;
  }

  toggleSidebar() {
    this.store.toggleSidebar();
    console.log('Toggle sidebar:', this.state.sidebarVisible);
    // Appeler la fonction existante si elle existe
    if (typeof window.toggleSidebar === 'function') {
      window.toggleSidebar();
    }
  }

  switchView(view) {
    this.store.switchView(view);
    console.log('Switched to view:', view);

    // Appeler les fonctions existantes
    if (view === 'notes' && typeof window.showNotesView === 'function') {
      window.showNotesView();
    } else if (view === 'archives' && typeof window.showArchivedView === 'function') {
      window.showArchivedView();
    }
  }

  saveCurrentNote() {
    console.log('Saving current note...');
    if (typeof window.saveCurrentNote === 'function') {
      window.saveCurrentNote(true);
    }
  }

  refreshNotes() {
    console.log('Refreshing notes...');
    if (typeof window.refreshNotes === 'function') {
      window.refreshNotes();
    }
  }

  onSearchInput() {
    this.store.setSearchQuery(this.state.searchQuery);
    console.log('Search query:', this.state.searchQuery);
    // Implémenter la recherche avec debounce
    if (typeof window.debounceSearch === 'function') {
      window.debounceSearch();
    }
  }

  async createNewNote() {
    console.log('Navbar: Creating new note...');

    try {
      const noteData = {
        title: "Nouvelle note",
        content: "",
        language: "FR"
      };

      await this.store.createNote(noteData);
      console.log('Note créée avec succès via API');
    } catch (error) {
      console.error('Erreur lors de la création de la note:', error);
      // Fallback: créer en local seulement
      const newNote = {
        id: Date.now(),
        title: "Nouvelle note",
        content: "",
        language: "FR",
        updated_at: "À l'instant"
      };
      this.store.addNote(newNote);
      this.store.setCurrentNote(newNote);
    }
  }
}

// Composant Sidebar
class Sidebar extends Component {
  static template = xml`
    <div class="sidebar-linguify" t-att-class="{ show: store.state.sidebarVisible }">
      <div class="sidebar-content">
        <!-- Notes list -->
        <div style="padding: 10px; background: #fffacd; margin-bottom: 10px; font-size: 12px;">
          Debug: <t t-esc="props.notes.length"/> notes dans le store (maj: <t t-esc="props.lastUpdate"/>)
        </div>
        <ul class="note-list" style="list-style: none; padding: 0; margin: 0;">
          <li t-foreach="props.notes" t-as="note" t-key="note.id"
              class="note-item"
              t-att-class="{ 'selected': props.currentNote?.id === note.id }"
              t-on-click="() => this.selectNote(note)"
              style="padding: 12px 16px; margin: 4px 8px; border-radius: 8px; cursor: pointer; border: 1px solid transparent; transition: all 0.2s;">
            <div class="note-title" style="font-weight: 600; font-size: 14px; color: #333; margin-bottom: 4px;" t-esc="note.title || 'Sans titre'"></div>
            <div class="note-preview" style="font-size: 12px; color: #666; margin-bottom: 8px; line-height: 1.3;" t-esc="(note.content || '...').substring(0, 60) + (note.content?.length > 60 ? '...' : '')"></div>
            <div class="note-meta" style="display: flex; justify-content: space-between; align-items: center;">
              <span class="note-language" style="background: #e9ecef; padding: 2px 6px; border-radius: 12px; font-size: 10px; color: #495057;" t-esc="note.language"></span>
              <span class="note-date" style="font-size: 11px; color: #6c757d;" t-esc="note.updated_at"></span>
            </div>
          </li>
        </ul>

        <!-- Empty state -->
        <div class="empty-state" t-if="props.notes.length === 0">
          <i class="bi bi-journal-text empty-state-icon"></i>
          <div class="empty-state-title">Aucune note</div>
          <div class="empty-state-description">Créez votre première note pour commencer à organiser vos idées</div>
          <button class="btn-linguify create-note-btn" t-on-click="createNewNote">
            <i class="bi bi-plus-lg mr-2"></i>
            Créer une note
          </button>
        </div>

        <!-- Load more -->
        <div class="text-center load-more-container" t-if="props.notes.length > 0">
          <button class="btn-linguify-secondary" t-on-click="loadMore">
            <i class="bi bi-arrow-down-circle mr-2"></i>
            Charger plus
          </button>
        </div>
      </div>
    </div>
  `;

  setup() {
    this.store = this.props.store;
  }

  selectNote(note) {
    console.log('Sélection de la note:', note);
    this.store.setCurrentNote(note);
    console.log('Note actuelle dans le store:', this.store.state.currentNote);
  }

  createNewNote() {
    console.log('Créer nouvelle note depuis sidebar');
    if (typeof window.createNewNote === 'function') {
      window.createNewNote();
    }
  }

  loadMore() {
    console.log('Charger plus de notes');
    // Implémenter le chargement de plus de notes
  }
}

// Composant Editor
class NoteEditor extends Component {
  static template = xml`
    <div class="note-editor-panel h-100 d-flex flex-column" style="background: white; border-left: 1px solid #ddd;">
      <!-- État: Aucune note sélectionnée -->
      <div t-if="!props.currentNote" class="no-note-selected d-flex align-items-center justify-content-center h-100" style="background: #f8f9fa;">
        <div class="text-center text-muted p-4">
          <i class="bi bi-journal-text" style="font-size: 4rem; color: #6c757d; margin-bottom: 1rem;"></i>
          <h3 style="color: #495057; margin-bottom: 1rem;">Aucune note sélectionnée</h3>
          <p style="color: #6c757d; margin-bottom: 2rem;">Choisissez une note dans la sidebar ou créez-en une nouvelle</p>
          <button class="btn btn-primary btn-lg" t-on-click="createNewNote">
            <i class="bi bi-plus-lg me-2"></i>
            Créer une nouvelle note
          </button>
        </div>
      </div>

      <!-- État: Note sélectionnée -->
      <div t-if="props.currentNote" class="editor-container h-100 d-flex flex-column">
        <!-- En-tête de l'éditeur avec titre -->
        <div class="editor-header p-4 border-bottom" style="background: #fff; border-bottom: 2px solid #e9ecef;">
          <input type="text"
                 class="form-control form-control-lg border-0 fw-bold"
                 placeholder="Titre de la note..."
                 t-att-value="props.currentNote.title"
                 t-on-input="updateTitle"
                 t-on-blur="saveNote"
                 style="font-size: 1.5rem; background: transparent; outline: none; box-shadow: none;" />
        </div>

        <!-- Zone d'édition principale -->
        <div class="editor-content flex-grow-1 p-4">
          <textarea class="form-control h-100 border-0 resize-none"
                    placeholder="Écrivez votre note ici..."
                    t-att-value="props.currentNote.content"
                    t-on-input="updateContent"
                    t-on-blur="saveNote"
                    style="font-size: 1rem; line-height: 1.6; outline: none; box-shadow: none; background: transparent;"></textarea>
        </div>

        <!-- Barre d'état avec métadonnées -->
        <div class="editor-footer p-3 border-top" style="background: #f8f9fa; border-top: 1px solid #dee2e6;">
          <div class="row align-items-center">
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">Langue</label>
              <select class="form-select form-select-sm" t-att-value="props.currentNote.language" t-on-change="updateLanguage">
                <option value="FR">Français</option>
                <option value="EN">Anglais</option>
                <option value="ES">Espagnol</option>
                <option value="DE">Allemand</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label small text-muted mb-1">Dernière modification</label>
              <div class="small text-muted" t-esc="props.currentNote.updated_at"></div>
            </div>
            <div class="col-md-5 text-end">
              <button class="btn btn-sm btn-outline-primary me-2" t-on-click="saveNote">
                <i class="bi bi-save me-1"></i>
                Sauvegarder
              </button>
              <button class="btn btn-sm btn-outline-secondary" t-on-click="createNewNote">
                <i class="bi bi-plus me-1"></i>
                Nouvelle
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  setup() {
    this.store = this.props.store;

    // Debounce pour la sauvegarde automatique
    this.saveTimeout = null;
    this.debouncedSave = () => {
      if (this.saveTimeout) {
        clearTimeout(this.saveTimeout);
      }
      this.saveTimeout = setTimeout(() => {
        this.saveNote();
      }, 1000); // Sauvegarde 1 seconde après la dernière modification
    };
  }

  updateTitle(event) {
    if (this.store.state.currentNote) {
      this.store.state.currentNote.title = event.target.value;
      // Sauvegarde automatique avec debounce
      this.debouncedSave();
    }
  }

  updateContent(event) {
    if (this.store.state.currentNote) {
      this.store.state.currentNote.content = event.target.value;
      // Sauvegarde automatique avec debounce
      this.debouncedSave();
    }
  }

  updateLanguage(event) {
    if (this.store.state.currentNote) {
      this.store.state.currentNote.language = event.target.value;
      this.saveNote();
    }
  }

  async createNewNote() {
    console.log('Editor: Creating new note...');

    try {
      const noteData = {
        title: "Nouvelle note",
        content: "",
        language: "FR"
      };

      await this.store.createNote(noteData);
      console.log('Note créée avec succès via API');

      // Focus sur le titre après création
      setTimeout(() => {
        const titleInput = document.querySelector('input[placeholder="Titre de la note..."]');
        if (titleInput) {
          titleInput.focus();
          titleInput.select();
        }
      }, 100);
    } catch (error) {
      console.error('Erreur lors de la création de la note:', error);
    }
  }

  async saveNote() {
    if (this.store.state.currentNote && this.store.state.currentNote.id) {
      try {
        await this.store.updateNote(this.store.state.currentNote.id, {
          title: this.store.state.currentNote.title,
          content: this.store.state.currentNote.content,
          language: this.store.state.currentNote.language
        });
        console.log('Note sauvegardée via API:', this.store.state.currentNote);
      } catch (error) {
        console.error('Erreur lors de la sauvegarde:', error);
      }
    }
  }
}

// Store global pour l'application
class NotebookStore {
  constructor() {
    this.state = useState({
      currentView: 'notes',
      notes: [],
      archivedNotes: [],
      currentNote: null,
      searchQuery: '',
      filters: {
        language: '',
        sort: 'updated_desc',
        tags: ''
      },
      loading: false,
      sidebarVisible: true,
      lastUpdate: Date.now()
    });
  }

  switchView(view) {
    this.state.currentView = view;
  }

  setSearchQuery(query) {
    this.state.searchQuery = query;
  }

  toggleSidebar() {
    this.state.sidebarVisible = !this.state.sidebarVisible;
  }

  setCurrentNote(note) {
    console.log('Store.setCurrentNote appelé avec:', note);
    this.state.currentNote = note;
    console.log('Nouvelle currentNote dans state:', this.state.currentNote);
  }

  addNote(note) {
    // Ajouter la nouvelle note en tête de liste
    this.state.notes = [note, ...this.state.notes];
    this.state.lastUpdate = Date.now();
    console.log('Note ajoutée à la liste locale:', note);
  }

  async loadNotes() {
    this.state.loading = true;
    try {
      const response = await window.apiService.request('/notebook/ajax/notes/?page=1');
      console.log('Notes chargées depuis l\'API:', response);

      if (response.results) {
        // Formater les dates pour l'affichage
        const formattedNotes = response.results.map(note => ({
          ...note,
          updated_at: this.formatDate(note.updated_at)
        }));

        // Forcer la réactivité en créant un nouveau tableau
        this.state.notes = [...formattedNotes];
        this.state.lastUpdate = Date.now();
        console.log('Notes ajoutées au state:', this.state.notes.length, 'notes');
      }
    } catch (error) {
      console.error('Erreur lors du chargement des notes:', error);
    } finally {
      this.state.loading = false;
    }
  }

  async createNote(noteData) {
    try {
      const response = await window.apiService.request('/notebook/ajax/notes/create/', {
        method: 'POST',
        body: JSON.stringify(noteData)
      });

      console.log('Note créée via API:', response);

      // Formater la date et ajouter à la liste
      const formattedNote = {
        ...response,
        updated_at: this.formatDate(response.updated_at)
      };

      this.addNote(formattedNote);
      this.setCurrentNote(formattedNote);

      return formattedNote;
    } catch (error) {
      console.error('Erreur lors de la création de la note:', error);
      throw error;
    }
  }

  async updateNote(noteId, noteData) {
    try {
      const response = await window.apiService.request(`/notebook/ajax/notes/${noteId}/update/`, {
        method: 'POST',
        body: JSON.stringify(noteData)
      });

      console.log('Note mise à jour via API:', response);

      // Mettre à jour dans la liste locale
      const formattedNote = {
        ...response,
        updated_at: this.formatDate(response.updated_at)
      };

      const index = this.state.notes.findIndex(n => n.id === noteId);
      if (index !== -1) {
        this.state.notes = [
          ...this.state.notes.slice(0, index),
          formattedNote,
          ...this.state.notes.slice(index + 1)
        ];
        this.state.lastUpdate = Date.now();
      }

      // Mettre à jour la note courante si c'est celle-ci
      if (this.state.currentNote?.id === noteId) {
        this.state.currentNote = formattedNote;
      }

      return formattedNote;
    } catch (error) {
      console.error('Erreur lors de la mise à jour de la note:', error);
      throw error;
    }
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Aujourd'hui";
    if (diffDays === 1) return "Hier";
    if (diffDays < 7) return `Il y a ${diffDays} jours`;

    return date.toLocaleDateString('fr-FR');
  }
}

class WebClient extends Component {
  static template = xml`
    <div class="o_webclient">
      <Navbar store="store" notes="state.notes" currentNote="state.currentNote" />
      <div class="notebook-workspace d-flex h-100">
        <Sidebar store="store" notes="state.notes" currentNote="state.currentNote" lastUpdate="state.lastUpdate" />

        <!-- Zone d'édition principale -->
        <div class="notebook-editor flex-grow-1">
          <NoteEditor store="store" currentNote="state.currentNote" />
        </div>
      </div>
    </div>
  `;
  static components = { Navbar, Sidebar, NoteEditor };

  setup() {
    this.store = new NotebookStore();
    // Exposer le state du store pour la réactivité
    this.state = this.store.state;

    // Charger les vraies notes depuis l'API
    this.store.loadNotes();
  }
}

// Mount when ready
document.addEventListener('DOMContentLoaded', () => {
  const mountPoint = document.getElementById('owl-navbar-mount');

  if (mountPoint) {
    console.log('Montage de WebClient...');
    mount(WebClient, mountPoint, { dev: true });
  } else {
    console.error('Point de montage #owl-navbar-mount non trouvé');
  }
});