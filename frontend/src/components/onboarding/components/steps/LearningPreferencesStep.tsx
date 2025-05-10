'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { BookOpen, Settings } from 'lucide-react';
import {
  Card,
  CardContent,
} from '@/components/ui/card';
import OnboardingField from '../OnboardingField';
import { OnboardingFormData } from '../../hooks/useOnboardingForm';
import { useLocalizedLanguages } from '@/core/utils/languageUtils';

interface LearningPreferencesStepProps {
  formData: OnboardingFormData;
  validationErrors: Record<string, string>;
  onChange: (field: keyof OnboardingFormData, value: string) => void;
}

export const LearningPreferencesStep: React.FC<LearningPreferencesStepProps> = ({
  formData,
  validationErrors,
  onChange,
}) => {
  const { t } = useTranslation();
  const { getLevelOptions, getObjectivesOptions, getInterfaceLanguageOptions } = useLocalizedLanguages();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <BookOpen className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
        <h3 className="text-xl font-bold">{t('onboarding.steps.learningPreferences.title', {}, "Learning preferences")}</h3>
      </div>

      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-0 mb-6">
        <CardContent className="p-4">
          <h4 className="font-medium flex items-center mb-2">
            <Settings className="mr-2 h-4 w-4 text-blue-500" />
            {t('onboarding.steps.learningPreferences.settingsBoxTitle', {}, "Customize Your Learning Experience")}
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {t('onboarding.steps.learningPreferences.settingsBoxDescription', {}, "These settings help tailor your lessons and determine which content you'll see.")}
          </p>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <OnboardingField
          field="language_level"
          defaultLabel="Your Current Level"
          value={formData.language_level}
          onChange={onChange}
          type="select"
          options={getLevelOptions()}
          validationErrors={validationErrors}
          defaultHelperText="Your current proficiency in the target language"
        />

        <OnboardingField
          field="objectives"
          defaultLabel="Learning Objectives"
          value={formData.objectives}
          onChange={onChange}
          type="select"
          options={getObjectivesOptions()}
          validationErrors={validationErrors}
          defaultHelperText="What you want to achieve with your language learning"
        />

        <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
          <OnboardingField
            field="interface_language"
            defaultLabel="Interface Language"
            value={formData.interface_language}
            onChange={onChange}
            type="select"
            options={getInterfaceLanguageOptions()}
            validationErrors={validationErrors}
            defaultHelperText="The language used for buttons, menus, and instructions"
          />
        </div>
      </div>
    </div>
  );
};

export default LearningPreferencesStep;