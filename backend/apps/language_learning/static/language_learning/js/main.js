console.log('🚀 Language Learning App Starting...');

// Simple vanilla JS implementation pour l'instant
document.addEventListener('DOMContentLoaded', function() {
    const appContainer = document.getElementById('language-learning-app');
    const dataScript = document.getElementById('language-learning-data');

    if (appContainer && dataScript) {
        // Extraire les données du script JSON
        let data;
        try {
            data = JSON.parse(dataScript.textContent);
            console.log('📊 Data parsed successfully:', data);
        } catch (error) {
            console.error('❌ Error parsing data:', error);
            data = {
                selectedLanguage: 'EN',
                selectedLanguageName: 'English',
                courseUnits: [],
                activeUnit: null,
                activeUnitModules: [],
                userStreak: 0,
                viewType: 'home'
            };
        }

        const { selectedLanguage, selectedLanguageName, courseUnits, userStreak } = data;

        console.log('📚 Données reçues:', {
            selectedLanguage,
            selectedLanguageName,
            courseUnits,
            userStreak
        });

        // Créer l'interface simple
        appContainer.innerHTML = `
            <div class="language-learning-interface">
                <div class="learning-header bg-primary text-white p-4 rounded mb-4">
                    <h1 class="h3 mb-2">🌟 Language Learning</h1>
                    <p class="mb-2">Langue sélectionnée: <strong>${selectedLanguageName || selectedLanguage}</strong></p>
                    <p class="mb-0">Streak actuel: <strong>${userStreak} jours</strong> 🔥</p>
                </div>

                <div class="learning-content row">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="card-title mb-0">Unités de cours</h5>
                            </div>
                            <div class="card-body">
                                <div id="course-units-list">
                                    ${courseUnits.length > 0 ?
                                        courseUnits.map(unit => `
                                            <div class="unit-card border rounded p-3 mb-3">
                                                <h6>Unité ${unit.unit_number}: ${unit.title}</h6>
                                                <p class="text-muted small">${unit.description}</p>
                                                <div class="progress mb-2">
                                                    <div class="progress-bar" style="width: ${unit.progress_percentage}%">
                                                        ${unit.progress_percentage}%
                                                    </div>
                                                </div>
                                                <small class="text-muted">
                                                    ${unit.completed_modules}/${unit.modules_count} modules complétés
                                                </small>
                                            </div>
                                        `).join('')
                                        : '<p class="text-muted">Aucune unité de cours disponible.</p>'
                                    }
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="card-title mb-0">Progression</h6>
                            </div>
                            <div class="card-body">
                                <div class="text-center">
                                    <div class="mb-3">
                                        <h4 class="text-primary">${userStreak}</h4>
                                        <small class="text-muted">Jours de suite</small>
                                    </div>
                                    <div class="mb-3">
                                        <h4 class="text-success">${courseUnits.length}</h4>
                                        <small class="text-muted">Unités disponibles</small>
                                    </div>
                                    <button class="btn btn-primary btn-sm">
                                        Continuer l'apprentissage
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        console.log('✅ Interface Language Learning chargée avec succès!');
    } else {
        if (!appContainer) {
            console.error('❌ Conteneur #language-learning-app non trouvé');
        }
        if (!dataScript) {
            console.error('❌ Script #language-learning-data non trouvé');
        }
    }
});