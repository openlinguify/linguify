/**
 * Learning App - Main JavaScript
 */

class LearningApp {
    constructor(config) {
        this.config = config;
        this.currentChapter = null;
        this.currentLesson = null;
        this.init();
    }

    init() {
        console.log('🎓 Learning App initialized');
        this.bindEvents();
        this.animateProgress();
    }

    bindEvents() {
        // Language selector
        const langSelector = document.querySelector('.language-selector');
        if (langSelector) {
            langSelector.addEventListener('click', () => this.toggleLanguageMenu());
        }

        // Close modals on ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeLesson();
            }
        });
    }

    animateProgress() {
        // Animate circular progress on load
        const circles = document.querySelectorAll('.circular-progress');
        circles.forEach(circle => {
            const progress = circle.dataset.progress || 0;
            const progressBar = circle.querySelector('.progress-bar');
            if (progressBar) {
                setTimeout(() => {
                    progressBar.style.strokeDasharray = `${progress * 3.14} 314`;
                }, 100);
            }
        });

        // Animate progress bars
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    }

    selectChapter(chapterId) {
        console.log('📘 Selecting chapter:', chapterId);
        
        // Fetch chapter details
        fetch(`${this.config.apiUrl}chapters/${chapterId}/`)
            .then(response => response.json())
            .then(data => {
                this.currentChapter = data;
                this.showChapterDetails(data);
            })
            .catch(error => {
                console.error('Error loading chapter:', error);
                this.showError('Impossible de charger le chapitre');
            });
    }

    showChapterDetails(chapter) {
        // Create chapter detail view
        const content = `
            <div class="chapter-detail-view">
                <div class="chapter-detail-header">
                    <button class="btn-back" onclick="window.location.reload()">
                        <i class="bi bi-arrow-left"></i> Retour
                    </button>
                    <h2>${chapter.title}</h2>
                    <p>${chapter.description}</p>
                </div>
                
                <div class="lessons-list">
                    ${chapter.lessons.map((lesson, index) => `
                        <div class="lesson-item ${lesson.is_completed ? 'completed' : ''}" 
                             onclick="learningApp.loadLesson(${lesson.id})">
                            <div class="lesson-number">${index + 1}</div>
                            <div class="lesson-info">
                                <h4>${lesson.title}</h4>
                                <p>${lesson.description || ''}</p>
                                <div class="lesson-meta">
                                    <span><i class="bi bi-clock"></i> ${lesson.duration || 10} min</span>
                                    <span><i class="bi bi-star"></i> ${lesson.points || 10} pts</span>
                                </div>
                            </div>
                            <div class="lesson-status">
                                ${lesson.is_completed ? 
                                    '<i class="bi bi-check-circle-fill text-success"></i>' : 
                                    '<i class="bi bi-play-circle"></i>'}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Show in modal
        const modal = new bootstrap.Modal(document.getElementById('lessonModal'));
        document.getElementById('lessonContent').innerHTML = content;
        modal.show();
    }

    loadLesson(lessonId) {
        console.log('📝 Loading lesson:', lessonId);
        
        // Show loading state
        this.showLoading();
        
        // Fetch lesson content
        fetch(`${this.config.apiUrl}lessons/${lessonId}/`)
            .then(response => response.json())
            .then(data => {
                this.currentLesson = data;
                this.showLesson(data);
            })
            .catch(error => {
                console.error('Error loading lesson:', error);
                this.showError('Impossible de charger la leçon');
            });
    }

    showLesson(lesson) {
        let content = '';
        
        // Render based on lesson type
        switch(lesson.type) {
            case 'vocabulary':
                content = this.renderVocabularyLesson(lesson);
                break;
            case 'grammar':
                content = this.renderGrammarLesson(lesson);
                break;
            case 'exercise':
                content = this.renderExerciseLesson(lesson);
                break;
            default:
                content = this.renderDefaultLesson(lesson);
        }

        // Show in modal
        document.getElementById('lessonContent').innerHTML = content;
        
        // Initialize lesson interactions
        this.initLessonInteractions();
    }

    renderVocabularyLesson(lesson) {
        this.currentCardIndex = 0;
        this.totalCards = lesson.vocabulary.length;
        
        return `
            <div class="lesson-container vocabulary-lesson">
                <div class="lesson-header">
                    <h2>${lesson.title}</h2>
                    <div class="lesson-progress">
                        <span class="progress-text">1 / ${this.totalCards}</span>
                        <div class="progress">
                            <div class="progress-bar" id="lessonProgress" style="width: ${100/this.totalCards}%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="vocabulary-slider">
                    <div class="vocabulary-cards" id="vocabularyCards">
                        ${lesson.vocabulary.map((word, index) => `
                            <div class="vocab-card ${index === 0 ? 'active' : ''}" data-index="${index}">
                                <div class="vocab-front">
                                    <h3>${word.word}</h3>
                                    ${word.pronunciation ? `<p class="pronunciation">[${word.pronunciation}]</p>` : ''}
                                    ${word.image_url ? `<img src="${word.image_url}" alt="${word.word}" class="vocab-image">` : ''}
                                </div>
                                <div class="vocab-back">
                                    <h4>${word.translation}</h4>
                                    ${word.example ? `
                                        <div class="example-section">
                                            <p class="example">"${word.example}"</p>
                                            ${word.example_translation ? `<p class="example-translation">${word.example_translation}</p>` : ''}
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="lesson-controls">
                    <button class="btn btn-secondary" onclick="learningApp.previousCard()" id="prevBtn" disabled>
                        <i class="bi bi-arrow-left"></i> Précédent
                    </button>
                    <span class="card-counter">${this.currentCardIndex + 1} / ${this.totalCards}</span>
                    <button class="btn btn-primary" onclick="learningApp.nextCard()" id="nextBtn">
                        Suivant <i class="bi bi-arrow-right"></i>
                    </button>
                </div>
                
                <div class="lesson-tip">
                    <i class="bi bi-lightbulb"></i>
                    Cliquez sur la carte pour voir la traduction
                </div>
            </div>
        `;
    }

    renderGrammarLesson(lesson) {
        return `
            <div class="lesson-container grammar-lesson">
                <div class="lesson-header">
                    <h2>${lesson.title}</h2>
                </div>
                
                <div class="grammar-content">
                    <div class="grammar-explanation">
                        ${lesson.content}
                    </div>
                    
                    ${lesson.examples ? `
                        <div class="grammar-examples">
                            <h3>Exemples</h3>
                            ${lesson.examples.map(ex => `
                                <div class="example-item">
                                    <p class="example-text">${ex.text}</p>
                                    <p class="example-translation">${ex.translation}</p>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
                
                <div class="lesson-controls">
                    <button class="btn btn-primary" onclick="learningApp.completeLesson()">
                        Terminer la leçon <i class="bi bi-check"></i>
                    </button>
                </div>
            </div>
        `;
    }

    renderExerciseLesson(lesson) {
        // Render based on exercise type
        if (lesson.content_type === 'matching') {
            return this.renderMatchingExercise(lesson);
        } else if (lesson.content_type === 'test_recap') {
            return this.renderTestRecap(lesson);
        }
        
        return `
            <div class="lesson-container exercise-lesson">
                <div class="lesson-header">
                    <h2>${lesson.title}</h2>
                    <div class="score-display">
                        <i class="bi bi-star-fill"></i>
                        <span id="currentScore">0</span> / ${lesson.totalPoints || 100}
                    </div>
                </div>
                
                <div class="exercise-content" id="exerciseContent">
                    <!-- Exercise questions will be loaded here -->
                </div>
                
                <div class="lesson-controls">
                    <button class="btn btn-primary" id="checkAnswer" onclick="learningApp.checkAnswer()">
                        Vérifier
                    </button>
                </div>
            </div>
        `;
    }
    
    renderMatchingExercise(lesson) {
        this.matchingPairs = lesson.matching_pairs || [];
        this.userMatches = {};
        
        // Shuffle right items for the exercise
        const rightItems = this.matchingPairs.map(p => ({id: p.id, text: p.right_item}));
        this.shuffledRight = this.shuffleArray([...rightItems]);
        
        return `
            <div class="lesson-container matching-exercise">
                <div class="lesson-header">
                    <h2>${lesson.title}</h2>
                    <p class="instructions">${lesson.instructions || 'Associez les éléments correspondants'}</p>
                </div>
                
                <div class="matching-container">
                    <div class="matching-column left-column">
                        <h4>Français</h4>
                        ${this.matchingPairs.map(pair => `
                            <div class="matching-item left-item" data-id="${pair.id}">
                                <span>${pair.left_item}</span>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="matching-lines" id="matchingLines">
                        <svg width="100%" height="100%"></svg>
                    </div>
                    
                    <div class="matching-column right-column">
                        <h4>Traduction</h4>
                        ${this.shuffledRight.map((item, index) => `
                            <div class="matching-item right-item" 
                                 data-id="${item.id}" 
                                 data-index="${index}"
                                 ondrop="learningApp.handleDrop(event)"
                                 ondragover="learningApp.allowDrop(event)">
                                <span draggable="true" 
                                      ondragstart="learningApp.handleDragStart(event, '${item.id}')"
                                      class="draggable-item">
                                    ${item.text}
                                </span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="lesson-controls">
                    <button class="btn btn-secondary" onclick="learningApp.resetMatching()">
                        <i class="bi bi-arrow-clockwise"></i> Réinitialiser
                    </button>
                    <button class="btn btn-primary" onclick="learningApp.checkMatching()">
                        <i class="bi bi-check"></i> Vérifier
                    </button>
                </div>
            </div>
        `;
    }
    
    renderTestRecap(lesson) {
        this.questions = lesson.questions || [];
        this.currentQuestionIndex = 0;
        this.score = 0;
        
        return `
            <div class="lesson-container test-recap">
                <div class="lesson-header">
                    <h2>${lesson.title}</h2>
                    <div class="question-progress">
                        Question <span id="currentQuestion">1</span> / ${this.questions.length}
                    </div>
                </div>
                
                <div class="question-container" id="questionContainer">
                    ${this.renderQuestion(this.questions[0])}
                </div>
                
                <div class="lesson-controls">
                    <button class="btn btn-primary" onclick="learningApp.submitAnswer()" id="submitBtn">
                        Valider
                    </button>
                </div>
            </div>
        `;
    }
    
    renderQuestion(question) {
        return `
            <div class="question" data-question-id="${question.id}">
                <h3>${question.question}</h3>
                <div class="options">
                    ${question.options.map((option, index) => `
                        <label class="option-label">
                            <input type="radio" name="answer" value="${option}" />
                            <span class="option-text">${option}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderDefaultLesson(lesson) {
        return `
            <div class="lesson-container default-lesson">
                <div class="lesson-header">
                    <h2>${lesson.title}</h2>
                </div>
                
                <div class="lesson-content">
                    ${lesson.content || '<p>Contenu de la leçon</p>'}
                </div>
                
                <div class="lesson-controls">
                    <button class="btn btn-primary" onclick="learningApp.completeLesson()">
                        Terminer <i class="bi bi-check"></i>
                    </button>
                </div>
            </div>
        `;
    }

    initLessonInteractions() {
        // Add interactions based on lesson type
        if (this.currentLesson.type === 'vocabulary') {
            this.initVocabularyCards();
        }
    }

    initVocabularyCards() {
        const cards = document.querySelectorAll('.vocab-card');
        cards.forEach(card => {
            card.addEventListener('click', () => {
                card.classList.toggle('flipped');
            });
        });
    }

    showLoading() {
        document.getElementById('lessonContent').innerHTML = `
            <div class="loading-container">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <p>Chargement de la leçon...</p>
            </div>
        `;
    }

    showError(message) {
        document.getElementById('lessonContent').innerHTML = `
            <div class="error-container">
                <i class="bi bi-exclamation-triangle"></i>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="window.location.reload()">
                    Réessayer
                </button>
            </div>
        `;
    }

    completeLesson() {
        // Mark lesson as complete
        if (this.currentLesson) {
            fetch(`${this.config.apiUrl}lessons/${this.currentLesson.id}/complete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.config.csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                this.showSuccess('Leçon terminée !');
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            })
            .catch(error => {
                console.error('Error completing lesson:', error);
            });
        }
    }

    showSuccess(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <i class="bi bi-check-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 3000);
    }
    
    showError(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <i class="bi bi-exclamation-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 3000);
    }

    closeLesson() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('lessonModal'));
        if (modal) {
            modal.hide();
        }
    }
    
    // Vocabulary card navigation
    nextCard() {
        if (this.currentCardIndex < this.totalCards - 1) {
            this.currentCardIndex++;
            this.updateCardDisplay();
        } else {
            // Last card - complete lesson
            this.completeLesson();
        }
    }
    
    previousCard() {
        if (this.currentCardIndex > 0) {
            this.currentCardIndex--;
            this.updateCardDisplay();
        }
    }
    
    updateCardDisplay() {
        const cards = document.querySelectorAll('.vocab-card');
        cards.forEach((card, index) => {
            card.classList.toggle('active', index === this.currentCardIndex);
        });
        
        // Update progress
        const progress = ((this.currentCardIndex + 1) / this.totalCards) * 100;
        document.getElementById('lessonProgress').style.width = progress + '%';
        document.querySelector('.progress-text').textContent = `${this.currentCardIndex + 1} / ${this.totalCards}`;
        document.querySelector('.card-counter').textContent = `${this.currentCardIndex + 1} / ${this.totalCards}`;
        
        // Update button states
        document.getElementById('prevBtn').disabled = this.currentCardIndex === 0;
        document.getElementById('nextBtn').innerHTML = 
            this.currentCardIndex === this.totalCards - 1 
                ? 'Terminer <i class="bi bi-check"></i>' 
                : 'Suivant <i class="bi bi-arrow-right"></i>';
    }
    
    // Matching exercise methods
    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }
    
    handleDragStart(event, itemId) {
        event.dataTransfer.setData('text/plain', itemId);
        event.dataTransfer.effectAllowed = 'move';
    }
    
    allowDrop(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }
    
    handleDrop(event) {
        event.preventDefault();
        const droppedId = event.dataTransfer.getData('text/plain');
        const targetElement = event.target.closest('.right-item');
        
        if (targetElement) {
            // Store the match
            const leftId = droppedId;
            const rightText = targetElement.querySelector('.draggable-item').textContent.trim();
            this.userMatches[leftId] = rightText;
            
            // Visual feedback
            targetElement.classList.add('matched');
            this.drawMatchingLine(leftId, targetElement.dataset.index);
        }
    }
    
    drawMatchingLine(leftId, rightIndex) {
        // Simple visual indicator - you can enhance this with actual SVG lines
        const leftItem = document.querySelector(`.left-item[data-id="${leftId}"]`);
        if (leftItem) {
            leftItem.classList.add('matched');
        }
    }
    
    resetMatching() {
        this.userMatches = {};
        document.querySelectorAll('.matched').forEach(el => el.classList.remove('matched'));
        document.querySelectorAll('.correct').forEach(el => el.classList.remove('correct'));
        document.querySelectorAll('.incorrect').forEach(el => el.classList.remove('incorrect'));
    }
    
    checkMatching() {
        const pairs = this.matchingPairs.map(pair => ({
            id: pair.id,
            answer: this.userMatches[pair.id] || null
        }));
        
        // Submit to API
        fetch(`${this.config.apiUrl}lessons/${this.currentLesson.id}/submit_answer/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.config.csrfToken
            },
            body: JSON.stringify({ pairs })
        })
        .then(response => response.json())
        .then(data => {
            if (data.correct) {
                this.showSuccess(data.message);
                setTimeout(() => this.completeLesson(), 2000);
            } else {
                this.showError(data.message);
                // Show which ones are wrong
                this.showMatchingFeedback(data);
            }
        });
    }
    
    // Test recap methods
    submitAnswer() {
        const selectedOption = document.querySelector('input[name="answer"]:checked');
        if (!selectedOption) {
            this.showError('Veuillez sélectionner une réponse');
            return;
        }
        
        const question = this.questions[this.currentQuestionIndex];
        
        // Submit to API
        fetch(`${this.config.apiUrl}lessons/${this.currentLesson.id}/submit_answer/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.config.csrfToken
            },
            body: JSON.stringify({
                question_id: question.id,
                answer: selectedOption.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.correct) {
                this.score++;
                selectedOption.parentElement.classList.add('correct');
                this.showSuccess('Bonne réponse !');
            } else {
                selectedOption.parentElement.classList.add('incorrect');
                if (data.explanation) {
                    this.showExplanation(data.explanation);
                }
            }
            
            // Move to next question after delay
            setTimeout(() => {
                if (this.currentQuestionIndex < this.questions.length - 1) {
                    this.currentQuestionIndex++;
                    document.getElementById('currentQuestion').textContent = this.currentQuestionIndex + 1;
                    document.getElementById('questionContainer').innerHTML = 
                        this.renderQuestion(this.questions[this.currentQuestionIndex]);
                } else {
                    // Show final score
                    this.showFinalScore();
                }
            }, 2000);
        });
    }
    
    showExplanation(explanation) {
        const explDiv = document.createElement('div');
        explDiv.className = 'explanation-box';
        explDiv.innerHTML = `<i class="bi bi-info-circle"></i> ${explanation}`;
        document.querySelector('.question-container').appendChild(explDiv);
    }
    
    showFinalScore() {
        const percentage = Math.round((this.score / this.questions.length) * 100);
        const content = `
            <div class="final-score">
                <h2>Test terminé !</h2>
                <div class="score-circle">
                    <span class="score-number">${this.score}</span>
                    <span class="score-total">/ ${this.questions.length}</span>
                </div>
                <p class="score-percentage">${percentage}%</p>
                <button class="btn btn-primary" onclick="learningApp.completeLesson()">
                    Continuer
                </button>
            </div>
        `;
        document.getElementById('lessonContent').innerHTML = content;
    }
}

// Make it globally available
window.LearningApp = LearningApp;