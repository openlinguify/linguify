/** @odoo-module **/

import { xml } from "@odoo/owl";
import templatesXML from 'raw-loader!./templates.xml';

// Simple template registry - just define templates directly
export const templates = {
  "language_learning.UnitCard": xml`
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
</div>`,

  "language_learning.ProgressPanel": xml`
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
</div>`,

  "language_learning.Navbar": xml`
<div class="navbar-linguify">
  <!-- Gauche: Navigation + Actions principales -->
  <div class="navbar-section">
    <!-- Start Learning Button - Left side -->
    <button t-on-click="startLearning" class="btn-navbar btn-navbar-primary">
      <i class="bi bi-play-circle"></i>
      <span class="d-none d-xl-inline">Start Learning</span>
    </button>

    <!-- Navigation tabs -->
    <div class="nav-tabs-group">
      <a href="#" class="nav-tab active" t-on-click="() => this.selectTab('dashboard')">
        <i class="bi bi-house"></i>
        Dashboard
      </a>
      <a href="#" class="nav-tab" t-on-click="() => this.selectTab('lessons')">
        <i class="bi bi-book"></i>
        Lessons
      </a>
      <a href="#" class="nav-tab" t-on-click="() => this.selectTab('progress')">
        <i class="bi bi-trophy"></i>
        Progress
      </a>
      <a href="#" class="nav-tab" t-on-click="() => this.selectTab('community')">
        <i class="bi bi-people"></i>
        Community
      </a>
    </div>

    <div class="container-extra">
      <!-- Language Selector -->
      <div class="language-selector d-flex align-items-center me-3">
        <span class="navbar-label me-2">Learning:</span>
        <button class="btn btn-outline-primary btn-sm dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown">
          <t t-esc="languageFlag"/> <t t-esc="props.selectedLanguageName"/>
        </button>
        <ul class="dropdown-menu">
          <li><a class="dropdown-item" href="#" t-on-click="() => this.selectLanguage('EN')">🇬🇧 English</a></li>
          <li><a class="dropdown-item" href="#" t-on-click="() => this.selectLanguage('FR')">🇫🇷 Français</a></li>
          <li><a class="dropdown-item" href="#" t-on-click="() => this.selectLanguage('ES')">🇪🇸 Español</a></li>
          <li><a class="dropdown-item" href="#" t-on-click="() => this.selectLanguage('DE')">🇩🇪 Deutsch</a></li>
        </ul>
      </div>

      <!-- Streak Display -->
      <div class="streak-display d-flex align-items-center me-3">
        <i class="bi bi-fire text-warning me-1"></i>
        <span class="fw-bold"><t t-esc="props.userStreak"/></span>
        <span class="d-none d-lg-inline ms-1">day streak</span>
      </div>
    </div>
  </div>

  <!-- Droite: Actions et filtres contextuels -->
  <div class="navbar-section-right">
    <!-- Level Display -->
    <div class="level-display d-flex align-items-center me-3">
      <span class="navbar-label me-2">Level:</span>
      <span class="badge bg-primary"><t t-esc="userLevel"/></span>
    </div>

    <!-- Quick Actions -->
    <div class="navbar-actions-group">
      <button t-on-click="openPractice" class="btn-navbar btn-navbar-outline" title="Quick Practice">
        <i class="bi bi-lightning"></i>
        <span class="d-none d-xl-inline">Practice</span>
      </button>

      <button t-on-click="openVocabulary" class="btn-navbar btn-navbar-outline" title="Vocabulary">
        <i class="bi bi-journal-text"></i>
        <span class="d-none d-xl-inline">Vocabulary</span>
      </button>

      <button t-on-click="openSettings" class="btn-navbar btn-navbar-outline" title="Language Learning Settings">
        <i class="bi bi-gear"></i>
        <span class="d-none d-xxl-inline">Settings</span>
      </button>
    </div>
  </div>
</div>`,

  "language_learning.Dashboard": xml`
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
    <LanguageLearningNavbar selectedLanguage="learningState.selectedLanguage"
                            selectedLanguageName="learningState.selectedLanguageName"
                            userStreak="learningState.userStreak"
                            onLanguageChange.bind="onLanguageChange"
                            onTabChange.bind="onTabChange"/>

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
</div>`
};

console.log('🎯 Templates loaded:', Object.keys(templates));