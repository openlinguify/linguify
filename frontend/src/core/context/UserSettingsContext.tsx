// src/core/context/UserSettingsContext.tsx
import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import apiClient from '@/core/api/apiClient';
import { useAuthContext } from '@/core/auth/AuthAdapter';
import { toast } from '@/components/ui/use-toast';
import { DEFAULT_USER_SETTINGS } from '@/addons/settings/constants/usersettings';

// Type du contexte
export interface UserSettingsContextType {
  settings: typeof DEFAULT_USER_SETTINGS;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  updateSetting: <K extends keyof typeof DEFAULT_USER_SETTINGS>(
    key: K, 
    value: typeof DEFAULT_USER_SETTINGS[K]
  ) => Promise<void>;
  updateSettings: (newSettings: Partial<typeof DEFAULT_USER_SETTINGS>) => Promise<void>;
  refreshSettings: () => Promise<void>;
  
  // Getters pour faciliter l'accès aux paramètres courants
  getTargetLanguage: () => string;
  getNativeLanguage: () => string;
  getLanguageLevel: () => string;
}

// Création du contexte
const UserSettingsContext = createContext<UserSettingsContextType | null>(null);

// Provider Component
export const UserSettingsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated, user, token, isLoading: authLoading } = useAuthContext();
  
  const [settings, setSettings] = useState<typeof DEFAULT_USER_SETTINGS>({ ...DEFAULT_USER_SETTINGS });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialized, setInitialized] = useState(false);

  // Fonction pour charger les paramètres (stable avec useCallback)
  const loadSettings = useCallback(async () => {
      // Déjà en cours de chargement ou initialisé, ne pas recharger
      if (isLoading || initialized) return;

      setIsLoading(true);
      setError(null);

      try {
        // Récupérer la langue UI stockée dans localStorage pour synchronisation
        const storedUILanguage = localStorage.getItem('language');
        let finalSettings = { ...DEFAULT_USER_SETTINGS };

        // Charger les paramètres depuis le backend si authentifié
        if (isAuthenticated && token && token.length > 10 && !authLoading) {
          try {
            const response = await apiClient.get('/api/auth/profile/');
            
            if (response?.data) {
              const backendSettings = {
                ...finalSettings,
                email_notifications: response.data.email_notifications ?? true,
                push_notifications: response.data.push_notifications ?? true,
                interface_language: storedUILanguage || response.data.interface_language || 'en',
                daily_goal: response.data.daily_goal ?? 20,
                weekday_reminders: response.data.weekday_reminders ?? true,
                weekend_reminders: response.data.weekend_reminders ?? false,
                reminder_time: response.data.reminder_time || '18:00',
                target_language: response.data.target_language || finalSettings.target_language,
                native_language: response.data.native_language || finalSettings.native_language,
                language_level: response.data.language_level || finalSettings.language_level
              };
              finalSettings = backendSettings;
              // Settings loaded successfully
            } else {
              // No backend data, using defaults
            }
          } catch (error) {
            console.error('[UserSettings] Error loading from backend, using defaults:', error);
            // Fallback to defaults on error
          }
        } else {
        // Si non authentifié OU pas de token valide, charger depuis localStorage
          const storedData = localStorage.getItem('userSettings');
          if (storedData) {
            try {
              const parsedSettings = JSON.parse(storedData);
              finalSettings = { ...finalSettings, ...parsedSettings };
              console.debug('[UserSettings] Loaded settings from localStorage', parsedSettings);
            } catch (parseError) {
              console.error('[UserSettings] Error parsing stored settings:', parseError);
            }
          }
        }

        // Synchroniser avec la langue UI si elle existe et est valide
        if (storedUILanguage && ['en', 'fr', 'es', 'nl'].includes(storedUILanguage)) {
          // Si la langue UI diffère de celle des paramètres, la priorité va à la langue UI
          if (finalSettings.interface_language !== storedUILanguage) {
            console.debug('[UserSettings] Synchronizing with UI language:', storedUILanguage);
            finalSettings.interface_language = storedUILanguage;
          }
        }

        // Mettre à jour les paramètres
        setSettings(finalSettings);

        // Mettre à jour localStorage
        localStorage.setItem('userSettings', JSON.stringify(finalSettings));
      } catch (e) {
        console.error('[UserSettings] Error loading settings:', e);
        setError('Failed to load user settings');
      } finally {
        setIsLoading(false);
        setInitialized(true);
      }
  }, [isAuthenticated, token, isLoading, initialized, authLoading]);

  // Charger les paramètres initiaux
  useEffect(() => {
    // Si l'authentification est chargée, charger les paramètres seulement si authentifié
    if (!authLoading && !initialized) {
      if (isAuthenticated && token) {
        loadSettings();
      } else {
        setInitialized(true);
        setIsLoading(false);
      }
    }
  }, [isAuthenticated, authLoading, token, initialized, loadSettings]);

  // Si l'utilisateur est connecté, utiliser les données du profil
  useEffect(() => {
    if (user && initialized) {
      const userLanguageSettings = {
        native_language: (user as any).native_language as string,
        target_language: (user as any).target_language as string,
        language_level: (user as any).language_level as string,
        objectives: (user as any).objectives as string,
      };
      
      // Mettre à jour les paramètres avec les données utilisateur seulement si nécessaire
      setSettings(prev => {
        const needsUpdate = Object.entries(userLanguageSettings).some(
          ([key, value]) => prev[key as keyof typeof prev] !== value
        );
        
        if (needsUpdate) {
          const updatedSettings = { ...prev, ...userLanguageSettings };
          // Mettre à jour localStorage
          localStorage.setItem('userSettings', JSON.stringify(updatedSettings));
          return updatedSettings;
        }
        
        return prev;
      });
    }
  }, [user, initialized]);

  // Mettre à jour un paramètre individuel
  const updateSetting = async <K extends keyof typeof DEFAULT_USER_SETTINGS>(
    key: K, 
    value: typeof DEFAULT_USER_SETTINGS[K]
  ) => {
    // Mettre à jour d'abord en local pour une interface réactive
    setSettings(prev => ({ ...prev, [key]: value }));
    
    // Mettre à jour dans localStorage
    const currentSettings = { ...settings, [key]: value };
    localStorage.setItem('userSettings', JSON.stringify(currentSettings));
    
    // Si authentifié, synchroniser avec le backend
    if (isAuthenticated && token) {
      setIsSaving(true);
      
      try {
        // Format spécial pour les paramètres de langue qui vont dans le profil
        if (['native_language', 'target_language', 'language_level', 'objectives'].includes(key as string)) {
          await apiClient.patch('/api/auth/profile/', { [key]: value });
        } else {
          // Autres paramètres via l'endpoint settings
          await apiClient.post('/api/auth/me/settings/', { [key]: value });
        }
        
        console.debug(`[UserSettings] Successfully updated ${String(key)} to ${String(value)}`);
      } catch (error) {
        console.error(`[UserSettings] Error updating ${String(key)}:`, error);
        // Restaurer l'ancienne valeur en cas d'erreur
        setSettings(prev => ({ ...prev, [key]: prev[key] }));
        
        // Afficher une notification d'erreur
        toast({
          title: "Settings Update Failed",
          description: `Failed to update ${String(key)}. Please try again.`,
          variant: "destructive",
        });
        
        throw error;
      } finally {
        setIsSaving(false);
      }
    }
  };

  // Mettre à jour plusieurs paramètres à la fois
  const updateSettings = async (newSettings: Partial<typeof DEFAULT_USER_SETTINGS>) => {
    // Mettre à jour d'abord en local
    setSettings(prev => ({ ...prev, ...newSettings }));
    
    // Mettre à jour dans localStorage
    const currentSettings = { ...settings, ...newSettings };
    localStorage.setItem('userSettings', JSON.stringify(currentSettings));
    
    // Si authentifié, synchroniser avec le backend
    if (isAuthenticated && token) {
      setIsSaving(true);
      
      try {
        // Séparer les paramètres de langue des autres paramètres
        const languageSettings: Record<string, any> = {};
        const otherSettings: Record<string, any> = {};
        
        Object.entries(newSettings).forEach(([key, value]) => {
          if (['native_language', 'target_language', 'language_level', 'objectives'].includes(key)) {
            languageSettings[key] = value;
          } else {
            otherSettings[key] = value;
          }
        });
        
        // Mise à jour parallèle si nécessaire
        const promises = [];
        
        if (Object.keys(languageSettings).length > 0) {
          promises.push(apiClient.patch('/api/auth/profile/', languageSettings));
        }
        
        if (Object.keys(otherSettings).length > 0) {
          promises.push(apiClient.post('/api/auth/me/settings/', otherSettings));
        }
        
        await Promise.all(promises);
        
        toast({
          title: "Settings Updated",
          description: "Your settings have been updated successfully.",
        });
        
      } catch (error) {
        console.error('[UserSettings] Error updating multiple settings:', error);
        
        // Restaurer les anciens paramètres en cas d'erreur
        await refreshSettings();
        
        toast({
          title: "Settings Update Failed",
          description: "Failed to update settings. Please try again.",
          variant: "destructive",
        });
        
        throw error;
      } finally {
        setIsSaving(false);
      }
    }
  };

  // Recharger les paramètres depuis le serveur
  const refreshSettings = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      if (isAuthenticated && token) {
        const response = await apiClient.get('/api/auth/me/settings/');
        
        if (response.data) {
          const mergedSettings = { ...DEFAULT_USER_SETTINGS, ...response.data };
          setSettings(mergedSettings);
          
          // Mettre à jour localStorage
          localStorage.setItem('userSettings', JSON.stringify(mergedSettings));
        }
      } else {
        // Si non authentifié, charger depuis localStorage
        const storedData = localStorage.getItem('userSettings');
        if (storedData) {
          const parsedSettings = JSON.parse(storedData);
          setSettings({ ...DEFAULT_USER_SETTINGS, ...parsedSettings });
        }
      }
    } catch (e) {
      console.error('[UserSettings] Error refreshing settings:', e);
      setError('Failed to refresh user settings');
      
      toast({
        title: "Error",
        description: "Failed to refresh settings. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Fonction helper pour obtenir la langue cible formatée
  const getTargetLanguage = () => {
    return settings.target_language?.toLowerCase() || 'en';
  };

  // Fonction helper pour obtenir la langue maternelle formatée
  const getNativeLanguage = () => {
    return settings.native_language?.toLowerCase() || 'fr';
  };

  // Fonction helper pour obtenir le niveau de langue
  const getLanguageLevel = () => {
    return settings.language_level;
  };

  // Valeur du contexte
  const contextValue: UserSettingsContextType = {
    settings,
    isLoading,
    isSaving,
    error,
    updateSetting,
    updateSettings,
    refreshSettings,
    getTargetLanguage,
    getNativeLanguage,
    getLanguageLevel
  };

  return (
    <UserSettingsContext.Provider value={contextValue}>
      {children}
    </UserSettingsContext.Provider>
  );
};

// Hook personnalisé pour utiliser le contexte
export const useUserSettings = () => {
  const context = useContext(UserSettingsContext);
  
  if (!context) {
    throw new Error('useUserSettings must be used within a UserSettingsProvider');
  }
  
  return context;
};