/**
 * Linguify Command Palette
 * Notion-style slash command menu for rich text editing
 * 
 * Usage: new LinguifyCommandPalette(textareaElement)
 */
class LinguifyCommandPalette {
    constructor(textarea) {
        this.textarea = textarea;
        this.isVisible = false;
        this.currentIndex = 0;
        this.filteredCommands = [];
        this.palette = null;
        
        // Command definitions organized by categories
        this.commands = {
            'Structure': [
                { name: 'Séparateur', description: 'Insérer une ligne horizontale de séparation', icon: 'bi-dash', insert: '\n---\n' },
                { name: '2 colonnes', description: 'Convertir en 2 colonnes', icon: 'bi-columns', insert: '\n<div class="row"><div class="col-md-6">\n\n</div><div class="col-md-6">\n\n</div></div>\n' },
                { name: '3 colonnes', description: 'Convertir en 3 colonnes', icon: 'bi-columns', insert: '\n<div class="row"><div class="col-md-4">\n\n</div><div class="col-md-4">\n\n</div><div class="col-md-4">\n\n</div></div>\n' },
                { name: '4 colonnes', description: 'Convertir en 4 colonnes', icon: 'bi-columns', insert: '\n<div class="row"><div class="col-3">\n\n</div><div class="col-3">\n\n</div><div class="col-3">\n\n</div><div class="col-3">\n\n</div></div>\n' },
                { name: 'Tableau', description: 'Insérer un tableau', icon: 'bi-table', insert: '\n| Colonne 1 | Colonne 2 | Colonne 3 |\n|-----------|-----------|--------|\n|           |           |        |\n|           |           |        |\n' },
                { name: 'Liste à puces', description: 'Créer une simple liste à puces', icon: 'bi-list-ul', insert: '\n- Point 1\n- Point 2\n- Point 3\n' },
                { name: 'Liste numérotée', description: 'Créer une liste avec numérotation', icon: 'bi-list-ol', insert: '\n1. Premier point\n2. Deuxième point\n3. Troisième point\n' },
                { name: 'Check-list', description: 'Suivre les tâches grâce à une check-list', icon: 'bi-check-square', insert: '\n- [ ] Tâche à faire\n- [ ] Autre tâche\n- [x] Tâche terminée\n' },
                { name: 'Citation', description: 'Ajouter une section de citation', icon: 'bi-quote', insert: '\n> Ceci est une citation\n> Elle peut s\'étaler sur plusieurs lignes\n' },
                { name: 'Code', description: 'Ajouter une section de code', icon: 'bi-code-slash', insert: '\n```\nvotre code ici\n```\n' }
            ],
            'Bannière': [
                { name: 'Bannière Info', description: 'Insérer une bannière d\'info', icon: 'bi-info-circle', insert: '\n> **ℹ️ Information**\n> Votre message d\'information ici\n' },
                { name: 'Bannière Réussite', description: 'Insérer une bannière de réussite', icon: 'bi-check-circle', insert: '\n> **✅ Succès**\n> Votre message de réussite ici\n' },
                { name: 'Bannière Avertissement', description: 'Insérer une bannière d\'avertissement', icon: 'bi-exclamation-triangle', insert: '\n> **⚠️ Attention**\n> Votre message d\'avertissement ici\n' },
                { name: 'Bannière Danger', description: 'Insérer une bannière de danger', icon: 'bi-exclamation-circle', insert: '\n> **🚨 Danger**\n> Votre message d\'erreur ici\n' }
            ],
            'Format': [
                { name: 'Titre 1', description: 'Grand titre de section', icon: 'bi-type-h1', insert: '\n# Votre titre ici\n' },
                { name: 'Titre 2', description: 'Moyen titre de section', icon: 'bi-type-h2', insert: '\n## Votre titre ici\n' },
                { name: 'Titre 3', description: 'Petit titre de section', icon: 'bi-type-h3', insert: '\n### Votre titre ici\n' },
                { name: 'Texte', description: 'Bloc de paragraphe', icon: 'bi-paragraph', insert: '\n\nVotre texte ici\n\n' }
            ],
            'Média': [
                { name: 'Image', description: 'Insérer une image', icon: 'bi-image', insert: '\n![Description de l\'image](url-de-votre-image)\n' },
                { name: 'Vidéo', description: 'Insérer une vidéo', icon: 'bi-play-circle', insert: '\n[Vidéo: Titre de votre vidéo](url-de-votre-video)\n' }
            ],
            'Navigation': [
                { name: 'Lien', description: 'Ajouter un lien', icon: 'bi-link-45deg', insert: '[Texte du lien](https://example.com)' },
                { name: 'Bouton', description: 'Ajouter un bouton', icon: 'bi-square', insert: '\n<button class="btn-linguify">Texte du bouton</button>\n' }
            ],
            'Widget': [
                { name: 'Émoji', description: 'Ajouter un émoji', icon: 'bi-emoji-smile', insert: '😊' },
                { name: '3 étoiles', description: 'Insérer une note sur 3 étoiles', icon: 'bi-star', insert: '⭐⭐⭐' },
                { name: '5 étoiles', description: 'Insérer une note sur 5 étoiles', icon: 'bi-star-fill', insert: '⭐⭐⭐⭐⭐' }
            ],
            'Outils IA': [
                { name: 'ChatGPT', description: 'Générer ou transformer du contenu grâce à l\'IA', icon: 'bi-magic', insert: '\n<!-- Contenu généré par IA -->\n' }
            ]
        };
        
        this.init();
    }
    
