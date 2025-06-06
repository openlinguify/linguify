'use client';

// src/hooks/useTranslation.ts
import { useState, useEffect, useCallback } from 'react';

// Dynamically import translation files
const translationModules = {
  en: async () => {
    try {
      const common = await import('./translations/en/common.json');
      const commonAdditions = await import('./translations/en/common_additions.json');
      const footer = await import('./translations/en/footer.json');
      const sidebar = await import('./translations/en/sidebar.json');
      const dashboard = await import('./translations/en/dashboard.json');
      const terms = await import('./translations/en/terms.json');
      const onboarding = await import('./translations/en/onboarding.json');
      const onboardingTerms = await import('./translations/en/onboarding_terms.json');
      const languages = await import('./translations/en/languages.json');
      const notifications = await import('./translations/en/notifications.json');
      const settings = await import('./translations/en/settings.json').catch(() => ({ default: {} }));

      // Note: dashboard, terms, onboarding, and languages are nested objects
      return {
        ...common.default,
        ...commonAdditions.default,
        ...footer.default,
        ...sidebar.default,
        ...settings.default,
        ...notifications.default, // Charge toute la structure (notifications, test_notifications, etc.)
        dashboard: dashboard.default,
        terms: terms.default.en,
        onboarding: {
          ...onboarding.default,
          ...onboardingTerms.default
        },
        languages: languages.default
      };
    } catch (error) {
      console.error('Error loading English translations:', error);
      // Return at least empty objects for nested namespaces in case of error
      return { dashboard: {}, terms: {}, onboarding: {}, languages: {} };
    }
  },
  fr: async () => {
    try {
      const common = await import('./translations/fr/common.json');
      const commonAdditions = await import('./translations/fr/common_additions.json');
      const footer = await import('./translations/fr/footer.json');
      const sidebar = await import('./translations/fr/sidebar.json');
      const dashboard = await import('./translations/fr/dashboard.json');
      const terms = await import('./translations/fr/terms.json');
      const onboarding = await import('./translations/fr/onboarding.json');
      const onboardingTerms = await import('./translations/fr/onboarding_terms.json');
      const languages = await import('./translations/fr/languages.json');
      const notifications = await import('./translations/fr/notifications.json');
      const settings = await import('./translations/fr/settings.json').catch(() => ({ default: {} }));

      return {
        ...common.default,
        ...commonAdditions.default,
        ...footer.default,
        ...sidebar.default,
        ...settings.default,
        ...notifications.default,
        dashboard: dashboard.default,
        terms: terms.default.fr,
        onboarding: {
          ...onboarding.default,
          ...onboardingTerms.default
        },
        languages: languages.default
      };
    } catch (error) {
      console.error('Error loading French translations:', error);
      // Use English translations as fallback
      const enDashboard = await import('./translations/en/dashboard.json').catch(() => ({ default: {} }));
      const enTerms = await import('./translations/en/terms.json').catch(() => ({ default: { en: {} } }));
      const enOnboarding = await import('./translations/en/onboarding.json').catch(() => ({ default: {} }));
      const enLanguages = await import('./translations/en/languages.json').catch(() => ({ default: {} }));
      const enSettings = await import('./translations/en/settings.json').catch(() => ({ default: {} }));
      return {
        dashboard: enDashboard.default || {},
        terms: enTerms.default.en || {},
        onboarding: enOnboarding.default || {},
        languages: enLanguages.default || {},
        ...(enSettings.default || {})
      };
    }
  },
  es: async () => {
    try {
      const common = await import('./translations/es/common.json');
      const commonAdditions = await import('./translations/es/common_additions.json');
      const footer = await import('./translations/es/footer.json');
      const sidebar = await import('./translations/es/sidebar.json');
      const dashboard = await import('./translations/es/dashboard.json');
      const terms = await import('./translations/es/terms.json');
      const onboarding = await import('./translations/es/onboarding.json');
      const onboardingTerms = await import('./translations/es/onboarding_terms.json');
      const languages = await import('./translations/es/languages.json');
      const notifications = await import('./translations/es/notifications.json');
      const settings = await import('./translations/es/settings.json').catch(() => ({ default: {} }));

      return {
        ...common.default,
        ...commonAdditions.default,
        ...footer.default,
        ...sidebar.default,
        ...settings.default,
        ...notifications.default,
        dashboard: dashboard.default,
        terms: terms.default.es,
        onboarding: {
          ...onboarding.default,
          ...onboardingTerms.default
        },
        languages: languages.default
      };
    } catch (error) {
      console.error('Error loading Spanish translations:', error);
      // Use English translations as fallback
      const enDashboard = await import('./translations/en/dashboard.json').catch(() => ({ default: {} }));
      const enTerms = await import('./translations/en/terms.json').catch(() => ({ default: { en: {} } }));
      const enOnboarding = await import('./translations/en/onboarding.json').catch(() => ({ default: {} }));
      const enLanguages = await import('./translations/en/languages.json').catch(() => ({ default: {} }));
      const enSettings = await import('./translations/en/settings.json').catch(() => ({ default: {} }));
      return {
        dashboard: enDashboard.default || {},
        terms: enTerms.default.en || {},
        onboarding: enOnboarding.default || {},
        languages: enLanguages.default || {},
        ...(enSettings.default || {})
      };
    }
  },
  nl: async () => {
    try {
      const common = await import('./translations/nl/common.json');
      const commonAdditions = await import('./translations/nl/common_additions.json');
      const footer = await import('./translations/nl/footer.json');
      const sidebar = await import('./translations/nl/sidebar.json');
      const dashboard = await import('./translations/nl/dashboard.json');
      const terms = await import('./translations/nl/terms.json');
      const onboarding = await import('./translations/nl/onboarding.json');
      const onboardingTerms = await import('./translations/nl/onboarding_terms.json');
      const languages = await import('./translations/nl/languages.json');
      const notifications = await import('./translations/nl/notifications.json');
      const settings = await import('./translations/nl/settings.json').catch(() => ({ default: {} }));

      return {
        ...common.default,
        ...commonAdditions.default,
        ...footer.default,
        ...sidebar.default,
        ...settings.default,
        ...notifications.default,
        dashboard: dashboard.default,
        terms: terms.default.nl,
        onboarding: {
          ...onboarding.default,
          ...onboardingTerms.default
        },
        languages: languages.default
      };
    } catch (error) {
      console.error('Error loading Dutch translations:', error);
      // Use English translations as fallback
      const enDashboard = await import('./translations/en/dashboard.json').catch(() => ({ default: {} }));
      const enTerms = await import('./translations/en/terms.json').catch(() => ({ default: { en: {} } }));
      const enOnboarding = await import('./translations/en/onboarding.json').catch(() => ({ default: {} }));
      const enLanguages = await import('./translations/en/languages.json').catch(() => ({ default: {} }));
      const enSettings = await import('./translations/en/settings.json').catch(() => ({ default: {} }));
      return {
        dashboard: enDashboard.default || {},
        terms: enTerms.default.en || {},
        onboarding: enOnboarding.default || {},
        languages: enLanguages.default || {},
        ...(enSettings.default || {})
      };
    }
  }
};

