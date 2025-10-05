/**
 * Keyboard Shortcuts Manager
 * Gère les raccourcis clavier pour les modes d'étude
 */

class KeyboardShortcutsManager {
    constructor() {
        this.enabled = true;
        this.shortcuts = {
            previous: 'ArrowLeft',
            next: 'ArrowRight',
            flip: 'Space',
            easy: '1',
            medium: '2',
            difficult: '3',
            audio: 'a',
            edit: 'e',
            shuffle: 'h',
            star: 's'
        };
        this.handlers = {};
        this.initialized = false;
    }

    /**
     * Charge les raccourcis depuis les paramètres utilisateur
     */
    async loadUserShortcuts() {
        try {
            const response = await fetch('/revision/api/settings/user/');
            if (response.ok) {
                const data = await response.json();

                if (data.keyboard_shortcuts_enabled !== undefined) {
                    this.enabled = data.keyboard_shortcuts_enabled;
                }

                // Charger les raccourcis personnalisés
                if (data.shortcut_previous) this.shortcuts.previous = data.shortcut_previous;
                if (data.shortcut_next) this.shortcuts.next = data.shortcut_next;
                if (data.shortcut_flip) this.shortcuts.flip = data.shortcut_flip;
                if (data.shortcut_easy) this.shortcuts.easy = data.shortcut_easy;
                if (data.shortcut_medium) this.shortcuts.medium = data.shortcut_medium;
                if (data.shortcut_difficult) this.shortcuts.difficult = data.shortcut_difficult;
                if (data.shortcut_audio) this.shortcuts.audio = data.shortcut_audio;
                if (data.shortcut_edit) this.shortcuts.edit = data.shortcut_edit;
                if (data.shortcut_shuffle) this.shortcuts.shuffle = data.shortcut_shuffle;
                if (data.shortcut_star) this.shortcuts.star = data.shortcut_star;

                console.log('[Keyboard] Raccourcis chargés:', this.shortcuts);
            }
        } catch (error) {
            console.error('[Keyboard] Erreur chargement raccourcis:', error);
        }
    }

    /**
     * Initialise les raccourcis clavier
     */
    async init() {
        if (this.initialized) return;

        await this.loadUserShortcuts();

        document.addEventListener('keydown', (e) => {
            if (!this.enabled) return;

            // Ignorer si on tape dans un input/textarea
            if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) {
                return;
            }

            // Ignorer si des modificateurs sont pressés (sauf Shift pour certaines touches)
            if (e.ctrlKey || e.metaKey || e.altKey) {
                return;
            }

            const key = e.key;
            const keyCode = e.code;

            // Normaliser la touche pour comparaison
            const normalizedKey = this.normalizeKey(key, keyCode);

            // Debug: log des touches pressées
            console.log(`[Keyboard] Key pressed: ${key}, Code: ${keyCode}, Normalized: ${normalizedKey}`);

            // Trouver l'action correspondante
            for (const [action, shortcut] of Object.entries(this.shortcuts)) {
                if (normalizedKey === shortcut.toLowerCase() || keyCode === shortcut) {
                    if (this.handlers[action]) {
                        e.preventDefault();
                        this.handlers[action](e);
                        console.log(`[Keyboard] Action executed: ${action} (${shortcut})`);
                    }
                    break;
                }
            }
        });

        this.initialized = true;
        console.log('[Keyboard] Gestionnaire de raccourcis initialisé');
    }

    /**
     * Normalise une touche pour comparaison
     */
    normalizeKey(key, code) {
        // Cas spéciaux
        if (code === 'Space') return 'space';
        if (code.startsWith('Arrow')) return code.toLowerCase();

        // Touches normales
        return key.toLowerCase();
    }

    /**
     * Enregistre un handler pour une action
     */
    on(action, handler) {
        this.handlers[action] = handler;
    }

    /**
     * Supprime un handler
     */
    off(action) {
        delete this.handlers[action];
    }

    /**
     * Active/désactive les raccourcis
     */
    setEnabled(enabled) {
        this.enabled = enabled;
        console.log(`[Keyboard] Raccourcis ${enabled ? 'activés' : 'désactivés'}`);
    }

    /**
     * Met à jour un raccourci
     */
    setShortcut(action, key) {
        if (this.shortcuts.hasOwnProperty(action)) {
            this.shortcuts[action] = key;
            console.log(`[Keyboard] Raccourci ${action} mis à jour: ${key}`);
        }
    }

    /**
     * Obtient la liste des raccourcis
     */
    getShortcuts() {
        return { ...this.shortcuts };
    }

    /**
     * Formate un raccourci pour affichage
     */
    formatShortcut(action) {
        const key = this.shortcuts[action];
        const mapping = {
            'ArrowLeft': '←',
            'ArrowRight': '→',
            'ArrowUp': '↑',
            'ArrowDown': '↓',
            'Space': 'Espace',
            'Enter': 'Entrée',
            'Escape': 'Échap'
        };
        return mapping[key] || key.toUpperCase();
    }
}

// Créer instance globale
window.keyboardShortcuts = new KeyboardShortcutsManager();
