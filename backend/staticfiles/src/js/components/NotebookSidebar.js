/**
 * Composant pour la sidebar de l'application Notebook
 */

import { Component } from "@odoo/owl";

export class NotebookSidebar extends Component {
    static template = "notebook.NotebookSidebar";
    static props = {
        notes: Array,
        selectedNoteId: { type: [Number, String, null] },
        searchQuery: String,
        selectedTags: Array,
        onSelectNote: Function,
        onCreateNote: Function,
        onSearchChange: Function,
        onTagsChange: Function,
    };
}