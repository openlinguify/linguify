/**
 * Document Detail JavaScript
 * Linguify - Gestion interactive de la page de détail des documents
 */

class DocumentDetailManager {
    constructor() {
        this.documentId = document.getElementById('document-id')?.value;
        this.documentContent = document.getElementById('document-content')?.value || '';
        this.documentType = this.getDocumentType();
        
        this.init();
    }
    
    /**
     * Initialise toutes les fonctionnalités
     */
    init() {
        this.calculateStatistics();
        this.initializeTableOfContents();
        this.setupSmoothScrolling();
        this.initializeReadingProgress();
        this.setupKeyboardShortcuts();
        this.initializeTooltips();
        this.setupAutoRefresh();
    }
    
    /**
     * Calcule et affiche les statistiques du document
     */
    calculateStatistics() {
        if (!this.documentContent) return;
        
        const stats = this.analyzeContent(this.documentContent);
        
        // Mise à jour des éléments avec animation
        this.animateStatUpdate('word-count', stats.wordCount.toLocaleString());
        this.animateStatUpdate('char-count', stats.charCount.toLocaleString());
        this.animateStatUpdate('reading-time', stats.readingTime + ' min');
        
        // Ajout d'informations supplémentaires
        this.addAdvancedStats(stats);
    }
    
    /**
     * Analyse le contenu du document
     */
    analyzeContent(content) {
        const words = content.trim() ? content.trim().split(/\s+/) : [];
        const wordCount = words.length;
        const charCount = content.length;
        const charCountNoSpaces = content.replace(/\s/g, '').length;
        const paragraphs = content.split(/\n\s*\n/).filter(p => p.trim()).length;
        const sentences = content.split(/[.!?]+/).filter(s => s.trim()).length;
        const readingTime = Math.ceil(wordCount / 200); // 200 mots/minute
        const readingTimeDetailed = this.calculateDetailedReadingTime(wordCount);
        
        return {
            wordCount,
            charCount,
            charCountNoSpaces,
            paragraphs,
            sentences,
            readingTime,
            readingTimeDetailed,
            complexity: this.calculateComplexity(words, sentences)
        };
    }
    
    /**
     * Calcule le temps de lecture détaillé
     */
    calculateDetailedReadingTime(wordCount) {
        const wordsPerMinute = 200;
        const totalMinutes = wordCount / wordsPerMinute;
        const minutes = Math.floor(totalMinutes);
        const seconds = Math.round((totalMinutes - minutes) * 60);
        
        if (minutes === 0) {
            return `${seconds}s`;
        } else if (seconds === 0) {
            return `${minutes}min`;
        } else {
            return `${minutes}min ${seconds}s`;
        }
    }
    
    /**
     * Calcule la complexité du texte
     */
    calculateComplexity(words, sentences) {
        if (sentences === 0) return 'Simple';
        
        const avgWordsPerSentence = words.length / sentences;
        const longWords = words.filter(word => word.length > 6).length;
        const complexityRatio = longWords / words.length;
        
        if (avgWordsPerSentence > 20 || complexityRatio > 0.3) {
            return 'Complexe';
        } else if (avgWordsPerSentence > 15 || complexityRatio > 0.2) {
            return 'Intermédiaire';
        } else {
            return 'Simple';
        }
    }
    
    /**
     * Anime la mise à jour d'une statistique
     */
    animateStatUpdate(elementId, value) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        element.style.transform = 'scale(1.1)';
        element.style.transition = 'transform 0.3s ease';
        
