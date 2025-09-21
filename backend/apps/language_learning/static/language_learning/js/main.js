/**
 * Language Learning App - OWL Frontend
 * Based on Notebook app architecture
 */

const { mount, Component, xml, useState, useRef, onMounted, onWillUnmount } = owl;

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

    async loadLearningData(language = null, unit = null) {
        this.setState({ isLoading: true, error: null });

        try {
            const params = new URLSearchParams();
            if (language) params.append('lang', language);
            if (unit) params.append('unit', unit);
            params.append('view', this.state.viewType);

            const response = await fetch(`/language_learning/learn/?${params}`, {
                headers: {
                    'HX-Request': 'true',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const html = await response.text();

            // Parse the HTML to extract data (temporary solution)
            // In production, you'd want a proper JSON API
            this.setState({
                isLoading: false,
                // Update state based on response
            });

        } catch (error) {
            console.error('Error loading learning data:', error);
            this.setState({
                isLoading: false,
                error: error.message
            });
        }
    }

    async refreshProgress() {
        try {
            const response = await fetch(`/language_learning/api/refresh-progress/?lang=${this.state.selectedLanguage}`, {
                headers: {
                    'HX-Request': 'true'
                }
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const html = await response.text();
            // Parse progress data from HTML response
            // This would be better as JSON in production

        } catch (error) {
            console.error('Error refreshing progress:', error);
        }
    }

    async startModule(moduleId) {
        try {
            const response = await fetch(`/language_learning/module/${moduleId}/start/`, {
                headers: {
                    'HX-Request': 'true'
                }
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const html = await response.text();
            return html; // Return modal HTML

        } catch (error) {
            console.error('Error starting module:', error);
            throw error;
        }
    }

    async completeModule(moduleId, score = 100) {
        try {
            const formData = new FormData();
            formData.append('score', score);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

            const response = await fetch(`/language_learning/module/${moduleId}/complete/`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();

            // Refresh progress after completion
            await this.refreshProgress();

            return data;

        } catch (error) {
            console.error('Error completing module:', error);
            throw error;
        }
    }
}

// Navbar Component
class Navbar extends Component {
    static template = xml`
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand d-flex align-items-center" href="/language_learning/">
                    <i class="bi bi-globe me-2"></i>
                    Linguify Learn
                </a>

                <div class="navbar-nav ms-auto">
                    <div class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-white" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="bi bi-translate me-1"></i>
                            <t t-esc="state.selectedLanguageName || 'Select Language'"/>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" t-on-click="selectLanguage.bind(this, 'EN')">English</a></li>
                            <li><a class="dropdown-item" href="#" t-on-click="selectLanguage.bind(this, 'ES')">Español</a></li>
                            <li><a class="dropdown-item" href="#" t-on-click="selectLanguage.bind(this, 'FR')">Français</a></li>
                            <li><a class="dropdown-item" href="#" t-on-click="selectLanguage.bind(this, 'DE')">Deutsch</a></li>
                        </ul>
                    </div>

                    <a class="nav-link text-white" href="/language_learning/progress/">
                        <i class="bi bi-graph-up"></i>
                        Progress
                    </a>

                    <a class="nav-link text-white" href="/language_learning/settings/">
                        <i class="bi bi-gear"></i>
                        Settings
                    </a>
                </div>
            </div>
        </nav>
    `;

    setup() {
        this.store = this.props.store;
        this.state = useState(this.store.state);
    }

    selectLanguage(langCode) {
        this.store.setState({ selectedLanguage: langCode });
        this.store.loadLearningData(langCode);
    }
}

// Progress Info Component
class ProgressInfo extends Component {
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
        <div class="units-container">
            <h3 class="mb-3">Course Units</h3>
            <div class="units-list" t-if="state.courseUnits && state.courseUnits.length > 0">
                <div t-foreach="state.courseUnits" t-as="unit" t-key="unit.id"
                     class="unit-card mb-3"
                     t-att-class="{ 'active': state.activeUnit and state.activeUnit.id === unit.id }"
                     t-on-click="selectUnit.bind(this, unit)">
                    <div class="unit-header d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="unit-title">Unit <t t-esc="unit.unit_number"/>: <t t-esc="unit.title"/></h5>
                            <p class="unit-description text-muted"><t t-esc="unit.description"/></p>
                        </div>
                        <div class="unit-progress">
                            <div class="progress-circle">
                                <span><t t-esc="unit.progress_percentage"/>%</span>
                            </div>
                        </div>
                    </div>
                    <div class="unit-stats">
                        <small class="text-muted">
                            <t t-esc="unit.completed_modules"/>/<t t-esc="unit.modules_count"/> modules completed
                        </small>
                    </div>
                </div>
            </div>
            <div t-else class="text-center py-5">
                <i class="bi bi-book text-muted" style="font-size: 3rem;"></i>
                <h5 class="text-muted mt-3">Aucun cours disponible</h5>
                <p class="text-muted">Les cours d'apprentissage apparaîtront ici.</p>
            </div>
        </div>
    `;

    setup() {
        this.store = this.props.store;
        this.state = useState(this.store.state);
    }

    selectUnit(unit) {
        this.store.setState({ activeUnit: unit });
        this.store.loadLearningData(this.state.selectedLanguage, unit.id);
    }
}

// Module List Component
class ModuleList extends Component {
    static template = xml`
        <div class="modules-container" t-if="state.activeUnit">
            <h4 class="mb-3">
                Unit <t t-esc="state.activeUnit.unit_number"/> Modules
            </h4>
            <div class="modules-list">
                <div t-foreach="state.activeUnitModules" t-as="module" t-key="module.id"
                     class="module-card mb-2"
                     t-att-class="{ 'completed': module.is_completed, 'locked': module.is_locked }">
                    <div class="module-content d-flex justify-content-between align-items-center">
                        <div class="module-info">
                            <h6 class="module-title">
                                Module <t t-esc="module.module_number"/>: <t t-esc="module.title"/>
                            </h6>
                            <p class="module-description text-muted"><t t-esc="module.description"/></p>
                            <div class="module-meta">
                                <span class="badge bg-secondary me-2"><t t-esc="module.get_module_type_display"/></span>
                                <small class="text-muted">
                                    <i class="bi bi-clock me-1"></i><t t-esc="module.estimated_duration"/> min
                                    <i class="bi bi-star ms-2 me-1"></i><t t-esc="module.xp_reward"/> XP
                                </small>
                            </div>
                        </div>
                        <div class="module-actions">
                            <button t-if="module.is_completed" class="btn btn-success btn-sm" disabled="">
                                <i class="bi bi-check-circle"></i> Completed
                            </button>
                            <button t-elif="module.is_locked" class="btn btn-secondary btn-sm" disabled="">
                                <i class="bi bi-lock"></i> Locked
                            </button>
                            <button t-else class="btn btn-primary btn-sm" t-on-click="startModule.bind(this, module)">
                                <i class="bi bi-play"></i> Start
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    setup() {
        this.store = this.props.store;
        this.state = useState(this.store.state);
    }

    async startModule(module) {
        try {
            const modalHtml = await this.store.startModule(module.id);
            // Show modal with module content
            this.showModuleModal(modalHtml, module);
        } catch (error) {
            console.error('Failed to start module:', error);
        }
    }

    showModuleModal(html, module) {
        // Create and show bootstrap modal
        const modalElement = document.createElement('div');
        modalElement.innerHTML = html;
        document.body.appendChild(modalElement);

        // Initialize bootstrap modal
        const modal = new bootstrap.Modal(modalElement.querySelector('.modal'));
        modal.show();

        // Clean up when modal is hidden
        modalElement.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modalElement);
        });
    }
}

// Supprimé - LearningInterface fusionné dans WebClient

// Main Web Client Component - Version simplifiée
class LanguageLearningWebClient extends Component {
    static template = xml`
        <div class="language-learning-app">
            <div class="container-fluid mt-3">
                <div class="row">
                    <div class="col-12">
                        <h1><i class="bi bi-globe"></i> Linguify Learn</h1>
                        <p class="text-muted">Plateforme d'apprentissage des langues</p>
                    </div>
                </div>

                <ProgressInfo store="store"/>

                <div class="row">
                    <div class="col-md-8">
                        <CourseUnits store="store"/>
                    </div>
                    <div class="col-md-4">
                        <ModuleList store="store"/>
                    </div>
                </div>
            </div>
        </div>
    `;

    static components = {
        ProgressInfo,
        CourseUnits,
        ModuleList
    };

    setup() {
        this.store = new LanguageLearningStore();

        // Initialize with data from Django if available
        if (this.props.initialData) {
            console.log('Initial data received:', this.props.initialData);
            this.store.setState(this.props.initialData);
        }

        onMounted(() => {
            // Load data if not already provided by Django
            if (!this.props.initialData || Object.keys(this.props.initialData).length === 0) {
                this.store.loadLearningData();
            }
        });
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('language-learning-app')) {
        // Get initial data from Django template
        const initialDataElement = document.getElementById('initial-data');
        let initialData = {};

        if (initialDataElement) {
            try {
                initialData = JSON.parse(initialDataElement.textContent);
                console.log('Parsed initial data:', initialData);
            } catch (e) {
                console.warn('Failed to parse initial data:', e);
                console.log('Raw content:', initialDataElement.textContent);
            }
        } else {
            console.log('No initial-data element found');
        }

        console.log('Mounting OWL app with data:', initialData);
        mount(LanguageLearningWebClient, document.getElementById('language-learning-app'), {
            initialData: initialData
        });
    }
});

// Export for potential external use
window.LanguageLearningApp = {
    LanguageLearningWebClient,
    LanguageLearningStore
};