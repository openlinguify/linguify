// src/components/onboarding/OnboardingFlow.tsx
'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './styles/focusIndicator.css';
import {
  Globe,
  BookOpen,
  User,
  Languages,
  Settings,
  CheckCircle,
  FileText
} from 'lucide-react';

// Hooks
import { useAuthContext } from '@/core/auth/AuthProvider';
import { useOnboardingForm } from './hooks/useOnboardingForm';
import { useOnboardingValidation } from './hooks/useOnboardingValidation';
import { useFocusManagement } from './hooks/useFocusManagement';
import { useTranslation } from '@/core/i18n/useTranslations';

// Components
import OnboardingHeader from './components/OnboardingHeader';
import OnboardingDevTools from './components/OnboardingDevTools';
import OnboardingNavigation from './components/OnboardingNavigation';
import FocusTrap from './components/FocusTrap';
import A11yAnnouncer from './components/A11yAnnouncer';
import FirstTimeUserTutorial from './components/FirstTimeUserTutorial';
import {
  WelcomeStep,
  PersonalInfoStep,
  LanguagesStep,
  LearningPreferencesStep,
  TermsAcceptanceStep,
  ReviewStep,
  CompletionStep
} from './components/steps';

/**
 * Linguify Onboarding Flow Component
 *
 * A comprehensive onboarding process for new users to set up their language learning profile.
 * Features step-by-step configuration, validation, and developer tools for debugging.
 */

interface OnboardingFlowProps {
  onComplete: () => void;
  finalFocusRef?: React.RefObject<HTMLElement>;
}

