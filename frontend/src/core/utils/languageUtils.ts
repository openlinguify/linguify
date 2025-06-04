// src/core/utils/languageUtils.ts
// This file provides utility functions for language-related operations
// both for React components (via hooks) and static functions for non-React code

import { LANGUAGE_OPTIONS, LEVEL_OPTIONS, OBJECTIVES_OPTIONS, INTERFACE_LANGUAGE_OPTIONS } from '@/addons/settings/constants/usersettings';
import { useTranslation } from '../i18n/useTranslations';

/**
 * Récupère la langue cible de l'utilisateur depuis les paramètres stockés
 * Normalise la langue au format attendu par l'API (en, fr, es, nl)
 */
export function getUserTargetLanguage(): string {
  try {
    // Vérifier si localStorage est disponible (côté client)
    if (typeof window !== 'undefined' && window.localStorage) {
      // Récupérer depuis localStorage
      const userSettingsStr = localStorage.getItem('userSettings');
      if (userSettingsStr) {
        const userSettings = JSON.parse(userSettingsStr);
        if (userSettings.target_language) {
          // Normaliser le format (EN -> en, FR -> fr, etc.)
          const lang = userSettings.target_language.toLowerCase();
          // Vérifier que c'est une langue supportée
          if (['en', 'fr', 'es', 'nl'].includes(lang)) {
            return lang;
          }
        }
      }
    }
  } catch (error) {
    console.error('Error getting user target language:', error);
  }
  // Retourner 'fr' par défaut
  return 'fr';
}

/**
 * Configure les en-têtes HTTP appropriés pour les requêtes API
 * avec la langue cible de l'utilisateur
 */
export function getLanguageHeaders(targetLanguage?: string): Headers {
  const headers = new Headers({
    'Content-Type': 'application/json',
  });
  
  // Utiliser la langue spécifiée ou récupérer depuis les paramètres utilisateur
  const lang = targetLanguage || getUserTargetLanguage();
  
  // Ajouter l'en-tête Accept-Language pour les API qui s'appuient sur cet en-tête
  headers.append('Accept-Language', lang);
  
  return headers;
}

/**
 * Ajoute le paramètre de langue cible à une URL d'API
 */
export function addLanguageParam(url: URL, targetLanguage?: string): URL {
  const lang = targetLanguage || getUserTargetLanguage();
  url.searchParams.append('target_language', lang);
  return url;
}

/**
 * Récupère la langue maternelle de l'utilisateur depuis les paramètres stockés
 */
export function getUserNativeLanguage(): string {
  try {
    // Vérifier si localStorage est disponible (côté client)
    if (typeof window !== 'undefined' && window.localStorage) {
      // Récupérer depuis localStorage ou utiliser 'en' par défaut
      const userSettingsStr = localStorage.getItem('userSettings');
      if (userSettingsStr) {
        const settings = JSON.parse(userSettingsStr);
        return settings.native_language?.toLowerCase() || 'en';
      }
    }
  } catch (e) {
    console.error("Error parsing user settings:", e);
  }
  // Retourner 'en' par défaut
  return 'en';
}

/**
 * Enregistre les paramètres de langue dans localStorage
 * Utile pour les modules qui ne peuvent pas utiliser les hooks React
 */
export function saveLanguageSettings(settings: {
  target_language?: string;
  native_language?: string;
  language_level?: string;
}): void {
  try {
    // Vérifier si localStorage est disponible (côté client)
    if (typeof window !== 'undefined' && window.localStorage) {
      // Lire les paramètres actuels
      const userSettingsStr = localStorage.getItem('userSettings');
      let userSettings = {};
      
      if (userSettingsStr) {
        userSettings = JSON.parse(userSettingsStr);
      }
      
      // Mettre à jour avec les nouveaux paramètres
      const updatedSettings = { 
        ...userSettings, 
        ...settings 
      };
      
      // Enregistrer dans localStorage
      localStorage.setItem('userSettings', JSON.stringify(updatedSettings));
      
      console.log('Language settings saved locally:', settings);
    }
  } catch (error) {
    console.error('Error saving language settings:', error);
  }
}

/**
 * Obtient le nom complet d'une langue à partir de son code
 */
