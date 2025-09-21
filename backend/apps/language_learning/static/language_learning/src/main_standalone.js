console.log('🚀 Language Learning OWL Standalone App Starting...');

// Attendre que OWL soit chargé depuis le CDN
document.addEventListener('DOMContentLoaded', function() {
    if (typeof owl === 'undefined') {
        console.error('❌ OWL not loaded from CDN');
        return;
    }

    console.log('✅ OWL loaded from CDN:', owl);

    const { Component, useState, onWillStart, xml, mount } = owl;

    // Template inline pour commencer
    const TEMPLATES = `
        <t t-name="LearningDashboard">
            <div class="language-learning-app">
                <t t-if="!state.isReady">
                    <div class="d-flex justify-content-center align-items-center" style="height: 60vh;">
                        <div class="text-center">
                            <div class="spinner-border text-primary mb-3" role="status">
                                <span class="visually-hidden">Chargement...</span>
                            </div>
                            <p class="text-muted">Chargement de l'interface d'apprentissage OWL...</p>
                        </div>
                    </div>
                </t>
                <t t-else="">
                    <div class="container-fluid mt-4">
                        <div class="alert alert-success">
                            <h4><i class="bi bi-check-circle"></i> OWL Application chargée!</h4>
                            <p>Langue: <strong t-esc="data.selectedLanguageName"/> (<t t-esc="data.selectedLanguage"/>)</p>
                            <p>Streak: <strong t-esc="data.userStreak"/> jours</p>
                            <p>Unités: <strong t-esc="data.courseUnits.length"/> disponibles</p>
                        </div>

                        <div class="row">
                            <div class="col-md-8">
                                <div class="card">
                                    <div class="card-header bg-primary text-white">
                                        <h5><i class="bi bi-book"></i> Unités de cours</h5>
                                    </div>
                                    <div class="card-body">
                                        <t t-if="data.courseUnits.length === 0">
                                            <p class="text-muted">Aucune unité disponible</p>
                                        </t>
                                        <t t-else="">
                                            <t t-foreach="data.courseUnits" t-as="unit" t-key="unit.id">
                                                <div class="border rounded p-3 mb-3" t-on-click="() => this.selectUnit(unit)">
                                                    <h6>Unité <t t-esc="unit.unit_number"/>: <t t-esc="unit.title"/></h6>
                                                    <p class="text-muted small" t-esc="unit.description"/>
                                                    <div class="progress" style="height: 8px;">
                                                        <div class="progress-bar bg-primary"
                                                             t-att-style="'width: ' + unit.progress_percentage + '%'"></div>
                                                    </div>
                                                    <small><t t-esc="unit.completed_modules"/>/<t t-esc="unit.modules_count"/> modules</small>
                                                </div>
                                            </t>
                                        </t>
                                    </div>
                                </div>
                            </div>

                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-header bg-success text-white">
                                        <h6><i class="bi bi-graph-up"></i> Progression</h6>
                                    </div>
                                    <div class="card-body text-center">
                                        <h3 class="text-primary" t-esc="data.userStreak"/>
                                        <p>jours de suite</p>
                                        <button class="btn btn-primary">Continuer</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </t>
            </div>
        </t>
    `;

    // Créer le composant principal
    class LearningDashboard extends Component {
        static template = xml`${TEMPLATES}`;

        setup() {
            this.state = useState({
                isReady: false
            });

            this.data = {
                selectedLanguage: 'EN',
                selectedLanguageName: 'English',
                courseUnits: [],
                userStreak: 0
            };

            onWillStart(async () => {
                await this.loadData();
                this.state.isReady = true;
            });
        }

        async loadData() {
            try {
                const dataScript = document.getElementById('language-learning-data');
                if (dataScript) {
                    const data = JSON.parse(dataScript.textContent);
                    Object.assign(this.data, {
                        selectedLanguage: data.selectedLanguage || 'EN',
                        selectedLanguageName: data.selectedLanguageName || 'English',
                        courseUnits: data.courseUnits || [],
                        userStreak: data.userStreak || 0
                    });
                    console.log('📊 Data loaded:', this.data);
                }
            } catch (error) {
                console.error('❌ Error loading data:', error);
            }
        }

        selectUnit(unit) {
            console.log('🎯 Unit selected:', unit);
            // TODO: Implémenter la sélection d'unité
        }
    }

    // Monter l'application
    const appContainer = document.getElementById('language-learning-app');
    if (appContainer) {
        console.log('🎯 Mounting OWL app...');
        mount(LearningDashboard, appContainer);
        console.log('✅ OWL app mounted successfully!');
    } else {
        console.error('❌ Container not found');
    }
});