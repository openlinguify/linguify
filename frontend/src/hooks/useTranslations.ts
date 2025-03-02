// src/hooks/useTranslation.ts
import { useState, useEffect, useCallback } from 'react';

// Dynamically import translation files
const translationModules = {
  en: async () => {
    const common = await import('@/locales/en/common.json');
    const footer = await import('@/locales/en/footer.json');
    return { ...common.default, ...footer.default };
  },
  fr: async () => {
    const common = await import('@/locales/fr/common.json');
    const footer = await import('@/locales/fr/footer.json');
    return { ...common.default, ...footer.default };
  },
  es: async () => {
    const common = await import('@/locales/es/common.json');
    const footer = await import('@/locales/es/footer.json');
    return { ...common.default, ...footer.default };
  },
  nl: async () => {
    const common = await import('@/locales/nl/common.json');
    const footer = await import('@/locales/nl/footer.json');
    return { ...common.default, ...footer.default };
  }
};

type AvailableLocales = keyof typeof translationModules;
type TranslationFunction = (key: string, params?: Record<string, string>) => string;

export function useTranslation() {
  const [locale, setLocale] = useState<AvailableLocales>('en');
  const [translations, setTranslations] = useState<any>({});

  // Load translations
  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const module = await translationModules[locale]();
        setTranslations(module);
      } catch (error) {
        console.error('Translation load error:', error);
        setTranslations({});
      }
    };

    loadTranslations();
  }, [locale]);

  // Translation function
  const t: TranslationFunction = useCallback((key, params = {}) => {
    const keys = key.split('.');
    let value: any = translations;

    for (const k of keys) {
      if (!value || typeof value !== 'object') return key;
      value = value[k];
    }

    // Simple parameter replacement
    if (typeof value === 'string') {
      return value.replace(/\{(\w+)\}/g, (_, p) => params[p] || _);
    }

    return key;
  }, [translations]);

  // Language change handler
  const changeLanguage = useCallback((newLocale: AvailableLocales) => {
    setLocale(newLocale);
    localStorage.setItem('language', newLocale);
  }, []);

  return {
    t,
    locale,
    changeLanguage
  };
}