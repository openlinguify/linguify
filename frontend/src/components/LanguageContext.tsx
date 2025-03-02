// src/context/LanguageContext.tsx
'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type LanguageContextType = {
  currentLanguage: string;
  setLanguage: (lang: string) => void;
};

// Créer le contexte avec des valeurs par défaut
const LanguageContext = createContext<LanguageContextType>({
  currentLanguage: 'fr',
  setLanguage: () => {},
});

// Hook personnalisé pour utiliser le contexte de langue
export const useLanguage = () => useContext(LanguageContext);

// Fournisseur du contexte
export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  // État local pour stocker la langue courante
  const [currentLanguage, setCurrentLanguage] = useState('fr');

  // Charger la langue depuis localStorage au démarrage
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage) {
      setCurrentLanguage(savedLanguage);
    }
  }, []);

  // Fonction pour changer la langue
  const setLanguage = (lang: string) => {
    setCurrentLanguage(lang);
    localStorage.setItem('language', lang);
    // Déclencher un événement pour que d'autres composants puissent réagir
    window.dispatchEvent(new Event('languageChanged'));
  };

  return (
    <LanguageContext.Provider value={{ currentLanguage, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};