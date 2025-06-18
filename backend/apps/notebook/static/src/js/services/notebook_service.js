/**
 * Service pour gérer les interactions avec l'API Notebook
 */

export class NotebookService {
    constructor() {
        this.baseUrl = '/api/v1/notebook';
        this.csrfToken = this.getCsrfToken();
    }

    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken,
            },
            credentials: 'same-origin',
        };

        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Une erreur est survenue');
        }

        return response.json();
    }

    async getNotes() {
        return this.request(`${this.baseUrl}/notes/`);
    }

    async getNote(noteId) {
        return this.request(`${this.baseUrl}/notes/${noteId}/`);
    }

    async createNote(noteData) {
        return this.request(`${this.baseUrl}/notes/`, {
            method: 'POST',
            body: JSON.stringify(noteData),
        });
    }

    async updateNote(noteId, noteData) {
        return this.request(`${this.baseUrl}/notes/${noteId}/`, {
            method: 'PUT',
            body: JSON.stringify(noteData),
        });
    }

    async deleteNote(noteId) {
        return this.request(`${this.baseUrl}/notes/${noteId}/`, {
            method: 'DELETE',
        });
    }

    async searchNotes(query) {
        const params = new URLSearchParams({ q: query });
        return this.request(`${this.baseUrl}/notes/search/?${params}`);
    }

    async getTags() {
        return this.request(`${this.baseUrl}/tags/`);
    }

    async shareNote(noteId, shareData) {
        return this.request(`${this.baseUrl}/notes/${noteId}/share/`, {
            method: 'POST',
            body: JSON.stringify(shareData),
        });
    }
}