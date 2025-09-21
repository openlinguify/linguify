import { Component, mount, xml, useState, onWillStart } from "@odoo/owl";

console.log('🚀 Language Learning OWL App Starting (NPM version)...');

// Import styles
import './scss/learning.scss';


// Unit Card Component
class UnitCard extends Component {
  static template = xml`
    <div class="unit-card border rounded p-3 mb-3 cursor-pointer" t-on-click="onClick">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <h6 class="unit-title mb-1">
          <span class="badge bg-primary me-2">Unité <t t-esc="props.unit.unit_number"/></span>
          <t t-esc="props.unit.title"/>
        </h6>
        <t t-if="props.unit.progress_percentage === 100">
          <i class="bi bi-check-circle-fill text-success fs-5"></i>
        </t>
      </div>
      <p class="text-muted small mb-3" t-esc="props.unit.description"/>
      <div class="progress mb-2" style="height: 8px;">
        <div class="progress-bar" t-att-class="progressClass"
             t-att-style="'width: ' + progressWidth"></div>
      </div>
      <small class="text-muted">
        <t t-esc="props.unit.completed_modules"/>/<t t-esc="props.unit.modules_count"/> modules
      </small>
    </div>
  `;

  static props = {
    unit: Object,
    isActive: { type: Boolean, optional: true },
    onUnitClick: { type: Function, optional: true }
  };

  onClick() {
    if (this.props.onUnitClick) {
      this.props.onUnitClick(this.props.unit.id);
    }
  }

  get progressWidth() {
    return `${this.props.unit.progress_percentage || 0}%`;
  }

  get progressClass() {
    const percentage = this.props.unit.progress_percentage || 0;
    if (percentage === 100) return 'bg-success';
    if (percentage >= 50) return 'bg-primary';
    if (percentage > 0) return 'bg-warning';
    return 'bg-secondary';
  }
}

// Progress Panel Component
class ProgressPanel extends Component {
  static template = xml`
    <div class="card">
      <div class="card-header">
        <h6 class="card-title mb-0">
          <i class="bi bi-graph-up me-2"></i>Progression
        </h6>
      </div>
      <div class="card-body text-center">
        <div class="mb-4">
          <h3 class="text-primary mb-0"><t t-esc="props.userStreak"/></h3>
          <small class="text-muted">jours de suite <t t-esc="streakIcon"/></small>
        </div>
        <div class="row text-center mb-3">
          <div class="col-6">
            <h4 class="text-success mb-0"><t t-esc="completedUnits"/></h4>
            <small class="text-muted">Complétées</small>
          </div>
          <div class="col-6">
            <h4 class="text-info mb-0"><t t-esc="props.unitsCount"/></h4>
            <small class="text-muted">Total</small>
          </div>
        </div>
        <button class="btn btn-primary w-100">
          <i class="bi bi-play-circle me-2"></i>Continuer
        </button>
      </div>
    </div>
  `;

  static props = {
    userStreak: Number,
    unitsCount: Number,
    completedUnitsCount: { type: Number, optional: true }
  };

  get completedUnits() {
    return this.props.completedUnitsCount || 0;
  }

  get streakIcon() {
    if (this.props.userStreak >= 30) return '🔥';
    if (this.props.userStreak >= 7) return '⚡';
    if (this.props.userStreak >= 3) return '✨';
    return '🌟';
  }
}

// Navbar Component
class Navbar extends Component {
  static template = xml`
    <nav class="navbar navbar-expand-lg bg-primary text-white mb-4">
      <div class="container-fluid">
        <div class="navbar-brand text-white">
          <i class="bi bi-translate me-2"></i>Language Learning
        </div>
        <div class="d-flex align-items-center">
          <div class="me-4">
            <span class="badge bg-light text-dark me-2"><t t-esc="languageFlag"/></span>
            <span class="text-white fw-bold"><t t-esc="props.selectedLanguageName"/></span>
          </div>
          <div class="me-3">
            <span class="badge bg-warning text-dark">
              <i class="bi bi-fire me-1"></i><t t-esc="props.userStreak"/> jours
            </span>
          </div>
        </div>
      </div>
    </nav>
  `;

  static props = {
    selectedLanguage: String,
    selectedLanguageName: String,
    userStreak: Number
  };

