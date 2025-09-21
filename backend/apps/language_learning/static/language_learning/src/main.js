/** @odoo-module **/

import { Component, mount, useState, onWillStart, whenReady } from "@odoo/owl";
import { templates } from "./assets";
import { UnitCard } from "./components/unit_card";
import { ModuleCard } from "./components/module_card";

console.log('🚀 Language Learning OWL App Starting (NPM version)...');

// Import styles
import './scss/learning.scss';

// Unit View Component
class UnitView extends Component {
  static template = "language_learning.UnitView";
  static components = { ModuleCard };

  static props = {
    unit: Object,
    modules: Array,
    onBackClick: { type: Function, optional: true },
    onModuleClick: { type: Function, optional: true }
  };

  onBackClick() {
    if (this.props.onBackClick) {
      this.props.onBackClick();
    }
  }

  onModuleClick(moduleId) {
    if (this.props.onModuleClick) {
      this.props.onModuleClick(moduleId);
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
  static template = "language_learning.ProgressPanel";

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
  static template = "language_learning.Navbar";

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
  static template = "language_learning.Dashboard";
  static components = { UnitCard, ProgressPanel, LanguageLearningNavbar, UnitView };

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
      activeUnit: null,
      activeUnitModules: []
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

  async onUnitClick(unitId) {
    const unit = this.learningState.courseUnits.find(u => u.id === unitId);
    if (unit) {
      console.log('🎯 Unit selected:', unit);

      // Charger les modules de l'unité
      try {
        const modules = await this.loadUnitModules(unitId);
        this.learningState.activeUnit = unit;
        this.learningState.activeUnitModules = modules;
        console.log('✅ Modules loaded:', modules);
      } catch (error) {
        console.error('❌ Error loading modules:', error);
        // Afficher l'unité même si on ne peut pas charger les modules
        this.learningState.activeUnit = unit;
        this.learningState.activeUnitModules = [];
      }
    }
  }

  onBackToUnits() {
    console.log('🔙 Returning to units list');
    this.learningState.activeUnit = null;
    this.learningState.activeUnitModules = [];
  }

  onModuleClick(moduleId) {
    console.log('📖 Module clicked:', moduleId);
    // Ici on pourrait naviguer vers le contenu du module
    // Pour l'instant, on affiche juste un message
    alert(`Module ${moduleId} sélectionné! (Navigation vers le contenu du module à implémenter)`);
  }

  async loadUnitModules(unitId) {
    try {
      // Faire un appel API pour charger les modules de l'unité
      const response = await fetch(`/language_learning/api/units/${unitId}/modules/`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return data.modules || [];
    } catch (error) {
      console.error('❌ Error fetching unit modules:', error);
      // Fallback: utiliser des données de test ou retourner un tableau vide
      return [];
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

// Mount the Language Learning component when the container is ready
whenReady(() => {
  try {
    console.log('🎯 Mounting OWL app...');

    const appContainer = document.getElementById('language-learning-app');
    if (!appContainer) {
      throw new Error('Container #language-learning-app not found');
    }

    console.log('📦 Container found, clearing content...');
    // Clear any existing content before mounting
    appContainer.innerHTML = '';

    mount(LearningDashboard, appContainer, {
      dev: true,
      name: "Language Learning App",
    });

    console.log('✅ OWL app mounted successfully!');

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
});