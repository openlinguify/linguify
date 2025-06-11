'use client';

import { useState, useCallback, useEffect } from 'react';
import { useAuthContext } from '@/core/auth/AuthAdapter';
import { useToast } from '@/components/ui/use-toast';
import { useTranslation } from '@/core/i18n/useTranslations';
import apiClient from '@/core/api/apiClient';

// Define types
export interface OnboardingFormData {
  first_name: string;
  last_name: string;
  username: string;
  bio: string | null;
  native_language: string;
  target_language: string;
  language_level: string;
  objectives: string;
  interface_language: string;
  termsAccepted: boolean;
}

export interface ServerResponseData {
  first_name?: string;
  last_name?: string;
  username?: string;
  bio?: string | null;
  native_language?: string;
  target_language?: string;
  language_level?: string;
  objectives?: string;
  public_id?: string;
  email?: string;
  updated_at?: string;
  created_at?: string;
  [key: string]: any;
}

export interface ApiRequest {
  endpoint: string;
  method: string;
  timestamp: string;
  status?: "success" | "error" | "pending";
  duration?: number;
}

export const DEFAULT_FORM_DATA: OnboardingFormData = {
  first_name: "",
  last_name: "",
  username: "",
  bio: "",
  native_language: "",
  target_language: "",
  language_level: "A1",
  objectives: "Travel",
  interface_language: "en",
  termsAccepted: false // Important: default to false for legal reasons
};

