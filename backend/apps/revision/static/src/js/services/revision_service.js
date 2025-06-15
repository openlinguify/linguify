// apps/revision/static/src/js/services/revision_service.js

/**
 * Service pour gérer les flashcards et decks - App Revision
 * Migré depuis frontend/src/addons/flashcard/api/revisionAPI.ts
 */
export class RevisionService {
    constructor() {
        this.API_BASE = '/api/v1/revision';
        this.cache = new Map();
        this.pendingRequests = new Map();
        this.CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
    }

    /**
     * Helper pour les requêtes avec cache et déduplication
     */
    async getOrFetch(key, fetcher) {
        // Vérifier le cache
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
            return cached.data;
        }

        // Vérifier si la requête est déjà en cours
        const pending = this.pendingRequests.get(key);
        if (pending) {
            return pending;
        }

        // Créer une nouvelle requête
        const request = fetcher().then(result => {
            this.cache.set(key, { data: result, timestamp: Date.now() });
            this.pendingRequests.delete(key);
            return result;
        }).catch(error => {
            this.pendingRequests.delete(key);
            throw error;
        });

        this.pendingRequests.set(key, request);
        return request;
    }

    /**
     * Helper pour les requêtes HTTP avec gestion CSRF
     */
    async makeRequest(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.API_BASE}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Ajouter le token CSRF pour Django
        const csrfToken = this.getCSRFToken();
        if (csrfToken && (options.method === 'POST' || options.method === 'PUT' || options.method === 'PATCH' || options.method === 'DELETE')) {
            config.headers['X-CSRFToken'] = csrfToken;
        }

        // Ajouter le token d'authentification si disponible
        const token = this.getAuthToken();
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, config);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        }
        
        return response.text();
    }

    /**
     * Récupère le token CSRF Django
     */
    getCSRFToken() {
        // Méthode 1: depuis un cookie
        const csrfCookie = this.getCookie('csrftoken');
        if (csrfCookie) return csrfCookie;

        // Méthode 2: depuis un meta tag
        const csrfMeta = document.querySelector('meta[name=csrf-token]');
        if (csrfMeta) return csrfMeta.getAttribute('content');

        // Méthode 3: depuis un input hidden
        const csrfInput = document.querySelector('input[name=csrfmiddlewaretoken]');
        if (csrfInput) return csrfInput.value;

        return null;
    }

    /**
     * Récupère le token d'authentification
     */
    getAuthToken() {
        // Priorité au token de session
        if (window.userService && window.userService.getAuthToken) {
            return window.userService.getAuthToken();
        }
        
        // Fallback vers le localStorage
        return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    }

    /**
     * Helper pour lire les cookies
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // === API DECKS ===

    /**
     * Récupère tous les decks
     */
    async getAllDecks(params = {}) {
        const key = `decks_all_${JSON.stringify(params)}`;
        return this.getOrFetch(key, async () => {
            const queryString = new URLSearchParams(params).toString();
            const endpoint = `/decks/${queryString ? '?' + queryString : ''}`;
            return this.makeRequest(endpoint);
        });
    }

    /**
     * Récupère un deck par son ID
     */
    async getDeckById(id) {
        const key = `deck_${id}`;
        return this.getOrFetch(key, async () => {
            return this.makeRequest(`/decks/${id}/`);
        });
    }

    /**
     * Crée un nouveau deck
     */
    async createDeck(data) {
        const payload = {
            ...data,
            description: data.description?.trim() || `Deck created on ${new Date().toLocaleDateString()}`,
            is_active: true
        };

        const result = await this.makeRequest('/decks/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        // Invalider le cache des decks
        this.invalidateCache('decks_all');
        return result;
    }

    /**
     * Met à jour un deck
     */
    async updateDeck(id, data) {
        const result = await this.makeRequest(`/decks/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });

        // Invalider le cache
        this.invalidateCache(`deck_${id}`);
        this.invalidateCache('decks_all');
        return result;
    }

    /**
     * Supprime un deck
     */
    async deleteDeck(id) {
        const result = await this.makeRequest(`/decks/${id}/`, {
            method: 'DELETE'
        });

        // Invalider le cache
        this.invalidateCache(`deck_${id}`);
        this.invalidateCache('decks_all');
        this.invalidateCache(`cards_${id}`);
        return result;
    }

    /**
     * Bascule la visibilité publique d'un deck
     */
    async toggleDeckPublic(id, makePublic) {
        const data = makePublic !== undefined ? { make_public: makePublic } : {};
        const result = await this.makeRequest(`/decks/${id}/toggle_public/`, {
            method: 'POST',
            body: JSON.stringify(data)
        });

        // Invalider le cache
        this.invalidateCache(`deck_${id}`);
        this.invalidateCache('decks_all');
        return result;
    }

    /**
     * Clone un deck
     */
    async cloneDeck(id, options = {}) {
        try {
            // Essayer l'endpoint public d'abord
            const result = await this.makeRequest(`/public/${id}/clone/`, {
                method: 'POST',
                body: JSON.stringify(options)
            });

            // Invalider le cache des decks
            this.invalidateCache('decks_all');
            return result;
        } catch (error) {
            if (error.message.includes('404')) {
                // Fallback vers l'endpoint normal
                const result = await this.makeRequest(`/decks/${id}/clone/`, {
                    method: 'POST',
                    body: JSON.stringify(options)
                });

                this.invalidateCache('decks_all');
                return result;
            }
            throw error;
        }
    }

    /**
     * Récupère les decks publics
     */
    async getPublicDecks(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/public/${queryString ? '?' + queryString : ''}`;
        return this.makeRequest(endpoint);
    }

    /**
     * Récupère les decks populaires
     */
    async getPopularDecks(limit = 10) {
        return this.makeRequest(`/public/popular/?limit=${limit}`);
    }

    /**
     * Récupère les decks récents
     */
    async getRecentDecks(limit = 10) {
        return this.makeRequest(`/public/recent/?limit=${limit}`);
    }

    /**
     * Récupère un deck public par son ID
     */
    async getPublicDeckById(id) {
        return this.makeRequest(`/decks/${id}/`, {
            headers: {
                'X-Public-Access': 'true'
            }
        });
    }

    // === API FLASHCARDS ===

    /**
     * Récupère toutes les cartes d'un deck
     */
    async getDeckCards(deckId) {
        const key = `cards_${deckId}`;
        return this.getOrFetch(key, async () => {
            return this.makeRequest(`/decks/${deckId}/cards/`);
        });
    }

    /**
     * Récupère une carte par son ID
     */
    async getCardById(id) {
        return this.makeRequest(`/flashcards/${id}/`);
    }

    /**
     * Crée une nouvelle carte
     */
    async createCard(data) {
        const payload = {
            ...data,
            deck: data.deck_id || data.deck
        };
        
        const result = await this.makeRequest('/flashcards/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        // Invalider le cache
        this.invalidateCache(`cards_${payload.deck}`);
        this.invalidateCache(`deck_${payload.deck}`);
        return result;
    }

    /**
     * Met à jour une carte
     */
    async updateCard(id, data) {
        const result = await this.makeRequest(`/flashcards/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });

        // Invalider le cache des cartes
        if (result.deck) {
            this.invalidateCache(`cards_${result.deck}`);
            this.invalidateCache(`deck_${result.deck}`);
        }
        
        return result;
    }

    /**
     * Supprime une carte
     */
    async deleteCard(id) {
        // Récupérer les infos de la carte avant suppression pour invalider le cache
        const card = await this.getCardById(id);
        
        const result = await this.makeRequest(`/flashcards/${id}/`, {
            method: 'DELETE'
        });

        // Invalider le cache
        if (card.deck) {
            this.invalidateCache(`cards_${card.deck}`);
            this.invalidateCache(`deck_${card.deck}`);
        }

        return result;
    }

    /**
     * Bascule l'état d'apprentissage d'une carte
     */
    async toggleCardLearned(id, success = true) {
        const result = await this.makeRequest(`/flashcards/${id}/toggle_learned/`, {
            method: 'PATCH',
            body: JSON.stringify({ success })
        });

        // Invalider le cache
        if (result.deck) {
            this.invalidateCache(`cards_${result.deck}`);
            this.invalidateCache(`deck_${result.deck}`);
        }

        return result;
    }

    /**
     * Récupère les cartes à réviser
     */
    async getDueForReviewCards(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/flashcards/due_for_review/${queryString ? '?' + queryString : ''}`;
        return this.makeRequest(endpoint);
    }

    /**
     * Importe des cartes depuis un fichier Excel
     */
    async importFromExcel(deckId, file, options = {}) {
        // Vérifier le format du fichier
        if (!file.name.match(/\.(xlsx|xls|csv)$/i)) {
            throw new Error('Format de fichier non supporté. Utilisez .xlsx, .xls ou .csv');
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('has_header', String(options.hasHeader ?? true));

        if (options.previewOnly) {
            formData.append('preview_only', 'true');
        }

        const headers = {};
        
        // Ajouter le token CSRF
        const csrfToken = this.getCSRFToken();
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }

        // Ajouter le token d'auth
        const token = this.getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const result = await this.makeRequest(`/decks/${deckId}/import/`, {
            method: 'POST',
            headers,
            body: formData
        });

        // Invalider le cache
        this.invalidateCache(`cards_${deckId}`);
        this.invalidateCache(`deck_${deckId}`);
        
        return result;
    }

    // === MÉTHODES UTILITAIRES ===

    /**
     * Invalide le cache pour un type de données
     */
    invalidateCache(pattern = '') {
        if (!pattern) {
            this.cache.clear();
            this.pendingRequests.clear();
            return;
        }

        for (const key of this.cache.keys()) {
            if (key.includes(pattern)) {
                this.cache.delete(key);
            }
        }

        for (const key of this.pendingRequests.keys()) {
            if (key.includes(pattern)) {
                this.pendingRequests.delete(key);
            }
        }
    }

    /**
     * Retourne les statistiques du cache
     */
    getCacheStats() {
        return {
            cacheSize: this.cache.size,
            pendingRequests: this.pendingRequests.size,
            cachedKeys: Array.from(this.cache.keys())
        };
    }

    /**
     * Debug: log des requêtes
     */
    logDebug(message, data) {
        if (window.DEBUG) {
            console.log(`🔄 REVISION: ${message}`, data || '');
        }
    }

    logError(message, error) {
        console.error(`❌ REVISION ERROR: ${message}`, error);
    }
}

export default RevisionService;