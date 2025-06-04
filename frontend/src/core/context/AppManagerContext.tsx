// src/core/context/AppManagerContext.tsx
'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { appManagerService, App, UserAppSettings } from '@/core/api/appManagerApi';
import { useAuthContext } from '@/core/auth/AuthAdapter';

interface AppManagerContextType {
  availableApps: App[];
  enabledApps: App[];
  enabledAppCodes: string[];
  userAppSettings: UserAppSettings | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  refreshApps: () => Promise<void>;
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
  const [enabledApps, setEnabledApps] = useState<App[]>([]);
  const [enabledAppCodes, setEnabledAppCodes] = useState<string[]>([]);
  const [userAppSettings, setUserAppSettings] = useState<UserAppSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshApps = async () => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Fetch available apps and user settings in parallel
      const [apps, userSettings] = await Promise.all([
        appManagerService.getAvailableApps(),
        appManagerService.getUserAppSettings()
      ]);

      setAvailableApps(apps);
      setUserAppSettings(userSettings);
      setEnabledApps(userSettings.enabled_apps);
      setEnabledAppCodes(userSettings.enabled_apps.map(app => app.code));

    } catch (err) {
      console.error('Error fetching app data:', err);
      setError('Failed to load app data');
    } finally {
      setLoading(false);
    }
  };

  const toggleApp = async (appCode: string, enabled: boolean): Promise<boolean> => {
    try {
      const response = await appManagerService.toggleApp(appCode, enabled);
      
      if (response.success) {
        // Update local state
        await refreshApps();
        return true;
      } else {
        setError(response.message);
        return false;
      }
    } catch (err) {
      console.error('Error toggling app:', err);
      setError('Failed to toggle app');
      return false;
    }
  };

  const isAppEnabled = (appCode: string): boolean => {
    return enabledAppCodes.includes(appCode);
  };

  // Load apps when user authentication changes
  useEffect(() => {
    if (isAuthenticated && user) {
      refreshApps();
    } else {
      // Clear data when user logs out
      setAvailableApps([]);
      setEnabledApps([]);
      setEnabledAppCodes([]);
      setUserAppSettings(null);
      setLoading(false);
    }
  }, [isAuthenticated, user]);

  const value: AppManagerContextType = {
    availableApps,
    enabledApps,
    enabledAppCodes,
    userAppSettings,
    loading,
    error,
    refreshApps,
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