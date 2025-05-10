'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { OnboardingFormData } from '../hooks/useOnboardingForm';

interface OnboardingFieldProps {
  field: keyof OnboardingFormData;
  defaultLabel: string;
  value: string;
  onChange: (field: keyof OnboardingFormData, value: string) => void;
  type?: 'text' | 'textarea' | 'select';
  options?: { value: string; label: string }[];
  defaultHelperText?: string;
  validationErrors: Record<string, string>;
  required?: boolean;
}

export const OnboardingField: React.FC<OnboardingFieldProps> = ({
  field,
  defaultLabel,
  value,
  onChange,
  type = 'text',
  options,
  defaultHelperText,
  validationErrors,
  required = false,
}) => {
  const { t } = useTranslation();
  const hasError = field in validationErrors;
  
  // Map field name to translation key
  const getFieldTranslationPath = (fieldName: string): string => {
    if (fieldName === 'first_name') return 'onboarding.steps.personalInfo.fields.firstName';
    if (fieldName === 'last_name') return 'onboarding.steps.personalInfo.fields.lastName';
    if (fieldName === 'username') return 'onboarding.steps.personalInfo.fields.username';
    if (fieldName === 'bio') return 'onboarding.steps.personalInfo.fields.bio';
    if (fieldName === 'native_language') return 'onboarding.steps.languages.fields.nativeLanguage';
    if (fieldName === 'target_language') return 'onboarding.steps.languages.fields.targetLanguage';
    if (fieldName === 'language_level') return 'onboarding.steps.learningPreferences.fields.languageLevel';
    if (fieldName === 'objectives') return 'onboarding.steps.learningPreferences.fields.objectives';
    if (fieldName === 'interface_language') return 'onboarding.steps.learningPreferences.fields.interfaceLanguage';
    return '';
  };
  
  const translationPath = getFieldTranslationPath(field);
  const label = translationPath ? t(`${translationPath}.label`, {}, defaultLabel) : defaultLabel;
  const helperText = translationPath && defaultHelperText ? t(`${translationPath}.helper`, {}, defaultHelperText) : defaultHelperText;

  return (
    <div className="space-y-2">
      <div className="flex justify-between">
        <Label htmlFor={field} className={hasError ? "text-red-500" : ""}>
          {label} {required && <span className="text-red-500">*</span>}
        </Label>
        {hasError && (
          <span className="text-xs text-red-500 font-medium">{validationErrors[field]}</span>
        )}
      </div>

      {type === 'text' && (
        <Input
          id={field}
          value={value as string}
          onChange={(e) => onChange(field, e.target.value)}
          className={hasError ? "border-red-500 focus-visible:ring-red-500" : ""}
          aria-invalid={hasError}
          aria-describedby={hasError ? `${field}-error` : helperText ? `${field}-helper` : undefined}
          aria-required={required}
        />
      )}

      {type === 'textarea' && (
        <Textarea
          id={field}
          value={value as string}
          onChange={(e) => onChange(field, e.target.value)}
          className={hasError ? "border-red-500 focus-visible:ring-red-500" : ""}
          rows={3}
          aria-invalid={hasError}
          aria-describedby={hasError ? `${field}-error` : helperText ? `${field}-helper` : undefined}
          aria-required={required}
        />
      )}

      {type === 'select' && options && (
        <Select
          value={value as string}
          onValueChange={(value) => onChange(field, value)}
        >
          <SelectTrigger 
            className={hasError ? "border-red-500 focus-visible:ring-red-500" : ""}
            aria-invalid={hasError}
            aria-describedby={hasError ? `${field}-error` : helperText ? `${field}-helper` : undefined}
            aria-required={required}
          >
            <SelectValue placeholder={t('onboarding.common.select', { field: label.toLowerCase() }, `Select ${label.toLowerCase()}`)} />
          </SelectTrigger>
          <SelectContent>
            {options.map((option) => (
              <SelectItem
                key={option.value}
                value={option.value}
                disabled={field === 'target_language' && option.value === value}
              >
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {helperText && !hasError && (
        <p id={`${field}-helper`} className="text-xs text-gray-500 mt-1">{helperText}</p>
      )}
      
      {hasError && (
        <p id={`${field}-error`} className="sr-only">{validationErrors[field]}</p>
      )}
    </div>
  );
};

export default OnboardingField;