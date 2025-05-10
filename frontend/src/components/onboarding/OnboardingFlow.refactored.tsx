'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Globe,
  BookOpen,
  User,
  Languages,
  Settings,
  CheckCircle
} from 'lucide-react';

// Hooks
import { useAuthContext } from '@/core/auth/AuthProvider';
import { useOnboardingForm } from './hooks/useOnboardingForm';
import { useOnboardingValidation } from './hooks/useOnboardingValidation';

// Components
import OnboardingHeader from './components/OnboardingHeader';
import OnboardingDevTools from './components/OnboardingDevTools';
import OnboardingNavigation from './components/OnboardingNavigation';
import {
  WelcomeStep,
  PersonalInfoStep,
  LanguagesStep,
  LearningPreferencesStep,
  ReviewStep,
  CompletionStep
} from './components/steps';

interface OnboardingFlowProps {
  onComplete: () => void;
}

export const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete }) => {
  // Hooks
  const { user } = useAuthContext();
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
  
  // Total number of steps
  const totalSteps = 6;

  // Define step information
  const steps = [
    {
      id: 1,
      title: "Welcome",
      description: "Begin your language learning journey",
      icon: Globe
    },
    {
      id: 2,
      title: "Personal Info",
      description: "Tell us about yourself",
      icon: User
    },
    {
      id: 3,
      title: "Languages",
      description: "Select your languages",
      icon: Languages
    },
    {
      id: 4,
      title: "Learning Goals",
      description: "Customize your experience",
      icon: BookOpen
    },
    {
      id: 5,
      title: "Review",
      description: "Confirm your settings",
      icon: Settings
    },
    {
      id: 6,
      title: "Completion",
      description: "You're all set!",
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
        setStep(step + 1);
      } else {
        submitForm();
      }
    }
  };

  const prevStep = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const goToStep = (stepNumber: number) => {
    if (stepNumber >= 1 && stepNumber <= totalSteps) {
      setStep(stepNumber);
    }
  };

  // Submit the form
  const submitForm = async () => {
    const success = await handleSubmit();
    if (success) {
      // Move to the final step
      setStep(totalSteps);
      
      // Set a timeout to allow the user to see the completion screen
      setTimeout(() => {
        onComplete();
      }, 2000);
    }
  };

  // Check if the Next button should be disabled
  const isNextDisabled = step === 3 && (
    !formData.native_language ||
    !formData.target_language ||
    formData.native_language === formData.target_language
  );

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
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-2xl overflow-hidden"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        {/* Header with progress and navigation */}
        <OnboardingHeader
          currentStep={step}
          totalSteps={totalSteps}
          steps={steps}
          onShowDevTools={() => setShowDevTools(!showDevTools)}
          onSkipOnboarding={skipOnboarding}
          onGoToStep={goToStep}
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

              {/* Step 5: Review Information */}
              {step === 5 && (
                <ReviewStep
                  formData={formData}
                  initialData={initialData}
                  changedFieldsCount={changedFieldsCount}
                  onRefreshData={fetchCurrentProfile}
                />
              )}

              {/* Step 6: Completion */}
              {step === 6 && (
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
          isSubmitting={isSubmitting}
          isNextDisabled={isNextDisabled}
          changedFieldsCount={changedFieldsCount}
          onPrevStep={prevStep}
          onNextStep={nextStep}
          onSubmit={submitForm}
          onComplete={onComplete}
        />
      </motion.div>
    </div>
  );
};

export default OnboardingFlow;