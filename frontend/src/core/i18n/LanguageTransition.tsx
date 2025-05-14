'use client';

import React, { useState, useEffect } from 'react';
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
    };
  }, []);

  // Ne rien afficher si inactif
  if (!state.active) {
    return null;
  }

  // Titre basé sur le type de transition et la langue
  const getTitle = (type: TransitionType, locale: string) => {
    if (locale === 'en') {
      switch (type) {
        case TransitionType.LANGUAGE: return 'Changing language...';
        case TransitionType.PROFILE: return 'Updating profile...';
        case TransitionType.SETTINGS: return 'Saving settings...';
        case TransitionType.NOTIFICATION: return 'Updating notifications...';
        case TransitionType.APPEARANCE: return 'Updating appearance...';
        case TransitionType.LEARNING: return 'Updating learning preferences...';
        case TransitionType.PRIVACY: return 'Updating privacy settings...';
        default: return 'Saving changes...';
      }
    } else if (locale === 'fr') {
      switch (type) {
        case TransitionType.LANGUAGE: return 'Changement de langue...';
        case TransitionType.PROFILE: return 'Mise à jour du profil...';
        case TransitionType.SETTINGS: return 'Enregistrement des paramètres...';
        case TransitionType.NOTIFICATION: return 'Mise à jour des notifications...';
        case TransitionType.APPEARANCE: return 'Mise à jour de l\'apparence...';
        case TransitionType.LEARNING: return 'Mise à jour des préférences d\'apprentissage...';
        case TransitionType.PRIVACY: return 'Mise à jour des paramètres de confidentialité...';
        default: return 'Enregistrement des modifications...';
      }
    } else if (locale === 'es') {
      switch (type) {
        case TransitionType.LANGUAGE: return 'Cambiando idioma...';
        case TransitionType.PROFILE: return 'Actualizando perfil...';
        case TransitionType.SETTINGS: return 'Guardando configuración...';
        case TransitionType.NOTIFICATION: return 'Actualizando notificaciones...';
        case TransitionType.APPEARANCE: return 'Actualizando apariencia...';
        case TransitionType.LEARNING: return 'Actualizando preferencias de aprendizaje...';
        case TransitionType.PRIVACY: return 'Actualizando configuración de privacidad...';
        default: return 'Guardando cambios...';
      }
    } else if (locale === 'nl') {
      switch (type) {
        case TransitionType.LANGUAGE: return 'Taal wijzigen...';
        case TransitionType.PROFILE: return 'Profiel bijwerken...';
        case TransitionType.SETTINGS: return 'Instellingen opslaan...';
        case TransitionType.NOTIFICATION: return 'Meldingen bijwerken...';
        case TransitionType.APPEARANCE: return 'Uiterlijk bijwerken...';
        case TransitionType.LEARNING: return 'Leervoorkeuren bijwerken...';
        case TransitionType.PRIVACY: return 'Privacy-instellingen bijwerken...';
        default: return 'Wijzigingen opslaan...';
      }
    }
    return 'Saving changes...';
  };

  // Description basée sur le type de transition et la langue
  const getDescription = (type: TransitionType, locale: string) => {
    if (locale === 'en') {
      switch (type) {
        case TransitionType.LANGUAGE: return 'Please wait while we update the interface.';
        case TransitionType.PROFILE: return 'Please wait while we update your profile information.';
        case TransitionType.SETTINGS: return 'Please wait while we apply your new settings.';
        case TransitionType.NOTIFICATION: return 'Please wait while we update your notification preferences.';
        case TransitionType.APPEARANCE: return 'Please wait while we apply your appearance preferences.';
        case TransitionType.LEARNING: return 'Please wait while we update your learning preferences.';
        case TransitionType.PRIVACY: return 'Please wait while we update your privacy settings.';
        default: return 'Please wait while we save your changes.';
      }
    } else if (locale === 'fr') {
      switch (type) {
        case TransitionType.LANGUAGE: return 'Veuillez patienter pendant que nous mettons à jour l\'interface.';
        case TransitionType.PROFILE: return 'Veuillez patienter pendant que nous mettons à jour vos informations de profil.';
        case TransitionType.SETTINGS: return 'Veuillez patienter pendant que nous appliquons vos nouveaux paramètres.';
        case TransitionType.NOTIFICATION: return 'Veuillez patienter pendant que nous mettons à jour vos préférences de notification.';
        case TransitionType.APPEARANCE: return 'Veuillez patienter pendant que nous appliquons vos préférences d\'apparence.';
        case TransitionType.LEARNING: return 'Veuillez patienter pendant que nous mettons à jour vos préférences d\'apprentissage.';
        case TransitionType.PRIVACY: return 'Veuillez patienter pendant que nous mettons à jour vos paramètres de confidentialité.';
        default: return 'Veuillez patienter pendant que nous enregistrons vos modifications.';
      }
    } else if (locale === 'es') {
      switch (type) {
        case TransitionType.LANGUAGE: return 'Por favor espere mientras actualizamos la interfaz.';
        case TransitionType.PROFILE: return 'Por favor espere mientras actualizamos su información de perfil.';
        case TransitionType.SETTINGS: return 'Por favor espere mientras aplicamos su nueva configuración.';
        case TransitionType.NOTIFICATION: return 'Por favor espere mientras actualizamos sus preferencias de notificación.';
        case TransitionType.APPEARANCE: return 'Por favor espere mientras aplicamos sus preferencias de apariencia.';
        case TransitionType.LEARNING: return 'Por favor espere mientras actualizamos sus preferencias de aprendizaje.';
        case TransitionType.PRIVACY: return 'Por favor espere mientras actualizamos su configuración de privacidad.';
        default: return 'Por favor espere mientras guardamos sus cambios.';
      }
    } else if (locale === 'nl') {
      switch (type) {
        case TransitionType.LANGUAGE: return 'Een ogenblik geduld terwijl we de interface bijwerken.';
        case TransitionType.PROFILE: return 'Een ogenblik geduld terwijl we uw profielinformatie bijwerken.';
        case TransitionType.SETTINGS: return 'Een ogenblik geduld terwijl we uw nieuwe instellingen toepassen.';
        case TransitionType.NOTIFICATION: return 'Een ogenblik geduld terwijl we uw meldingsvoorkeuren bijwerken.';
        case TransitionType.APPEARANCE: return 'Een ogenblik geduld terwijl we uw uiterlijke voorkeuren toepassen.';
        case TransitionType.LEARNING: return 'Een ogenblik geduld terwijl we uw leervoorkeuren bijwerken.';
        case TransitionType.PRIVACY: return 'Een ogenblik geduld terwijl we uw privacy-instellingen bijwerken.';
        default: return 'Een ogenblik geduld terwijl we uw wijzigingen opslaan.';
      }
    }
    return 'Please wait while we save your changes.';
  };

  // Titre et description basés sur le type et la langue
  const title = getTitle(state.type, state.locale || 'en');
  const description = getDescription(state.type, state.locale || 'en');

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
    document.body
  );
}

/**
 * Fonction utilitaire pour déclencher la transition visuelle
 * @param locale Code de langue ('en', 'fr', etc.)
 * @param type Type de transition (optionnel, défaut: TransitionType.LANGUAGE)
 */
export function triggerLanguageTransition(locale: string, type: TransitionType = TransitionType.LANGUAGE) {
  const event = new CustomEvent(LANGUAGE_TRANSITION_EVENT, {
    detail: { locale, type }
  });
  window.dispatchEvent(event);
}