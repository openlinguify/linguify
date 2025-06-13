// src/core/context/AppManagerContext.tsx
'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { appManagerService, App } from '@/core/api/appManagerApi';
import { useAuthContext } from '@/core/auth/AuthAdapter';

/**
 * LOGIQUE SIMPLIFIÉE - UN SEUL CHEMIN DE VÉRITÉ
 * 
 * Le serveur détient la vérité absolue sur l'état des applications.
 * Aucune logique côté client - on utilise directement les réponses serveur.
 */
interface AppManagerContextType {
  // État des applications (lecture seule côté client)
  availableApps: App[];
  enabledAppCodes: string[]; // SEULE SOURCE DE VÉRITÉ
  loading: boolean;
  error: string | null;
  
  // Actions
  refreshApps: () => Promise<void>;
  forceRefresh: () => Promise<void>; // Rafraîchissement forcé sans cache
  toggleApp: (appCode: string, enabled: boolean) => Promise<boolean>;
  isAppEnabled: (appCode: string) => boolean;
}

const AppManagerContext = createContext<AppManagerContextType | undefined>(undefined);

interface AppManagerProviderProps {
  children: ReactNode;
}

export function AppManagerProvider({ children }: AppManagerProviderProps) {
  const { user, isAuthenticated } = useAuthContext();
  
  const [availableApps, setAvailableApps] = useState<App[]>([]);
  const [enabledAppCodes, setEnabledAppCodes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  console.log('[AppManagerProvider] Rendered with isAuthenticated:', isAuthenticated);

  const refreshApps = useCallback(async () => {
    console.log('[AppManager] refreshApps called, isAuthenticated:', isAuthenticated);
    
    if (!isAuthenticated) {
      console.log('[AppManager] Not authenticated, loading default apps');
      // Charger les apps par défaut même sans auth
      const defaultApps = [
        {
          id: 1,
          code: 'learning',
          display_name: 'Learning',
          description: 'Interactive language lessons',
          icon_name: 'BookOpen',
          color: '#3B82F6',
          route_path: '/learning',
          is_enabled: true,
          order: 1,
          created_at: '',
          updated_at: ''
        },
        {
          id: 2,
          code: 'flashcard',
          display_name: 'Flashcards',
          description: 'Review vocabulary with flashcards',
          icon_name: 'CreditCard',
          color: '#10B981',
          route_path: '/flashcard',
          is_enabled: true,
          order: 2,
          created_at: '',
          updated_at: ''
        },
        {
          id: 3,
          code: 'notebook',
          display_name: 'Notebook',
          description: 'Take notes and track progress',
          icon_name: 'FileText',
          color: '#F59E0B',
          route_path: '/notebook',
          is_enabled: true,
          order: 3,
          created_at: '',
          updated_at: ''
        },
        {
          id: 4,
          code: 'quizz',
          display_name: 'Quiz',
          description: 'Test your knowledge',
          icon_name: 'Brain',
          color: '#EF4444',
          route_path: '/quizz',
          is_enabled: true,
          order: 4,
          created_at: '',
          updated_at: ''
        }
      ];
      
      setAvailableApps(defaultApps);
      setEnabledAppCodes(['learning', 'flashcard', 'notebook', 'quizz']);
      setLoading(false);
      console.log('[AppManager] Default apps loaded (no auth)');
      return;
    }

    try {
      setError(null);
      console.log('[AppManager] Refreshing apps data...');
      
      // Timeout après 2 secondes pour éviter l'attente infinie
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      
      // Récupérer les applications disponibles et les paramètres utilisateur
      const [appsResponse, userSettingsResponse] = await Promise.all([
        appManagerService.getAvailableApps(),
        appManagerService.getUserAppSettings()
      ]);
      
      clearTimeout(timeoutId);

      const apps = appsResponse || [];
      const userSettings = userSettingsResponse || { enabled_apps: [] };

      // Extraire les codes d'applications activées
      console.log('[AppManager] Raw userSettings:', userSettings);
      console.log('[AppManager] enabled_apps type:', typeof userSettings.enabled_apps);
      console.log('[AppManager] enabled_apps content:', userSettings.enabled_apps);
      
      // Debug détaillé du contenu
      if (Array.isArray(userSettings.enabled_apps)) {
        console.log('[AppManager] enabled_apps détail:');
        userSettings.enabled_apps.forEach((app, index) => {
          console.log(`  [${index}] Code: ${app.code}, Name: ${app.display_name}`);
        });
      }
      
      const enabledAppCodes = userSettings.enabled_apps.map(app => 
        typeof app === 'string' ? app : app.code
      );

      console.log('[AppManager] Apps loaded:', apps.length);
      console.log('[AppManager] Raw apps from server:', apps);
      console.log('[AppManager] Final enabled app codes:', enabledAppCodes);
      
      // Debug détaillé des apps disponibles
      console.log('[AppManager] Apps disponibles détail:');
      apps.forEach((app, index) => {
        console.log(`  [${index}] Code: ${app.code}, Name: ${app.display_name}, ID: ${app.id}`);
      });
      
      // Vérifier s'il y a des doublons par code
      const appCodes = apps.map(app => app.code);
      const duplicateCodes = appCodes.filter((code, index) => appCodes.indexOf(code) !== index);
      if (duplicateCodes.length > 0) {
        console.warn('[AppManager] ⚠️ DUPLICATE APP CODES:', duplicateCodes);
      }

      // Vérifier s'il y a des doublons par nom (problème principal)
      const appNames = apps.map(app => app.display_name);
      const duplicateNames = appNames.filter((name, index) => appNames.indexOf(name) !== index);
      if (duplicateNames.length > 0) {
        console.warn('[AppManager] ⚠️ DUPLICATE APP NAMES:', duplicateNames);
        console.warn('[AppManager] Apps with duplicate names:', 
          apps.filter(app => duplicateNames.includes(app.display_name))
        );
      }

      // Déduplication par code ET par nom - priorité aux apps avec manifest (codes longs)
      const uniqueApps = apps.filter((app, index, arr) => {
        // Garde la première occurrence par code
        const firstByCode = arr.findIndex(a => a.code === app.code) === index;
        if (!firstByCode) return false;
        
        // Pour les doublons de nom, garde l'app avec le code le plus long (manifest-based)
        const sameNameApps = arr.filter(a => a.display_name === app.display_name);
        if (sameNameApps.length > 1) {
          const longest = sameNameApps.reduce((prev, curr) => 
            curr.code.length > prev.code.length ? curr : prev
          );
          return app.code === longest.code;
        }
        
        return true;
      });
      
      if (uniqueApps.length !== apps.length) {
        console.log('[AppManager] 🧹 Deduplicated apps:', apps.length, '->', uniqueApps.length);
      }

      setAvailableApps(uniqueApps);
      setEnabledAppCodes(enabledAppCodes);

    } catch (err) {
      console.error('[AppManager] Backend unavailable, using default apps:', err);
      
      // Backend indisponible - utiliser les apps par défaut
      const defaultApps = [
        {
          id: 1,
          code: 'learning',
          display_name: 'Learning',
          description: 'Interactive language lessons',
          icon_name: 'BookOpen',
          color: '#3B82F6',
          route_path: '/learning',
          is_enabled: true,
          order: 1,
          created_at: '',
          updated_at: ''
        },
        {
          id: 2,
          code: 'flashcard',
          display_name: 'Flashcards',
          description: 'Review vocabulary with flashcards',
          icon_name: 'CreditCard',
          color: '#10B981',
          route_path: '/flashcard',
          is_enabled: true,
          order: 2,
          created_at: '',
          updated_at: ''
        },
        {
          id: 3,
          code: 'notebook',
          display_name: 'Notebook',
          description: 'Take notes and track progress',
          icon_name: 'FileText',
          color: '#F59E0B',
          route_path: '/notebook',
          is_enabled: true,
          order: 3,
          created_at: '',
          updated_at: ''
        },
        {
          id: 4,
          code: 'quizz',
          display_name: 'Quiz',
          description: 'Test your knowledge',
          icon_name: 'Brain',
          color: '#EF4444',
          route_path: '/quizz',
          is_enabled: true,
          order: 4,
          created_at: '',
          updated_at: ''
        }
      ];
      
      setAvailableApps(defaultApps);
      setEnabledAppCodes(['learning', 'flashcard', 'notebook', 'quizz']);
      setError(null); // Pas d'erreur - on a des apps par défaut
      console.log('[AppManager] Default apps loaded (offline mode):', defaultApps.length);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const toggleApp = async (appCode: string, enabled: boolean): Promise<boolean> => {
    try {
      console.log(`[AppManager] === TOGGLE START ===`);
      console.log(`[AppManager] Action: ${enabled ? 'INSTALL' : 'UNINSTALL'} app: ${appCode}`);
      console.log(`[AppManager] State BEFORE toggle:`, enabledAppCodes);
      
      // Appel API - Le serveur détient la vérité absolue
      const response = await appManagerService.toggleApp(appCode, enabled);
      
      if (response.success) {
        console.log(`[AppManager] ✅ Toggle SUCCESS for ${appCode}`);
        console.log(`[AppManager] Server returned enabled_apps:`, response.enabled_apps);
        
        // LE SERVEUR EST LA SEULE SOURCE DE VÉRITÉ
        // On utilise directement sa réponse, sans transformation
        const serverEnabledApps = response.enabled_apps || [];
        
        console.log(`[AppManager] Setting state to server response:`, serverEnabledApps);
        setEnabledAppCodes(serverEnabledApps);
        
        console.log(`[AppManager] === TOGGLE END - SUCCESS ===`);
        return true;
      } else {
        console.error(`[AppManager] ❌ Toggle FAILED for ${appCode}:`, response.message);
        console.log(`[AppManager] === TOGGLE END - FAILED ===`);
        return false;
      }
    } catch (err) {
      console.error(`[AppManager] ❌ Toggle ERROR for ${appCode}:`, err);
      console.log(`[AppManager] === TOGGLE END - ERROR ===`);
      return false;
    }
  };

  const isAppEnabled = (appCode: string): boolean => {
    return enabledAppCodes.includes(appCode);
  };

  // Load apps when user authentication changes (only on initial auth, not on every user change)
  useEffect(() => {
    if (isAuthenticated && user) {
      console.log('[AppManager] User authenticated, loading apps...');
      refreshApps();
    } else if (!isAuthenticated) {
      console.log('[AppManager] User not authenticated, loading default apps');
      refreshApps(); // Load default apps même sans auth
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]); // Ne se déclenche que sur les changements d'authentification, pas sur chaque changement d'user

  // FORCE: Load apps immédiatement au montage
  useEffect(() => {
    console.log('[AppManager] Component mounted, force loading apps in 2 seconds');
    const timer = setTimeout(() => {
      if (loading) {
        console.log('[AppManager] Force timeout - loading default apps anyway');
        refreshApps();
      }
    }, 2000);
    
    return () => clearTimeout(timer);
  }, [loading, refreshApps]);

  const forceRefresh = useCallback(async () => {
    console.log('[AppManager] 🔄 FORCE REFRESH - Clearing cache...');
    setLoading(true);
    setError(null);
    // Force une requête fraîche en invalidant le cache
    await refreshApps();
  }, [refreshApps]);

  const value: AppManagerContextType = {
    availableApps,
    enabledAppCodes,
    loading,
    error,
    refreshApps,
    forceRefresh,
    toggleApp,
    isAppEnabled,
  };

  return (
    <AppManagerContext.Provider value={value}>
      {children}
    </AppManagerContext.Provider>
  );
}

export function useAppManager(): AppManagerContextType {
  const context = useContext(AppManagerContext);
  if (context === undefined) {
    throw new Error('useAppManager must be used within an AppManagerProvider');
  }
  return context;
}

export default AppManagerContext;