type AvailableLocales = keyof typeof translationModules;
type TranslationFunction = (key: string, params?: Record<string, string>, fallback?: string) => string;

// Create a singleton to share language state between components
let currentLocale: AvailableLocales = 'en';
let eventBus: EventTarget | null = null;
const LANGUAGE_CHANGE_EVENT = 'app:language:changed';
const listeners: (() => void)[] = [];

// Setup global event bus for more reactive updates
if (typeof window !== 'undefined' && !eventBus) {
  eventBus = new EventTarget();
}

// Function to notify all translation hooks of a change
const notifyLocaleChange = (newLocale: AvailableLocales) => {
  // Update current locale
  currentLocale = newLocale;

  // Notify hook listeners
  listeners.forEach(listener => listener());

  // Dispatch global event for all components
  if (eventBus) {
    const event = new CustomEvent(LANGUAGE_CHANGE_EVENT, {
      detail: { locale: newLocale }
    });
    eventBus.dispatchEvent(event);
  }
};

// Load saved language at module initialization
if (typeof window !== 'undefined') {
  const savedLanguage = localStorage.getItem('language') as AvailableLocales | null;
  if (savedLanguage && translationModules[savedLanguage]) {
    currentLocale = savedLanguage;
  }
}

// Default fallback for dashboard translations
const dashboardFallback = {
  // Add basic dashboard translation keys here
  "dashboard": {
    "welcome": "Welcome to Linguify",
    "todayGoal": "Today's Goal",
    "streak": "Current Streak",
    "level": "Current Level",
    "recentActivity": "Recent Activity",
    "continueLesson": "Continue Learning"
  }
};

