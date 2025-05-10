'use client';

/**
 * OnboardingLanguageSelector Component
 *
 * This component provides a language selector dropdown for the onboarding flow.
 * It allows users to change the interface language during the onboarding process.
 *
 * The component displays the current language with its native name and flag,
 * and provides a dropdown menu with all available languages.
 *
 * When a language is selected, it:
 * 1. Updates the application's language context
 * 2. Calls the optional onLanguageChange callback with the new language code
 * 3. Shows a toast notification confirming the language change
 *
 * @component
 */

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Check, ChevronDown, Globe } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { useToast } from '@/components/ui/use-toast';

interface LanguageOption {
  value: string;
  label: string;
  nativeLabel: string;
  flag: string;
}

const LANGUAGES: LanguageOption[] = [
  { value: 'en', label: 'English', nativeLabel: 'English', flag: '🇬🇧' },
  { value: 'fr', label: 'French', nativeLabel: 'Français', flag: '🇫🇷' },
  { value: 'es', label: 'Spanish', nativeLabel: 'Español', flag: '🇪🇸' },
  { value: 'nl', label: 'Dutch', nativeLabel: 'Nederlands', flag: '🇳🇱' },
];

/**
 * Props for the OnboardingLanguageSelector component
 *
 * @interface OnboardingLanguageSelectorProps
 * @property {Function} [onLanguageChange] - Optional callback that is called when the language is changed
 */
interface OnboardingLanguageSelectorProps {
  /**
   * Callback function that is called when the language is changed
   * @param {string} language - The language code (e.g., "en", "fr")
   */
  onLanguageChange?: (language: string) => void;
}

const OnboardingLanguageSelector: React.FC<OnboardingLanguageSelectorProps> = ({
  onLanguageChange
}) => {
  const { t, locale, changeLanguage } = useTranslation();
  const { toast } = useToast();

  const handleLanguageChange = (langCode: string) => {
    changeLanguage(langCode as any);
    if (onLanguageChange) {
      onLanguageChange(langCode);
    }

    // Show a toast notification when the language changes
    toast({
      title: t('interface.languageChanged', { language: LANGUAGES.find(l => l.value === langCode)?.label || langCode }),
      duration: 3000
    });
  };

  const currentLanguage = LANGUAGES.find(lang => lang.value === locale) || LANGUAGES[0];

  return (
    <div className="relative">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button 
            variant="ghost" 
            size="sm" 
            className="flex items-center gap-1 px-2 text-xs font-normal"
            aria-label={t('interface.changeLanguage', {}, 'Change interface language')}
          >
            <Globe className="h-3 w-3 mr-1" />
            <span>{currentLanguage.nativeLabel}</span>
            <span className="text-base">{currentLanguage.flag}</span>
            <ChevronDown className="h-3 w-3 ml-1 opacity-70" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="min-w-[160px]">
          {LANGUAGES.map((language) => (
            <DropdownMenuItem
              key={language.value}
              onClick={() => handleLanguageChange(language.value)}
              className={`flex items-center justify-between py-2 ${locale === language.value ? 'bg-gray-100 dark:bg-gray-800' : ''}`}
            >
              <div className="flex items-center">
                <span className="text-base mr-2">{language.flag}</span>
                <span>{language.nativeLabel}</span>
              </div>
              {locale === language.value && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                >
                  <Check className="h-4 w-4 text-primary ml-2" />
                </motion.div>
              )}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

export default OnboardingLanguageSelector;