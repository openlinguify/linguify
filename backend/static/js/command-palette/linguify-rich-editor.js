/**
 * Linguify Rich Text Editor
 * Visual block-based editor with slash commands
 * Transforms raw HTML/Markdown into editable visual blocks
 */
class LinguifyRichEditor {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            placeholder: 'Décrivez votre tâche ici...\n\nRaccourcis utiles:\n• Entrée = nouvelle ligne\n• Ctrl+Entrée = nouveau bloc\n• / = menu de commandes',
            ...options
        };
        
        this.blocks = [];
        this.currentBlock = null;
        this.commandPalette = null;
        
        this.init();
    }
    
    init() {
        this.setupContainer();
        this.createInitialBlock();
        this.attachEventListeners();
        this.initCommandPalette();
    }
    
    setupContainer() {
        this.container.classList.add('linguify-rich-editor');
        this.container.innerHTML = '';
        this.container.setAttribute('contenteditable', 'false');
    }
    
    createInitialBlock() {
        this.addBlock('paragraph', '');
    }
    
    addBlock(type, content = '', position = -1) {
        const block = this.createBlock(type, content);
        
        if (position === -1) {
            this.container.appendChild(block.element);
            this.blocks.push(block);
        } else {
            const targetBlock = this.blocks[position];
            this.container.insertBefore(block.element, targetBlock.element);
            this.blocks.splice(position, 0, block);
        }
        
        return block;
    }
    
    createBlock(type, content = '') {
        const blockId = 'block-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const blockElement = document.createElement('div');
        blockElement.className = 'rich-block';
        blockElement.setAttribute('data-block-type', type);
        blockElement.setAttribute('data-block-id', blockId);
        
        let blockHTML = '';
        
        switch (type) {
            case 'paragraph':
                blockHTML = `
                    <div class="block-content">
                        <div class="block-input" contenteditable="true" data-placeholder="Tapez votre texte... (Entrée = nouvelle ligne, / = commandes)">${content}</div>
                    </div>
                `;
                break;
                
            case 'heading1':
                blockHTML = `
                    <div class="block-content">
                        <h1 class="block-heading" contenteditable="true" data-placeholder="Titre 1">${content}</h1>
                    </div>
                `;
                break;
                
            case 'heading2':
                blockHTML = `
                    <div class="block-content">
                        <h2 class="block-heading" contenteditable="true" data-placeholder="Titre 2">${content}</h2>
                    </div>
                `;
                break;
                
            case 'heading3':
                blockHTML = `
                    <div class="block-content">
                        <h3 class="block-heading" contenteditable="true" data-placeholder="Titre 3">${content}</h3>
                    </div>
                `;
                break;
                
            case 'quote':
                blockHTML = `
                    <div class="block-content block-quote">
                        <div class="quote-indicator"></div>
                        <div class="block-input" contenteditable="true" data-placeholder="Citation...">${content}</div>
                    </div>
                `;
                break;
                
            case 'code':
                blockHTML = `
                    <div class="block-content block-code">
                        <div class="code-header">
                            <span class="code-language">Code</span>
                        </div>
                        <pre class="block-input" contenteditable="true" data-placeholder="Votre code ici...">${content}</pre>
                    </div>
                `;
                break;
                
            case 'separator':
                blockHTML = `
                    <div class="block-content block-separator">
                        <hr class="separator-line">
                    </div>
                `;
                break;
                
            case 'columns2':
                blockHTML = `
                    <div class="block-content block-columns" data-columns="2">
                        <div class="column-container">
                            <div class="column">
                                <div class="block-input" contenteditable="true" data-placeholder="Colonne 1..."></div>
                            </div>
                            <div class="column">
                                <div class="block-input" contenteditable="true" data-placeholder="Colonne 2..."></div>
                            </div>
                        </div>
                    </div>
                `;
                break;
                
            case 'columns3':
                blockHTML = `
                    <div class="block-content block-columns" data-columns="3">
                        <div class="column-container">
                            <div class="column">
                                <div class="block-input" contenteditable="true" data-placeholder="Colonne 1..."></div>
                            </div>
                            <div class="column">
                                <div class="block-input" contenteditable="true" data-placeholder="Colonne 2..."></div>
                            </div>
                            <div class="column">
                                <div class="block-input" contenteditable="true" data-placeholder="Colonne 3..."></div>
                            </div>
                        </div>
                    </div>
                `;
                break;
                
            case 'banner-info':
                blockHTML = `
                    <div class="block-content block-banner banner-info">
                        <div class="banner-icon">
                            <i class="bi bi-info-circle"></i>
                        </div>
                        <div class="banner-content">
                            <div class="block-input" contenteditable="true" data-placeholder="Information...">${content}</div>
                        </div>
                    </div>
                `;
                break;
                
            case 'banner-success':
                blockHTML = `
                    <div class="block-content block-banner banner-success">
                        <div class="banner-icon">
                            <i class="bi bi-check-circle"></i>
                        </div>
                        <div class="banner-content">
                            <div class="block-input" contenteditable="true" data-placeholder="Succès...">${content}</div>
                        </div>
                    </div>
                `;
                break;
                
            case 'banner-warning':
                blockHTML = `
                    <div class="block-content block-banner banner-warning">
                        <div class="banner-icon">
                            <i class="bi bi-exclamation-triangle"></i>
                        </div>
                        <div class="banner-content">
                            <div class="block-input" contenteditable="true" data-placeholder="Attention...">${content}</div>
                        </div>
                    </div>
                `;
                break;
                
            case 'banner-danger':
                blockHTML = `
                    <div class="block-content block-banner banner-danger">
                        <div class="banner-icon">
                            <i class="bi bi-exclamation-circle"></i>
                        </div>
                        <div class="banner-content">
                            <div class="block-input" contenteditable="true" data-placeholder="Danger...">${content}</div>
                        </div>
                    </div>
                `;
                break;
                
            case 'list-bulleted':
                blockHTML = `
                    <div class="block-content block-list">
                        <ul class="list-container">
                            <li>
                                <div class="block-input" contenteditable="true" data-placeholder="Élément de liste..."></div>
                            </li>
                        </ul>
                        <button class="add-list-item" onclick="this.closest('.rich-block').editor.addListItem(this)">
                            <i class="bi bi-plus"></i> Ajouter un élément
                        </button>
                    </div>
                `;
                break;
                
            case 'list-numbered':
                blockHTML = `
                    <div class="block-content block-list">
                        <ol class="list-container">
                            <li>
                                <div class="block-input" contenteditable="true" data-placeholder="Élément de liste..."></div>
                            </li>
                        </ol>
                        <button class="add-list-item" onclick="this.closest('.rich-block').editor.addListItem(this)">
                            <i class="bi bi-plus"></i> Ajouter un élément
                        </button>
                    </div>
                `;
                break;
        }
        
        // Add block controls
        blockHTML = `
            <div class="block-controls">
                <div class="block-drag-handle">
                    <i class="bi bi-grip-vertical"></i>
                </div>
                <div class="block-actions">
                    <button class="block-action" onclick="this.closest('.rich-block').editor.duplicateBlock(this)" title="Dupliquer">
                        <i class="bi bi-files"></i>
                    </button>
                    <button class="block-action block-delete" onclick="this.closest('.rich-block').editor.deleteBlock(this)" title="Supprimer">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            ${blockHTML}
        `;
        
        blockElement.innerHTML = blockHTML;
        
        const block = {
            id: blockId,
            type: type,
            element: blockElement,
            getContent: () => this.getBlockContent(blockElement),
            setContent: (content) => this.setBlockContent(blockElement, content)
        };
        
        // Add reference for event handlers
        blockElement.editor = this;
        
        return block;
    }
    
    attachEventListeners() {
        // Handle block focus and slash commands
        this.container.addEventListener('input', (e) => {
            if (e.target.matches('.block-input, .block-heading')) {
                this.handleBlockInput(e);
            }
        });
        
        this.container.addEventListener('keydown', (e) => {
            if (e.target.matches('.block-input, .block-heading')) {
                this.handleBlockKeydown(e);
            }
        });
        
        this.container.addEventListener('focus', (e) => {
            if (e.target.matches('.block-input, .block-heading')) {
                this.currentBlock = e.target.closest('.rich-block');
                this.showBlockControls(this.currentBlock);
            }
        }, true);
        
        this.container.addEventListener('blur', (e) => {
            if (!this.container.contains(e.relatedTarget)) {
                this.hideAllBlockControls();
            }
        }, true);
    }
    
    handleBlockInput(e) {
        const input = e.target;
        const block = input.closest('.rich-block');
        const value = input.innerText || input.textContent;
        
        // Check for slash command
        if (value.endsWith('/')) {
            const selection = window.getSelection();
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();
            
            this.showCommandPalette(block, {
                x: rect.left,
                y: rect.bottom + window.scrollY
            });
        } else {
            this.hideCommandPalette();
        }
    }
    
    handleBlockKeydown(e) {
        const input = e.target;
        const block = input.closest('.rich-block');
        
        if (e.key === 'Enter') {
            if (e.shiftKey) {
                // Shift+Enter: Insert line break within the same block
                e.preventDefault();
                const selection = window.getSelection();
                const range = selection.getRangeAt(0);
                const br = document.createElement('br');
                range.insertNode(br);
                range.setStartAfter(br);
                range.setEndAfter(br);
                selection.removeAllRanges();
                selection.addRange(range);
            } else if (e.ctrlKey || e.metaKey) {
                // Ctrl+Enter (or Cmd+Enter): Create new block
                e.preventDefault();
                this.createNewBlockAfter(block);
            } else {
                // Regular Enter: Allow natural line break (browser default behavior)
                // Don't prevent default - let the browser handle it naturally
            }
        } else if (e.key === 'Backspace' && input.innerText.trim() === '') {
            e.preventDefault();
            this.deleteBlock(block);
        }
    }
    
    createNewBlockAfter(currentBlock) {
        const currentIndex = this.blocks.findIndex(b => b.element === currentBlock);
        const newBlock = this.addBlock('paragraph', '', currentIndex + 1);
        
        // Focus the new block
        setTimeout(() => {
            const input = newBlock.element.querySelector('.block-input, .block-heading');
            if (input) {
                input.focus();
            }
        }, 0);
    }
    
    showBlockControls(block) {
        // Hide all controls first
        this.hideAllBlockControls();
        
        // Show controls for current block
        const controls = block.querySelector('.block-controls');
        if (controls) {
            controls.style.opacity = '1';
        }
    }
    
    hideAllBlockControls() {
        this.container.querySelectorAll('.block-controls').forEach(controls => {
            controls.style.opacity = '0';
        });
    }
    
    // Command palette integration
    initCommandPalette() {
        this.commands = {
            'Format': [
                { name: 'Texte', description: 'Paragraphe normal', icon: 'bi-paragraph', action: () => this.convertCurrentBlock('paragraph') },
                { name: 'Titre 1', description: 'Grand titre', icon: 'bi-type-h1', action: () => this.convertCurrentBlock('heading1') },
                { name: 'Titre 2', description: 'Titre moyen', icon: 'bi-type-h2', action: () => this.convertCurrentBlock('heading2') },
                { name: 'Titre 3', description: 'Petit titre', icon: 'bi-type-h3', action: () => this.convertCurrentBlock('heading3') }
            ],
            'Éléments': [
                { name: 'Citation', description: 'Bloc de citation', icon: 'bi-quote', action: () => this.convertCurrentBlock('quote') },
                { name: 'Code', description: 'Bloc de code', icon: 'bi-code-slash', action: () => this.convertCurrentBlock('code') },
                { name: 'Séparateur', description: 'Ligne de séparation', icon: 'bi-dash', action: () => this.convertCurrentBlock('separator') },
                { name: 'Liste à puces', description: 'Liste avec puces', icon: 'bi-list-ul', action: () => this.convertCurrentBlock('list-bulleted') },
                { name: 'Liste numérotée', description: 'Liste numérotée', icon: 'bi-list-ol', action: () => this.convertCurrentBlock('list-numbered') }
            ],
            'Colonnes': [
                { name: '2 colonnes', description: 'Mise en page 2 colonnes', icon: 'bi-columns', action: () => this.convertCurrentBlock('columns2') },
                { name: '3 colonnes', description: 'Mise en page 3 colonnes', icon: 'bi-columns', action: () => this.convertCurrentBlock('columns3') }
            ],
            'Bannières': [
                { name: 'Info', description: 'Bannière d\'information', icon: 'bi-info-circle', action: () => this.convertCurrentBlock('banner-info') },
                { name: 'Succès', description: 'Bannière de succès', icon: 'bi-check-circle', action: () => this.convertCurrentBlock('banner-success') },
                { name: 'Attention', description: 'Bannière d\'avertissement', icon: 'bi-exclamation-triangle', action: () => this.convertCurrentBlock('banner-warning') },
                { name: 'Danger', description: 'Bannière de danger', icon: 'bi-exclamation-circle', action: () => this.convertCurrentBlock('banner-danger') }
            ]
        };
    }
    
    showCommandPalette(block, position) {
        this.currentBlock = block;
        this.hideCommandPalette();
        
        // Create palette if it doesn't exist
        if (!this.commandPalette) {
            this.commandPalette = document.createElement('div');
            this.commandPalette.className = 'rich-editor-command-palette';
            document.body.appendChild(this.commandPalette);
        }
        
        // Render commands
        let html = '<div class="command-palette-content">';
        Object.entries(this.commands).forEach(([category, commands]) => {
            html += `<div class="command-category">${category}</div>`;
            commands.forEach((command, index) => {
                html += `
                    <div class="command-item" data-command-index="${index}" data-command-category="${category}">
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
        
        this.commandPalette.innerHTML = html;
        
        // Position and show
        this.commandPalette.style.left = position.x + 'px';
        this.commandPalette.style.top = position.y + 'px';
        this.commandPalette.style.display = 'block';
        
        // Add click handlers
        this.commandPalette.querySelectorAll('.command-item').forEach(item => {
            item.addEventListener('click', () => {
                const category = item.dataset.commandCategory;
                const index = parseInt(item.dataset.commandIndex);
                const command = this.commands[category][index];
                command.action();
                this.hideCommandPalette();
            });
        });
    }
    
    hideCommandPalette() {
        if (this.commandPalette) {
            this.commandPalette.style.display = 'none';
        }
    }
    
    convertCurrentBlock(newType) {
        if (!this.currentBlock) return;
        
        const currentContent = this.getBlockContent(this.currentBlock);
        const blockIndex = this.blocks.findIndex(b => b.element === this.currentBlock);
        
        // Remove current block
        this.currentBlock.remove();
        this.blocks.splice(blockIndex, 1);
        
        // Add new block
        const newBlock = this.addBlock(newType, currentContent, blockIndex);
        
        // Focus new block
        setTimeout(() => {
            const input = newBlock.element.querySelector('.block-input, .block-heading');
            if (input) {
                input.focus();
                // Remove the trailing slash that triggered the command
                const content = input.innerText || input.textContent;
                if (content.endsWith('/')) {
                    input.innerText = content.slice(0, -1);
                }
            }
        }, 0);
    }
    
    getBlockContent(blockElement) {
        const input = blockElement.querySelector('.block-input, .block-heading');
        return input ? (input.innerText || input.textContent || '') : '';
    }
    
    setBlockContent(blockElement, content) {
        const input = blockElement.querySelector('.block-input, .block-heading');
        if (input) {
            input.innerText = content;
        }
    }
    
    // Block actions
    duplicateBlock(button) {
        const block = button.closest('.rich-block');
        const blockIndex = this.blocks.findIndex(b => b.element === block);
        const blockType = block.dataset.blockType;
        const blockContent = this.getBlockContent(block);
        
        this.addBlock(blockType, blockContent, blockIndex + 1);
    }
    
    deleteBlock(button) {
        const block = typeof button === 'string' ? document.querySelector(button) : 
                     button.closest ? button.closest('.rich-block') : button;
        
        if (this.blocks.length <= 1) {
            // Always keep at least one block
            this.setBlockContent(block, '');
            this.convertCurrentBlock('paragraph');
            return;
        }
        
        const blockIndex = this.blocks.findIndex(b => b.element === block);
        
        // Focus previous or next block
        const targetIndex = blockIndex > 0 ? blockIndex - 1 : blockIndex + 1;
        if (this.blocks[targetIndex]) {
            const input = this.blocks[targetIndex].element.querySelector('.block-input, .block-heading');
            if (input) input.focus();
        }
        
        // Remove block
        block.remove();
        this.blocks.splice(blockIndex, 1);
    }
    
    addListItem(button) {
        const listContainer = button.previousElementSibling;
        const newItem = document.createElement('li');
        newItem.innerHTML = '<div class="block-input" contenteditable="true" data-placeholder="Élément de liste..."></div>';
        
        listContainer.appendChild(newItem);
        newItem.querySelector('.block-input').focus();
    }
    
    // Export/Import functionality
    getHTML() {
        let html = '';
        this.blocks.forEach(block => {
            const type = block.element.dataset.blockType;
            const content = this.getBlockContent(block.element);
            
            switch (type) {
                case 'paragraph':
                    html += `<p>${content}</p>\n`;
                    break;
                case 'heading1':
                    html += `<h1>${content}</h1>\n`;
                    break;
                case 'heading2':
                    html += `<h2>${content}</h2>\n`;
                    break;
                case 'heading3':
                    html += `<h3>${content}</h3>\n`;
                    break;
                case 'quote':
                    html += `<blockquote>${content}</blockquote>\n`;
                    break;
                case 'code':
                    html += `<pre><code>${content}</code></pre>\n`;
                    break;
                case 'separator':
                    html += `<hr>\n`;
                    break;
                // Add more cases as needed
            }
        });
        return html;
    }
    
    destroy() {
        if (this.commandPalette) {
            this.commandPalette.remove();
        }
    }
}

// Auto-initialize on elements with data-rich-editor attribute
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-rich-editor]').forEach(element => {
        new LinguifyRichEditor(element);
    });
});

// Export for manual initialization
window.LinguifyRichEditor = LinguifyRichEditor;