    init() {
        this.createPalette();
        this.attachEventListeners();
    }
    
    createPalette() {
        this.palette = document.createElement('div');
        this.palette.className = 'linguify-command-palette';
        this.palette.style.display = 'none';
        document.body.appendChild(this.palette);
    }
    
    attachEventListeners() {
        this.textarea.addEventListener('input', (e) => this.handleInput(e));
        this.textarea.addEventListener('keydown', (e) => this.handleKeydown(e));
        document.addEventListener('click', (e) => this.handleOutsideClick(e));
    }
    
    handleInput(e) {
        const value = this.textarea.value;
        const cursorPos = this.textarea.selectionStart;
        
        // Check if user typed "/" and it's at start of line or after whitespace
        const beforeCursor = value.substring(0, cursorPos);
        const slashIndex = beforeCursor.lastIndexOf('/');
        
        if (slashIndex !== -1) {
            const lineStart = beforeCursor.lastIndexOf('\n', slashIndex - 1) + 1;
            const beforeSlash = beforeCursor.substring(lineStart, slashIndex);
            
            // Only show if "/" is at start of line or after whitespace
            if (beforeSlash.trim() === '') {
                const query = beforeCursor.substring(slashIndex + 1);
                this.showPalette(query, slashIndex, cursorPos);
                return;
            }
        }
        
        this.hidePalette();
    }
    
