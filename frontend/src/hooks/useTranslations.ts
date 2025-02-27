// src/hooks/useTranslations.ts
'use client';
import { useState } from 'react';

// Variable globale pour stocker la langue active
let currentLocale = 'fr';

// Fonction pour définir la langue active
export function setLocale(locale: string) {
  currentLocale = locale;
  // Déclenche un événement pour informer les composants du changement
  window.dispatchEvent(new Event('localeChange'));
}

// Hook simplifié qui utilise un état local pour forcer le rendu
export function useTranslations(namespace: string = 'common') {
  // État local pour forcer le rendu quand la langue change
  const [, setRender] = useState({});

  // S'abonner aux changements de langue
  useState(() => {
    const handleLocaleChange = () => setRender({});
    window.addEventListener('localeChange', handleLocaleChange);
    return () => window.removeEventListener('localeChange', handleLocaleChange);
  });

  // Fonction de traduction simplifiée
  const t = (key: string): string => {
    try {
      // Essayer de charger les traductions pour la langue actuelle
      let translations;
      try {
        translations = require(`../../locales/${currentLocale}/${namespace}.json`);
      } catch (e) {
        // Fallback à la langue par défaut
        translations = require(`../../locales/fr/${namespace}.json`);
      }

      // Accéder à la traduction via la clé
      const keys = key.split('.');
      let value: any = translations;
      
      for (const k of keys) {
        if (!value || typeof value !== 'object') return key;
        value = value[k];
      }
      
      return typeof value === 'string' ? value : key;
    } catch (error) {
      // En cas d'erreur, retourner la clé
      return key;
    }
  };

  return t;
}


