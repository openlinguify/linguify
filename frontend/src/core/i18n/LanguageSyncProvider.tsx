'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useLanguageSync } from './useLanguageSync';

// Event name constant
const LANGUAGE_CHANGE_EVENT = 'app:language:changed';

// Context type
interface LanguageSyncContextType {
  refreshLanguage: () => void;
}

// Create context
const LanguageSyncContext = createContext<LanguageSyncContextType | null>(null);

// Provider component
export function LanguageSyncProvider({ children }: { children: ReactNode }) {
  // Use our language sync hook
  useLanguageSync();
  
  // Function to manually trigger a refresh across all components
  const refreshLanguage = () => {
    const currentLanguage = localStorage.getItem('language');
    if (currentLanguage) {
      // Create a custom event
      const event = new CustomEvent(LANGUAGE_CHANGE_EVENT, {
        detail: { locale: currentLanguage, source: 'manual-refresh' }
      });
      
      // Dispatch the event
      window.dispatchEvent(event);
    }
  };
  
  // Context value
  const contextValue: LanguageSyncContextType = {
    refreshLanguage
  };
  
  return (
    <LanguageSyncContext.Provider value={contextValue}>
      {children}
    </LanguageSyncContext.Provider>
  );
}

// Hook to use the language sync context
export function useLanguageSyncContext() {
  const context = useContext(LanguageSyncContext);
  
  if (!context) {
    throw new Error('useLanguageSyncContext must be used within a LanguageSyncProvider');
  }
  
  return context;
}