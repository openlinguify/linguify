'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Globe, CheckCircle } from 'lucide-react';
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from '@/components/ui/alert';
import OnboardingField from '../OnboardingField';
import { OnboardingFormData } from '../../hooks/useOnboardingForm';
import { useLocalizedLanguages } from '@/core/utils/languageUtils';

interface LanguagesStepProps {
  formData: OnboardingFormData;
  validationErrors: Record<string, string>;
  onChange: (field: keyof OnboardingFormData, value: string) => void;
}

export const LanguagesStep: React.FC<LanguagesStepProps> = ({
  formData,
  validationErrors,
  onChange,
}) => {
  const { t } = useTranslation();
  const { getLanguageOptions, getLocalizedLabel } = useLocalizedLanguages();

  // Helper to get display value for languages
  const getLanguageDisplayName = (code: string): string => {
    return getLocalizedLabel(getLanguageOptions(), code);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <Globe className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
        <h3 className="text-xl font-bold">{t('onboarding.steps.languages.title', {}, "Your languages")}</h3>
      </div>

      <Alert className="mb-4">
        <AlertTitle className="flex items-center">
          <Globe className="h-4 w-4 mr-2" />
          {t('onboarding.steps.languages.title', {}, "Your languages")}
        </AlertTitle>
        <AlertDescription>
          {t('onboarding.steps.languages.description', {}, "Your native language and target language must be different. This helps us personalize your learning path.")}
        </AlertDescription>
      </Alert>

      <div className="space-y-4">
        <OnboardingField
          field="native_language"
          defaultLabel="Native Language"
          value={formData.native_language}
          onChange={onChange}
          type="select"
          options={getLanguageOptions()}
          validationErrors={validationErrors}
          defaultHelperText="The language you are fluent in"
          required={true}
        />

        <div className="relative">
          <OnboardingField
            field="target_language"
            defaultLabel="Target Language"
            value={formData.target_language}
            onChange={onChange}
            type="select"
            options={getLanguageOptions()}
            validationErrors={validationErrors}
            defaultHelperText="The language you want to learn"
            required={true}
          />

          {formData.native_language && formData.target_language &&
            formData.native_language !== formData.target_language && (
              <div className="mt-2 text-sm text-green-600 dark:text-green-400 flex items-center">
                <CheckCircle className="h-4 w-4 mr-1" />
                <span>
                  {t('onboarding.steps.languages.fields.learningConfirmation', 
                    { 
                      target: getLanguageDisplayName(formData.target_language), 
                      native: getLanguageDisplayName(formData.native_language) 
                    }, 
                    `Learning ${getLanguageDisplayName(formData.target_language)} from ${getLanguageDisplayName(formData.native_language)}`)}
                </span>
              </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default LanguagesStep;