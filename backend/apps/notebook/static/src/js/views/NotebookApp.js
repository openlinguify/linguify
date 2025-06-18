/**
 * Vue principale de l'application Notebook
 */

import { Component, useState, onWillStart } from "@openlinguify/owl";
import { NoteList } from "../components/NoteList";
import { NoteEditor } from "../components/NoteEditor";
import { NotebookSidebar } from "../components/NotebookSidebar";

export class NotebookApp extends Component {
    static template = "notebook.NotebookApp";
    static components = { NoteList, NoteEditor, NotebookSidebar };

    setup() {
        this.state = useState({
            selectedNoteId: null,
            notes: [],
            loading: true,
            searchQuery: "",
            selectedTags: [],
        });

        this.notebookService = this.env.services.notebook;
        
        onWillStart(async () => {
            await this.loadNotes();
        });
    }

    async loadNotes() {
        try {
            this.state.loading = true;
            const notes = await this.notebookService.getNotes();
            this.state.notes = notes;
        } catch (error) {
            this.env.services.notification.add("Erreur lors du chargement des notes", { 
                type: "danger" 
            });
        } finally {
            this.state.loading = false;
        }
    }

    async selectNote(noteId) {
        this.state.selectedNoteId = noteId;
    }

    async createNote() {
        try {
            const newNote = await this.notebookService.createNote({
                title: "Nouvelle note",
                content: "",
                tags: []
            });
            this.state.notes.push(newNote);
            this.state.selectedNoteId = newNote.id;
        } catch (error) {
            this.env.services.notification.add("Erreur lors de la création de la note", { 
                type: "danger" 
            });
        }
    }

    async deleteNote(noteId) {
        try {
            await this.notebookService.deleteNote(noteId);
            this.state.notes = this.state.notes.filter(note => note.id !== noteId);
            if (this.state.selectedNoteId === noteId) {
                this.state.selectedNoteId = null;
            }
        } catch (error) {
            this.env.services.notification.add("Erreur lors de la suppression", { 
                type: "danger" 
            });
        }
    }

    async saveNote(noteData) {
        try {
            const updatedNote = await this.notebookService.updateNote(
                this.state.selectedNoteId, 
                noteData
            );
            const index = this.state.notes.findIndex(
                note => note.id === this.state.selectedNoteId
            );
            if (index !== -1) {
                this.state.notes[index] = updatedNote;
            }
            this.env.services.notification.add("Note sauvegardée", { 
                type: "success" 
            });
        } catch (error) {
            this.env.services.notification.add("Erreur lors de la sauvegarde", { 
                type: "danger" 
            });
        }
    }

    get filteredNotes() {
        let notes = [...this.state.notes];
        
        // Filtrer par recherche
        if (this.state.searchQuery) {
            const query = this.state.searchQuery.toLowerCase();
            notes = notes.filter(note => 
                note.title.toLowerCase().includes(query) ||
                note.content.toLowerCase().includes(query)
            );
        }
        
        // Filtrer par tags
        if (this.state.selectedTags.length > 0) {
            notes = notes.filter(note =>
                this.state.selectedTags.some(tag => 
                    note.tags.includes(tag)
                )
            );
        }
        
        return notes;
    }

    get selectedNote() {
        return this.state.notes.find(
            note => note.id === this.state.selectedNoteId
        );
    }
}