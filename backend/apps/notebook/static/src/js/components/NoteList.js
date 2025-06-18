/**
 * Composant pour afficher la liste des notes
 */

import { Component } from "@openlinguify/owl";

export class NoteList extends Component {
    static template = "notebook.NoteList";
    static props = {
        notes: Array,
        selectedNoteId: { type: [Number, String, null] },
        onSelectNote: Function,
    };

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
                month: 'short',
                year: 'numeric'
            });
        }
    }
}