const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete, finalFocusRef }) => {
  // Hooks
  const { user } = useAuthContext();
  const { t } = useTranslation();
  const {
    formData,
    initialData,
    validationErrors,
    isSubmitting,
    lastServerResponse,
    apiRequests,
    changedFieldsCount,
    fetchCurrentProfile,
    handleInputChange,
    handleSubmit,
    clearApiRequests
  } = useOnboardingForm();

  const { validateStep } = useOnboardingValidation();

  // State for current step and UI options
  const [step, setStep] = useState(1);
  const [showDevTools, setShowDevTools] = useState(false);

  // State for accessibility announcements
  const [announcement, setAnnouncement] = useState('');

  // State for tutorial
  const [showTutorial, setShowTutorial] = useState(true);

  // Focus management
  const { containerRef, refocusOnUpdate } = useFocusManagement({
    trapFocus: true,
    autoFocus: true,
    finalFocusRef
  });

  // Total number of steps
  const totalSteps = 7;

  // Define step information for better navigation and context
  const steps = [
    {
      id: 1,
      title: t('onboarding.steps.welcome.title', {}, "Welcome"),
      description: t('onboarding.steps.welcome.description', {}, "Begin your language learning journey"),
      icon: Globe
    },
    {
      id: 2,
      title: t('onboarding.steps.personalInfo.title', {}, "Personal Info"),
      description: t('onboarding.steps.personalInfo.description', {}, "Tell us about yourself"),
      icon: User
    },
    {
      id: 3,
      title: t('onboarding.steps.languages.title', {}, "Languages"),
      description: t('onboarding.steps.languages.description', {}, "Select your languages"),
      icon: Languages
    },
    {
      id: 4,
      title: t('onboarding.steps.learningPreferences.title', {}, "Learning Goals"),
      description: t('onboarding.steps.learningPreferences.description', {}, "Customize your experience"),
      icon: BookOpen
    },
    {
      id: 5,
      title: t('onboarding.steps.terms.title', {}, "Legal Terms"),
      description: t('onboarding.steps.terms.description', {}, "Review our terms and conditions"),
      icon: FileText
    },
    {
      id: 6,
      title: t('onboarding.steps.review.title', {}, "Review"),
      description: t('onboarding.steps.review.description', {}, "Confirm your settings"),
      icon: Settings
    },
    {
      id: 7,
      title: t('onboarding.steps.completion.title', {}, "Completion"),
      description: t('onboarding.steps.completion.description', {}, "You're all set!"),
      icon: CheckCircle
    }
  ];

  // Skip the entire onboarding
  const skipOnboarding = () => {
    localStorage.setItem("onboardingCompleted", "true");
    onComplete();
  };

  // Navigation functions
  const nextStep = () => {
    // Validate current step
    const { isValid } = validateStep(step, formData);

    if (isValid) {
      if (step < totalSteps) {
        const nextStepNumber = step + 1;
        setStep(nextStepNumber);
        // Announce step change to screen readers
        setAnnouncement(t('onboarding.a11y.stepChange', { step: nextStepNumber.toString(), total: totalSteps.toString() }, `Step ${nextStepNumber} of ${totalSteps}: ${steps[nextStepNumber - 1].title}`));
        // Need to refocus after step change
        setTimeout(() => refocusOnUpdate(), 100);
      } else {
        submitForm();
      }
    }
  };

  const prevStep = () => {
    if (step > 1) {
      const prevStepNumber = step - 1;
      setStep(prevStepNumber);
      // Announce step change to screen readers
      setAnnouncement(t('onboarding.a11y.stepChange', { step: prevStepNumber.toString(), total: totalSteps.toString() }, `Step ${prevStepNumber} of ${totalSteps}: ${steps[prevStepNumber - 1].title}`));
      // Need to refocus after step change
      setTimeout(() => refocusOnUpdate(), 100);
    }
  };

  const goToStep = (stepNumber: number) => {
    if (stepNumber >= 1 && stepNumber <= totalSteps) {
      setStep(stepNumber);
      // Announce step change to screen readers
      setAnnouncement(t('onboarding.a11y.stepChange', { step: stepNumber.toString(), total: totalSteps.toString() }, `Step ${stepNumber} of ${totalSteps}: ${steps[stepNumber - 1].title}`));
      // Need to refocus after step change
      setTimeout(() => refocusOnUpdate(), 100);
    }
  };

  // State for tracking loading status
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);

  // Submit the form
  const submitForm = async () => {
    setIsFormSubmitting(true);
    try {
      const success = await handleSubmit();
      if (success) {
        // Move to the final step
        setStep(totalSteps);

        // Set a timeout to allow the user to see the completion screen
        setTimeout(() => {
          onComplete();
        }, 2000);
      }
    } finally {
      setIsFormSubmitting(false);
    }
  };

  // Check if the Next button should be disabled
  const isNextDisabled =
    (step === 3 && (
      !formData.native_language ||
      !formData.target_language ||
      formData.native_language === formData.target_language
    )) ||
    (step === 5 && !formData.termsAccepted); // Disable Next if terms are not accepted

  // Handle keyboard navigation through the form
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    // Global keyboard shortcuts
    if (e.altKey && e.key === 'n' && step < totalSteps && !isFormSubmitting) {
      // Alt+N for Next
      e.preventDefault();
      nextStep();
    } else if (e.altKey && e.key === 'p' && step > 1 && !isFormSubmitting) {
      // Alt+P for Previous
      e.preventDefault();
      prevStep();
    } else if (e.altKey && e.key === 's' && step === 6 && !isFormSubmitting) {
      // Alt+S for Save/Submit (only on review step)
      e.preventDefault();
      submitForm();
    } else if (e.altKey && e.key === 'h') {
      // Alt+H for Help - could toggle a help modal
      e.preventDefault();
      // Optional: toggle keyboard shortcuts help
    }
  }, [step, totalSteps, isFormSubmitting, nextStep, prevStep, submitForm]);

  // Animation variants for page transitions
  const pageVariants = {
    initial: {
      opacity: 0,
      x: 100,
    },
    in: {
      opacity: 1,
      x: 0,
    },
    out: {
      opacity: 0,
      x: -100,
    },
  };
  
  return (
    <>
      {/* First Time User Tutorial */}
      <FirstTimeUserTutorial
        autoShow={showTutorial}
        onClose={() => setShowTutorial(false)}
      />

      <FocusTrap isActive={true} returnFocusOnDeactivate={true} onEscape={skipOnboarding}>
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 onboarding-focus-container"
          role="dialog"
          aria-modal="true"
          aria-labelledby="onboarding-title"
          onKeyDown={handleKeyDown}
        >
      <motion.div
        ref={containerRef as React.RefObject<HTMLDivElement>}
        className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-2xl overflow-hidden"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, type: "spring", stiffness: 170, damping: 26 }}
        role="document"
        tabIndex={-1}
        aria-describedby="onboarding-description"
        onKeyDown={(e) => {
          // Handle escape key to close the dialog (if allowed)
          if (e.key === 'Escape') {
            // Optional: Skip onboarding on escape
            // skipOnboarding();
          }
        }}
      >
        {/* Screen reader description */}
        <div id="onboarding-description" className="sr-only">
          {t('onboarding.a11y.description', {}, 'This is an onboarding dialog to help you set up your language learning profile. Use tab to navigate through the form fields and buttons.')}
        </div>

        {/* Screen reader announcer for dynamic changes */}
        <A11yAnnouncer message={announcement} />
        {/* Header with progress and navigation */}
        <OnboardingHeader
          currentStep={step}
          totalSteps={totalSteps}
          steps={steps}
          onShowDevTools={() => setShowDevTools(!showDevTools)}
          onSkipOnboarding={skipOnboarding}
          onGoToStep={goToStep}
          onLanguageChange={(language) => handleInputChange('interface_language', language)}
        />

        {/* Developer Tools Panel */}
        {showDevTools && (
          <OnboardingDevTools
            formData={formData}
            lastServerResponse={lastServerResponse}
            apiRequests={apiRequests}
            user={user}
            onRefreshData={fetchCurrentProfile}
            onClearLog={clearApiRequests}
          />
        )}

        {/* Content area with step content */}
        <div className="p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial="initial"
              animate="in"
              exit="out"
              variants={pageVariants}
              transition={{ duration: 0.3 }}
              className="min-h-[350px] flex flex-col"
              role="tabpanel"
              id={`step-panel-${step}`}
              aria-labelledby={`step-tab-${step}`}
              tabIndex={0}
              onAnimationComplete={() => {
                // Ensure proper focus when animation completes
                const panel = document.getElementById(`step-panel-${step}`);
                if (panel) {
                  // Find the first interactive element in the panel
                  const focusableElements = panel.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                  );

                  if (focusableElements.length > 0) {
                    // Focus the first interactive element
                    (focusableElements[0] as HTMLElement).focus();
                  } else {
                    // If no interactive elements, focus the panel itself
                    panel.focus();
                  }
                }
              }}
            >
              {/* Step 1: Welcome */}
              {step === 1 && <WelcomeStep />}

              {/* Step 2: Personal Information */}
              {step === 2 && (
                <PersonalInfoStep
                  formData={formData}
                  validationErrors={validationErrors}
                  onChange={handleInputChange}
                />
              )}

              {/* Step 3: Language Selection */}
              {step === 3 && (
                <LanguagesStep
                  formData={formData}
                  validationErrors={validationErrors}
                  onChange={handleInputChange}
                />
              )}

              {/* Step 4: Learning Preferences */}
              {step === 4 && (
                <LearningPreferencesStep
                  formData={formData}
                  validationErrors={validationErrors}
                  onChange={handleInputChange}
                />
              )}

              {/* Step 5: Terms Acceptance */}
              {step === 5 && (
                <TermsAcceptanceStep
                  formData={formData}
                  validationErrors={validationErrors}
                  onChange={handleInputChange}
                />
              )}

              {/* Step 6: Review Information */}
              {step === 6 && (
                <ReviewStep
                  formData={formData}
                  initialData={initialData}
                  changedFieldsCount={changedFieldsCount}
                  onRefreshData={fetchCurrentProfile}
                />
              )}

              {/* Step 7: Completion */}
              {step === 7 && (
                <CompletionStep
                  formData={formData}
                  lastServerResponse={lastServerResponse}
                  showDevTools={showDevTools}
                  onToggleDevTools={() => setShowDevTools(!showDevTools)}
                />
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Navigation buttons */}
        <OnboardingNavigation
          currentStep={step}
          totalSteps={totalSteps}
          isSubmitting={isSubmitting || isFormSubmitting}
          isNextDisabled={isNextDisabled}
          changedFieldsCount={changedFieldsCount}
          onPrevStep={prevStep}
          onNextStep={nextStep}
          onSubmit={submitForm}
          onComplete={onComplete}
        />
      </motion.div>
    </div>
    </FocusTrap>
    </>
  );
};

export default OnboardingFlow;