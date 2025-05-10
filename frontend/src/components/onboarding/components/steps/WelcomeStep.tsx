'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { User, Languages, Sparkles } from 'lucide-react';

export const WelcomeStep: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col items-center text-center space-y-6 flex-grow justify-center min-h-[400px]">
      <div className="bg-indigo-100 dark:bg-indigo-900/50 p-4 rounded-full">
        <Sparkles className="h-12 w-12 text-indigo-600 dark:text-indigo-400" />
      </div>
      <h3 className="text-2xl font-bold">{t('onboarding.steps.welcome.title', {}, "Welcome to Linguify!")}</h3>
      <p className="text-gray-600 dark:text-gray-400 max-w-md">
        {t('onboarding.steps.welcome.description', {}, "Let's set up your profile and language preferences to customize your learning experience.")}
      </p>
      <p className="text-sm text-gray-500 dark:text-gray-500">
        {t('onboarding.steps.welcome.timePromise', {}, "This will only take 2 minutes to complete.")}
      </p>

      {/* Feature highlights */}
      <div className="w-full max-w-md grid grid-cols-2 gap-4 mt-4">
        <div className="flex flex-col items-center justify-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <User className="h-8 w-8 text-purple-500 mb-2" />
          <h4 className="font-medium">{t('onboarding.steps.welcome.features.profileSetup.title', {}, "Profile Setup")}</h4>
          <p className="text-xs text-gray-500">{t('onboarding.steps.welcome.features.profileSetup.description', {}, "Personalize your account")}</p>
        </div>
        <div className="flex flex-col items-center justify-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <Languages className="h-8 w-8 text-blue-500 mb-2" />
          <h4 className="font-medium">{t('onboarding.steps.welcome.features.languageSettings.title', {}, "Language Settings")}</h4>
          <p className="text-xs text-gray-500">{t('onboarding.steps.welcome.features.languageSettings.description', {}, "Choose what to learn")}</p>
        </div>
      </div>
    </div>
  );
};

export default WelcomeStep;