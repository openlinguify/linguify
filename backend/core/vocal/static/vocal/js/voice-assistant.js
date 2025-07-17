/**
 * Linguify Voice Assistant
 * Assistant vocal intégré pour navigation et commandes
 */

class LinguifyVoiceAssistant {
    constructor() {
        this.isListening = false;
        this.isEnabled = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.currentLanguage = 'fr-FR'; // Langue par défaut
        this.apiBaseUrl = '/api/v1/vocal/';
        
        // Initialisation
        this.initializeSpeechRecognition();
        this.initializeUI();
        this.loadUserPreferences();
    }

    /**
     * Initialise la reconnaissance vocale
     */
    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
        } else if ('SpeechRecognition' in window) {
            this.recognition = new SpeechRecognition();
        } else {
            console.warn('Speech recognition not supported in this browser');
            return;
        }

        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = this.currentLanguage;

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUI();
            this.showStatusMessage("🎤 Je vous écoute...", 'info');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('Voice command received:', transcript);
            this.processCommand(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.updateUI();
            
            let errorMessage = "Erreur de reconnaissance vocale";
            switch(event.error) {
                case 'no-speech':
                    errorMessage = "Aucune parole détectée";
                    break;
                case 'audio-capture':
                    errorMessage = "Microphone non accessible";
                    break;
                case 'not-allowed':
                    errorMessage = "Permission microphone refusée";
                    break;
            }
            this.showStatusMessage(errorMessage, 'error');
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateUI();
        };

        this.isEnabled = true;
    }

    /**
     * Initialise l'interface utilisateur
     */
    initializeUI() {
        const vocalButton = document.getElementById('vocalAssistantButton');
        const vocalIcon = document.getElementById('vocalIcon');
        const statusBadge = document.getElementById('vocalStatusBadge');

        if (!vocalButton) return;

        // Événement clic sur le bouton
        vocalButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleListening();
        });

        // Raccourci clavier (Ctrl + .)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === '.') {
                e.preventDefault();
                this.toggleListening();
            }
        });

        // Mise à jour initiale de l'UI
        this.updateUI();
    }

    /**
     * Charge les préférences utilisateur
     */
    async loadUserPreferences() {
        try {
            // Récupérer la langue native de l'utilisateur depuis l'API
            const response = await fetch('/api/v1/vocal/user-language/');
            const data = await response.json();
            
            if (data.success && data.native_language) {
                this.currentLanguage = this.getLanguageCode(data.native_language);
            } else {
                // Fallback: utiliser la langue de l'interface
                const currentLang = document.documentElement.lang || 'fr';
                this.currentLanguage = this.getLanguageCode(currentLang);
            }
            
            if (this.recognition) {
                this.recognition.lang = this.currentLanguage;
                console.log('Voice recognition language set to:', this.currentLanguage);
            }
        } catch (error) {
            console.error('Error loading voice preferences:', error);
            // Fallback en cas d'erreur
            const currentLang = document.documentElement.lang || 'fr';
            this.currentLanguage = this.getLanguageCode(currentLang);
            if (this.recognition) {
                this.recognition.lang = this.currentLanguage;
            }
        }
    }

    /**
     * Convertit le code de langue de l'interface vers le code de reconnaissance vocale
     */
    getLanguageCode(interfaceLang) {
        if (!interfaceLang) return 'fr-FR';
        
        const cleanLang = interfaceLang.toLowerCase().trim();
        
        const langMap = {
            'fr': 'fr-FR',
            'french': 'fr-FR',
            'français': 'fr-FR',
            'en': 'en-US',
            'english': 'en-US',
            'anglais': 'en-US',
            'es': 'es-ES',
            'spanish': 'es-ES',
            'español': 'es-ES',
            'espagnol': 'es-ES',
            'de': 'de-DE',
            'german': 'de-DE',
            'deutsch': 'de-DE',
            'allemand': 'de-DE',
            'it': 'it-IT',
            'italian': 'it-IT',
            'italiano': 'it-IT',
            'italien': 'it-IT',
            'nl': 'nl-NL',
            'dutch': 'nl-NL',
            'nederlands': 'nl-NL',
            'néerlandais': 'nl-NL'
        };
        
        // Chercher correspondance exacte d'abord
        if (langMap[cleanLang]) {
            return langMap[cleanLang];
        }
        
        // Chercher par code de base (ex: 'en' depuis 'en-US')
        const baseLang = cleanLang.split('-')[0];
        if (langMap[baseLang]) {
            return langMap[baseLang];
        }
        
        return 'fr-FR'; // Fallback par défaut
    }

    /**
     * Active/désactive l'écoute
     */
    toggleListening() {
        if (!this.isEnabled) {
            this.showStatusMessage("Assistant vocal non disponible", 'error');
            return;
        }

        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    /**
     * Démarre l'écoute
     */
    startListening() {
        if (!this.recognition) {
            this.showStatusMessage("Reconnaissance vocale non supportée", 'error');
            return;
        }

        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting speech recognition:', error);
            this.showStatusMessage("Erreur lors du démarrage", 'error');
        }
    }

    /**
     * Arrête l'écoute
     */
    stopListening() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    /**
     * Traite une commande vocale
     */
    async processCommand(command) {
        this.showStatusMessage(`Commande: "${command}"`, 'info');

        try {
            const response = await fetch(`${this.apiBaseUrl}voice-command/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    command: command
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.executeAction(result);
                this.speak(result.response);
            } else {
                this.showStatusMessage(result.response || "Commande non reconnue", 'warning');
                this.speak(result.response || "Je n'ai pas compris cette commande");
            }
        } catch (error) {
            console.error('Error processing voice command:', error);
            this.showStatusMessage("Erreur de traitement", 'error');
            this.speak("Une erreur est survenue lors du traitement de votre commande");
        }
    }

    /**
     * Exécute une action basée sur la réponse du serveur
     */
    executeAction(result) {
        const { action, params } = result;

        switch (action) {
            case 'navigate':
                if (params.url) {
                    // Navigation avec transition douce
                    this.showStatusMessage(`Navigation vers ${params.page}...`, 'success');
                    setTimeout(() => {
                        window.location.href = params.url;
                    }, 500);
                }
                break;

            case 'start_lesson':
                this.showStatusMessage("Démarrage d'une leçon...", 'success');
                // Rediriger vers les leçons
                setTimeout(() => {
                    window.location.href = '/lessons/';
                }, 500);
                break;

            case 'start_quiz':
                this.showStatusMessage("Démarrage d'un quiz...", 'success');
                // Rediriger vers les quiz
                setTimeout(() => {
                    window.location.href = '/quiz/';
                }, 500);
                break;

            case 'enable_tts':
                this.enableTTS();
                break;

            case 'disable_tts':
                this.disableTTS();
                break;

            case 'toggle_theme':
                this.toggleTheme(params.theme);
                break;

            case 'show_help':
            case 'list_commands':
                this.showCommandsHelp();
                break;

            case 'get_user_info':
                this.handleUserInfoAction(params);
                break;

            case 'update_user_setting':
                this.handleUpdateSettingAction(params, result);
                break;

            case 'get_system_info':
                this.handleSystemInfoAction(params);
                break;

            case 'get_user_stats':
                this.handleUserStatsAction(params);
                break;

            // === NOUVELLES ACTIONS IA ===
            case 'ai_recommendation':
                this.handleAIRecommendationAction(params, result);
                break;

            case 'ai_study_plan':
                this.handleAIStudyPlanAction(params, result);
                break;

            case 'ai_support':
                this.handleAISupportAction(params, result);
                break;

            case 'ai_motivation':
                this.handleAIMotivationAction(params, result);
                break;

            case 'ai_activity_suggestion':
                this.handleAIActivitySuggestionAction(params, result);
                break;

            // === NOUVELLES ACTIONS FLASHCARD ===
            case 'create_flashcard':
                this.handleCreateFlashcardAction(params, result);
                break;

            case 'extract_vocabulary':
                this.handleExtractVocabularyAction(params, result);
                break;

            case 'unknown':
                if (result.learn_suggestion) {
                    this.handleUnknownCommand(result);
                }
                break;

            default:
                console.log('Action not implemented:', action);
        }
    }

    /**
     * Synthèse vocale
     */
    speak(text, language = null) {
        if (!this.synthesis) return;

        // Arrêter toute synthèse en cours
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = language || this.currentLanguage;
        utterance.rate = 0.9;
        utterance.pitch = 1.0;

        // Sélectionner une voix appropriée
        const voices = this.synthesis.getVoices();
        const voice = voices.find(v => v.lang.startsWith(utterance.lang.split('-')[0]));
        if (voice) {
            utterance.voice = voice;
        }

        this.synthesis.speak(utterance);
    }

    /**
     * Active la synthèse vocale
     */
    enableTTS() {
        localStorage.setItem('linguify_tts_enabled', 'true');
        this.showStatusMessage("Lecture vocale activée", 'success');
    }

    /**
     * Désactive la synthèse vocale
     */
    disableTTS() {
        localStorage.setItem('linguify_tts_enabled', 'false');
        this.synthesis.cancel();
        this.showStatusMessage("Lecture vocale désactivée", 'success');
    }

    /**
     * Change le thème de l'interface
     */
    toggleTheme(theme) {
        try {
            if (theme === 'dark') {
                document.documentElement.setAttribute('data-bs-theme', 'dark');
                localStorage.setItem('linguify_theme', 'dark');
                this.showStatusMessage("Mode sombre activé", 'success');
            } else {
                document.documentElement.setAttribute('data-bs-theme', 'light');
                localStorage.setItem('linguify_theme', 'light');
                this.showStatusMessage("Mode clair activé", 'success');
            }
        } catch (error) {
            console.error('Error toggling theme:', error);
            this.showStatusMessage("Erreur lors du changement de thème", 'error');
        }
    }

    /**
     * Gère les commandes inconnues avec suggestion d'apprentissage
     */
    handleUnknownCommand(result) {
        const originalCommand = result.params.original_command;
        
        this.showStatusMessage(`Commande inconnue: "${originalCommand}"`, 'warning');
        
        // Proposer d'ajouter la commande
        if (confirm(`Voulez-vous ajouter "${originalCommand}" comme nouvelle commande personnalisée ?`)) {
            this.showLearnCommandDialog(originalCommand);
        }
    }

    /**
     * Affiche un dialogue pour apprendre une nouvelle commande
     */
    showLearnCommandDialog(originalCommand) {
        // Créer un modal simple pour l'apprentissage
        const action = prompt(`Quelle action doit effectuer la commande "${originalCommand}" ?\n\nExemples:\n- navigate (pour navigation)\n- custom_action\n- macro`);
        
        if (action) {
            const url = prompt(`Si c'est une navigation, quelle URL ? (optionnel)`);
            const customResponse = prompt(`Quelle réponse vocale souhaitez-vous ?`);
            
            this.learnNewCommand(originalCommand, action, { url: url || '' }, customResponse || `Exécution de ${originalCommand}`);
        }
    }

    /**
     * Apprend une nouvelle commande
     */
    async learnNewCommand(triggerPhrase, action, params, response) {
        try {
            const result = await fetch(`${this.apiBaseUrl}learn-command/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    trigger_phrase: triggerPhrase,
                    action: action,
                    params: params,
                    response: response
                })
            });

            const data = await result.json();
            
            if (data.success) {
                this.showStatusMessage(`Commande "${triggerPhrase}" apprise avec succès !`, 'success');
                this.speak(`La commande ${triggerPhrase} a été ajoutée`);
            } else {
                this.showStatusMessage(`Erreur lors de l'apprentissage: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error learning command:', error);
            this.showStatusMessage("Erreur lors de l'apprentissage de la commande", 'error');
        }
    }

    /**
     * Affiche l'aide sur les commandes
     */
    showCommandsHelp() {
        // Récupérer les commandes dynamiquement selon la langue
        fetch(`${this.apiBaseUrl}commands/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const commands = data.commands;
                    let helpText = "Commandes disponibles :\n\n";
                    
                    Object.entries(commands).forEach(([category, commandList]) => {
                        helpText += `${category.toUpperCase()}:\n`;
                        commandList.forEach(cmd => {
                            helpText += `• "${cmd.command}" - ${cmd.description}\n`;
                        });
                        helpText += "\n";
                    });
                    
                    console.log(helpText);
                    this.showStatusMessage("Consultez la console pour la liste complète des commandes", 'info');
                } else {
                    this.showBasicHelp();
                }
            })
            .catch(() => {
                this.showBasicHelp();
            });
    }

    /**
     * Affiche l'aide de base en cas d'erreur
     */
    showBasicHelp() {
        const helpText = `
            Commandes disponibles :
            • "tableau de bord" - Retour au dashboard
            • "notes" - Accéder aux notes
            • "révision" - App révision
            • "quiz" - Quiz interactifs
            • "mode sombre" / "mode clair" - Changer le thème
            • "activer la lecture" - Synthèse vocale
            • "quelle est ma langue native" - Informations profil
            • "changer ma langue native en anglais" - Modifier paramètres
            • "aide" - Afficher cette aide
        `;
        
        this.showStatusMessage("Consultez la console pour la liste des commandes", 'info');
        console.log(helpText);
    }

    /**
     * Gère les actions d'information utilisateur
     */
    async handleUserInfoAction(params) {
        try {
            const response = await fetch(`${this.apiBaseUrl}user-info/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();
            
            if (data.success) {
                let responseText = "";
                
                if (params.info_type === 'profile_summary') {
                    const info = data.info;
                    responseText = `Votre profil : ${info.username}, langue native : ${info.native_language}, vous apprenez le ${info.target_language}, niveau ${info.language_level}`;
                } else {
                    responseText = `Votre ${params.info_type.replace('_', ' ')} est ${data.info}`;
                }
                
                this.showStatusMessage(responseText, 'success');
                this.speak(responseText);
            } else {
                this.showStatusMessage(data.error, 'error');
                this.speak("Impossible de récupérer cette information");
            }
        } catch (error) {
            console.error('Error getting user info:', error);
            this.showStatusMessage("Erreur lors de la récupération des informations", 'error');
        }
    }

    /**
     * Gère les actions de mise à jour des paramètres
     */
    async handleUpdateSettingAction(params, result) {
        // Vérifier si une confirmation est requise
        if (result.confirmation_required || (result.command && result.command.includes('confirmation_required'))) {
            const confirmed = confirm(`Êtes-vous sûr de vouloir ${result.response.toLowerCase()} ?`);
            if (!confirmed) {
                this.showStatusMessage("Action annulée", 'info');
                this.speak("Action annulée");
                return;
            }
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}update-setting/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showStatusMessage(data.message, 'success');
                this.speak(result.response);
                
                // Si la langue native a changé, recharger les commandes vocales
                if (params.setting === 'native_language') {
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                }
            } else {
                this.showStatusMessage(data.error, 'error');
                this.speak("Impossible de modifier ce paramètre");
            }
        } catch (error) {
            console.error('Error updating setting:', error);
            this.showStatusMessage("Erreur lors de la mise à jour", 'error');
        }
    }

    /**
     * Gère les actions d'information système
     */
    async handleSystemInfoAction(params) {
        try {
            const response = await fetch(`${this.apiBaseUrl}system-info/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();
            
            if (data.success && params.info_type === 'user_count') {
                const responseText = `Linguify compte actuellement ${data.info.user_count} utilisateurs, dont ${data.info.active_users} actifs`;
                this.showStatusMessage(responseText, 'success');
                this.speak(responseText);
            } else {
                this.showStatusMessage(data.error || "Information non disponible", 'error');
            }
        } catch (error) {
            console.error('Error getting system info:', error);
            this.showStatusMessage("Erreur lors de la récupération des informations système", 'error');
        }
    }

    /**
     * Gère les actions de statistiques utilisateur
     */
    async handleUserStatsAction(params) {
        try {
            const response = await fetch(`${this.apiBaseUrl}user-stats/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();
            
            if (data.success) {
                let responseText = "";
                
                if (params.stats_type === 'learning_progress') {
                    const stats = data.stats;
                    responseText = `Vous avez complété ${stats.lessons_completed} leçons, avec un niveau de progression de ${stats.progress_percentage}%`;
                } else if (params.stats_type === 'study_time') {
                    const stats = data.stats;
                    responseText = `Vous avez étudié ${stats.total_study_minutes} minutes au total cette semaine`;
                }
                
                this.showStatusMessage(responseText, 'success');
                this.speak(responseText);
            } else {
                this.showStatusMessage(data.error || "Statistiques non disponibles", 'error');
            }
        } catch (error) {
            console.error('Error getting user stats:', error);
            this.showStatusMessage("Erreur lors de la récupération des statistiques", 'error');
        }
    }

    /**
     * Met à jour l'interface utilisateur
     */
    updateUI() {
        const vocalIcon = document.getElementById('vocalIcon');
        const vocalButton = document.getElementById('vocalAssistantButton');

        if (!vocalIcon || !vocalButton) {
            console.warn('Voice assistant UI elements not found');
            return;
        }

        // Créer ou trouver le badge de statut
        let statusBadge = document.getElementById('vocalStatusBadge');
        if (!statusBadge) {
            statusBadge = document.createElement('span');
            statusBadge.id = 'vocalStatusBadge';
            vocalButton.style.position = 'relative';
            vocalButton.appendChild(statusBadge);
        }

        if (this.isListening) {
            vocalIcon.className = 'bi bi-mic-fill text-danger';
            statusBadge.style.display = 'block';
            statusBadge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
            statusBadge.innerHTML = '•';
            vocalButton.classList.add('border-danger');
        } else if (this.isEnabled) {
            vocalIcon.className = 'bi bi-mic';
            statusBadge.style.display = 'none';
            vocalButton.classList.remove('border-danger');
        } else {
            vocalIcon.className = 'bi bi-mic-mute text-muted';
            statusBadge.style.display = 'none';
            vocalButton.classList.remove('border-danger');
        }
    }

    /**
     * Affiche un message de statut
     */
    showStatusMessage(message, type = 'info') {
        // Utiliser le système de notifications existant de Linguify
        if (window.showNotification) {
            window.showNotification(message, type);
        } else {
            // Fallback avec console
            console.log(`[Voice Assistant] ${message}`);
            
            // Affichage temporaire dans le bouton
            const vocalButton = document.getElementById('vocalAssistantButton');
            if (vocalButton) {
                const originalTitle = vocalButton.title;
                vocalButton.title = message;
                setTimeout(() => {
                    vocalButton.title = originalTitle;
                }, 3000);
            }
        }
    }

    /**
     * === NOUVELLES MÉTHODES POUR L'IA ===
     */

    /**
     * Gère les recommandations IA
     */
    handleAIRecommendationAction(params, result) {
        this.showStatusMessage("💡 " + result.response, 'success');
        this.speak(result.response);
        
        // Afficher les actions suggérées si disponibles
        if (result.suggested_actions && result.suggested_actions.length > 0) {
            setTimeout(() => {
                this.showSuggestedActions(result.suggested_actions);
            }, 2000);
        }
    }

    /**
     * Gère les plans d'étude IA
     */
    handleAIStudyPlanAction(params, result) {
        this.showStatusMessage("📅 " + result.response, 'success');
        this.speak(result.response);
        
        // Afficher les détails du plan si disponibles
        if (result.plan_details) {
            const details = result.plan_details;
            setTimeout(() => {
                this.showStatusMessage(
                    `Plan détaillé: ${details.duration}, ${details.daily_time} par jour, focus sur ${details.focus}`, 
                    'info'
                );
            }, 3000);
        }
    }

    /**
     * Gère le support d'apprentissage IA
     */
    handleAISupportAction(params, result) {
        this.showStatusMessage("🤝 " + result.response, 'success');
        this.speak(result.response);
        
        // Afficher les actions suggérées pour l'aide
        if (result.suggested_actions && result.suggested_actions.length > 0) {
            setTimeout(() => {
                this.showSuggestedActions(result.suggested_actions);
            }, 2000);
        }
    }

    /**
     * Gère la motivation IA
     */
    handleAIMotivationAction(params, result) {
        this.showStatusMessage("🌟 " + result.response, 'success');
        this.speak(result.response);
        
        // Afficher le conseil motivationnel si disponible
        if (result.motivational_tip) {
            setTimeout(() => {
                this.showStatusMessage("💫 Conseil: " + result.motivational_tip, 'info');
            }, 3000);
        }
    }

    /**
     * Gère les suggestions d'activités IA
     */
    handleAIActivitySuggestionAction(params, result) {
        this.showStatusMessage("🎯 " + result.response, 'success');
        this.speak(result.response);
        
        // Afficher les activités suggérées
        if (result.suggested_actions && result.suggested_actions.length > 0) {
            setTimeout(() => {
                this.showSuggestedActions(result.suggested_actions);
            }, 2000);
        }
    }

    /**
     * === NOUVELLES MÉTHODES FLASHCARD ===
     */

    /**
     * Gère la création de flashcards via IA
     */
    async handleCreateFlashcardAction(params, result) {
        this.showStatusMessage("📚 Création de flashcard...", 'info');
        
        try {
            const response = await fetch(`${this.apiBaseUrl}create-flashcard/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();
            
            if (data.success) {
                const message = `✅ ${data.message}`;
                this.showStatusMessage(message, 'success');
                this.speak(result.response || data.message);
                
                // Actions suggérées pour continuer
                setTimeout(() => {
                    this.showSuggestedActions([
                        {'text': 'Aller réviser', 'action': 'navigate', 'params': {'url': '/revision/'}},
                        {'text': 'Créer une autre carte', 'action': 'create_flashcard', 'params': {}}
                    ]);
                }, 2000);
            } else {
                this.showStatusMessage(`❌ Erreur: ${data.error}`, 'error');
                this.speak("Impossible de créer la flashcard");
            }
        } catch (error) {
            console.error('Error creating flashcard:', error);
            this.showStatusMessage("❌ Erreur lors de la création de la flashcard", 'error');
        }
    }

    /**
     * Gère l'extraction de vocabulaire
     */
    async handleExtractVocabularyAction(params, result) {
        this.showStatusMessage("🔍 Extraction du vocabulaire...", 'info');
        
        try {
            const response = await fetch(`${this.apiBaseUrl}extract-vocabulary/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();
            
            if (data.success) {
                const message = `✅ ${data.message}`;
                this.showStatusMessage(message, 'success');
                this.speak(result.response || data.message);
                
                // Afficher les détails si disponibles
                if (data.created_cards && data.created_cards.length > 0) {
                    setTimeout(() => {
                        this.showStatusMessage(
                            `📝 Mots créés: ${data.created_cards.join(', ')}`, 
                            'info'
                        );
                    }, 3000);
                }
                
                // Actions suggérées
                setTimeout(() => {
                    this.showSuggestedActions([
                        {'text': 'Aller réviser', 'action': 'navigate', 'params': {'url': '/revision/'}},
                        {'text': 'Voir le deck', 'action': 'navigate', 'params': {'url': `/revision/deck/${data.deck_id}/`}}
                    ]);
                }, 4000);
            } else {
                this.showStatusMessage(`❌ Erreur: ${data.error}`, 'error');
                this.speak("Impossible d'extraire le vocabulaire");
            }
        } catch (error) {
            console.error('Error extracting vocabulary:', error);
            this.showStatusMessage("❌ Erreur lors de l'extraction", 'error');
        }
    }

    /**
     * Affiche des actions suggérées à l'utilisateur
     */
    showSuggestedActions(actions) {
        if (!actions || actions.length === 0) return;
        
        // Créer un message avec les actions suggérées
        let message = "Actions suggérées: ";
        actions.forEach((action, index) => {
            message += `${index + 1}) ${action.text}`;
            if (index < actions.length - 1) message += ", ";
        });
        
        this.showStatusMessage(message, 'info');
        
        // Option: créer des boutons cliquables (si vous voulez une interface plus riche)
        this.createActionButtons(actions);
    }

    /**
     * Crée des boutons d'action cliquables (optionnel)
     */
    createActionButtons(actions) {
        // Éviter de créer plusieurs séries de boutons
        const existingContainer = document.getElementById('voiceAssistantActions');
        if (existingContainer) {
            existingContainer.remove();
        }
        
        // Créer un conteneur temporaire pour les boutons d'action
        const container = document.createElement('div');
        container.id = 'voiceAssistantActions';
        container.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
            max-width: 300px;
        `;
        
        const title = document.createElement('h6');
        title.textContent = '🎯 Actions suggérées:';
        title.style.margin = '0 0 8px 0';
        container.appendChild(title);
        
        actions.forEach((action, index) => {
            const button = document.createElement('button');
            button.className = 'btn btn-sm btn-outline-primary me-2 mb-2';
            button.textContent = action.text;
            button.onclick = () => {
                this.executeAction({ action: action.action, params: action.params });
                container.remove();
            };
            container.appendChild(button);
        });
        
        // Bouton pour fermer
        const closeBtn = document.createElement('button');
        closeBtn.className = 'btn btn-sm btn-outline-secondary';
        closeBtn.textContent = '✕';
        closeBtn.style.float = 'right';
        closeBtn.onclick = () => container.remove();
        container.appendChild(closeBtn);
        
        document.body.appendChild(container);
        
        // Auto-suppression après 10 secondes
        setTimeout(() => {
            if (container.parentNode) {
                container.remove();
            }
        }, 10000);
    }

    /**
     * Récupère le token CSRF
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Fallback: chercher dans les meta tags
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.content;
        }
        
        // Fallback: chercher dans les inputs cachés
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        return '';
    }
}

// Initialisation globale
let linguifyVoiceAssistant = null;

// Initialiser l'assistant vocal quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si les éléments UI existent avant d'initialiser
    const vocalButton = document.getElementById('vocalAssistantButton');
    if (!vocalButton) {
        console.log('Voice assistant button not found, skipping initialization');
        return;
    }
    
    // Attendre que Bootstrap soit chargé et que les éléments soient prêts
    setTimeout(() => {
        try {
            linguifyVoiceAssistant = new LinguifyVoiceAssistant();
            // Rendre accessible globalement
            window.linguifyVoiceAssistant = linguifyVoiceAssistant;
            console.log('Linguify Voice Assistant initialized successfully');
        } catch (error) {
            console.error('Error initializing Voice Assistant:', error);
        }
    }, 200);
});

// Fallback d'initialisation pour le cas où DOMContentLoaded a déjà été déclenché
if (document.readyState === 'loading') {
    // DOMContentLoaded pas encore déclenché
} else {
    // DOM déjà chargé
    setTimeout(() => {
        if (!linguifyVoiceAssistant) {
            const vocalButton = document.getElementById('vocalAssistantButton');
            if (vocalButton) {
                try {
                    linguifyVoiceAssistant = new LinguifyVoiceAssistant();
                    window.linguifyVoiceAssistant = linguifyVoiceAssistant;
                    console.log('Linguify Voice Assistant initialized (fallback)');
                } catch (error) {
                    console.error('Error initializing Voice Assistant (fallback):', error);
                }
            }
        }
    }, 100);
}

// Export pour utilisation externe
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LinguifyVoiceAssistant;
}