'use client';

import React, { useState, useEffect } from 'react';
import { Settings, Cookie, Check, X } from 'lucide-react';
import { 
  getCookieConsent, 
  setCookieConsent,
  getConsentAnalytics,
  type CookieConsent 
} from '@/core/utils/cookieUtils';

// Import translations
import enTranslations from '@/core/i18n/translations/en/cookieBanner.json';
import esTranslations from '@/core/i18n/translations/es/cookieBanner.json';
import frTranslations from '@/core/i18n/translations/fr/cookieBanner.json';
import nlTranslations from '@/core/i18n/translations/nl/cookieBanner.json';

// Supported languages
type AvailableLocales = 'en' | 'fr' | 'es' | 'nl';
type TranslationType = typeof enTranslations.en;

interface CookieSettingsProps {
  className?: string;
  showIcon?: boolean;
}

export const CookieSettings: React.FC<CookieSettingsProps> = ({ 
  className = '', 
  showIcon = true 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentLocale, setCurrentLocale] = useState<AvailableLocales>('fr');
  const [preferences, setPreferences] = useState({
    essential: true,
    analytics: false,
    functionality: false,
    performance: false
  });
  const [analytics, setAnalytics] = useState<ReturnType<typeof getConsentAnalytics>>();

  // Load language and consent on startup
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage && ['fr', 'en', 'es', 'nl'].includes(savedLanguage)) {
      setCurrentLocale(savedLanguage as AvailableLocales);
    }

    const consent = getCookieConsent();
    if (consent) {
      setPreferences({
        essential: consent.essential,
        analytics: consent.analytics,
        functionality: consent.functionality,
        performance: consent.performance
      });
    }

    setAnalytics(getConsentAnalytics());
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

  const t = getTranslation(currentLocale);

  const handleSave = () => {
    setCookieConsent(preferences);
    setAnalytics(getConsentAnalytics());
    setIsOpen(false);
  };

  const handlePreferenceChange = (category: keyof typeof preferences, value: boolean) => {
    setPreferences(prev => ({
      ...prev,
      [category]: category === 'essential' ? true : value
    }));
  };

  const cookieCategories = [
    {
      key: 'essential' as const,
      required: true,
      title: t.categories.essential.title,
      description: t.categories.essential.description
    },
    {
      key: 'functionality' as const,
      required: false,
      title: t.categories.functionality.title,
      description: t.categories.functionality.description
    },
    {
      key: 'analytics' as const,
      required: false,
      title: t.categories.analytics.title,
      description: t.categories.analytics.description
    },
    {
      key: 'performance' as const,
      required: false,
      title: t.categories.performance.title,
      description: t.categories.performance.description
    }
  ];

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`inline-flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors ${className}`}
      >
        {showIcon && <Settings className="h-4 w-4" />}
        Paramètres des cookies
      </button>

      {/* Modal */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Modal Content */}
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-xl shadow-2xl">
                {/* Header */}
                <div className="border-b border-gray-200 dark:border-gray-700 p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Cookie className="h-6 w-6 text-indigo-600" />
                      <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                        Paramètres des cookies
                      </h2>
                    </div>
                    <button
                      onClick={() => setIsOpen(false)}
                      className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                {/* Current Status */}
                {analytics && (
                  <div className="p-6 bg-gray-50 dark:bg-gray-700/50">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                      État actuel du consentement
                    </h3>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {analytics.hasConsent ? (
                        <div className="flex items-center gap-2">
                          <Check className="h-4 w-4 text-green-600" />
                          Consentement donné le {analytics.consentDate?.toLocaleDateString(currentLocale === 'en' ? 'en-US' : currentLocale)}
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <X className="h-4 w-4 text-red-600" />
                          Aucun consentement donné
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Cookie Categories */}
                <div className="p-6 space-y-4">
                  {cookieCategories.map((category) => {
                    const isEnabled = preferences[category.key];
                    
                    return (
                      <div
                        key={category.key}
                        className="border border-gray-200 dark:border-gray-600 rounded-lg p-4"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {category.title}
                              {category.required && (
                                <span className="ml-2 text-xs bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-400 px-2 py-1 rounded">
                                  Requis
                                </span>
                              )}
                            </h4>
                          </div>
                          
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              checked={isEnabled}
                              disabled={category.required}
                              onChange={(e) => handlePreferenceChange(category.key, e.target.checked)}
                              className="w-4 h-4 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500 focus:ring-2 disabled:opacity-50"
                            />
                          </div>
                        </div>
                        
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {category.description}
                        </p>
                      </div>
                    );
                  })}
                </div>

                {/* Footer */}
                <div className="border-t border-gray-200 dark:border-gray-700 p-6">
                  <div className="flex justify-end gap-3">
                    <button
                      onClick={() => setIsOpen(false)}
                      className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded-lg transition-colors"
                    >
                      Annuler
                    </button>
                    <button
                      onClick={handleSave}
                      className="px-6 py-2 bg-indigo-600 text-white hover:bg-indigo-700 rounded-lg transition-colors"
                    >
                      Sauvegarder
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
};