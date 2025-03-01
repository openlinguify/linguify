'use client';

import React, { useEffect, useState, useMemo, useCallback } from 'react';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { GlobeIcon, BookOpen, Brain, Users, MessageCircle, UserCog } from 'lucide-react';

// Import translations (consider using a translation library like i18next or next-intl instead)
import frTranslations from '@/locales/fr/common.json';
import enTranslations from '@/locales/en/common.json';
import esTranslations from '@/locales/es/common.json';
import nlTranslations from '@/locales/nl/common.json';

// Type definitions
type AvailableLocales = 'fr' | 'en' | 'es' | 'nl';
type TranslationType = typeof enTranslations;

interface Feature {
  id: keyof typeof FEATURE_ICONS;
  title: string;
  description: string;
  image: string;
}

// Constants
const FEATURE_ICONS = {
  learning: BookOpen,
  flashcards: Brain,
  notebook: BookOpen, // Note: This is a duplicate icon, consider using a different one
  community: Users,
  chat: MessageCircle,
  coaching: UserCog,
};

const AVAILABLE_LOCALES: AvailableLocales[] = ['en', 'fr', 'es', 'nl'];

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { 
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: { 
    y: 0, 
    opacity: 1,
    transition: { duration: 0.5 }
  }
};

export default function Features() {
  const [locale, setLocale] = useState<AvailableLocales>('en');

  // Function to validate locales
  const isValidLocale = useCallback((locale: string): locale is AvailableLocales => {
    return AVAILABLE_LOCALES.includes(locale as AvailableLocales);
  }, []);

  // Load and handle language changes
  useEffect(() => {
    const updateLanguage = () => {
      const savedLanguage = localStorage.getItem('language');
      if (savedLanguage && isValidLocale(savedLanguage)) {
        setLocale(savedLanguage);
      }
    };

    // Initialize
    updateLanguage();

    // Set up event listener
    window.addEventListener('languageChanged', updateLanguage);
    
    // Cleanup
    return () => {
      window.removeEventListener('languageChanged', updateLanguage);
    };
  }, [isValidLocale]);

  // Create translation map
  const translations = useMemo<Record<AvailableLocales, TranslationType>>(() => ({
    fr: frTranslations,
    en: enTranslations,
    es: esTranslations,
    nl: nlTranslations
  }), []);

  // Translation function
  const t = useCallback((key: string): string => {
    try {
      const keys = key.split('.');
      
      // Make sure the locale exists, otherwise use English
      const currentTranslation = translations[locale] || translations['en'];
      
      let value: any = currentTranslation;
      for (const k of keys) {
        if (!value || typeof value !== 'object') {
          console.warn(`Translation key not found: ${key} (stopped at ${k})`);
          return key;
        }
        value = value[k];
      }
      
      return typeof value === 'string' ? value : key;
    } catch (error) {
      console.error('Translation error:', error);
      return key;
    }
  }, [locale, translations]);

  // Generate features list with translations
  const features = useMemo<Feature[]>(() => [
    {
      id: 'learning',
      title: t("learning.title"),
      description: t("learning.description"),
      image: "/units-pic1.png",
    },
    {
      id: 'flashcards',
      title: t("flashcards.title"),
      description: t("flashcards.description"),
      image: "/landing/features/flashcard-pic1.png",
    },
    {
      id: 'notebook',
      title: t("notebook.title"),
      description: t("notebook.description"),
      image: "/img/feature3.png",
    },
    {
      id: 'community',
      title: t("community.title"),
      description: t("community.description"),
      image: "/img/feature4.png",
    },
    {
      id: 'chat',
      title: t("chat.title"),
      description: t("chat.description"),
      image: "/img/feature5.png",
    },
    {
      id: 'coaching',
      title: t("coaching.title"),
      description: t("coaching.description"),
      image: "/img/feature6.png",
    },
  ], [t]);

  // Handler for feature clicks
  const handleFeatureClick = useCallback((feature: Feature) => {
    console.log("Feature clicked:", feature.title);
    // Here you could add navigation to feature-specific pages
  }, []);

  // Feature card component to reduce repetition
  const FeatureCard = useCallback(({ feature }: { feature: Feature }) => {
    const FeatureIcon = FEATURE_ICONS[feature.id];
    
    return (
      <motion.div
        key={feature.id}
        className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300 cursor-pointer"
        onClick={() => handleFeatureClick(feature)}
        variants={itemVariants}
      >
        <div className="p-6">
          <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center mb-4">
            <FeatureIcon className="h-6 w-6 text-blue-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">{feature.title}</h3>
          <p className="text-gray-600">{feature.description}</p>
        </div>
        <div className="relative h-48 w-full bg-gray-100 overflow-hidden">
          {feature.image ? (
            <Image
              src={feature.image}
              alt={feature.title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              priority={feature.id === 'learning'} // Only prioritize the first image
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-400">Image coming soon</p>
            </div>
          )}
        </div>
      </motion.div>
    );
  }, [handleFeatureClick]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center p-2 bg-blue-50 rounded-full mb-4">
            <GlobeIcon className="h-6 w-6 text-blue-600" aria-hidden="true" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 lg:text-5xl mb-6">
            {t("features.heading")}
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t("features.subheading")}
          </p>
        </div>

        {/* Features Grid */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {features.map(feature => (
            <FeatureCard key={feature.id} feature={feature} />
          ))}
        </motion.div>

        {/* Call to Action */}
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">{t("features.cta.title")}</h2>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">{t("features.cta.description")}</p>
          <button 
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-lg shadow hover:shadow-lg transition-all duration-200"
            aria-label={t("features.cta.button")}
          >
            {t("features.cta.button")}
          </button>
        </div>

        {/* Language Indicator (for debugging) */}
        {process.env.NODE_ENV !== 'production' && (
          <div className="fixed bottom-4 right-4 bg-white rounded-full shadow px-3 py-1 text-xs text-gray-500 flex items-center space-x-1">
            <GlobeIcon className="h-3 w-3" />
            <span>Language: {locale.toUpperCase()}</span>
          </div>
        )}
      </div>
    </div>
  );
}