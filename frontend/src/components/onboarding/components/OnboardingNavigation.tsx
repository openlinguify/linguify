'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Button } from '@/components/ui/button';
import { ArrowLeft, ArrowRight, Save, Sparkles, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface OnboardingNavigationProps {
  currentStep: number;
  totalSteps: number;
  isSubmitting: boolean;
  isNextDisabled?: boolean;
  changedFieldsCount: number;
  onPrevStep: () => void;
  onNextStep: () => void;
  onSubmit: () => void;
  onComplete: () => void;
}

export const OnboardingNavigation: React.FC<OnboardingNavigationProps> = ({
  currentStep,
  totalSteps,
  isSubmitting,
  isNextDisabled = false,
  changedFieldsCount,
  onPrevStep,
  onNextStep,
  onSubmit,
  onComplete,
}) => {
  const { t } = useTranslation();

  return (
    <motion.div
      className="border-t border-gray-200 dark:border-gray-800 p-6 flex justify-between"
      initial={{ opacity: 0.8, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Back button */}
      <Button
        variant="outline"
        onClick={onPrevStep}
        disabled={currentStep === 1 || currentStep === totalSteps || isSubmitting}
        className={currentStep === 1 || currentStep === totalSteps ? "invisible" : ""}
        aria-label="Go back to previous step"
        onKeyDown={(e) => {
          // Use left arrow as shortcut for back
          if (e.key === 'ArrowLeft' && !(currentStep === 1 || currentStep === totalSteps || isSubmitting)) {
            e.preventDefault();
            onPrevStep();
          }
        }}
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        {t('onboarding.actions.back', {}, "Back")}
      </Button>

      {/* Action buttons */}
      <div className="flex gap-2">
        {currentStep === totalSteps ? (
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{
              duration: 0.5,
              repeat: 2,
              repeatType: "reverse"
            }}
          >
            <Button
              onClick={onComplete}
              className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
              aria-label="Complete onboarding and start learning"
              autoFocus
            >
              <Sparkles className="h-4 w-4 mr-2" />
              {t('onboarding.actions.startLearning', {}, "Start Learning")}
            </Button>
          </motion.div>
        ) : currentStep === 6 ? (
          <>
            <Button
              variant="outline"
              onClick={onNextStep}
              disabled={isSubmitting}
              aria-label="Continue to next step"
            >
              {t('onboarding.actions.continue', {}, "Continue")}
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>

            <Button
              onClick={onSubmit}
              disabled={isSubmitting || changedFieldsCount === 0}
              className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 relative"
              aria-label="Save profile changes"
              aria-busy={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  {t('onboarding.messages.saving', {}, "Saving...")}
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {t('onboarding.actions.saveProfile', {}, "Save Profile")}
                </>
              )}
            </Button>
          </>
        ) : (
          <Button
            onClick={onNextStep}
            disabled={isSubmitting || isNextDisabled}
            aria-label="Continue to next step"
            className="relative group"
            autoFocus={currentStep < totalSteps - 1}
            onKeyDown={(e) => {
              // Use right arrow as shortcut for next
              if (e.key === 'ArrowRight' && !(isSubmitting || isNextDisabled)) {
                e.preventDefault();
                onNextStep();
              }
            }}
          >
            <span className="flex items-center">
              {t('onboarding.actions.next', {}, "Next")}
              <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
            </span>

            {isNextDisabled && (
              <span className="absolute -top-10 right-0 bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                {t('onboarding.messages.completeRequired', {}, "Complete required fields")}
              </span>
            )}
          </Button>
        )}
      </div>
    </motion.div>
  );
};

export default OnboardingNavigation;