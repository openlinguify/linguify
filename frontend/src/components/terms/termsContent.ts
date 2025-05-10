'use client';

import { ReactNode } from 'react';

// Imports for translations
import enTranslations from '@/core/i18n/translations/en/terms.json';
import esTranslations from '@/core/i18n/translations/es/terms.json';
import frTranslations from '@/core/i18n/translations/fr/terms.json';
import nlTranslations from '@/core/i18n/translations/nl/terms.json';

// Define constants
export const CURRENT_TERMS_VERSION = 'v1.0';
export const TERMS_LAST_UPDATED = new Date('2025-05-10').toLocaleDateString();

// Define types
export interface TermsSection {
  id: string;
  title: string;
  content: string;
}

export interface KeyPoint {
  title: string;
  description: string;
  icon?: ReactNode;
}

export type AvailableLocale = 'fr' | 'en' | 'es' | 'nl';

// Helper function to get translations
export function getTranslations(locale: AvailableLocale = 'fr') {
  const translationMap: Record<AvailableLocale, any> = {
    fr: frTranslations.fr,
    en: enTranslations.en,
    es: esTranslations.es,
    nl: nlTranslations.nl
  };
  
  return translationMap[locale] || translationMap.fr;
}

// Helper function to get terms sections from translations
export function getTermsSections(locale: AvailableLocale = 'fr'): TermsSection[] {
  const translations = getTranslations(locale);
  return translations.sections || [];
}

// Helper function to get key points from translations
export function getTermsKeyPoints(locale: AvailableLocale = 'fr'): KeyPoint[] {
  const translations = getTranslations(locale);
  return translations.keyPoints || [];
}