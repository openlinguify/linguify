/**
 * Interactive Exercise Engine
 * Handles all exercise types with modern UX patterns
 */

class InteractiveExerciseEngine {
    constructor(exerciseData) {
        this.data = exerciseData;
        this.state = {
            currentQuestionIndex: 0,
            selectedAnswer: null,
            isAnswered: false,
            score: 0,
            startTime: Date.now(),
            questionStartTime: Date.now(),
            hintsUsed: 0,
            answers: []
        };
        
        this.elements = {};
        this.audioContext = null;
        this.mediaRecorder = null;
        this.isRecording = false;
        
        // Bind methods
        this.checkAnswer = this.checkAnswer.bind(this);
        this.nextQuestion = this.nextQuestion.bind(this);
        this.selectAnswer = this.selectAnswer.bind(this);
        this.skipQuestion = this.skipQuestion.bind(this);
        this.showHint = this.showHint.bind(this);
    }
    
    /**
     * Initialize the exercise engine
     */
    init() {
        console.log('🎮 Initializing Exercise Engine', this.data);
        
        this.initializeElements();
        this.setupEventListeners();
        this.loadCurrentQuestion();
        this.updateProgress();
        
        // Initialize audio context for speaking exercises
        if (this.data.type === 'speaking') {
            this.initializeAudio();
        }
        
        console.log('✅ Exercise Engine initialized');
    }
    
    /**
     * Cache DOM elements
     */
    initializeElements() {
        this.elements = {
            content: document.getElementById('exerciseContent'),
            progress: document.getElementById('exerciseProgress'),
            progressText: document.getElementById('progressText'),
            checkBtn: document.getElementById('checkBtn'),
            continueBtn: document.getElementById('continueBtn'),
            skipBtn: document.getElementById('skipBtn'),
            hintBtn: document.getElementById('hintBtn'),
            resultsModal: document.getElementById('resultsModal'),
            resultsContent: document.getElementById('resultsContent')
        };
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Global functions for template access
        window.checkAnswer = this.checkAnswer;
        window.nextQuestion = this.nextQuestion;
        window.selectAnswer = this.selectAnswer;
        window.skipQuestion = this.skipQuestion;
        window.showHint = this.showHint;
        window.playAudio = this.playAudio.bind(this);
        window.playReference = this.playReference.bind(this);
        window.toggleRecording = this.toggleRecording.bind(this);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }
    
    /**
     * Load and render current question
     */
    loadCurrentQuestion() {
        const question = this.getCurrentQuestion();
        if (!question) {
            this.showResults();
            return;
        }
        
        this.state.questionStartTime = Date.now();
        this.state.selectedAnswer = null;
        this.state.isAnswered = false;
        
        // Reset button states
        this.elements.checkBtn.disabled = true;
        this.elements.checkBtn.style.display = 'block';
        this.elements.continueBtn.style.display = 'none';
        
        // Render question based on type
        switch (this.data.type) {
            case 'vocabulary':
            case 'multiple_choice':
                this.renderVocabularyQuestion(question);
                break;
            case 'matching':
                this.renderMatchingQuestion(question);
                break;
            case 'fill_blank':
                this.renderFillBlankQuestion(question);
                break;
            case 'speaking':
                this.renderSpeakingQuestion(question);
                break;
            default:
                console.error('Unknown exercise type:', this.data.type);
        }
        
        // Add entrance animation
        this.elements.content.classList.add('fade-in-up');
        setTimeout(() => {
            this.elements.content.classList.remove('fade-in-up');
        }, 600);
    }
    
