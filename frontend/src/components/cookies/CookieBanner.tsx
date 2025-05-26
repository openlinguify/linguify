'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { X, Settings, Cookie, Shield, BarChart3, Zap } from 'lucide-react';
import { 
  shouldShowCookieBanner, 
  acceptAllCookies, 
  acceptEssentialOnly,
  saveCustomConsent,
  getCookieConsent,
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

interface CookieBannerProps {
  className?: string;
}

export const CookieBanner: React.FC<CookieBannerProps> = ({ className = '' }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [currentLocale, setCurrentLocale] = useState<AvailableLocales>('fr');
  const [preferences, setPreferences] = useState({
    essential: true,
    analytics: false,
    functionality: false,
    performance: false
  });

  // Load language from localStorage on startup
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage && ['fr', 'en', 'es', 'nl'].includes(savedLanguage)) {
      setCurrentLocale(savedLanguage as AvailableLocales);
    }
  }, []);

  // Check if banner should be shown
  useEffect(() => {
    setIsVisible(shouldShowCookieBanner());
  }, []);

  // Listen for language changes
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

  const handleAcceptAll = async () => {
    try {
      await acceptAllCookies();
      setIsVisible(false);
    } catch (error) {
      console.error('Error accepting all cookies:', error);
      // Still hide banner on error to prevent blocking UI
      setIsVisible(false);
    }
  };

  const handleAcceptEssential = async () => {
    try {
      await acceptEssentialOnly();
      setIsVisible(false);
    } catch (error) {
      console.error('Error accepting essential cookies:', error);
      setIsVisible(false);
    }
  };

  const handleCustomSave = async () => {
    try {
      await saveCustomConsent(preferences);
      setIsVisible(false);
    } catch (error) {
      console.error('Error saving custom consent:', error);
      setIsVisible(false);
    }
  };

  const handlePreferenceChange = (category: keyof typeof preferences, value: boolean) => {
    setPreferences(prev => ({
      ...prev,
      [category]: category === 'essential' ? true : value // Essential always true
    }));
  };

  if (!isVisible) return null;

  const cookieCategories = [
    {
      key: 'essential' as const,
      icon: Shield,
      required: true,
      title: t.categories.essential.title,
      description: t.categories.essential.description
    },
    {
      key: 'functionality' as const,
      icon: Settings,
      required: false,
      title: t.categories.functionality.title,
      description: t.categories.functionality.description
    },
    {
      key: 'analytics' as const,
      icon: BarChart3,
      required: false,
      title: t.categories.analytics.title,
      description: t.categories.analytics.description
    },
    {
      key: 'performance' as const,
      icon: Zap,
      required: false,
      title: t.categories.performance.title,
      description: t.categories.performance.description
    }
  ];

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40" />
      {/* Banner */}
      <div className={`fixed bottom-0 left-0 right-0 z-50 ${className}`}>
        <div className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 shadow-2xl">
          <div className="max-w-7xl mx-auto p-6">
            {!showDetails ? (
              /* Simple Banner */
              (<div className="flex flex-col lg:flex-row items-start lg:items-center gap-4">
                <div className="flex items-start gap-3 flex-1">
                  <Cookie className="h-6 w-6 text-indigo-600 flex-shrink-0 mt-1" />
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {t.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                      {t.description}{' '}
                      <Link
                        href="/annexes/cookies"
                        className="text-indigo-600 dark:text-indigo-400 hover:underline"
                      >
                        {t.learnMore}
                      </Link>
                    </p>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
                  <button
                    onClick={() => setShowDetails(true)}
                    className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm font-medium"
                  >
                    {t.buttons.customize}
                  </button>
                  <button
                    onClick={handleAcceptEssential}
                    className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm font-medium"
                  >
                    {t.buttons.essential}
                  </button>
                  <button
                    onClick={handleAcceptAll}
                    className="px-6 py-2 bg-indigo-600 text-white hover:bg-indigo-700 rounded-lg transition-colors text-sm font-medium"
                  >
                    {t.buttons.acceptAll}
                  </button>
                </div>
              </div>)
            ) : (
              /* Detailed Banner */
              (<div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Cookie className="h-6 w-6 text-indigo-600" />
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {t.customization.title}
                    </h3>
                  </div>
                  <button
                    onClick={() => setShowDetails(false)}
                    className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    aria-label="Close details"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  {t.customization.description}
                </p>
                <div className="grid gap-4 md:grid-cols-2">
                  {cookieCategories.map((category) => {
                    const Icon = category.icon;
                    const isEnabled = preferences[category.key];
                    
                    return (
                      <div
                        key={category.key}
                        className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-3"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <Icon className="h-5 w-5 text-indigo-600 flex-shrink-0" />
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {category.title}
                                {category.required && (
                                  <span className="ml-2 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded">
                                    {t.customization.required}
                                  </span>
                                )}
                              </h4>
                            </div>
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
                <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={handleAcceptEssential}
                    className="px-6 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm font-medium"
                  >
                    {t.buttons.essential}
                  </button>
                  <button
                    onClick={handleCustomSave}
                    className="px-6 py-2 bg-indigo-600 text-white hover:bg-indigo-700 rounded-lg transition-colors text-sm font-medium"
                  >
                    {t.buttons.savePreferences}
                  </button>
                  <button
                    onClick={handleAcceptAll}
                    className="px-6 py-2 bg-green-600 text-white hover:bg-green-700 rounded-lg transition-colors text-sm font-medium"
                  >
                    {t.buttons.acceptAll}
                  </button>
                </div>
              </div>)
            )}
          </div>
        </div>
      </div>
    </>
  );
};