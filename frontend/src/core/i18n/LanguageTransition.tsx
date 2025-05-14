'use client';

import React, { useState, useEffect, useMemo, useRef } from 'react';
import { createPortal } from 'react-dom';

// Constantes pour l'événement de changement de langue
const LANGUAGE_TRANSITION_EVENT = 'app:language:transition';

// Types de transition disponibles
export enum TransitionType {
  LANGUAGE = 'language',
  PROFILE = 'profile',
  SETTINGS = 'settings',
  NOTIFICATION = 'notification',
  APPEARANCE = 'appearance',
  LEARNING = 'learning',
  PRIVACY = 'privacy'
}

// Structure de données pour les textes de transition
// Extraits pour faciliter la maintenance et performance
const transitionTexts = {
  title: {
    en: {
      [TransitionType.LANGUAGE]: 'Changing language...',
      [TransitionType.PROFILE]: 'Updating profile...',
      [TransitionType.SETTINGS]: 'Saving settings...',
      [TransitionType.NOTIFICATION]: 'Updating notifications...',
      [TransitionType.APPEARANCE]: 'Updating appearance...',
      [TransitionType.LEARNING]: 'Updating learning preferences...',
      [TransitionType.PRIVACY]: 'Updating privacy settings...',
      default: 'Saving changes...'
    },
    fr: {
      [TransitionType.LANGUAGE]: 'Changement de langue...',
      [TransitionType.PROFILE]: 'Mise à jour du profil...',
      [TransitionType.SETTINGS]: 'Enregistrement des paramètres...',
      [TransitionType.NOTIFICATION]: 'Mise à jour des notifications...',
      [TransitionType.APPEARANCE]: 'Mise à jour de l\'apparence...',
      [TransitionType.LEARNING]: 'Mise à jour des préférences d\'apprentissage...',
      [TransitionType.PRIVACY]: 'Mise à jour des paramètres de confidentialité...',
      default: 'Enregistrement des modifications...'
    },
    es: {
      [TransitionType.LANGUAGE]: 'Cambiando idioma...',
      [TransitionType.PROFILE]: 'Actualizando perfil...',
      [TransitionType.SETTINGS]: 'Guardando configuración...',
      [TransitionType.NOTIFICATION]: 'Actualizando notificaciones...',
      [TransitionType.APPEARANCE]: 'Actualizando apariencia...',
      [TransitionType.LEARNING]: 'Actualizando preferencias de aprendizaje...',
      [TransitionType.PRIVACY]: 'Actualizando configuración de privacidad...',
      default: 'Guardando cambios...'
    },
    nl: {
      [TransitionType.LANGUAGE]: 'Taal wijzigen...',
      [TransitionType.PROFILE]: 'Profiel bijwerken...',
      [TransitionType.SETTINGS]: 'Instellingen opslaan...',
      [TransitionType.NOTIFICATION]: 'Meldingen bijwerken...',
      [TransitionType.APPEARANCE]: 'Uiterlijk bijwerken...',
      [TransitionType.LEARNING]: 'Leervoorkeuren bijwerken...',
      [TransitionType.PRIVACY]: 'Privacy-instellingen bijwerken...',
      default: 'Wijzigingen opslaan...'
    }
  },
  description: {
    en: {
      [TransitionType.LANGUAGE]: 'Please wait while we update the interface.',
      [TransitionType.PROFILE]: 'Please wait while we update your profile information.',
      [TransitionType.SETTINGS]: 'Please wait while we apply your new settings.',
      [TransitionType.NOTIFICATION]: 'Please wait while we update your notification preferences.',
      [TransitionType.APPEARANCE]: 'Please wait while we apply your appearance preferences.',
      [TransitionType.LEARNING]: 'Please wait while we update your learning preferences.',
      [TransitionType.PRIVACY]: 'Please wait while we update your privacy settings.',
      default: 'Please wait while we save your changes.'
    },
    fr: {
      [TransitionType.LANGUAGE]: 'Veuillez patienter pendant que nous mettons à jour l\'interface.',
      [TransitionType.PROFILE]: 'Veuillez patienter pendant que nous mettons à jour vos informations de profil.',
      [TransitionType.SETTINGS]: 'Veuillez patienter pendant que nous appliquons vos nouveaux paramètres.',
      [TransitionType.NOTIFICATION]: 'Veuillez patienter pendant que nous mettons à jour vos préférences de notification.',
      [TransitionType.APPEARANCE]: 'Veuillez patienter pendant que nous appliquons vos préférences d\'apparence.',
      [TransitionType.LEARNING]: 'Veuillez patienter pendant que nous mettons à jour vos préférences d\'apprentissage.',
      [TransitionType.PRIVACY]: 'Veuillez patienter pendant que nous mettons à jour vos paramètres de confidentialité.',
      default: 'Veuillez patienter pendant que nous enregistrons vos modifications.'
    },
    es: {
      [TransitionType.LANGUAGE]: 'Por favor espere mientras actualizamos la interfaz.',
      [TransitionType.PROFILE]: 'Por favor espere mientras actualizamos su información de perfil.',
      [TransitionType.SETTINGS]: 'Por favor espere mientras aplicamos su nueva configuración.',
      [TransitionType.NOTIFICATION]: 'Por favor espere mientras actualizamos sus preferencias de notificación.',
      [TransitionType.APPEARANCE]: 'Por favor espere mientras aplicamos sus preferencias de apariencia.',
      [TransitionType.LEARNING]: 'Por favor espere mientras actualizamos sus preferencias de aprendizaje.',
      [TransitionType.PRIVACY]: 'Por favor espere mientras actualizamos su configuración de privacidad.',
      default: 'Por favor espere mientras guardamos sus cambios.'
    },
    nl: {
      [TransitionType.LANGUAGE]: 'Een ogenblik geduld terwijl we de interface bijwerken.',
      [TransitionType.PROFILE]: 'Een ogenblik geduld terwijl we uw profielinformatie bijwerken.',
      [TransitionType.SETTINGS]: 'Een ogenblik geduld terwijl we uw nieuwe instellingen toepassen.',
      [TransitionType.NOTIFICATION]: 'Een ogenblik geduld terwijl we uw meldingsvoorkeuren bijwerken.',
      [TransitionType.APPEARANCE]: 'Een ogenblik geduld terwijl we uw uiterlijke voorkeuren toepassen.',
      [TransitionType.LEARNING]: 'Een ogenblik geduld terwijl we uw leervoorkeuren bijwerken.',
      [TransitionType.PRIVACY]: 'Een ogenblik geduld terwijl we uw privacy-instellingen bijwerken.',
      default: 'Een ogenblik geduld terwijl we uw wijzigingen opslaan.'
    }
  }
};

