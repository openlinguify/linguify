/**
 * Language Learning App - Version Complète OWL
 */

const { mount, Component, xml, useState } = owl;

// Store for managing language learning state
class LanguageLearningStore {
    constructor() {
        this.state = {
            selectedLanguage: 'EN',
            selectedLanguageName: '',
            courseUnits: [],
            activeUnit: null,
            activeUnitModules: [],
            userProgress: {
                level: 1,
                total_xp: 0,
                get_completion_percentage: 0
            },
            userStreak: 0,
            viewType: 'home',
            isLoading: false,
            error: null
        };
        this.listeners = new Set();
    }

    subscribe(callback) {
        this.listeners.add(callback);
        return () => this.listeners.delete(callback);
    }

    setState(newState) {
        Object.assign(this.state, newState);
        this.listeners.forEach(callback => callback(this.state));
    }

    async refreshProgress() {
        try {
            const response = await fetch(`/language_learning/api/refresh-progress/?lang=${this.state.selectedLanguage}`, {
                headers: { 'HX-Request': 'true' }
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
        } catch (error) {
            console.error('Error refreshing progress:', error);
        }
    }
}

// Progress Cards Component
class ProgressCards extends Component {
    static template = xml`
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="progress-card progress-card-primary">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="progress-card-label">Niveau actuel</h6>
                            <p class="progress-card-value" t-esc="getLevel()"></p>
                        </div>
                        <i class="bi bi-trophy-fill progress-card-icon"></i>
                    </div>
                </div>
            </div>

            <div class="col-md-3">
                <div class="progress-card progress-card-success">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="progress-card-label">XP Total</h6>
                            <p class="progress-card-value" t-esc="getXP()"></p>
                        </div>
                        <i class="bi bi-star-fill progress-card-icon"></i>
                    </div>
                </div>
            </div>

            <div class="col-md-3">
                <div class="progress-card progress-card-info">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="progress-card-label">Progression</h6>
                            <p class="progress-card-value"><t t-esc="getProgress()"/>%</p>
                        </div>
                        <i class="bi bi-graph-up-arrow progress-card-icon"></i>
                    </div>
                </div>
            </div>

            <div class="col-md-3">
                <div class="progress-card progress-card-warning">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="progress-card-label">Streak</h6>
                            <p class="progress-card-value"><t t-esc="getStreak()"/> jours</p>
                        </div>
                        <i class="bi bi-fire progress-card-icon"></i>
                    </div>
                </div>
            </div>
        </div>
    `;

    setup() {
        this.store = this.props.store;
        this.state = useState(this.store.state);
    }

    getLevel() {
        return this.state.userProgress?.level || 1;
    }

    getXP() {
        return this.state.userProgress?.total_xp || 0;
    }

    getProgress() {
        return this.state.userProgress?.get_completion_percentage || 0;
    }

    getStreak() {
        return this.state.userStreak || 0;
    }
}

// Course Units Component
class CourseUnits extends Component {
    static template = xml`
        <div class="card">
            <div class="card-header">
                <h5><i class="bi bi-book"></i> Unités de cours</h5>
            </div>
            <div class="card-body">
                <div t-if="hasUnits()">
                    <div t-foreach="state.courseUnits" t-as="unit" t-key="unit_index">
                        <div class="unit-card mb-3" t-on-click="selectUnit">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6>Unité <t t-esc="unit.unit_number"/>: <t t-esc="unit.title"/></h6>
                                    <p class="text-muted mb-0" t-esc="unit.description"></p>
                                    <small class="text-muted">
                                        <t t-esc="unit.completed_modules"/>/<t t-esc="unit.modules_count"/> modules complétés
                                    </small>
                                </div>
                                <div class="text-end">
                                    <div class="badge bg-primary"><t t-esc="unit.progress_percentage"/>%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div t-else="" class="text-center py-4">
                    <i class="bi bi-book text-muted" style="font-size: 3rem;"></i>
                    <h6 class="text-muted mt-3">Aucune unité disponible</h6>
                    <p class="text-muted">Les unités de cours apparaîtront ici.</p>
                </div>
            </div>
        </div>
    `;

    setup() {
        this.store = this.props.store;
        this.state = useState(this.store.state);
    }

    hasUnits() {
        return this.state.courseUnits && this.state.courseUnits.length > 0;
    }

    selectUnit(event) {
        console.log('Unit selected:', event);
        window.notificationService.info('Unité sélectionnée');
    }
}

// Module List Component
class ModuleList extends Component {
    static template = xml`
        <div class="card">
            <div class="card-header">
                <h5><i class="bi bi-puzzle"></i> Modules</h5>
            </div>
            <div class="card-body">
                <div t-if="hasModules()">
                    <div t-foreach="state.activeUnitModules" t-as="module" t-key="module_index">
                        <div class="module-card mb-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="flex-grow-1">
                                    <h6>Module <t t-esc="module.module_number"/>: <t t-esc="module.title"/></h6>
                                    <p class="text-muted mb-1" t-esc="module.description"></p>
                                    <div class="d-flex gap-2">
                                        <span class="badge bg-secondary" t-esc="module.get_module_type_display"></span>
                                        <small class="text-muted">
                                            <i class="bi bi-clock"></i> <t t-esc="module.estimated_duration"/> min
                                            <i class="bi bi-star ms-2"></i> <t t-esc="module.xp_reward"/> XP
                                        </small>
                                    </div>
                                </div>
                                <div>
                                    <button t-if="module.is_completed" class="btn btn-success btn-sm" disabled="">
                                        <i class="bi bi-check-circle"></i> Terminé
                                    </button>
                                    <button t-elif="module.is_locked" class="btn btn-secondary btn-sm" disabled="">
                                        <i class="bi bi-lock"></i> Verrouillé
                                    </button>
                                    <button t-else="" class="btn btn-primary btn-sm" t-on-click="startModule">
                                        <i class="bi bi-play"></i> Commencer
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div t-else="" class="text-center py-4">
                    <i class="bi bi-puzzle text-muted" style="font-size: 2.5rem;"></i>
                    <h6 class="text-muted mt-3">Aucun module disponible</h6>
                    <p class="text-muted">Sélectionnez une unité pour voir les modules.</p>
                </div>
            </div>
        </div>
    `;

    setup() {
        this.store = this.props.store;
        this.state = useState(this.store.state);
    }

    hasModules() {
        return this.state.activeUnitModules && this.state.activeUnitModules.length > 0;
    }

    startModule(event) {
        console.log('Module started:', event);
        window.notificationService.success('Module démarré !');
    }
}

// Navigation Bar Component
class NavigationBar extends Component {
    static template = xml`
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="/language_learning/">
                    <i class="bi bi-globe"></i> Linguify Learn
                </a>

                <div class="navbar-nav ms-auto">
                    <div class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            <i class="bi bi-translate"></i> <t t-esc="getLanguageName()"/>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" t-on-click="selectLanguage" data-lang="EN">🇬🇧 English</a></li>
                            <li><a class="dropdown-item" href="#" t-on-click="selectLanguage" data-lang="FR">🇫🇷 Français</a></li>
                            <li><a class="dropdown-item" href="#" t-on-click="selectLanguage" data-lang="ES">🇪🇸 Español</a></li>
                            <li><a class="dropdown-item" href="#" t-on-click="selectLanguage" data-lang="DE">🇩🇪 Deutsch</a></li>
                        </ul>
                    </div>

                    <a class="nav-link" href="/language_learning/progress/">
                        <i class="bi bi-graph-up"></i> Progrès
                    </a>

                    <a class="nav-link" href="/language_learning/settings/">
                        <i class="bi bi-gear"></i> Paramètres
                    </a>
                </div>
            </div>
        </nav>
    `;

    setup() {
        this.store = this.props.store;
        this.state = useState(this.store.state);
    }

    getLanguageName() {
        return this.state.selectedLanguageName || this.state.selectedLanguage || 'Langue';
    }

    selectLanguage(event) {
        const lang = event.target.getAttribute('data-lang');
        console.log('Language selected:', lang);
        this.store.setState({ selectedLanguage: lang });
        window.notificationService.info(`Langue changée: ${lang}`);
    }
}

// Main Application Component
class LanguageLearningApp extends Component {
    static template = xml`
        <div class="language-learning-app">
            <NavigationBar store="store"/>

            <div class="container-fluid">
                <ProgressCards store="store"/>

                <div class="row">
                    <div class="col-md-8">
                        <CourseUnits store="store"/>
                    </div>
                    <div class="col-md-4">
                        <ModuleList store="store"/>
                    </div>
                </div>

                <div class="row mt-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-body text-center">
                                <button class="btn btn-outline-primary me-2" t-on-click="refreshData">
                                    <i class="bi bi-arrow-clockwise"></i> Actualiser les données
                                </button>
                                <button class="btn btn-outline-success" t-on-click="testNotification">
                                    <i class="bi bi-bell"></i> Test notification
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div t-if="state.isLoading" class="loading-overlay">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
            </div>
        </div>
    `;

    static components = {
        NavigationBar,
        ProgressCards,
        CourseUnits,
        ModuleList
    };

    setup() {
        this.store = new LanguageLearningStore();

        // Initialize with data from Django if available
        if (this.props.initialData) {
            console.log('Full app initialized with data:', this.props.initialData);
            this.store.setState(this.props.initialData);
        }

        this.state = useState(this.store.state);
    }

    refreshData() {
        console.log('Refreshing data...');
        this.store.setState({ isLoading: true });

        setTimeout(() => {
            this.store.setState({
                isLoading: false,
                userProgress: {
                    ...this.state.userProgress,
                    total_xp: this.state.userProgress.total_xp + 25
                }
            });
            window.notificationService.success('Données actualisées (+25 XP)');
        }, 1000);
    }

    testNotification() {
        window.notificationService.info('Test de notification réussi !');
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== FULL LANGUAGE LEARNING APP ===');

    if (document.getElementById('language-learning-app')) {
        // Get initial data from Django template
        const initialDataElement = document.getElementById('initial-data');
        let initialData = {};

        if (initialDataElement) {
            try {
                initialData = JSON.parse(initialDataElement.textContent);
                console.log('Full app initial data:', initialData);
            } catch (e) {
                console.warn('Failed to parse initial data:', e);
            }
        }

        console.log('Mounting LanguageLearningApp...');
        mount(LanguageLearningApp, document.getElementById('language-learning-app'), {
            initialData: initialData
        });
        console.log('LanguageLearningApp mounted successfully!');
    }
});

// Export for debugging
window.FullLanguageLearningApp = {
    LanguageLearningApp,
    LanguageLearningStore
};