  get languageFlag() {
    const flagMap = {
      'EN': '🇬🇧',
      'FR': '🇫🇷',
      'ES': '🇪🇸',
      'DE': '🇩🇪',
      'IT': '🇮🇹'
    };
    return flagMap[this.props.selectedLanguage] || '🌍';
  }
}

// Main Dashboard Component
class LearningDashboard extends Component {
  static template = xml`
    <div class="language-learning-app">
      <t t-if="!state.isReady">
        <div class="d-flex justify-content-center align-items-center" style="height: 60vh;">
          <div class="text-center">
            <div class="spinner-border text-primary mb-3" role="status">
              <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="text-muted">Chargement de l'interface OWL...</p>
          </div>
        </div>
      </t>
      <t t-else="">
        <Navbar selectedLanguage="learningState.selectedLanguage"
                selectedLanguageName="learningState.selectedLanguageName"
                userStreak="learningState.userStreak"/>

        <div class="container-fluid mt-4">
          <div class="row">
            <div class="col-md-8">
              <div class="card">
                <div class="card-header">
                  <h5 class="card-title mb-0">
                    <i class="bi bi-book-half me-2"></i>Unités de cours
                  </h5>
                </div>
                <div class="card-body">
                  <t t-if="learningState.courseUnits.length === 0">
                    <p class="text-muted text-center">Aucune unité disponible</p>
                  </t>
                  <t t-else="">
                    <t t-foreach="learningState.courseUnits" t-as="unit" t-key="unit.id">
                      <UnitCard unit="unit" onUnitClick.bind="onUnitClick"/>
                    </t>
                  </t>
                </div>
              </div>
            </div>

            <div class="col-md-4">
              <ProgressPanel userStreak="learningState.userStreak"
                           unitsCount="learningState.courseUnits.length"
                           completedUnitsCount="0"/>
            </div>
          </div>
        </div>
      </t>
    </div>
  `;
  static components = { UnitCard, ProgressPanel, Navbar };

  setup() {
    console.log('🔧 LearningDashboard setup() called');

    this.state = useState({
      isReady: false
    });

    this.learningState = useState({
      selectedLanguage: 'EN',
      selectedLanguageName: 'English',
      courseUnits: [],
      userStreak: 0,
      activeUnit: null
    });

    onWillStart(async () => {
      console.log('🚀 onWillStart called');
      try {
        await this.loadInitialData();
        this.state.isReady = true;
        console.log('✅ State set to ready');
      } catch (error) {
        console.error('❌ Error in onWillStart:', error);
        this.state.isReady = true; // Set to true anyway to show something
      }
    });
  }

  async loadInitialData() {
    try {
      const dataScript = document.getElementById('language-learning-data');
      if (dataScript) {
        const data = JSON.parse(dataScript.textContent);
        Object.assign(this.learningState, {
          selectedLanguage: data.selectedLanguage || 'EN',
          selectedLanguageName: data.selectedLanguageName || 'English',
          courseUnits: data.courseUnits || [],
          userStreak: data.userStreak || 0,
          activeUnit: data.activeUnit || null
        });
        console.log('✅ Learning data loaded:', this.learningState);
      }
    } catch (error) {
      console.error('❌ Error loading initial data:', error);
    }
  }

  onUnitClick(unitId) {
    const unit = this.learningState.courseUnits.find(u => u.id === unitId);
    if (unit) {
      this.learningState.activeUnit = unit;
      console.log('🎯 Unit selected:', unit);
    }
  }
}

// Start the app when DOM is ready
async function startApp() {
  try {
    console.log('🎯 Mounting OWL app...');

    const appContainer = document.getElementById('language-learning-app');
    if (!appContainer) {
      throw new Error('Container #language-learning-app not found');
    }

    console.log('📦 Container found, clearing content...');
    // Clear any existing content before mounting
    appContainer.innerHTML = '';

    const app = await mount(LearningDashboard, appContainer);
    console.log('✅ OWL app mounted successfully!', app);

  } catch (error) {
    console.error('❌ Error starting app:', error);

    // Fallback
    const appContainer = document.getElementById('language-learning-app');
    if (appContainer) {
      appContainer.innerHTML = `
        <div class="alert alert-danger m-4">
          <h5><i class="bi bi-exclamation-triangle"></i> Erreur OWL</h5>
          <p>Impossible de charger l'interface OWL.</p>
          <small class="text-muted">Erreur: ${error.message}</small>
        </div>
      `;
    }
  }
}

// Start when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startApp);
} else {
  startApp();
}