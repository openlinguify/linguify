import { Component, mount, xml, useState, onWillStart } from "@odoo/owl";

console.log('🚀 Language Learning OWL App Starting (NPM version)...');

// Import styles
import './scss/learning.scss';

// Import templates from separate file
import {
  UnitCardTemplate,
  ProgressPanelTemplate,
  LanguageLearningNavbarTemplate,
  LearningDashboardTemplate
} from './templates.js';

// Unit Card Component
class UnitCard extends Component {
  static template = UnitCardTemplate;

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
  static template = ProgressPanelTemplate;

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

// Language Learning Navbar Component - Linguify Style
class LanguageLearningNavbar extends Component {
  static template = LanguageLearningNavbarTemplate;

  static props = {
    selectedLanguage: String,
    selectedLanguageName: String,
    userStreak: Number,
    onLanguageChange: { type: Function, optional: true },
    onTabChange: { type: Function, optional: true }
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

  get userLevel() {
    // Calculate user level based on progress
    return 'Beginner'; // For now, could be calculated from props
  }

  startLearning() {
    console.log('Starting learning session...');
    // Scroll to first unit or start first lesson
    if (this.props.onTabChange) {
      this.props.onTabChange('start-learning');
    }
  }

  selectTab(tab) {
    console.log('Selected tab:', tab);
    if (this.props.onTabChange) {
      this.props.onTabChange(tab);
    }
  }

  selectLanguage(langCode) {
    console.log('Selected language:', langCode);
    if (this.props.onLanguageChange) {
      this.props.onLanguageChange(langCode);
    }
  }

  openPractice() {
    console.log('Opening practice...');
    // Open practice modal or start practice session
  }

  openVocabulary() {
    console.log('Opening vocabulary...');
    // Open vocabulary modal or navigate to vocabulary page
  }

  openSettings() {
    console.log('Opening settings...');
    // Navigate to settings page
    window.location.href = '/settings/language_learning/';
  }
}

// Main Dashboard Component
class LearningDashboard extends Component {
  static template = LearningDashboardTemplate;
  static components = { UnitCard, ProgressPanel, LanguageLearningNavbar };

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

  onLanguageChange(langCode) {
    console.log('Language change requested:', langCode);
    // Here you would update the learning language
    // Could make an API call to update user preferences
    this.learningState.selectedLanguage = langCode;
    const languageNames = {
      'EN': 'English',
      'FR': 'Français',
      'ES': 'Español',
      'DE': 'Deutsch'
    };
    this.learningState.selectedLanguageName = languageNames[langCode] || langCode;
  }

  onTabChange(tab) {
    console.log('Tab change requested:', tab);
    // Handle navigation between different sections
    if (tab === 'start-learning') {
      // Scroll to first unit
      const firstUnit = document.querySelector('.unit-card');
      if (firstUnit) {
        firstUnit.scrollIntoView({ behavior: 'smooth' });
      }
    }
    // Could update state to show different views
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