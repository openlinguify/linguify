'use client';

import { useEffect } from 'react';
import { useUserSettings } from '@/core/context/UserSettingsContext';

// Event name constant must match the one in useTranslations.ts
const LANGUAGE_CHANGE_EVENT = 'app:language:changed';

/**
 * Hook personnalisé qui synchronise le changement de langue entre différents composants
 * sans nécessiter de rafraîchissement de page.
 */
export function useLanguageSync() {
  const { updateSetting } = useUserSettings();

  useEffect(() => {
    // Fonction qui gère les changements de langue globaux
    const handleLanguageChange = (event: Event) => {
      const customEvent = event as CustomEvent;
      if (customEvent.detail && customEvent.detail.locale) {
        const newLocale = customEvent.detail.locale;
        console.log('Language change detected by sync hook:', newLocale);
        
        // Mettre à jour les paramètres utilisateur avec la nouvelle langue
        updateSetting('interface_language', newLocale).catch(err => {
          console.error('Failed to sync user settings after language change:', err);
        });
      }
    };

    // Récupérer le bus d'événements globaux
    const eventBus = window as unknown as EventTarget;
    
    // S'abonner aux événements de changement de langue
    eventBus.addEventListener(LANGUAGE_CHANGE_EVENT, handleLanguageChange);
    
    // Nettoyer l'abonnement quand le composant est démonté
    return () => {
      eventBus.removeEventListener(LANGUAGE_CHANGE_EVENT, handleLanguageChange);
    };
  }, [updateSetting]);
  
  // Ce hook ne renvoie rien, il se contente de réagir aux changements
  return null;
}