export function useTranslation() {
  const [locale, setLocale] = useState<AvailableLocales>(currentLocale);
  const [translations, setTranslations] = useState<any>({});
  const [isLoading, setIsLoading] = useState(true);

  // Subscribe to language changes
  useEffect(() => {
    const handleChange = () => {
      setLocale(currentLocale);
    };
    
    listeners.push(handleChange);
    
    return () => {
      const index = listeners.indexOf(handleChange);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    };
  }, []);

  // Load translations when language changes
  useEffect(() => {
    let isMounted = true;
    const loadTranslations = async () => {
      try {
        setIsLoading(true);
        const module = await translationModules[locale]();
        if (isMounted) {
          setTranslations(module);
        }
      } catch (error) {
        console.error('Translation load error:', error);
        if (isMounted) {
          // At minimum, ensure we have a dashboard object
          setTranslations({ dashboard: dashboardFallback });
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadTranslations();
    return () => {
      isMounted = false;
    };
  }, [locale]);

  // Translation function with fallback support
  // Helper function to safely get nested keys
  const getNestedValue = useCallback((obj: any, keys: string[]): any => {
    if (!obj || typeof obj !== 'object' || keys.length === 0) return undefined;

    // Handle special cases for namespaced objects (dashboard, terms, onboarding)
    if (keys.length >= 2) {
      const namespace = keys[0];

      // If the first key is a namespace and it exists as an object
      if (obj[namespace] && typeof obj[namespace] === 'object') {
        if (keys.length === 2) {
          // Simple namespace.key pattern
          return obj[namespace][keys[1]];
        } else {
          // Deeper nesting like namespace.section.key
          let nestedValue = obj[namespace];
          for (let i = 1; i < keys.length; i++) {
            if (!nestedValue || typeof nestedValue !== 'object') return undefined;
            nestedValue = nestedValue[keys[i]];
          }
          return nestedValue;
        }
      }
    }

    // Normal nested key traversal
    let current = obj;
    for (const key of keys) {
      if (!current || typeof current !== 'object') return undefined;
      current = current[key];
    }
    return current;
  }, []);

  const t: TranslationFunction = useCallback((key, params = {}, fallback) => {
    const keys = key.split('.');
    let value = getNestedValue(translations, keys);

    if (value === undefined) {
      if (process.env.NODE_ENV === 'development') {
        console.debug(`Translation not found for key: ${key}, current locale: ${locale}`);
      }

      // Check if fallback is provided in params
      if (params.fallback !== undefined) {
        return params.fallback;
      }

      return fallback || key;
    }

    // Simple parameter replacement for strings
    if (typeof value === 'string') {
      return value.replace(/\{(\w+)\}/g, (_, p) => params[p] !== undefined ? params[p] : `{${p}}`);
    }

    // If value is an array or object and we have a fallback, use it directly
    if ((Array.isArray(value) || typeof value === 'object') && params.fallback !== undefined) {
      return params.fallback;
    }

    // Support for array and object values
    if (Array.isArray(value) || typeof value === 'object') {
      console.warn(`Unexpected object/array value for translation key: ${key}`, value);
      return fallback || key;
    }

    if (process.env.NODE_ENV === 'development') {
      console.warn(`No translation string found for key: ${key}, got:`, value);
    }
    return fallback || key;
  }, [translations, locale, getNestedValue]);

  // Language change handler
  const changeLanguage = useCallback((newLocale: AvailableLocales) => {
    console.log('Changing language to:', newLocale);

    // Update localStorage
    localStorage.setItem('language', newLocale);

    // Notify all instances and components with the new locale
    notifyLocaleChange(newLocale);

    // Emit legacy event for backward compatibility
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new Event('languageChanged'));
    }
  }, []);

  return {
    t,
    locale,
    changeLanguage,
    isLoading
  };
}