export function getLanguageName(code: string): string {
  const option = LANGUAGE_OPTIONS.find(opt => 
    opt.value.toLowerCase() === code.toLowerCase()
  );
  return option ? option.label : code;
}

/**
 * Obtient le libellé du niveau de langue à partir du code
 */
export function getLevelName(code: string): string {
  const option = LEVEL_OPTIONS.find(opt => opt.value === code);
  return option ? option.label : code;
}

// Exporter aussi un objet pour les cas où l'importation d'objets est préférée
export const languageUtils = {
  getUserTargetLanguage,
  getUserNativeLanguage,
  getLanguageHeaders,
  addLanguageParam,
  saveLanguageSettings,
  getLanguageName,
  getLevelName,
  
  // Retourne toutes les informations de langue en une seule fonction
  getLanguageInfo() {
    return {
      targetLanguage: getUserTargetLanguage(),
      nativeLanguage: getUserNativeLanguage(),
      targetLanguageName: getLanguageName(getUserTargetLanguage()),
      nativeLanguageName: getLanguageName(getUserNativeLanguage())
    };
  }
};

/**
 * Hook to get localized language names and options based on the user's interface language
 */
export function useLocalizedLanguages() {
  const { t } = useTranslation();

  // Language options with translation keys
  const getLanguageOptions = () => [
    {
      value: 'EN',
      label: t('languages.english', {}, 'English')
    },
    {
      value: 'FR',
      label: t('languages.french', {}, 'French')
    },
    {
      value: 'NL',
      label: t('languages.dutch', {}, 'Dutch')
    },
    {
      value: 'ES',
      label: t('languages.spanish', {}, 'Spanish')
    },
  ];

  // Interface language options with native names
  const getInterfaceLanguageOptions = () => [
    {
      value: 'en',
      label: t('languages.english', {}, 'English')
    },
    {
      value: 'fr',
      label: t('languages.frenchNative', {}, 'Français')
    },
    {
      value: 'es',
      label: t('languages.spanishNative', {}, 'Español')
    },
    {
      value: 'nl',
      label: t('languages.dutchNative', {}, 'Nederlands')
    },
  ];

  // Language level options with localized descriptions
  const getLevelOptions = () => [
    {
      value: 'A1',
      label: t('languages.levels.a1', {}, 'A1 - Beginner')
    },
    {
      value: 'A2',
      label: t('languages.levels.a2', {}, 'A2 - Elementary')
    },
    {
      value: 'B1',
      label: t('languages.levels.b1', {}, 'B1 - Intermediate')
    },
    {
      value: 'B2',
      label: t('languages.levels.b2', {}, 'B2 - Upper Intermediate')
    },
    {
      value: 'C1',
      label: t('languages.levels.c1', {}, 'C1 - Advanced')
    },
    {
      value: 'C2',
      label: t('languages.levels.c2', {}, 'C2 - Mastery')
    },
  ];

  // Learning objective options with localized names
  const getObjectivesOptions = () => [
    { value: 'Travel', label: t('languages.objectives.travel', {}, 'Travel') },
    { value: 'Business', label: t('languages.objectives.business', {}, 'Business') },
    { value: 'Live Abroad', label: t('languages.objectives.liveAbroad', {}, 'Live Abroad') },
    { value: 'Exam', label: t('languages.objectives.exam', {}, 'Exam Preparation') },
    { value: 'For Fun', label: t('languages.objectives.fun', {}, 'For Fun') },
    { value: 'Work', label: t('languages.objectives.work', {}, 'Work') },
    { value: 'School', label: t('languages.objectives.school', {}, 'School') },
    { value: 'Study', label: t('languages.objectives.study', {}, 'Study') },
    { value: 'Personal', label: t('languages.objectives.personal', {}, 'Personal Development') },
  ];

  // Helper to get localized label for a value
  const getLocalizedLabel = (options: { value: string, label: string }[], value: string): string => {
    const option = options.find(opt => opt.value === value);
    return option ? option.label : t('common.notSpecified', {}, 'Not specified');
  };

  return {
    getLanguageOptions,
    getInterfaceLanguageOptions,
    getLevelOptions,
    getObjectivesOptions,
    getLocalizedLabel
  };
}

export default languageUtils;