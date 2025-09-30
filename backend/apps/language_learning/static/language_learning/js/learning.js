// Language Learning Alpine.js Components

document.addEventListener('alpine:init', () => {

    // Main Learning Dashboard Component
    Alpine.data('learningDashboard', () => ({
        // State
        selectedLanguage: 'ES',
        selectedLanguageName: 'Español',
        courseUnits: [],
        userProgress: null,
        userStreak: 0,
        activeUnit: null,
        activeUnitModules: [],
        loading: false,
        apiUrls: {},
        currentView: 'units', // 'units', 'lessons', 'unit-detail' - Start with units

        // Exercise Interface State
        showExerciseInterface: false,
        currentModule: null,
        exercises: [],
        currentExerciseIndex: 0,
        totalExercises: 0,
        earnedXP: 0,
        answered: false,
        isCorrect: false,
        selectedOption: null,
        userAnswer: '',
        audioPlaying: false,

        // Initialize
        init() {
            console.log('🎯 Learning Dashboard initialized');
            this.loadConfig();
            this.loadDashboardData();

            // Listen for module exercise start events
            window.addEventListener('start-module-exercise', (event) => {
                console.log('🎮 Starting exercise for module:', event.detail.module);
                this.startExercise(event.detail.module);
            });
        },

        // Load configuration from the page
        loadConfig() {
            const configScript = document.getElementById('language-learning-config');
            if (configScript) {
                try {
                    const config = JSON.parse(configScript.textContent);
                    this.selectedLanguage = config.selectedLanguage || 'ES';
                    this.apiUrls = config.apiUrls || {};
                    console.log('✅ Config loaded:', config);
                } catch (error) {
                    console.error('❌ Error loading config:', error);
                }
            }
        },

        // Load dashboard data from API
        async loadDashboardData() {
            this.loading = true;
            try {
                const response = await fetch(`${this.apiUrls.dashboard}?lang=${this.selectedLanguage}`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        this.selectedLanguageName = data.selected_language_name;
                        this.courseUnits = data.course_units;
                        this.userProgress = data.user_progress;
                        this.userStreak = data.user_streak;
                        console.log('✅ Dashboard data loaded:', data);

                        // Auto-load first unit for lessons view
                        if (this.currentView === 'lessons' && this.courseUnits.length > 0) {
                            this.selectUnitForLessons(this.courseUnits[0]);
                        }
                    } else {
                        console.error('❌ API error:', data.error);
                    }
                } else {
                    console.error('❌ HTTP error:', response.status);
                }
            } catch (error) {
                console.error('❌ Error loading dashboard data:', error);
            } finally {
                this.loading = false;
            }
        },

        // Language selection
        selectLanguage(langCode) {
            console.log('🌍 Language selected:', langCode);
            this.selectedLanguage = langCode;
            this.loadDashboardData();
        },

        // Load unit details
        async loadUnitDetails(unitId, switchView = true) {
            this.loading = true;
            try {
                const response = await fetch(`${this.apiUrls.unitDetail}${unitId}/`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        this.activeUnit = data.unit;
                        this.activeUnitModules = data.modules;
                        if (switchView && this.currentView === 'units') {
                            this.currentView = 'lessons';
                        }
                        console.log('✅ Unit details loaded:', data);
                    } else {
                        console.error('❌ API error:', data.error);
                    }
                } else {
                    console.error('❌ HTTP error:', response.status);
                }
            } catch (error) {
                console.error('❌ Error loading unit details:', error);
            } finally {
                this.loading = false;
            }
        },

        // Go back to units list
        goBackToUnits() {
            this.activeUnit = null;
            this.activeUnitModules = [];
            this.currentView = 'units';
        },

        // Select unit for lessons view
        selectUnitForLessons(unit) {
            this.loadUnitDetails(unit.id, false); // Don't auto-switch view
        },

        // Switch to lessons view
        switchToLessonsView() {
            this.currentView = 'lessons';
            if (!this.activeUnit && this.courseUnits.length > 0) {
                // Auto-select first unit if available
                this.selectUnitForLessons(this.courseUnits[0]);
            }
        },

        // Exercise Interface Computed Properties
        get currentExercise() {
            return this.exercises[this.currentExerciseIndex] || null;
        },

        get canSubmit() {
            if (!this.currentExercise) return false;

            switch (this.currentExercise.type) {
                case 'multiple_choice':
                    return this.selectedOption !== null;
                case 'fill_blank':
                case 'translation':
                case 'audio':
                    return this.userAnswer.trim().length > 0;
                default:
                    return false;
            }
        },

        // Exercise Interface Methods
        startExercise(module) {
            this.currentModule = module;
            this.showExerciseInterface = true;
            this.loadExercises(module.id);
        },

        async loadExercises(moduleId) {
            this.loading = true;
            try {
                const response = await fetch(`${this.apiUrls.moduleExercises}${moduleId}/exercises/`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        this.exercises = data.exercises || [];
                        this.totalExercises = this.exercises.length;
                        this.currentExerciseIndex = 0;
                        this.earnedXP = 0;
                        this.resetExerciseState();
                        console.log('✅ Exercices chargés:', data);
                    } else {
                        console.error('❌ Erreur API exercices:', data.error);
                        // Fallback vers les exercices d'exemple
                        this.exercises = this.generateSampleExercises(moduleId);
                        this.totalExercises = this.exercises.length;
                        this.currentExerciseIndex = 0;
                        this.earnedXP = 0;
                        this.resetExerciseState();
                    }
                } else {
                    console.error('❌ Erreur HTTP:', response.status);
                    // Fallback vers les exercices d'exemple
                    this.exercises = this.generateSampleExercises(moduleId);
                    this.totalExercises = this.exercises.length;
                    this.currentExerciseIndex = 0;
                    this.earnedXP = 0;
                    this.resetExerciseState();
                }
            } catch (error) {
                console.error('❌ Erreur de chargement des exercices:', error);
                // Fallback vers les exercices d'exemple
                this.exercises = this.generateSampleExercises(moduleId);
                this.totalExercises = this.exercises.length;
                this.currentExerciseIndex = 0;
                this.earnedXP = 0;
                this.resetExerciseState();
            } finally {
                this.loading = false;
            }
        },

        generateSampleExercises(moduleId) {
            // Génération d'exercices d'exemple basés sur le type de module
            const exercises = [];

            // Exercice à choix multiples
            exercises.push({
                type: 'multiple_choice',
                question: 'Comment dit-on "Bonjour" en espagnol ?',
                prompt: 'Choisissez la bonne réponse',
                options: ['Hola', 'Adiós', 'Gracias', 'Por favor'],
                correct_answer: 'Hola',
                explanation: '"Hola" est la façon la plus courante de dire bonjour en espagnol.'
            });

            // Exercice de complétion
            exercises.push({
                type: 'fill_blank',
                question: 'Complétez la phrase',
                sentence_with_blank: 'Me llamo _____ y tengo 25 ans.',
                placeholder: 'votre nom',
                correct_answer: ['María', 'Juan', 'Ana', 'Carlos'],
                explanation: 'Cette phrase signifie "Je m\'appelle _____ et j\'ai 25 ans."'
            });

            // Exercice de traduction
            exercises.push({
                type: 'translation',
                text_to_translate: 'I am learning Spanish',
                correct_answer: ['Estoy aprendiendo español', 'Aprendo español'],
                explanation: 'Cette phrase peut se traduire de deux façons en espagnol selon le contexte.'
            });

            // Exercice audio (simulé)
            exercises.push({
                type: 'audio',
                audio_url: '/static/audio/hola.mp3',
                correct_answer: ['hola', 'Hola'],
                explanation: 'Vous avez entendu le mot "hola" qui signifie "bonjour".'
            });

            return exercises;
        },

        selectOption(index) {
            if (this.answered) return;
            this.selectedOption = index;
        },

        getOptionClass(index) {
            if (!this.answered) {
                return this.selectedOption === index ? 'option-selected' : '';
            }

            const isCorrectOption = this.currentExercise.options[index] === this.currentExercise.correct_answer;
            const isSelected = this.selectedOption === index;

            if (isCorrectOption) return 'option-correct';
            if (isSelected && !isCorrectOption) return 'option-incorrect';
            return 'option-disabled';
        },

        checkAnswer() {
            if (this.answered) return;

            let userResponse = '';
            let correct = false;

            switch (this.currentExercise.type) {
                case 'multiple_choice':
                    userResponse = this.currentExercise.options[this.selectedOption];
                    correct = userResponse === this.currentExercise.correct_answer;
                    break;

                case 'fill_blank':
                case 'translation':
                case 'audio':
                    userResponse = this.userAnswer.trim().toLowerCase();
                    const correctAnswers = Array.isArray(this.currentExercise.correct_answer)
                        ? this.currentExercise.correct_answer
                        : [this.currentExercise.correct_answer];

                    correct = correctAnswers.some(answer =>
                        answer.toLowerCase() === userResponse
                    );
                    break;
            }

            this.isCorrect = correct;
            this.answered = true;

            if (correct) {
                this.earnedXP += 20;
            }

            console.log('Exercise result:', { correct, userResponse, earnedXP: this.earnedXP });
        },

        nextExercise() {
            if (this.currentExerciseIndex < this.totalExercises - 1) {
                this.currentExerciseIndex++;
                this.resetExerciseState();
            } else {
                this.completeModule();
            }
        },

        resetExerciseState() {
            this.answered = false;
            this.isCorrect = false;
            this.selectedOption = null;
            this.userAnswer = '';
            this.audioPlaying = false;
        },

        async completeModule() {
            const score = Math.round((this.earnedXP / (this.totalExercises * 20)) * 100);

            console.log('Module completed!', {
                moduleId: this.currentModule.id,
                totalXP: this.earnedXP,
                score: score
            });

            try {
                const response = await fetch(`${this.apiUrls.completeModule}${this.currentModule.id}/complete/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                    },
                    body: JSON.stringify({
                        score: score
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        alert(`Module terminé ! Vous avez gagné ${data.rewards.xp_earned} XP !`);
                        console.log('✅ Module complété avec succès:', data);
                    } else {
                        alert(`Module terminé ! Vous avez gagné ${this.earnedXP} XP !`);
                        console.error('❌ Erreur lors de la completion:', data.error);
                    }
                } else {
                    alert(`Module terminé ! Vous avez gagné ${this.earnedXP} XP !`);
                    console.error('❌ Erreur HTTP completion:', response.status);
                }
            } catch (error) {
                alert(`Module terminé ! Vous avez gagné ${this.earnedXP} XP !`);
                console.error('❌ Erreur de completion du module:', error);
            }

            this.closeExercise();
        },

        closeExercise() {
            this.showExerciseInterface = false;
            this.currentModule = null;
            this.exercises = [];
            this.currentExerciseIndex = 0;
            this.totalExercises = 0;
            this.earnedXP = 0;
            this.resetExerciseState();
        },

        playAudio() {
            this.audioPlaying = true;
            setTimeout(() => {
                this.audioPlaying = false;
            }, 2000);
            console.log('Playing audio:', this.currentExercise?.audio_url);
        },

        // Get language flag emoji
        getLanguageFlag(langCode) {
            const flags = {
                'EN': '🇬🇧',
                'FR': '🇫🇷',
                'ES': '🇪🇸',
                'DE': '🇩🇪',
                'IT': '🇮🇹'
            };
            return flags[langCode] || '🌍';
        },

        // Get streak icon based on count
        getStreakIcon(streak) {
            if (streak >= 30) return '🔥';
            if (streak >= 7) return '⚡';
            if (streak >= 3) return '✨';
            return '🌟';
        }
    }));

    // Unit Card Component
    Alpine.data('unitCard', (unit, dashboard) => ({
        unit: unit,

        // Get progress bar width
        get progressWidth() {
            return `${this.unit.progress_percentage || 0}%`;
        },

        // Get progress bar class
        get progressClass() {
            const percentage = this.unit.progress_percentage || 0;
            if (percentage === 100) return 'bg-success';
            if (percentage >= 50) return 'bg-primary';
            if (percentage > 0) return 'bg-warning';
            return 'bg-secondary';
        },

        // Handle unit click
        selectUnit() {
            console.log('📚 Unit selected:', this.unit.id);
            dashboard.loadUnitDetails(this.unit.id);
        }
    }));


    // Module Card Component
    Alpine.data('moduleCard', (module) => ({
        module: module,

        // Get module type badge class
        get badgeClass() {
            const type = this.module.module_type;
            const classes = {
                'vocabulary': 'badge bg-info',
                'grammar': 'badge bg-warning',
                'listening': 'badge bg-success',
                'speaking': 'badge bg-primary',
                'reading': 'badge bg-secondary',
                'writing': 'badge bg-dark',
                'culture': 'badge bg-light text-dark',
                'review': 'badge bg-outline-primary'
            };
            return classes[type] || 'badge bg-light text-dark';
        },

        // Handle module click
        async selectModule() {
            console.log('🔘 Button clicked! Module:', this.module.title); // Debug log

            if (this.module.is_unlocked) {
                console.log('📖 Module selected:', this.module.id);

                // Dispatch event to trigger exercise start
                window.dispatchEvent(new CustomEvent('start-module-exercise', {
                    detail: { module: this.module }
                }));
            } else {
                alert('Ce module est verrouillé. Complétez les modules précédents pour y accéder.');
            }
        }
    }));

    // Removed old components - all functionality now in main learningDashboard
});

// HTMX Configuration and Event Handlers
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Language Learning App loaded with HTMX + Alpine.js');

    // HTMX event handlers
    document.body.addEventListener('htmx:configRequest', function(evt) {
        // Add CSRF token to all HTMX requests
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            evt.detail.headers['X-CSRFToken'] = csrfToken;
        }
    });

    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        console.log('🔄 HTMX request starting:', evt.detail.xhr.url);
    });

    document.body.addEventListener('htmx:afterRequest', function(evt) {
        console.log('✅ HTMX request completed:', evt.detail.xhr.status);

        // Handle errors
        if (evt.detail.xhr.status >= 400) {
            console.error('❌ HTMX request failed:', evt.detail.xhr.status);
        }
    });

    document.body.addEventListener('htmx:afterSwap', function(evt) {
        console.log('🔄 HTMX content swapped');

        // Reinitialize Alpine components if needed
        if (window.Alpine) {
            Alpine.initTree(evt.target);
        }
    });
});

// Utility functions
window.LearningUtils = {
    // Format duration
    formatDuration(minutes) {
        if (minutes < 60) {
            return `${minutes} min`;
        }
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours}h ${mins}min`;
    },

    // Format XP
    formatXP(xp) {
        if (xp >= 1000) {
            return `${(xp / 1000).toFixed(1)}k XP`;
        }
        return `${xp} XP`;
    },

    // Show notification
    showNotification(message, type = 'success') {
        // Simple notification - could be enhanced with a toast library
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
};