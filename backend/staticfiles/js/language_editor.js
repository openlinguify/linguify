// language_editor.js - Amélioration de l'éditeur JSON pour contenus multilingues
(function() {
    'use strict';
    
    // Initialiser quand le DOM est chargé
    document.addEventListener('DOMContentLoaded', function() {
        initJsonEditors();
        addLanguageControls();
    });
    
    /**
     * Initialise l'éditeur CodeMirror pour tous les champs JSON
     */
    function initJsonEditors() {
        // Trouver tous les champs JSON (en particulier language_specific_content)
        const jsonFields = document.querySelectorAll('textarea.json-editor, #id_language_specific_content');
        
        // Appliquer CodeMirror à chaque champ
        jsonFields.forEach(field => {
            // Si un CodeMirror est déjà attaché, ne pas le réinitialiser
            if (field.nextSibling && field.nextSibling.classList && field.nextSibling.classList.contains('CodeMirror')) {
                return;
            }
            
            // Initialiser CodeMirror avec options
            const editor = CodeMirror.fromTextArea(field, {
                mode: {
                    name: "javascript",
                    json: true
                },
                theme: "default",
                lineNumbers: true,
                autoCloseBrackets: true,
                matchBrackets: true,
                foldGutter: true,
                gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
                extraKeys: {
                    "Ctrl-Space": "autocomplete",
                    "Ctrl-Q": function(cm) {
                        cm.foldCode(cm.getCursor());
                    },
                    "Tab": function(cm) {
                        const spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
                        cm.replaceSelection(spaces);
                    }
                },
                indentUnit: 2,
                smartIndent: true,
                lineWrapping: true,
                lint: true // Active la validation JSON
            });
            
            // Mettre à jour le textarea quand le contenu de l'éditeur change
            editor.on("change", function() {
                editor.save();
                validateJson(field);
            });
            
            // Ajouter des boutons de navigation par langue au-dessus de l'éditeur
            addEditorControls(field, editor);
            
            // Mettre en forme le JSON initialement
            setTimeout(function() {
                formatJson(field, editor);
            }, 100);
        });
    }
    
    /**
     * Ajoute des contrôles personnalisés à l'éditeur CodeMirror
     */
    function addEditorControls(field, editor) {
        // Créer la barre d'outils
        const toolbar = document.createElement('div');
        toolbar.className = 'json-editor-toolbar';
        toolbar.innerHTML = `
            <div class="toolbar-controls">
                <button type="button" class="format-json-btn">Formater JSON</button>
                <button type="button" class="validate-json-btn">Valider JSON</button>
                <button type="button" class="fold-all-btn">Tout replier</button>
                <button type="button" class="unfold-all-btn">Tout déplier</button>
                <span class="json-status"></span>
            </div>
            <div class="language-navigation">
                <!-- Les onglets de langue seront ajoutés ici -->
            </div>
        `;
        
        // Insérer la barre d'outils avant l'éditeur
        field.parentNode.insertBefore(toolbar, field.nextSibling);
        
        // Ajouter des écouteurs d'événements aux boutons
        toolbar.querySelector('.format-json-btn').addEventListener('click', function() {
            formatJson(field, editor);
        });
        
        toolbar.querySelector('.validate-json-btn').addEventListener('click', function() {
            validateJson(field, editor);
        });
        
        toolbar.querySelector('.fold-all-btn').addEventListener('click', function() {
            foldAll(editor);
        });
        
        toolbar.querySelector('.unfold-all-btn').addEventListener('click', function() {
            unfoldAll(editor);
        });
        
        // Initialiser les onglets de navigation par langue
        if (field.id === 'id_language_specific_content') {
            initLanguageTabs(toolbar, editor);
        }
    }
    
    /**
     * Initialise les onglets de navigation par langue pour le champ JSON
     */
    function initLanguageTabs(toolbar, editor) {
        const languageNav = toolbar.querySelector('.language-navigation');
        
        // Essayer de récupérer et parser le JSON
        try {
            const jsonValue = editor.getValue();
            if (!jsonValue.trim()) return;
            
            const jsonData = JSON.parse(jsonValue);
            
            // Créer un onglet pour chaque langue
            for (const lang in jsonData) {
                const langTab = document.createElement('button');
                langTab.type = 'button';
                langTab.className = 'language-tab';
                langTab.textContent = lang.toUpperCase();
                langTab.dataset.lang = lang;
                
                // Au clic, naviguer vers la section de la langue
                langTab.addEventListener('click', function() {
                    navigateToLanguage(editor, lang);
                });
                
                languageNav.appendChild(langTab);
            }
            
            // Ajouter un bouton pour ajouter une nouvelle langue
            const addLangBtn = document.createElement('button');
            addLangBtn.type = 'button';
            addLangBtn.className = 'add-lang-btn';
            addLangBtn.textContent = '+';
            addLangBtn.title = 'Ajouter une langue';
            
            addLangBtn.addEventListener('click', function() {
                promptAddLanguage(editor);
            });
            
            languageNav.appendChild(addLangBtn);
            
        } catch (e) {
            console.error('Error parsing JSON for language tabs:', e);
        }
    }
    
    /**
     * Navigue vers la section d'une langue spécifique dans l'éditeur
     */
    function navigateToLanguage(editor, lang) {
        // Chercher la position de "lang": dans le JSON
        const content = editor.getValue();
        const searchFor = `"${lang}"`;
        
        // Trouver la position
        let pos = content.indexOf(searchFor);
        if (pos !== -1) {
            // Convertir l'index en position {line, ch}
            const doc = editor.getDoc();
            const cursor = doc.posFromIndex(pos);
            
            // Déplacer le curseur et défiler vers cette position
            editor.setCursor(cursor);
            editor.focus();
            
            // Déplier cette section
            editor.foldCode(cursor, null, 'unfold');
            
            // Mettre en surbrillance l'onglet actif
            const tabs = document.querySelectorAll('.language-tab');
            tabs.forEach(tab => {
                if (tab.dataset.lang === lang) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            });
        }
    }
    
    /**
     * Demande à l'utilisateur d'ajouter une nouvelle langue
     */
    function promptAddLanguage(editor) {
        const langCode = prompt('Entrez le code de langue à 2 lettres (ex: de, it, pt):');
        if (!langCode || langCode.length !== 2) {
            alert('Veuillez entrer un code de langue valide à 2 lettres.');
            return;
        }
        
        try {
            // Récupérer le JSON actuel
            const jsonString = editor.getValue();
            const jsonData = JSON.parse(jsonString);
            
            // Vérifier si la langue existe déjà
            if (jsonData[langCode]) {
                alert(`La langue "${langCode}" existe déjà.`);
                return;
            }
            
            // Ajouter le template de la nouvelle langue
            jsonData[langCode] = {
                "content": `Contenu en ${langCode}...`,
                "explanation": `Explication en ${langCode}...`,
                "formula": "",
                "example": "",
                "exception": ""
            };
            
            // Mettre à jour l'éditeur avec le nouveau JSON formaté
            const formattedJson = JSON.stringify(jsonData, null, 2);
            editor.setValue(formattedJson);
            
            // Valider et ajouter un onglet pour la nouvelle langue
            validateJson(editor.getTextArea(), editor);
            
            // Rafraîchir les onglets de langue
            const toolbar = editor.getTextArea().parentNode.querySelector('.json-editor-toolbar');
            const languageNav = toolbar.querySelector('.language-navigation');
            
            // Supprimer tous les onglets existants
            while (languageNav.firstChild) {
                languageNav.removeChild(languageNav.firstChild);
            }
            
            // Réinitialiser les onglets
            initLanguageTabs(toolbar, editor);
            
            // Aller à la nouvelle langue
            navigateToLanguage(editor, langCode);
            
        } catch (e) {
            console.error('Error adding new language:', e);
            alert('Erreur lors de l\'ajout de la langue: ' + e.message);
        }
    }
    
    /**
     * Formate le JSON dans l'éditeur
     */
    function formatJson(field, editor) {
        try {
            const value = editor.getValue().trim();
            if (!value) return;
            
            // Parser et reformater le JSON
            const json = JSON.parse(value);
            const formattedJson = JSON.stringify(json, null, 2);
            
            // Mettre à jour l'éditeur
            editor.setValue(formattedJson);
            
            // Mettre à jour le statut
            const statusEl = field.parentNode.querySelector('.json-status');
            if (statusEl) {
                statusEl.textContent = '✓ Valide';
                statusEl.className = 'json-status valid';
            }
        } catch (e) {
            console.error('Error formatting JSON:', e);
            
            // Mettre à jour le statut
            const statusEl = field.parentNode.querySelector('.json-status');
            if (statusEl) {
                statusEl.textContent = '✗ Invalide: ' + e.message;
                statusEl.className = 'json-status invalid';
            }
        }
    }
    
    /**
     * Valide le JSON dans l'éditeur
     */
    function validateJson(field, editor) {
        const statusEl = field.parentNode.querySelector('.json-status');
        if (!statusEl) return;
        
        try {
            const value = editor ? editor.getValue().trim() : field.value.trim();
            if (!value) {
                statusEl.textContent = '';
                return;
            }
            
            // Valider la structure JSON
            const json = JSON.parse(value);
            
            // Valider la structure pour le contenu multilingue
            if (field.id === 'id_language_specific_content') {
                validateLanguageContent(json);
            }
            
            statusEl.textContent = '✓ Valide';
            statusEl.className = 'json-status valid';
        } catch (e) {
            statusEl.textContent = '✗ Invalide: ' + e.message;
            statusEl.className = 'json-status invalid';
        }
    }
    
    /**
     * Valide la structure des contenus par langue
     */
    function validateLanguageContent(json) {
        // Vérifier que c'est bien un objet
        if (typeof json !== 'object' || Array.isArray(json)) {
            throw new Error('Le contenu doit être un objet JSON avec des codes de langue comme clés.');
        }
        
        // Pour chaque langue
        for (const lang in json) {
            const content = json[lang];
            
            // Vérifier que le contenu est un objet
            if (typeof content !== 'object' || Array.isArray(content)) {
                throw new Error(`Le contenu pour la langue "${lang}" doit être un objet.`);
            }
            
            // Vérifier les champs obligatoires
            if (!content.content) {
                throw new Error(`Champ "content" manquant pour la langue "${lang}".`);
            }
            
            if (!content.explanation) {
                throw new Error(`Champ "explanation" manquant pour la langue "${lang}".`);
            }
        }
    }
    
    /**
     * Replie toutes les sections de l'éditeur
     */
    function foldAll(editor) {
        for (let i = 0; i < editor.lineCount(); i++) {
            editor.foldCode({line: i, ch: 0});
        }
    }
    
    /**
     * Déplie toutes les sections de l'éditeur
     */
    function unfoldAll(editor) {
        for (let i = 0; i < editor.lineCount(); i++) {
            editor.foldCode({line: i, ch: 0}, null, 'unfold');
        }
    }
    
    /**
     * Ajoute des contrôles supplémentaires pour les langues
     */
    function addLanguageControls() {
        // Trouver tous les boutons d'ajout de langue existants
        const langButtons = document.querySelectorAll('[data-language-code]');
        
        langButtons.forEach(button => {
            button.addEventListener('click', function() {
                const langCode = this.dataset.languageCode;
                const langName = this.dataset.languageName;
                
                // Trouver l'éditeur CodeMirror actif
                const editors = document.querySelectorAll('.CodeMirror');
                if (editors.length > 0) {
                    const cm = editors[0].CodeMirror;
                    if (cm) {
                        addLanguageTemplate(cm, langCode, langName);
                    }
                }
            });
        });
    }
    
    /**
     * Ajoute un template pour une nouvelle langue
     */
    function addLanguageTemplate(editor, langCode, langName) {
        try {
            // Récupérer le JSON actuel
            const jsonString = editor.getValue();
            const jsonData = JSON.parse(jsonString);
            
            // Vérifier si la langue existe déjà
            if (jsonData[langCode]) {
                alert(`La langue ${langName} (${langCode}) existe déjà.`);
                return;
            }
            
            // Ajouter la nouvelle langue avec un template
            jsonData[langCode] = {
                "content": `Contenu en ${langName}...`,
                "explanation": `Explication en ${langName}...`,
                "formula": "",
                "example": "",
                "exception": ""
            };
            
            // Mettre à jour l'éditeur avec le JSON formaté
            editor.setValue(JSON.stringify(jsonData, null, 2));
            
            // Naviguer vers la nouvelle langue
            navigateToLanguage(editor, langCode);
            
        } catch (e) {
            console.error('Error adding language template:', e);
            alert('Erreur lors de l\'ajout du template: ' + e.message);
        }
    }
})();