    /**
     * Render vocabulary/multiple choice question
     */
    renderVocabularyQuestion(question) {
        this.elements.content.innerHTML = `
            <div class="vocabulary-exercise">
                <div class="question-header">
                    <h2 class="question-title">${question.text}</h2>
                    ${question.audio ? `
                        <button class="btn btn-audio" onclick="playAudio('${question.audio}')">
                            <i class="bi bi-volume-up"></i>
                            Écouter
                        </button>
                    ` : ''}
                </div>
                
                ${question.image ? `
                    <div class="question-image">
                        <img src="${question.image}" alt="Question image" />
                    </div>
                ` : ''}
                
                <div class="answer-options">
                    ${question.options.map((option, index) => `
                        <button class="answer-option" data-answer="${option.id}" onclick="selectAnswer(this, ${option.id})">
                            <span class="option-text">${option.text}</span>
                            ${option.image ? `
                                <img src="${option.image}" alt="${option.text}" class="option-image" />
                            ` : ''}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    /**
     * Render matching question
     */
    renderMatchingQuestion(question) {
        this.elements.content.innerHTML = `
            <div class="matching-exercise">
                <div class="question-header">
                    <h2 class="question-title">Associez les mots à leur traduction</h2>
                    <p class="question-instruction">Cliquez pour sélectionner, puis cliquez sur la traduction correspondante</p>
                </div>
                
                <div class="matching-area">
                    <div class="words-column">
                        <h3>Mots français</h3>
                        <div class="words-list" id="wordsList">
                            ${question.pairs.map((pair, index) => `
                                <div class="word-item" data-word-id="${pair.id}" onclick="selectWord(this, ${pair.id})">
                                    ${pair.word}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="connections-area" id="connectionsArea">
                        <svg width="60" height="100%">
                            <!-- Connection lines will be drawn here -->
                        </svg>
                    </div>
                    
                    <div class="translations-column">
                        <h3>Traductions</h3>
                        <div class="translations-list" id="translationsList">
                            ${this.shuffleArray([...question.pairs]).map((pair, index) => `
                                <div class="translation-item" data-translation-id="${pair.id}" onclick="selectTranslation(this, ${pair.id})">
                                    ${pair.translation}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Initialize matching state
        this.matchingState = {
            selectedWord: null,
            selectedTranslation: null,
            matches: [],
            pairs: question.pairs
        };
        
        // Setup matching functions
        window.selectWord = this.selectWord.bind(this);
        window.selectTranslation = this.selectTranslation.bind(this);
    }
    
    /**
     * Render fill blank question
     */
    renderFillBlankQuestion(question) {
        const sentence = this.createSentenceWithBlanks(question.sentence, question.blanks);
        const shuffledWords = this.shuffleArray([...question.options]);
        
        this.elements.content.innerHTML = `
            <div class="fill-blank-exercise">
                <div class="question-header">
                    <h2 class="question-title">Complétez la phrase</h2>
                    ${question.audio ? `
                        <button class="btn btn-audio" onclick="playAudio('${question.audio}')">
                            <i class="bi bi-volume-up"></i>
                            Écouter
                        </button>
                    ` : ''}
                </div>
                
                <div class="sentence-container">
                    <div class="sentence" id="sentenceContainer">
                        ${sentence}
                    </div>
                </div>
                
                <div class="word-bank" id="wordBank">
                    ${shuffledWords.map((word, index) => `
                        <button class="word-option" data-word="${word}" onclick="selectWord(this, '${word}')">
                            ${word}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Initialize fill blank state
        this.fillBlankState = {
            blanks: question.blanks,
            filledBlanks: {},
            correctAnswers: question.correct_answers
        };
        
        window.selectWord = this.selectWordForBlank.bind(this);
        window.selectBlank = this.selectBlank.bind(this);
    }
    
    /**
     * Render speaking question
     */
    renderSpeakingQuestion(question) {
        this.elements.content.innerHTML = `
            <div class="speaking-exercise">
                <div class="question-header">
                    <h2 class="question-title">Répétez la phrase</h2>
                    <p class="question-instruction">Cliquez sur le microphone et répétez clairement</p>
                </div>
                
                <div class="reference-audio">
                    <div class="audio-player">
                        <button class="btn btn-audio btn-lg" onclick="playReference()">
                            <i class="bi bi-play-circle"></i>
                            Écouter l'exemple
                        </button>
                        <div class="audio-waveform" id="referenceWaveform">
                            🎵 Audio de référence
                        </div>
                    </div>
                    <div class="reference-text">${question.text}</div>
                </div>
                
                <div class="recording-area">
                    <button class="btn btn-record" id="recordBtn" onclick="toggleRecording()">
                        <i class="bi bi-mic"></i>
                        <span>Appuyer pour parler</span>
                    </button>
                    <div class="recording-status" id="recordingStatus">Prêt à enregistrer</div>
                    <div class="audio-waveform" id="userWaveform">Votre enregistrement apparaîtra ici</div>
                </div>
                
                <div class="pronunciation-feedback" id="pronunciationFeedback" style="display: none;">
                    <!-- Pronunciation analysis will appear here -->
                </div>
            </div>
        `;
        
        this.speakingState = {
            referenceAudio: question.audio,
            referenceText: question.text,
            userRecording: null,
            isRecorded: false
        };
    }
    
    /**
     * Handle answer selection
     */
    selectAnswer(element, answerId) {
        if (this.state.isAnswered) return;
        
        // Remove previous selection
        document.querySelectorAll('.answer-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        
        // Add selection
        element.classList.add('selected');
        this.state.selectedAnswer = answerId;
        
        // Enable check button
        this.elements.checkBtn.disabled = false;
        
        // Add selection feedback
        element.style.transform = 'scale(0.95)';
        setTimeout(() => {
            element.style.transform = '';
        }, 150);
    }
    
    /**
     * Check the current answer
     */
    checkAnswer() {
        if (this.state.isAnswered) return;
        
        const question = this.getCurrentQuestion();
        let isCorrect = false;
        
        switch (this.data.type) {
            case 'vocabulary':
            case 'multiple_choice':
                isCorrect = this.checkVocabularyAnswer(question);
                break;
            case 'matching':
                isCorrect = this.checkMatchingAnswer(question);
                break;
            case 'fill_blank':
                isCorrect = this.checkFillBlankAnswer(question);
                break;
            case 'speaking':
                isCorrect = this.checkSpeakingAnswer(question);
                break;
        }
        
        this.state.isAnswered = true;
        
        // Record answer
        const questionTime = Date.now() - this.state.questionStartTime;
        this.state.answers.push({
            questionId: question.id,
            answer: this.state.selectedAnswer,
            isCorrect: isCorrect,
            timeSpent: questionTime,
            hintsUsed: this.state.hintsUsed
        });
        
        if (isCorrect) {
            this.state.score++;
        }
        
        // Show feedback
        this.showAnswerFeedback(isCorrect);
        
        // Update button states
        this.elements.checkBtn.style.display = 'none';
        this.elements.continueBtn.style.display = 'block';
        
        // Auto-continue after delay for correct answers
        if (isCorrect) {
            setTimeout(() => {
                this.nextQuestion();
            }, 1500);
        }
    }
    
    /**
     * Check vocabulary answer
     */
    checkVocabularyAnswer(question) {
        const isCorrect = this.state.selectedAnswer === question.correct_answer;
        
        // Visual feedback
        document.querySelectorAll('.answer-option').forEach(option => {
            const answerId = parseInt(option.dataset.answer);
            if (answerId === question.correct_answer) {
                option.classList.add('correct');
            } else if (answerId === this.state.selectedAnswer && !isCorrect) {
                option.classList.add('incorrect');
            }
        });
        
        return isCorrect;
    }
    
    /**
     * Show answer feedback
     */
    showAnswerFeedback(isCorrect) {
        // Create feedback notification
        const feedback = document.createElement('div');
        feedback.className = `answer-feedback ${isCorrect ? 'correct' : 'incorrect'}`;
        feedback.innerHTML = `
            <div class="feedback-content">
                <i class="bi bi-${isCorrect ? 'check-circle' : 'x-circle'}"></i>
                <span>${isCorrect ? 'Correct !' : 'Incorrect'}</span>
            </div>
        `;
        
        document.body.appendChild(feedback);
        
        // Animate in
        setTimeout(() => feedback.classList.add('show'), 10);
        
        // Remove after delay
        setTimeout(() => {
            feedback.classList.remove('show');
            setTimeout(() => feedback.remove(), 300);
        }, 2000);
        
        // Play sound effect
        this.playFeedbackSound(isCorrect);
    }
    
    /**
     * Move to next question
     */
    nextQuestion() {
        this.state.currentQuestionIndex++;
        this.updateProgress();
        
        if (this.state.currentQuestionIndex >= this.data.questions.length) {
            this.showResults();
        } else {
            this.loadCurrentQuestion();
        }
    }
    
    /**
     * Skip current question
     */
    skipQuestion() {
        if (confirm('Êtes-vous sûr de vouloir passer cette question ?')) {
            // Record as incorrect
            this.state.answers.push({
                questionId: this.getCurrentQuestion().id,
                answer: null,
                isCorrect: false,
                timeSpent: Date.now() - this.state.questionStartTime,
                skipped: true
            });
            
            this.nextQuestion();
        }
    }
    
    /**
     * Show hint for current question
     */
    showHint() {
        const question = this.getCurrentQuestion();
        if (!question.hint) {
            this.showNotification('Aucun indice disponible pour cette question', 'info');
            return;
        }
        
        this.state.hintsUsed++;
        
        // Create hint modal
        const hintModal = document.createElement('div');
        hintModal.className = 'hint-modal';
        hintModal.innerHTML = `
            <div class="hint-content">
                <div class="hint-header">
                    <h4><i class="bi bi-lightbulb"></i> Indice</h4>
                    <button class="btn-close" onclick="this.parentElement.parentElement.parentElement.remove()">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
                <div class="hint-body">
                    ${question.hint}
                </div>
            </div>
        `;
        
        document.body.appendChild(hintModal);
        setTimeout(() => hintModal.classList.add('show'), 10);
    }
    
    /**
     * Update progress display
     */
    updateProgress() {
        const progress = (this.state.currentQuestionIndex / this.data.questions.length) * 100;
        this.elements.progress.style.width = `${progress}%`;
        this.elements.progressText.textContent = `${this.state.currentQuestionIndex}/${this.data.questions.length}`;
    }
    
    /**
     * Show final results
     */
    showResults() {
        const totalTime = Date.now() - this.state.startTime;
        const accuracy = Math.round((this.state.score / this.data.questions.length) * 100);
        const averageTime = Math.round(totalTime / this.data.questions.length / 1000);
        
        this.elements.resultsContent.innerHTML = `
            <div class="results-summary">
                <div class="score-circle">
                    ${this.createProgressRing(accuracy)}
                    <div class="score-value">${accuracy}%</div>
                </div>
                <h3>Exercice terminé !</h3>
                <p>Vous avez obtenu ${this.state.score} bonnes réponses sur ${this.data.questions.length}</p>
                
                <div class="results-stats">
                    <div class="stat-item">
                        <div class="stat-value">${this.state.score}</div>
                        <div class="stat-label">Bonnes réponses</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${averageTime}s</div>
                        <div class="stat-label">Temps moyen</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.state.hintsUsed}</div>
                        <div class="stat-label">Indices utilisés</div>
                    </div>
                </div>
                
                <div class="xp-reward">
                    <h4>+${this.calculateXP()} XP gagnés !</h4>
                </div>
            </div>
        `;
        
        // Show modal
        const modal = new bootstrap.Modal(this.elements.resultsModal);
        modal.show();
        
        // Send results to server
        this.saveResults();
    }
    
    /**
     * Calculate XP based on performance
     */
    calculateXP() {
        const baseXP = this.data.points || 10;
        const accuracyBonus = Math.round((this.state.score / this.data.questions.length) * 0.5 * baseXP);
        const speedBonus = this.state.hintsUsed === 0 ? Math.round(baseXP * 0.2) : 0;
        
        return baseXP + accuracyBonus + speedBonus;
    }
    
    /**
     * Get current question
     */
    getCurrentQuestion() {
        return this.data.questions[this.state.currentQuestionIndex];
    }
    
    /**
     * Handle keyboard input
     */
    handleKeyboard(e) {
        if (this.state.isAnswered) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.nextQuestion();
            }
            return;
        }
        
        // Number keys for multiple choice
        if (this.data.type === 'vocabulary' || this.data.type === 'multiple_choice') {
            const num = parseInt(e.key);
            if (num >= 1 && num <= 4) {
                const options = document.querySelectorAll('.answer-option');
                if (options[num - 1]) {
                    const answerId = parseInt(options[num - 1].dataset.answer);
                    this.selectAnswer(options[num - 1], answerId);
                }
            }
        }
        
        // Enter to check answer
        if (e.key === 'Enter' && !this.elements.checkBtn.disabled) {
            e.preventDefault();
            this.checkAnswer();
        }
        
        // H for hint
        if (e.key === 'h' || e.key === 'H') {
            e.preventDefault();
            this.showHint();
        }
    }
    
    /**
     * Utility functions
     */
    shuffleArray(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }
    
    createProgressRing(percentage) {
        const radius = 40;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (percentage / 100) * circumference;
        
        return `
            <svg class="progress-ring" width="100" height="100">
                <circle cx="50" cy="50" r="${radius}" stroke="#e2e8f0" stroke-width="8" fill="transparent"></circle>
                <circle cx="50" cy="50" r="${radius}" stroke="url(#progressGradient)" stroke-width="8" 
                        fill="transparent" stroke-dasharray="${circumference}" 
                        stroke-dashoffset="${offset}" stroke-linecap="round"></circle>
            </svg>
        `;
    }
    
    createSentenceWithBlanks(sentence, blanks) {
        let result = sentence;
        blanks.forEach((blank, index) => {
            result = result.replace(`[${blank.placeholder}]`, 
                `<span class="blank-space" data-blank-id="${index}" onclick="selectBlank(this, ${index})"></span>`
            );
        });
        return result;
    }
    
    playAudio(audioUrl) {
        if (audioUrl) {
            const audio = new Audio(audioUrl);
            audio.play().catch(e => console.warn('Could not play audio:', e));
        }
    }
    
    playFeedbackSound(isCorrect) {
        // Play appropriate sound effect
        const frequency = isCorrect ? 800 : 400;
        const duration = 200;
        
        if (this.audioContext) {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration / 1000);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration / 1000);
        }
    }
    
    showNotification(message, type = 'info') {
        // Reuse notification system from main app
        if (window.LearningApp) {
            window.LearningApp.showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    /**
     * Save results to server
     */
    async saveResults() {
        try {
            const resultsData = {
                exercise_id: this.data.id,
                score: this.state.score,
                total_questions: this.data.questions.length,
                time_spent: Date.now() - this.state.startTime,
                answers: this.state.answers,
                hints_used: this.state.hintsUsed
            };
            
            const response = await fetch('/api/v1/course/exercises/results/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
                },
                body: JSON.stringify(resultsData)
            });
            
            if (response.ok) {
                console.log('✅ Results saved successfully');
            } else {
                console.warn('⚠️ Could not save results');
            }
        } catch (error) {
            console.error('❌ Error saving results:', error);
        }
    }
    
    /**
     * Initialize audio context for speaking exercises
     */
    initializeAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (error) {
            console.warn('⚠️ Could not initialize audio context:', error);
        }
    }
}