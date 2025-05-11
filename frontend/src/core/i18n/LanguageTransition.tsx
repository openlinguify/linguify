'use client';

import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';

// Constantes pour l'événement de changement de langue
const LANGUAGE_TRANSITION_EVENT = 'app:language:transition';

interface LanguageTransitionState {
  active: boolean;
  locale: string | null;
}

/**
 * Composant qui affiche une transition visuelle lors du changement de langue
 * Montré juste avant un rechargement de page pour une meilleure UX
 */
export function LanguageTransition() {
  const [state, setState] = useState<LanguageTransitionState>({
    active: false,
    locale: null
  });

  useEffect(() => {
    // Fonction qui gère l'événement de transition
    const handleTransition = (event: Event) => {
      const customEvent = event as CustomEvent;
      if (customEvent.detail && customEvent.detail.locale) {
        setState({
          active: true,
          locale: customEvent.detail.locale
        });
      }
    };

    // Ajouter l'écouteur d'événements
    window.addEventListener(LANGUAGE_TRANSITION_EVENT, handleTransition);

    // Nettoyer
    return () => {
      window.removeEventListener(LANGUAGE_TRANSITION_EVENT, handleTransition);
    };
  }, []);

  // Ne rien afficher si inactif
  if (!state.active) {
    return null;
  }

  // Portail pour monter au niveau le plus haut du DOM
  return createPortal(
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 transition-opacity duration-300 ease-in-out">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-md mx-auto text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <h3 className="text-xl font-semibold mb-2">
          {state.locale === 'en' && 'Changing language...'}
          {state.locale === 'fr' && 'Changement de langue...'}
          {state.locale === 'es' && 'Cambiando idioma...'}
          {state.locale === 'nl' && 'Taal wijzigen...'}
        </h3>
        <p className="text-gray-500 dark:text-gray-300">
          {state.locale === 'en' && 'Please wait while we update the interface.'}
          {state.locale === 'fr' && 'Veuillez patienter pendant que nous mettons à jour l\'interface.'}
          {state.locale === 'es' && 'Por favor espere mientras actualizamos la interfaz.'}
          {state.locale === 'nl' && 'Een ogenblik geduld terwijl we de interface bijwerken.'}
        </p>
      </div>
    </div>,
    document.body
  );
}

/**
 * Fonction utilitaire pour déclencher la transition visuelle
 */
export function triggerLanguageTransition(locale: string) {
  const event = new CustomEvent(LANGUAGE_TRANSITION_EVENT, {
    detail: { locale }
  });
  window.dispatchEvent(event);
}