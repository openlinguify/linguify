'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { User } from 'lucide-react';
import {
  Alert,
  AlertDescription,
} from '@/components/ui/alert';
import OnboardingField from '../OnboardingField';
import { OnboardingFormData } from '../../hooks/useOnboardingForm';

interface PersonalInfoStepProps {
  formData: OnboardingFormData;
  validationErrors: Record<string, string>;
  onChange: (field: keyof OnboardingFormData, value: string) => void;
}

export const PersonalInfoStep: React.FC<PersonalInfoStepProps> = ({
  formData,
  validationErrors,
  onChange,
}) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6 min-h-[400px] flex flex-col justify-start">
      <div className="flex items-center space-x-3 mb-6">
        <User className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
        <h3 className="text-xl font-bold">{t('onboarding.steps.personalInfo.title', {}, "Tell us about yourself")}</h3>
      </div>

      <Alert className="mb-4">
        <AlertDescription>
          {t('onboarding.steps.personalInfo.description', {}, "This information helps personalize your learning experience. Fields marked with * are required.")}
        </AlertDescription>
      </Alert>

      <div className="grid grid-cols-2 gap-4">
        <OnboardingField
          field="first_name"
          defaultLabel="First Name"
          value={formData.first_name}
          onChange={onChange}
          validationErrors={validationErrors}
          required={true}
        />
        <OnboardingField
          field="last_name"
          defaultLabel="Last Name"
          value={formData.last_name}
          onChange={onChange}
          validationErrors={validationErrors}
          required={true}
        />
      </div>

      <OnboardingField
        field="username"
        defaultLabel="Username"
        value={formData.username}
        onChange={onChange}
        validationErrors={validationErrors}
        defaultHelperText="This will be used as your display name on the platform"
        required={true}
      />

      <OnboardingField
        field="bio"
        defaultLabel="Bio (Optional)"
        value={formData.bio || ""}
        onChange={onChange}
        type="textarea"
        validationErrors={validationErrors}
        defaultHelperText="Tell other learners a bit about yourself"
      />
    </div>
  );
};

export default PersonalInfoStep;