// Optimisée pour la performance - aucun recalcul des textes à chaque rendu
const getTransitionText = (
  section: 'title' | 'description',
  locale: string,
  type: TransitionType
): string => {
  // Fallback à l'anglais si la langue n'est pas supportée
  const supportedLocale = ['en', 'fr', 'es', 'nl'].includes(locale) ? locale : 'en';
  
  // Récupérer les textes pour cette langue
  const textsForLocale = transitionTexts[section][supportedLocale as keyof typeof transitionTexts.title];
  
  // Retourner le texte spécifique ou la valeur par défaut
  return textsForLocale[type] || textsForLocale.default;
};

interface LanguageTransitionState {
  active: boolean;
  locale: string | null;
  type: TransitionType;
}

/**
 * Composant qui affiche une transition visuelle lors du changement de langue
 * Montré juste avant un rechargement de page pour une meilleure UX
 */
export function LanguageTransition() {
  const [state, setState] = useState<LanguageTransitionState>({
    active: false,
    locale: null,
    type: TransitionType.LANGUAGE
  });
  
  // Référence au nœud de portail pour éviter les recréations
  const portalRef = useRef<HTMLDivElement | null>(null);
  
  // Créer le nœud de portail une seule fois
  if (!portalRef.current && typeof document !== 'undefined') {
    portalRef.current = document.createElement('div');
    portalRef.current.id = 'language-transition-portal';
    document.body.appendChild(portalRef.current);
  }

  useEffect(() => {
    // Fonction qui gère l'événement de transition
    const handleTransition = (event: Event) => {
      const customEvent = event as CustomEvent;
      if (customEvent.detail && customEvent.detail.locale) {
        setState({
          active: true,
          locale: customEvent.detail.locale,
          type: customEvent.detail.type || TransitionType.LANGUAGE
        });
      }
    };

    // Ajouter l'écouteur d'événements
    window.addEventListener(LANGUAGE_TRANSITION_EVENT, handleTransition);

    // Nettoyer
    return () => {
      window.removeEventListener(LANGUAGE_TRANSITION_EVENT, handleTransition);
      
      // Nettoyer le nœud de portail lors du démontage du composant
      if (portalRef.current && document.body.contains(portalRef.current)) {
        document.body.removeChild(portalRef.current);
      }
    };
  }, []);

  // Ne rien afficher si inactif
  if (!state.active || !portalRef.current) {
    return null;
  }

  // Calculer les textes une seule fois par rendu avec les valeurs actuelles
  const title = getTransitionText('title', state.locale || 'en', state.type);
  const description = getTransitionText('description', state.locale || 'en', state.type);

  // Portail pour monter au niveau le plus haut du DOM
  return createPortal(
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 transition-opacity duration-300 ease-in-out">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-md mx-auto text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <h3 className="text-xl font-semibold mb-2">
          {title}
        </h3>
        <p className="text-gray-500 dark:text-gray-300">
          {description}
        </p>
      </div>
    </div>,
    portalRef.current
  );
}

// Fonction utilitaire pour déclencher la transition visuelle
// Memoizée pour éviter des déclenchements trop fréquents
let lastTransitionTime = 0;
const DEBOUNCE_TIME = 300; // ms

/**
 * Fonction utilitaire pour déclencher la transition visuelle avec protection debounce
 * @param locale Code de langue ('en', 'fr', etc.)
 * @param type Type de transition (optionnel, défaut: TransitionType.LANGUAGE)
 */
export function triggerLanguageTransition(locale: string, type: TransitionType = TransitionType.LANGUAGE) {
  const now = Date.now();
  
  // Protection contre les déclenchements trop rapprochés
  if (now - lastTransitionTime < DEBOUNCE_TIME) {
    console.log('Debounced language transition');
    return;
  }
  
  lastTransitionTime = now;
  
  const event = new CustomEvent(LANGUAGE_TRANSITION_EVENT, {
    detail: { locale, type }
  });
  window.dispatchEvent(event);
}