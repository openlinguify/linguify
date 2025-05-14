'use client';

import React, { useEffect, useState } from 'react';
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue
} from "@/components/ui/select";
import { useTranslation } from "@/core/i18n/useTranslations";
import { useToast } from "@/components/ui/use-toast";
import { useUserSettings } from "@/core/context/UserSettingsContext";
import { triggerLanguageTransition, TransitionType } from "@/core/i18n/LanguageTransition";

// Event name constant - must match the one in useTranslations.ts
const LANGUAGE_CHANGE_EVENT = 'app:language:changed';

interface LanguageSelectorProps {
  className?: string;
}

export function LanguageSelector({ className = "" }: LanguageSelectorProps) {
  const { t, locale, changeLanguage } = useTranslation();
  const { settings, updateSetting } = useUserSettings();
  const { toast } = useToast();
  const [selectedLanguage, setSelectedLanguage] = useState(locale);

  // Sync with user settings on mount and handle persistence across refreshes
  useEffect(() => {
    const initializeLanguage = () => {
      // First priority: user settings from context (backed by API)
      if (settings.interface_language &&
          ['en', 'fr', 'es', 'nl'].includes(settings.interface_language) &&
          settings.interface_language !== locale) {
        console.log('Setting language from user settings:', settings.interface_language);
        changeLanguage(settings.interface_language as any);
        setSelectedLanguage(settings.interface_language);
        return;
      }

      // Second priority: language stored in localStorage
      const storedLanguage = localStorage.getItem('language');
      if (storedLanguage &&
          ['en', 'fr', 'es', 'nl'].includes(storedLanguage) &&
          storedLanguage !== locale) {
        console.log('Setting language from localStorage:', storedLanguage);
        changeLanguage(storedLanguage as any);
        setSelectedLanguage(storedLanguage);

        // Also update user settings for consistency
        updateSetting('interface_language', storedLanguage).catch(err => {
          console.error('Failed to sync user settings with stored language:', err);
        });
        return;
      }

      // Default: use the current locale
      setSelectedLanguage(locale);
    };

    initializeLanguage();
  }, [settings.interface_language, locale, changeLanguage, updateSetting]);

  // Listen for language changes from other components
  useEffect(() => {
    const handleExternalLanguageChange = (event: Event) => {
      const customEvent = event as CustomEvent;
      if (customEvent.detail && customEvent.detail.locale) {
        const newLocale = customEvent.detail.locale;
        console.log('External language change detected:', newLocale);
        setSelectedLanguage(newLocale);
      }
    };

    // Add event listener
    window.addEventListener(LANGUAGE_CHANGE_EVENT, handleExternalLanguageChange);

    // Clean up
    return () => {
      window.removeEventListener(LANGUAGE_CHANGE_EVENT, handleExternalLanguageChange);
    };
  }, []);

  // Also update the selected language when locale changes
  useEffect(() => {
    setSelectedLanguage(locale);
  }, [locale]);

  const handleLanguageChange = async (value: string) => {
    try {
      // Update UI language first for immediate feedback
      changeLanguage(value as any);
      setSelectedLanguage(value);

      // Update user settings
      await updateSetting('interface_language', value);

      toast({
        title: t('dashboard.header.languageChanged'),
        description: t('dashboard.header.languageSetTo', { language: value.toUpperCase() }),
        duration: 800
      });

      // Déclencher la transition visuelle avant de recharger
      triggerLanguageTransition(value, TransitionType.LANGUAGE);

      // Force a hard reload for immediate effect
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error) {
      console.error('Failed to update language setting:', error);
      toast({
        title: 'Error',
        description: 'Failed to update language setting. Please try again.',
        variant: 'destructive',
      });
    }
  };

  return (
    <Select onValueChange={handleLanguageChange} value={selectedLanguage}>
      <SelectTrigger
        className={`w-32 dark:bg-transparent dark:border-none dark:text-gray-200 ${className}`}>
        <SelectValue placeholder={t('dashboard.header.language')} />
      </SelectTrigger>
      <SelectContent
        className="w-32 bg-background dark:bg-gray-900/70 backdrop-blur-xl shadow-lg border dark:border-gray-700/20"
      >
        <SelectItem value="en">{t('dashboard.header.english')}</SelectItem>
        <SelectItem value="fr">{t('dashboard.header.french')}</SelectItem>
        <SelectItem value="es">{t('dashboard.header.spanish')}</SelectItem>
        <SelectItem value="nl">{t('dashboard.header.dutch')}</SelectItem>
      </SelectContent>
    </Select>
  );
}