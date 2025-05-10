'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Info } from 'lucide-react';
import OnboardingLanguageSelector from './OnboardingLanguageSelector';
import KeyboardHelpModal from './KeyboardHelpModal';

interface StepInfo {
  id: number;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface OnboardingHeaderProps {
  currentStep: number;
  totalSteps: number;
  steps: StepInfo[];
  onShowDevTools: () => void;
  onSkipOnboarding: () => void;
  onGoToStep: (step: number) => void;
  onLanguageChange?: (language: string) => void;
}

export const OnboardingHeader: React.FC<OnboardingHeaderProps> = ({
  currentStep,
  totalSteps,
  steps,
  onShowDevTools,
  onSkipOnboarding,
  onGoToStep,
  onLanguageChange,
}) => {
  const { t } = useTranslation();
  
  const progressPercentage = (currentStep / totalSteps) * 100;

  return (
    <div className="bg-gradient-to-r from-violet-500 to-purple-600 p-6 text-white">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 id="onboarding-title" className="text-xl font-bold">{t('onboarding.title', {}, "Welcome to Linguify")}</h2>
          <p className="text-sm text-white/80">{steps[currentStep - 1].title}</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Language Selector */}
          <OnboardingLanguageSelector onLanguageChange={onLanguageChange} />

          {/* Keyboard Shortcuts Help */}
          <KeyboardHelpModal />

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-white hover:bg-white/20"
                  onClick={onShowDevTools}
                >
                  <Info className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{t('onboarding.devTools.toggle', {}, "Toggle developer tools")}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <Button variant="ghost" onClick={onSkipOnboarding} className="text-white hover:text-white/80">
            {t('onboarding.actions.skip', {}, "Skip")}
          </Button>
        </div>
      </div>

      {/* Progress bar */}
      <div className="relative">
        <Progress
          value={progressPercentage}
          className="h-2 bg-white/30"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(progressPercentage)}
          aria-label={t('onboarding.progress.label', { current: currentStep, total: totalSteps }, `Onboarding Progress: Step ${currentStep} of ${totalSteps}`)}
        />
        <motion.div
          className="absolute h-2 top-0 left-0 rounded-full bg-white/70 pointer-events-none"
          initial={{ width: 0 }}
          animate={{
            width: 8,
            x: progressPercentage < 3 ? 0 : `${progressPercentage - 3}%`
          }}
          transition={{
            duration: 0.5,
            delay: 0.2,
            ease: "easeOut"
          }}
        />
      </div>
      <div className="flex justify-between text-xs mt-2">
        <span className="flex items-center">
          <span className="inline-block w-2 h-2 bg-white rounded-full mr-1.5 animate-pulse" aria-hidden="true"></span>
          {t('onboarding.progress.step', { current: currentStep.toString(), total: totalSteps.toString() }, `Step ${currentStep} of ${totalSteps}`)}
        </span>
        <motion.span
          key={progressPercentage}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {t('onboarding.progress.percentComplete', { percent: Math.round(progressPercentage).toString() }, `${Math.round(progressPercentage)}% Complete`)}
        </motion.span>
      </div>

      {/* Step pills for direct navigation */}
      <nav aria-label="Onboarding steps">
        <div className="flex gap-1 mt-3 overflow-x-auto pb-1" role="tablist">
          {steps.map((step, index) => {
            const StepIcon = step.icon;
            const isCurrentStep = currentStep === index + 1;
            return (
              <button
                key={index}
                onClick={() => onGoToStep(index + 1)}
                onKeyDown={(e) => {
                  // Move to previous/next tab with arrow keys
                  if (e.key === 'ArrowLeft' && index > 0) {
                    onGoToStep(index);
                    e.preventDefault();
                  } else if (e.key === 'ArrowRight' && index < steps.length - 1) {
                    onGoToStep(index + 2);
                    e.preventDefault();
                  }
                }}
                className={`px-2 py-1 rounded-full text-xs flex items-center transition-colors ${
                  isCurrentStep
                    ? "bg-white text-purple-600 font-medium shadow-sm"
                    : "bg-white/20 hover:bg-white/30"
                }`}
                role="tab"
                aria-selected={isCurrentStep}
                aria-controls={`step-panel-${index + 1}`}
                id={`step-tab-${index + 1}`}
                tabIndex={isCurrentStep ? 0 : -1}
                aria-current={isCurrentStep ? "step" : undefined}
                aria-label={`Go to step ${index + 1}: ${step.title}`}
              >
                <StepIcon className={`h-3 w-3 mr-1 ${isCurrentStep ? 'text-purple-600' : 'text-white'}`} aria-hidden="true" />
                <span className="hidden sm:inline">{step.title}</span>
                <span className="inline sm:hidden">{index + 1}</span>
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
};

export default OnboardingHeader;