export function useOnboardingForm() {
  const { toast } = useToast();
  const { user } = useAuthContext();
  const { t } = useTranslation();

  // State hooks
  const [formData, setFormData] = useState<OnboardingFormData>(DEFAULT_FORM_DATA);
  const [initialData, setInitialData] = useState<OnboardingFormData>(DEFAULT_FORM_DATA);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastServerResponse, setLastServerResponse] = useState<ServerResponseData | null>(null);
  const [apiRequests, setApiRequests] = useState<ApiRequest[]>([]);

  // Helper to log API requests
  const logApiRequest = useCallback((endpoint: string, method: string, status?: "success" | "error" | "pending") => {
    const timestamp = new Date().toISOString();
    setApiRequests(prev => [
      { endpoint, method, timestamp, status },
      ...prev.slice(0, 9) // Keep only the last 10 requests
    ]);
  }, []);

  // Load initial data from user
  useEffect(() => {
    if (user) {
      const userData = {
        first_name: (user as any).first_name || "",
        last_name: (user as any).last_name || "",
        username: (user as any).username || "",
        bio: (user as any).bio || "",
        native_language: (user as any).native_language || "",
        target_language: (user as any).target_language || "",
        language_level: (user as any).language_level || "A1",
        objectives: (user as any).objectives || "Travel",
        interface_language: "en",
        termsAccepted: false // Always require explicit acceptance on onboarding
      };

      setFormData(userData);
      setInitialData(userData);
    }
  }, [user]);

  // Fetch profile data from API
  const fetchCurrentProfile = useCallback(async () => {
    try {
      logApiRequest('/api/auth/profile/', 'GET', 'pending');
      const startTime = Date.now();

      const response = await apiClient.get('/api/auth/profile/');

      logApiRequest('/api/auth/profile/', 'GET', 'success');

      if (response.data) {
        setLastServerResponse(response.data);

        // Update initialData with current server data
        const serverData = response.data;
        setInitialData({
          first_name: serverData.first_name || "",
          last_name: serverData.last_name || "",
          username: serverData.username || "",
          bio: serverData.bio || "",
          native_language: serverData.native_language || "",
          target_language: serverData.target_language || "",
          language_level: serverData.language_level || "A1",
          objectives: serverData.objectives || "Travel",
          interface_language: "en",
          termsAccepted: false // Always require explicit acceptance on onboarding
        });

        toast({
          title: t('onboarding.messages.profileDataRefreshed', {}, "Profile data refreshed"),
          description: t('onboarding.messages.dataLoaded', {}, "Latest data loaded from server"),
        });
      }
    } catch (error) {
      console.error("Error fetching profile:", error);
      logApiRequest('/api/auth/profile/', 'GET', 'error');

      toast({
        title: t('onboarding.messages.errorFetching', {}, "Error fetching profile"),
        description: t('onboarding.messages.couldNotLoad', {}, "Could not load your current profile data"),
        variant: "destructive",
      });
    }
  }, [t, toast, logApiRequest]);

  // Initialize profile data
  useEffect(() => {
    fetchCurrentProfile();
  }, [fetchCurrentProfile]);

  // Form validation function
  const validateForm = useCallback(() => {
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

    // Terms acceptance validation
    if (!formData.termsAccepted) {
      errors.termsAccepted = t('onboarding.steps.terms.acceptError', {}, "You must accept the terms and conditions to continue");
    }

    // Set validation errors in state
    setValidationErrors(errors);

    // Return true if no errors, false otherwise
    return Object.keys(errors).length === 0;
  }, [formData, t]);

  // Handle form submission
  const handleSubmit = useCallback(async () => {
    // Final validation before submission
    if (!validateForm()) {
      toast({
        title: t('onboarding.messages.validationError', {}, "Validation Error"),
        description: t('onboarding.messages.fixErrors', {}, "Please fix the errors before submitting"),
        variant: "destructive",
      });
      return false;
    }

    setIsSubmitting(true);

    try {
      // First, update the profile
      logApiRequest('/api/auth/profile/', 'PATCH', 'pending');

      // Prepare data object for API
      // Note: API uses snake_case while our form uses camelCase
      const profileData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        username: formData.username,
        bio: formData.bio,
        native_language: formData.native_language,
        target_language: formData.target_language,
        language_level: formData.language_level,
        objectives: formData.objectives,
        terms_accepted: formData.termsAccepted // Send to API with snake_case
      };

      console.log('Sending profile data to API:', profileData);
      const profileResponse = await apiClient.patch('/api/auth/profile/', profileData);

      logApiRequest('/api/auth/profile/', 'PATCH', 'success');
      setLastServerResponse(profileResponse.data);

      // Then, update settings with interface language
      try {
        logApiRequest('/api/auth/me/settings/', 'POST', 'pending');

        await apiClient.post('/api/auth/me/settings/', {
          interface_language: formData.interface_language
        });

        logApiRequest('/api/auth/me/settings/', 'POST', 'success');
      } catch (error) {
        logApiRequest('/api/auth/me/settings/', 'POST', 'error');
        console.log('Settings API not available, interface language saved locally only');

        // Save interface language to localStorage as fallback
        const userSettings = localStorage.getItem('userSettings');
        if (userSettings) {
          const settings = JSON.parse(userSettings);
          settings.interface_language = formData.interface_language;
          localStorage.setItem('userSettings', JSON.stringify(settings));
        } else {
          localStorage.setItem('userSettings', JSON.stringify({
            interface_language: formData.interface_language
          }));
        }
      }

      // Show success toast
      toast({
        title: t('onboarding.messages.profileUpdated', {}, "Profile updated successfully!"),
        description: t('onboarding.messages.journeyBegins', {}, "Your language learning journey begins now."),
        variant: "default",
      });

      // Set onboarding as completed in localStorage
      localStorage.setItem("onboardingCompleted", "true");
      
      return true;

    } catch (error: any) {
      console.error("Error updating profile:", error);
      logApiRequest('/api/auth/profile/', 'PATCH', 'error');

      const errorMessage = error.response?.data?.detail || "There was an error saving your information.";

      // Try to extract error details for more specific feedback
      if (error.response?.data) {
        setLastServerResponse(error.response.data);
      }

      toast({
        title: t('onboarding.messages.errorUpdating', {}, "Error updating profile"),
        description: errorMessage,
        variant: "destructive",
      });
      
      return false;
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, validateForm, t, toast, logApiRequest]);

  // Handle input changes and clear validation errors
  const handleInputChange = useCallback((field: keyof OnboardingFormData, value: string | boolean | null) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));

    // Clear validation error for this field if it exists
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  }, [validationErrors]);

  // Get display value for a field
  const getFieldLabel = useCallback((field: keyof OnboardingFormData): string => {
    const labelMap: Record<keyof OnboardingFormData, string> = {
      first_name: "First Name",
      last_name: "Last Name",
      username: "Username",
      bio: "Bio",
      native_language: "Native Language",
      target_language: "Target Language",
      language_level: "Language Level",
      objectives: "Learning Objectives",
      interface_language: "Interface Language",
      termsAccepted: "Terms and Conditions"
    };
    return labelMap[field] || field;
  }, []);

  // Count fields that will be updated
  const changedFieldsCount = Object.keys(formData).filter(key => {
    const field = key as keyof OnboardingFormData;
    return formData[field] !== initialData[field];
  }).length;

  return {
    formData,
    initialData,
    setFormData,
    validationErrors,
    isSubmitting,
    lastServerResponse,
    apiRequests,
    changedFieldsCount,
    logApiRequest,
    fetchCurrentProfile,
    validateForm,
    handleSubmit,
    handleInputChange,
    getFieldLabel,
    clearApiRequests: () => setApiRequests([])
  };
}

export default useOnboardingForm;