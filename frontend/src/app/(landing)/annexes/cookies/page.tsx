'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Container } from '../../_components/Container';

// Import translations
import enTranslations from '@/core/i18n/translations/en/cookies.json';
import esTranslations from '@/core/i18n/translations/es/cookies.json';
import frTranslations from '@/core/i18n/translations/fr/cookies.json';
import nlTranslations from '@/core/i18n/translations/nl/cookies.json';

// Supported languages
type AvailableLocales = 'en' | 'fr' | 'es' | 'nl';
type TranslationType = typeof enTranslations.en;

export default function CookiesPage() {
  const [currentLocale, setCurrentLocale] = useState<AvailableLocales>('fr');

  // Load language from localStorage on startup
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage && ['fr', 'en', 'es', 'nl'].includes(savedLanguage)) {
      setCurrentLocale(savedLanguage as AvailableLocales);
    }
  }, []);

  // Listen for language changes from other components
  useEffect(() => {
    const handleLanguageChange = () => {
      const savedLanguage = localStorage.getItem('language');
      if (savedLanguage && ['fr', 'en', 'es', 'nl'].includes(savedLanguage)) {
        setCurrentLocale(savedLanguage as AvailableLocales);
      }
    };

    window.addEventListener('languageChanged', handleLanguageChange);
    
    return () => {
      window.removeEventListener('languageChanged', handleLanguageChange);
    };
  }, []);

  // Translation helper function
  const getTranslation = (locale: AvailableLocales): TranslationType => {
    const translations: Record<AvailableLocales, TranslationType> = {
      fr: frTranslations.fr as TranslationType,
      en: enTranslations.en,
      es: esTranslations.es as TranslationType,
      nl: nlTranslations.nl as TranslationType
    };
    
    return translations[locale] || translations.en;
  };

  // Get current translation
  const t = getTranslation(currentLocale);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-950">
      <Container>
        <div className="py-16">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {t.title}
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              {t.subtitle}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-4">
              {t.lastUpdated.replace('{date}', new Date().toLocaleDateString(currentLocale === 'en' ? 'en-US' : currentLocale === 'es' ? 'es-ES' : currentLocale === 'nl' ? 'nl-NL' : 'fr-FR'))}
            </p>
          </div>

          {/* Content */}
          <div className="max-w-4xl mx-auto">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="p-8 space-y-8">
                {t.sections.map((section, index) => (
                  <div key={index} className="space-y-4">
                    <h2 className="text-2xl font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">
                      {section.title}
                    </h2>
                    <div className="prose prose-gray dark:prose-invert max-w-none">
                      {section.content.map((paragraph, pIndex) => (
                        <p key={pIndex} className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
                          {paragraph}
                        </p>
                      ))}
                      {section.items && (
                        <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
                          {section.items.map((item, iIndex) => (
                            <li key={iIndex}>{item}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                ))}

                {/* Contact Section */}
                <div className="mt-12 p-6 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {t.contact.title}
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 mb-4">
                    {t.contact.description}
                  </p>
                  <Link
                    href="/contact"
                    className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    legacyBehavior>
                    {t.contact.buttonText}
                  </Link>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <div className="mt-8 flex justify-center space-x-4">
              <Link
                href="/annexes/terms"
                className="text-indigo-600 dark:text-indigo-400 hover:underline"
                legacyBehavior>
                {t.navigation.terms}
              </Link>
              <span className="text-gray-400">•</span>
              <Link
                href="/annexes/privacy"
                className="text-indigo-600 dark:text-indigo-400 hover:underline"
                legacyBehavior>
                {t.navigation.privacy}
              </Link>
              <span className="text-gray-400">•</span>
              <Link
                href="/annexes/legal"
                className="text-indigo-600 dark:text-indigo-400 hover:underline"
                legacyBehavior>
                {t.navigation.legal}
              </Link>
            </div>
          </div>
        </div>
      </Container>
    </div>
  );
}