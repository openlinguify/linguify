/**
 * Language Learning App - Version Simple OWL
 */

const { mount, Component, xml, useState } = owl;

// Simple Test Component
class SimpleApp extends Component {
    static template = xml`
        <div class="container-fluid mt-4">
            <div class="alert alert-success">
                <h2><i class="bi bi-globe"></i> Linguify Learn - OWL Fonctionne!</h2>
                <p>Langue sélectionnée: <strong t-esc="state.selectedLanguage"></strong></p>
                <p>Niveau: <strong t-esc="state.userProgress.level"></strong></p>
                <p>XP: <strong t-esc="state.userProgress.total_xp"></strong></p>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Progression</h5>
                        </div>
                        <div class="card-body">
                            <div class="progress mb-3">
                                <div class="progress-bar" role="progressbar"
                                     t-att-style="'width: ' + state.userProgress.get_completion_percentage + '%'"></div>
                            </div>
                            <p>Progression: <span t-esc="state.userProgress.get_completion_percentage"></span>%</p>
                            <p>Streak: <span t-esc="state.userStreak"></span> jours</p>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Cours disponibles</h5>
                        </div>
                        <div class="card-body">
                            <div t-if="state.courseUnits.length === 0">
                                <p class="text-muted">Aucun cours disponible pour le moment.</p>
                                <p>Les cours d'apprentissage apparaîtront ici.</p>
                            </div>
                            <div t-else="">
                                <p>Nombre de cours: <span t-esc="state.courseUnits.length"></span></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mt-4">
                <button class="btn btn-primary me-2" t-on-click="testFunction">
                    <i class="bi bi-play"></i> Test Action
                </button>
                <button class="btn btn-info" t-on-click="refreshData">
                    <i class="bi bi-arrow-clockwise"></i> Actualiser
                </button>
            </div>
        </div>
    `;

    setup() {
        // Initialiser avec les données depuis Django
        const initialData = this.props.initialData || {};
        this.state = useState({
            selectedLanguage: initialData.selectedLanguage || 'FR',
            selectedLanguageName: initialData.selectedLanguageName || '',
            courseUnits: initialData.courseUnits || [],
            activeUnit: initialData.activeUnit || null,
            activeUnitModules: initialData.activeUnitModules || [],
            userProgress: initialData.userProgress || {
                level: 1,
                total_xp: 0,
                get_completion_percentage: 0
            },
            userStreak: initialData.userStreak || 0,
            viewType: initialData.viewType || 'home'
        });

        console.log('SimpleApp initialized with state:', this.state);
    }

    testFunction() {
        console.log('Test function clicked!');
        window.notificationService.success('Test réussi ! OWL fonctionne.');
    }

    refreshData() {
        console.log('Refreshing data...');
        this.state.userProgress.total_xp += 10;
        window.notificationService.info('Données mises à jour (+10 XP)');
    }
}

// Initialize the simple application
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== SIMPLE APP LOADING ===');

    if (document.getElementById('language-learning-app')) {
        // Get initial data from Django template
        const initialDataElement = document.getElementById('initial-data');
        let initialData = {};

        if (initialDataElement) {
            try {
                initialData = JSON.parse(initialDataElement.textContent);
                console.log('Initial data loaded:', initialData);
            } catch (e) {
                console.warn('Failed to parse initial data:', e);
            }
        }

        console.log('Mounting SimpleApp...');
        mount(SimpleApp, document.getElementById('language-learning-app'), {
            initialData: initialData
        });
        console.log('SimpleApp mounted successfully!');
    } else {
        console.error('Element language-learning-app not found');
    }
});

// Export for debugging
window.SimpleLanguageLearningApp = {
    SimpleApp
};