        setTimeout(() => {
            element.textContent = value;
            element.style.transform = 'scale(1)';
        }, 150);
    }
    
    /**
     * Ajoute des statistiques avancées
     */
    addAdvancedStats(stats) {
        const statsContainer = document.querySelector('.stats-grid-modern');
        if (!statsContainer) return;
        
        const advancedStatsHTML = `
            <div class="stat-modern advanced-stat" title="Paragraphes">
                <div class="stat-icon">
                    <i class="bi bi-paragraph"></i>
                </div>
                <div class="stat-details">
                    <span class="stat-number">${stats.paragraphs}</span>
                    <span class="stat-label">Paragraphes</span>
                </div>
            </div>
            <div class="stat-modern advanced-stat" title="Complexité du texte">
                <div class="stat-icon">
                    <i class="bi bi-speedometer2"></i>
                </div>
                <div class="stat-details">
                    <span class="stat-number">${stats.complexity}</span>
                    <span class="stat-label">Complexité</span>
                </div>
            </div>
        `;
        
        // Ajoute les stats avancées si elles n'existent pas déjà
        if (!statsContainer.querySelector('.advanced-stat')) {
            statsContainer.insertAdjacentHTML('beforeend', advancedStatsHTML);
        }
    }
    
    /**
     * Initialise la table des matières pour Markdown
     */
    initializeTableOfContents() {
        if (this.documentType !== 'markdown') return;
        
        const tocContainer = document.getElementById('table-of-contents');
        if (!tocContainer) return;
        
        const headings = this.extractHeadings(this.documentContent);
        
        if (headings.length === 0) {
            tocContainer.innerHTML = this.getEmptyTocHTML();
            return;
        }
        
        const tocHTML = this.generateTocHTML(headings);
        tocContainer.innerHTML = tocHTML;
        
        // Ajoute les ancres dans le contenu
        this.addContentAnchors(headings);
        
        // Active la navigation
        this.setupTocNavigation();
    }
    
    /**
     * Extrait les titres du contenu Markdown
     */
    extractHeadings(content) {
        const lines = content.split('\n');
        const headings = [];
        
        lines.forEach((line, index) => {
            const match = line.match(/^(#{1,6})\s+(.+)$/);
            if (match) {
                const level = match[1].length;
                const text = match[2].trim();
                const id = this.createHeadingId(text);
                
                headings.push({
                    level,
                    text,
                    id,
                    line: index + 1
                });
            }
        });
        
        return headings;
    }
    
    /**
     * Crée un ID unique pour un titre
     */
    createHeadingId(text) {
        return text
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '') // Supprime les accents
            .replace(/[^a-z0-9\s-]/g, '') // Garde seulement lettres, chiffres, espaces et tirets
            .replace(/\s+/g, '-') // Remplace espaces par tirets
            .replace(/-+/g, '-') // Évite les tirets multiples
            .replace(/^-|-$/g, ''); // Supprime tirets en début/fin
    }
    
    /**
     * Génère le HTML de la table des matières
     */
    generateTocHTML(headings) {
        let html = '<div class="toc-modern">';
        
        headings.forEach((heading, index) => {
            const indentClass = `toc-level-${heading.level}`;
            const isActive = index === 0 ? 'active' : '';
            
            html += `
                <div class="toc-item ${indentClass} ${isActive}" data-target="${heading.id}">
                    <a href="#${heading.id}" class="toc-link">
                        <span class="toc-bullet"></span>
                        <span class="toc-text">${heading.text}</span>
                    </a>
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }
    
    /**
     * Retourne le HTML pour une table des matières vide
     */
    getEmptyTocHTML() {
        return `
            <div class="empty-toc">
                <i class="bi bi-list-nested"></i>
                <p>Aucun titre trouvé</p>
                <small>Utilisez # ## ### pour créer des titres</small>
            </div>
        `;
    }
    
    /**
     * Ajoute des ancres dans le contenu
     */
    addContentAnchors(headings) {
        const contentContainer = document.querySelector('.markdown-content');
        if (!contentContainer) return;
        
        headings.forEach(heading => {
            const headingElements = contentContainer.querySelectorAll('h1, h2, h3, h4, h5, h6');
            headingElements.forEach(el => {
                if (el.textContent.trim() === heading.text) {
                    el.id = heading.id;
                    el.classList.add('heading-anchor');
                    
                    // Ajoute un lien d'ancrage
                    const anchor = document.createElement('a');
                    anchor.href = `#${heading.id}`;
                    anchor.className = 'heading-link';
                    anchor.innerHTML = '<i class="bi bi-link-45deg"></i>';
                    anchor.title = 'Lien vers cette section';
                    el.appendChild(anchor);
                }
            });
        });
    }
    
    /**
     * Configure la navigation dans la table des matières
     */
    setupTocNavigation() {
        const tocLinks = document.querySelectorAll('.toc-link');
        const tocItems = document.querySelectorAll('.toc-item');
        
        tocLinks.forEach((link, index) => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Met à jour l'état actif
                tocItems.forEach(item => item.classList.remove('active'));
                tocItems[index].classList.add('active');
                
                // Défilement fluide
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    this.scrollToElement(target);
                }
            });
        });
    }
    
    /**
     * Configure le défilement fluide
     */
    setupSmoothScrolling() {
        // Pour tous les liens d'ancrage
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href === '#') return;
                
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    this.scrollToElement(target);
                }
            });
        });
    }
    
    /**
     * Défilement fluide vers un élément
     */
    scrollToElement(element) {
        const headerHeight = 80; // Hauteur du header + marge
        const elementTop = element.getBoundingClientRect().top + window.pageYOffset;
        const targetPosition = elementTop - headerHeight;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
        
        // Highlight temporaire
        this.highlightElement(element);
    }
    
    /**
     * Surligne temporairement un élément
     */
    highlightElement(element) {
        element.classList.add('highlighted');
        setTimeout(() => {
            element.classList.remove('highlighted');
        }, 2000);
    }
    
    /**
     * Initialise la barre de progression de lecture
     */
    initializeReadingProgress() {
        const progressBar = this.createReadingProgressBar();
        
        window.addEventListener('scroll', () => {
            this.updateReadingProgress(progressBar);
            this.updateActiveSection();
        });
    }
    
    /**
     * Crée la barre de progression de lecture
     */
    createReadingProgressBar() {
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress';
        progressBar.innerHTML = '<div class="reading-progress-fill"></div>';
        
        document.body.appendChild(progressBar);
        return progressBar;
    }
    
    /**
     * Met à jour la progression de lecture
     */
    updateReadingProgress(progressBar) {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight - windowHeight;
        const scrollTop = window.pageYOffset;
        const progress = (scrollTop / documentHeight) * 100;
        
        const fill = progressBar.querySelector('.reading-progress-fill');
        fill.style.width = `${Math.min(progress, 100)}%`;
    }
    
    /**
     * Met à jour la section active dans la table des matières
     */
    updateActiveSection() {
        const headings = document.querySelectorAll('.heading-anchor');
        const tocItems = document.querySelectorAll('.toc-item');
        
        let activeHeading = null;
        
        headings.forEach(heading => {
            const rect = heading.getBoundingClientRect();
            if (rect.top <= 100 && rect.bottom > 0) {
                activeHeading = heading;
            }
        });
        
        if (activeHeading) {
            const headingId = activeHeading.id;
            tocItems.forEach(item => {
                item.classList.toggle('active', item.dataset.target === headingId);
            });
        }
    }
    
    /**
     * Configure les raccourcis clavier
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+E pour éditer
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault();
                const editButton = document.querySelector('a[href*="editor"]');
                if (editButton) {
                    window.location.href = editButton.href;
                }
            }
            
            // Ctrl+D pour dupliquer
            if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                this.duplicateDocument();
            }
            
            // Ctrl+P pour imprimer/exporter
            if (e.ctrlKey && e.key === 'p') {
                e.preventDefault();
                this.showExportOptions();
            }
        });
    }
    
    /**
     * Initialise les tooltips
     */
    initializeTooltips() {
        // Tooltips pour les statistiques
        const statElements = document.querySelectorAll('.stat-modern');
        statElements.forEach(stat => {
            const label = stat.querySelector('.stat-label').textContent;
            const number = stat.querySelector('.stat-number').textContent;
            stat.title = `${label}: ${number}`;
        });
        
        // Tooltips pour les actions
        const actionButtons = document.querySelectorAll('.document-actions-modern .btn');
        actionButtons.forEach(btn => {
            if (!btn.title) {
                const text = btn.textContent.trim();
                btn.title = text;
            }
        });
    }
    
    /**
     * Configure l'auto-refresh pour les collaborateurs
     */
    setupAutoRefresh() {
        if (!this.documentId) return;
        
        // Vérifie les mises à jour toutes les 30 secondes
        setInterval(() => {
            this.checkForUpdates();
        }, 30000);
    }
    
    /**
     * Vérifie les mises à jour du document
     */
    async checkForUpdates() {
        try {
            const response = await fetch(`/documents/api/v1/documents/${this.documentId}/status/`);
            const data = await response.json();
            
            if (data.updated_at !== this.lastUpdateTime) {
                this.showUpdateNotification();
                this.lastUpdateTime = data.updated_at;
            }
        } catch (error) {
            console.error('Erreur lors de la vérification des mises à jour:', error);
        }
    }
    
    /**
     * Affiche une notification de mise à jour
     */
    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="bi bi-info-circle"></i>
                <span>Ce document a été mis à jour</span>
                <button onclick="location.reload()" class="btn btn-sm btn-primary">
                    Recharger
                </button>
                <button onclick="this.parentElement.parentElement.remove()" class="btn btn-sm btn-outline-secondary">
                    Ignorer
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-suppression après 10 secondes
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 10000);
    }
    
    /**
     * Affiche les options d'export
     */
    showExportOptions() {
        const modal = document.createElement('div');
        modal.className = 'export-modal';
        modal.innerHTML = `
            <div class="export-modal-content">
                <h5><i class="bi bi-download me-2"></i>Exporter le document</h5>
                <div class="export-options">
                    <button class="btn btn-outline-primary" onclick="exportDocument('markdown')">
                        <i class="bi bi-markdown"></i> Markdown
                    </button>
                    <button class="btn btn-outline-primary" onclick="exportDocument('html')">
                        <i class="bi bi-filetype-html"></i> HTML
                    </button>
                    <button class="btn btn-outline-primary" onclick="exportDocument('pdf')">
                        <i class="bi bi-filetype-pdf"></i> PDF
                    </button>
                </div>
                <button class="btn btn-secondary" onclick="this.parentElement.parentElement.remove()">
                    Annuler
                </button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Fermeture sur clic extérieur
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    /**
     * Récupère le type de document
     */
    getDocumentType() {
        const titleIcon = document.querySelector('.document-title i');
        if (titleIcon?.classList.contains('bi-markdown')) return 'markdown';
        if (titleIcon?.classList.contains('bi-filetype-html')) return 'html';
        return 'text';
    }
}

/**
 * Fonctions utilitaires exposées globalement
 */
class DocumentActions {
    static async exportDocument(format) {
        const documentId = document.getElementById('document-id')?.value;
        if (!documentId) return;
        
        try {
            // Affiche un indicateur de chargement
            DocumentActions.showExportLoading(format);
            
            const response = await fetch(`/documents/api/v1/documents/${documentId}/export/?format=${format}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `document.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                DocumentActions.showSuccess(`Document exporté en ${format.toUpperCase()}`);
            } else {
                throw new Error('Erreur lors de l\'export');
            }
        } catch (error) {
            console.error('Export error:', error);
            DocumentActions.showError('Erreur lors de l\'export du document');
        } finally {
            DocumentActions.hideExportLoading();
        }
    }
    
    static async duplicateDocument() {
        const documentId = document.getElementById('document-id')?.value;
        if (!documentId) return;
        
        if (!confirm('Créer une copie de ce document ?')) return;
        
        try {
            DocumentActions.showLoading('Duplication en cours...');
            
            const response = await fetch(`/documents/api/v1/documents/${documentId}/duplicate/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': DocumentActions.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.id) {
                DocumentActions.showSuccess('Document dupliqué avec succès');
                setTimeout(() => {
                    window.location.href = `/documents/${data.id}/`;
                }, 1500);
            } else {
                throw new Error(data.error || 'Erreur lors de la duplication');
            }
        } catch (error) {
            console.error('Duplicate error:', error);
            DocumentActions.showError('Erreur lors de la duplication');
        } finally {
            DocumentActions.hideLoading();
        }
    }
    
    static async replyToComment(commentId) {
        // Implémentation basique - à étendre selon les besoins
        const reply = prompt('Votre réponse:');
        if (!reply) return;
        
        try {
            const response = await fetch(`/documents/api/v1/comments/${commentId}/reply/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': DocumentActions.getCSRFToken()
                },
                body: JSON.stringify({ content: reply })
            });
            
            if (response.ok) {
                DocumentActions.showSuccess('Réponse ajoutée');
                setTimeout(() => location.reload(), 1000);
            } else {
                throw new Error('Erreur serveur');
            }
        } catch (error) {
            console.error('Reply error:', error);
            DocumentActions.showError('Erreur lors de l\'ajout de la réponse');
        }
    }
    
    static async resolveComment(commentId) {
        if (!confirm('Marquer ce commentaire comme résolu ?')) return;
        
        try {
            const response = await fetch(`/documents/api/v1/comments/${commentId}/resolve/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': DocumentActions.getCSRFToken()
                }
            });
            
            if (response.ok) {
                DocumentActions.showSuccess('Commentaire résolu');
                setTimeout(() => location.reload(), 1000);
            } else {
                throw new Error('Erreur serveur');
            }
        } catch (error) {
            console.error('Resolve error:', error);
            DocumentActions.showError('Erreur lors de la résolution du commentaire');
        }
    }
    
    // Fonctions utilitaires pour les notifications et le loading
    static showExportLoading(format) {
        const loading = document.createElement('div');
        loading.id = 'export-loading';
        loading.className = 'loading-overlay';
        loading.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-primary"></div>
                <p>Export ${format.toUpperCase()} en cours...</p>
            </div>
        `;
        document.body.appendChild(loading);
    }
    
    static hideExportLoading() {
        const loading = document.getElementById('export-loading');
        if (loading) loading.remove();
    }
    
    static showLoading(message) {
        const loading = document.createElement('div');
        loading.id = 'action-loading';
        loading.className = 'loading-overlay';
        loading.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-primary"></div>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(loading);
    }
    
    static hideLoading() {
        const loading = document.getElementById('action-loading');
        if (loading) loading.remove();
    }
    
    static showSuccess(message) {
        DocumentActions.showNotification(message, 'success');
    }
    
    static showError(message) {
        DocumentActions.showNotification(message, 'danger');
    }
    
    static showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 1055; max-width: 400px;';
        notification.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    static getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

/**
 * Initialisation au chargement de la page
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialise le gestionnaire de détails du document
    new DocumentDetailManager();
    
    // Expose les fonctions globalement pour les boutons onclick
    window.exportDocument = DocumentActions.exportDocument;
    window.duplicateDocument = DocumentActions.duplicateDocument;
    window.replyToComment = DocumentActions.replyToComment;
    window.resolveComment = DocumentActions.resolveComment;
    
    // Ajoute les styles CSS dynamiques
    const style = document.createElement('style');
    style.textContent = `
        .highlighted {
            background-color: rgba(45, 91, 186, 0.1);
            transition: background-color 0.3s ease;
            padding: 0.5rem;
            border-radius: 0.25rem;
        }
        
        .reading-progress {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: rgba(45, 91, 186, 0.1);
            z-index: 1000;
        }
        
        .reading-progress-fill {
            height: 100%;
            background: var(--linguify-primary);
            transition: width 0.3s ease;
        }
        
        .heading-anchor {
            position: relative;
        }
        
        .heading-link {
            position: absolute;
            left: -30px;
            top: 50%;
            transform: translateY(-50%);
            opacity: 0;
            transition: opacity 0.2s ease;
            color: var(--linguify-primary);
            text-decoration: none;
        }
        
        .heading-anchor:hover .heading-link {
            opacity: 1;
        }
        
        .toc-modern {
            padding: 0;
        }
        
        .toc-item {
            margin-bottom: 0.25rem;
            border-radius: 0.25rem;
            transition: all 0.2s ease;
        }
        
        .toc-item.active {
            background: rgba(45, 91, 186, 0.1);
        }
        
        .toc-level-1 { padding-left: 0; }
        .toc-level-2 { padding-left: 1rem; }
        .toc-level-3 { padding-left: 2rem; }
        .toc-level-4 { padding-left: 3rem; }
        .toc-level-5 { padding-left: 4rem; }
        .toc-level-6 { padding-left: 5rem; }
        
        .toc-link {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem;
            color: var(--linguify-primary);
            text-decoration: none;
            font-size: 0.875rem;
            border-radius: 0.25rem;
        }
        
        .toc-link:hover {
            background: rgba(45, 91, 186, 0.05);
            color: var(--linguify-primary-dark);
        }
        
        .toc-bullet {
            width: 4px;
            height: 4px;
            background: currentColor;
            border-radius: 50%;
            flex-shrink: 0;
        }
        
        .empty-toc {
            text-align: center;
            padding: 2rem 1rem;
            color: var(--linguify-gray);
        }
        
        .empty-toc i {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            color: #cbd5e0;
            display: block;
        }
        
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }
        
        .loading-content {
            background: white;
            padding: 2rem;
            border-radius: 0.5rem;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .export-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1060;
        }
        
        .export-modal-content {
            background: white;
            padding: 2rem;
            border-radius: 0.5rem;
            text-align: center;
            max-width: 400px;
            width: 90%;
        }
        
        .export-options {
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .update-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border: 1px solid var(--linguify-primary);
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            z-index: 1050;
            max-width: 400px;
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }
        
        .notification-content i {
            color: var(--linguify-primary);
            font-size: 1.25rem;
        }
    `;
    document.head.appendChild(style);
});

/**
 * Export pour utilisation en module si nécessaire
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DocumentDetailManager, DocumentActions };
}