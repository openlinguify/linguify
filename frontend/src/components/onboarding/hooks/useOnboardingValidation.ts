'use client';

import { useCallback, useState } from 'react';
import { useToast } from '@/components/ui/use-toast';
import { useTranslation } from '@/core/i18n/useTranslations';
import { OnboardingFormData } from './useOnboardingForm';

export function useOnboardingValidation() {
  const { toast } = useToast();
  const { t } = useTranslation();
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Validate a specific step
  const validateStep = useCallback((step: number, formData: OnboardingFormData) => {
    let isValid = true;
    const errors: Record<string, string> = {};

    // Step 2: Personal Information
    if (step === 2) {
      // Basic user info validation
      if (!formData.first_name || !formData.last_name || !formData.username) {
        isValid = false;

        // Set specific errors
        if (!formData.first_name) {
          errors.first_name = t('onboarding.steps.personalInfo.fields.firstName.error', {}, "First name is required");
        }
        if (!formData.last_name) {
          errors.last_name = t('onboarding.steps.personalInfo.fields.lastName.error', {}, "Last name is required");
        }
        if (!formData.username) {
          errors.username = t('onboarding.steps.personalInfo.fields.username.error', {}, "Username is required");
        }

        setValidationErrors(errors);

        toast({
          title: t('onboarding.validationErrors.missingInformation', {}, "Missing information"),
          description: t('onboarding.validationErrors.fillRequired', {}, "Please fill in all required fields"),
          variant: "destructive",
        });
      }
    } 
    // Step 3: Language Selection
    else if (step === 3) {
      // Language selection validation
      if (!formData.native_language || !formData.target_language) {
        isValid = false;

        if (!formData.native_language) {
          errors.native_language = t('onboarding.steps.languages.fields.nativeLanguage.error', {}, "Native language is required");
        }
        if (!formData.target_language) {
          errors.target_language = t('onboarding.steps.languages.fields.targetLanguage.error', {}, "Target language is required");
        }

        setValidationErrors(errors);

        toast({
          title: t('onboarding.validationErrors.languageSelection', {}, "Language selection required"),
          description: t('onboarding.validationErrors.selectBothLanguages', {}, "Please select both your native and target languages"),
          variant: "destructive",
        });
      } else if (formData.native_language === formData.target_language) {
        isValid = false;

        setValidationErrors({
          target_language: t('onboarding.steps.languages.fields.targetLanguage.sameAsNativeError', {}, "Target language must be different from native language")
        });

        toast({
          title: t('onboarding.validationErrors.sameLanguage', {}, "Invalid language selection"),
          description: t('onboarding.validationErrors.differentLanguages', {}, "Native and target languages must be different"),
          variant: "destructive",
        });
      }
    }
    // Step 5: Terms Acceptance
    else if (step === 5) {
      // Terms acceptance validation
      if (!formData.termsAccepted) {
        isValid = false;

        errors.termsAccepted = t('onboarding.steps.terms.acceptError', {}, "You must accept the terms and conditions to continue");

        setValidationErrors(errors);

        toast({
          title: t('onboarding.validationErrors.termsRequired', {}, "Terms acceptance required"),
          description: t('onboarding.validationErrors.pleaseAcceptTerms', {}, "Please accept the terms and conditions to continue"),
          variant: "destructive",
        });
      }
    }

    return { isValid, errors };
  }, [t, toast]);

  // Full form validation
  const validateForm = useCallback((formData: OnboardingFormData) => {
    const errors: Record<string, string> = {};

    // Field-specific validations
    if (!formData.username.trim()) {
      errors.username = t('onboarding.steps.personalInfo.fields.username.error', {}, "Username is required");
    } else if (formData.username.length < 3) {
      errors.username = t('onboarding.steps.personalInfo.fields.username.minLengthError', {}, "Username must be at least 3 characters");
    }

    if (!formData.first_name.trim()) {
      errors.first_name = t('onboarding.steps.personalInfo.fields.firstName.error', {}, "First name is required");
    }

    if (!formData.last_name.trim()) {
      errors.last_name = t('onboarding.steps.personalInfo.fields.lastName.error', {}, "Last name is required");
    }

    if (!formData.native_language) {
      errors.native_language = t('onboarding.steps.languages.fields.nativeLanguage.error', {}, "Native language is required");
    }

    if (!formData.target_language) {
      errors.target_language = t('onboarding.steps.languages.fields.targetLanguage.error', {}, "Target language is required");
    } else if (formData.native_language === formData.target_language) {
      errors.target_language = t('onboarding.steps.languages.fields.targetLanguage.sameAsNativeError', {}, "Target language must be different from native language");
    }

    if (!formData.termsAccepted) {
      errors.termsAccepted = t('onboarding.steps.terms.acceptError', {}, "You must accept the terms and conditions to continue");
    }

    // Set validation errors in state
    setValidationErrors(errors);

    // Return true if no errors, false otherwise
    return { isValid: Object.keys(errors).length === 0, errors };
  }, [t]);

  // Clear validation errors
  const clearValidationError = useCallback((field: string) => {
    setValidationErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[field];
      return newErrors;
    });
  }, []);

  // Clear all validation errors
  const clearAllValidationErrors = useCallback(() => {
    setValidationErrors({});
  }, []);

  return {
    validationErrors,
    setValidationErrors,
    validateStep,
    validateForm,
    clearValidationError,
    clearAllValidationErrors
  };
}

export default useOnboardingValidation;