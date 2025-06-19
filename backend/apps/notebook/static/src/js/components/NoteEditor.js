/**
 * Composant pour l'édition d'une note
 */

import { Component, useState, useRef, onMounted } from "@openlinguify/owl";

export class NoteEditor extends Component {
    static template = "notebook.NoteEditor";
    static props = {
        note: Object,
        onSave: Function,
        onDelete: Function,
    };

    setup() {
        this.state = useState({
            localNote: { ...this.props.note },
            isSaving: false,
            showTagInput: false,
            newTag: "",
        });

        this.saveTimeout = null;
        this.tagInputRef = useRef("tagInput");

        onMounted(() => {
            // Mettre à jour la note locale quand la prop change
            this.updateLocalNote();
        });
    }

    updateLocalNote() {
        this.state.localNote = { ...this.props.note };
    }

    onTitleChange(ev) {
        this.state.localNote.title = ev.target.value;
        this.debouncedSave();
    }

    onContentChange(ev) {
        this.state.localNote.content = ev.target.value;
        this.debouncedSave();
    }

    debouncedSave() {
        // Annuler le timeout précédent
        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
        }

        // Créer un nouveau timeout
        this.saveTimeout = setTimeout(() => {
            this.save();
        }, 1000); // Sauvegarder après 1 seconde d'inactivité
    }

    async save() {
        if (this.state.isSaving) return;
        
        this.state.isSaving = true;
        try {
            await this.props.onSave(this.state.localNote);
        } finally {
            this.state.isSaving = false;
        }
    }

    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleString('fr-FR', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    async shareNote() {
        // Implémenter la logique de partage
        console.log('Partager la note:', this.state.localNote.id);
        // TODO: Ouvrir un modal de partage
    }

    async deleteNote() {
        if (confirm('Êtes-vous sûr de vouloir supprimer cette note ?')) {
            await this.props.onDelete(this.state.localNote.id);
        }
    }

    showTagInput() {
        this.state.showTagInput = true;
        // Focus sur l'input après le rendu
        setTimeout(() => {
            this.tagInputRef.el?.focus();
        }, 0);
    }

    async addTag() {
        const tag = this.state.newTag.trim();
        if (tag && !this.state.localNote.tags.includes(tag)) {
            this.state.localNote.tags.push(tag);
            this.state.newTag = "";
            this.state.showTagInput = false;
            await this.save();
        }
    }

    async removeTag(tag) {
        const index = this.state.localNote.tags.indexOf(tag);
        if (index > -1) {
            this.state.localNote.tags.splice(index, 1);
            await this.save();
        }
    }

    onTagInputKeydown(ev) {
        if (ev.key === 'Enter') {
            ev.preventDefault();
            this.addTag();
        } else if (ev.key === 'Escape') {
            this.state.showTagInput = false;
            this.state.newTag = "";
        }
    }
}