    handleKeydown(e) {
        if (!this.isVisible) return;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.currentIndex = Math.min(this.currentIndex + 1, this.filteredCommands.length - 1);
                this.updateSelection();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.currentIndex = Math.max(this.currentIndex - 1, 0);
                this.updateSelection();
                break;
            case 'Enter':
            case 'Tab':
                e.preventDefault();
                this.executeCommand(this.filteredCommands[this.currentIndex]);
                break;
            case 'Escape':
                e.preventDefault();
                this.hidePalette();
                break;
        }
    }
    
    handleOutsideClick(e) {
        if (this.isVisible && !this.palette.contains(e.target) && e.target !== this.textarea) {
            this.hidePalette();
        }
    }
    
    showPalette(query, slashIndex, cursorPos) {
        this.slashIndex = slashIndex;
        this.cursorPos = cursorPos;
        this.filterCommands(query);
        
        if (this.filteredCommands.length === 0) {
            this.hidePalette();
            return;
        }
        
        this.renderPalette();
        this.positionPalette();
        this.isVisible = true;
        this.currentIndex = 0;
        this.updateSelection();
    }
    
    hidePalette() {
        this.palette.style.display = 'none';
        this.isVisible = false;
        this.currentIndex = 0;
    }
    
    filterCommands(query) {
        this.filteredCommands = [];
        const lowerQuery = query.toLowerCase();
        
        Object.entries(this.commands).forEach(([category, commands]) => {
            commands.forEach(command => {
                if (command.name.toLowerCase().includes(lowerQuery) || 
                    command.description.toLowerCase().includes(lowerQuery)) {
                    this.filteredCommands.push({ ...command, category });
                }
            });
        });
    }
    
    renderPalette() {
        let html = '<div class="command-palette-content">';
        
        // Group by category
        const groupedCommands = {};
        this.filteredCommands.forEach(command => {
            if (!groupedCommands[command.category]) {
                groupedCommands[command.category] = [];
            }
            groupedCommands[command.category].push(command);
        });
        
        Object.entries(groupedCommands).forEach(([category, commands]) => {
            html += `<div class="command-category">${category}</div>`;
            commands.forEach((command, index) => {
                const globalIndex = this.filteredCommands.indexOf(command);
                html += `
                    <div class="command-item" data-index="${globalIndex}" data-category="${command.category}">
                        <div class="command-icon">
                            <i class="bi ${command.icon}"></i>
                        </div>
                        <div class="command-content">
                            <div class="command-name">${command.name}</div>
                            <div class="command-description">${command.description}</div>
                        </div>
                    </div>
                `;
            });
        });
        
        html += '</div>';
        this.palette.innerHTML = html;
        this.palette.style.display = 'block';
        
        // Add click listeners
        this.palette.querySelectorAll('.command-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.executeCommand(this.filteredCommands[index]);
            });
        });
    }
    
    updateSelection() {
        this.palette.querySelectorAll('.command-item').forEach((item, index) => {
            if (parseInt(item.dataset.index) === this.currentIndex) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
    
    positionPalette() {
        // Get textarea position and cursor position
        const textareaRect = this.textarea.getBoundingClientRect();
        const lineHeight = parseInt(getComputedStyle(this.textarea).lineHeight);
        
        // Calculate approximate cursor position
        const value = this.textarea.value;
        const beforeCursor = value.substring(0, this.slashIndex);
        const lines = beforeCursor.split('\n');
        const lineNumber = lines.length - 1;
        
        const top = textareaRect.top + (lineNumber * lineHeight) + lineHeight + window.scrollY;
        const left = textareaRect.left + window.scrollX;
        
        this.palette.style.position = 'absolute';
        this.palette.style.top = `${Math.min(top, window.innerHeight - 300)}px`;
        this.palette.style.left = `${left}px`;
        this.palette.style.zIndex = '10000';
    }
    
    executeCommand(command) {
        if (!command) return;
        
        const value = this.textarea.value;
        const beforeSlash = value.substring(0, this.slashIndex);
        const afterCursor = value.substring(this.cursorPos);
        
        // Replace the slash command with the insert text
        const newValue = beforeSlash + command.insert + afterCursor;
        this.textarea.value = newValue;
        
        // Position cursor after inserted text
        const newCursorPos = beforeSlash.length + command.insert.length;
        this.textarea.setSelectionRange(newCursorPos, newCursorPos);
        
        // Trigger input event for any listeners
        this.textarea.dispatchEvent(new Event('input', { bubbles: true }));
        
        this.hidePalette();
        this.textarea.focus();
    }
    
    destroy() {
        if (this.palette) {
            this.palette.remove();
        }
    }
}

// Auto-initialize on textareas with data-command-palette attribute
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('textarea[data-command-palette]').forEach(textarea => {
        new LinguifyCommandPalette(textarea);
    });
});

// Export for manual initialization
window.LinguifyCommandPalette = LinguifyCommandPalette;