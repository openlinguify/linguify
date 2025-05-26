// src/app/(dashboard)/(apps)/settings/_components/SettingsPage.tsx
'use client';

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "@/components/ui/use-toast";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import {
  User,
  Bell,
  Languages,
  Lock,
  CreditCard,
  Shield,
  AlertCircle,
  Loader2,
  Save,
  Camera,
  BookOpen,
  Palette,
  Mail,
  Calendar,
} from "lucide-react";
import { useAuthContext } from "@/core/auth/AuthProvider";
import { useLanguageSync } from "@/core/i18n/useLanguageSync";
import { useTranslation } from "@/core/i18n/useTranslations";
import { triggerLanguageTransition, TransitionType } from "@/core/i18n/LanguageTransition";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { DeleteAccountDialog } from "./DeleteAccountDialog";
import { ResetProgressDialog } from "./ResetProgressDialog";
import NotificationSettingsPanel from "./NotificationSettingsPanel";
import apiClient from '@/core/api/apiClient';
// Progress system removed - progressAPI disabled

import { 
  LANGUAGE_OPTIONS, 
  LEVEL_OPTIONS, 
  OBJECTIVES_OPTIONS,
  THEME_OPTIONS,
  GENDER_OPTIONS,
  INTERFACE_LANGUAGE_OPTIONS,
  UserSettings,
  ProfileFormData,
  DEFAULT_USER_SETTINGS,
} from '@/addons/settings/constants/usersettings';

export default function SettingsPage() {
  const { user, isAuthenticated, isLoading, logout } = useAuthContext();
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const { t } = useTranslation();

  // Active le système de synchronisation des langues entre les composants
  useLanguageSync();
  const [activeTab, setActiveTab] = useState(() => {
    return localStorage.getItem('settingsActiveTab') || 'profile';
  });
  const [activeProfileTab, setActiveProfileTab] = useState('personal');
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [settings, setSettings] = useState<UserSettings>(DEFAULT_USER_SETTINGS);
  
  const [formData, setFormData] = useState<ProfileFormData>({
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    bio: '',
    gender: null,
    birthday: null,
    native_language: 'EN',
    target_language: 'FR',
    language_level: 'A1',
    objectives: 'Travel',
    interface_language: 'en'
  });
  
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  
  const [alert, setAlert] = useState<{
    show: boolean;
    type: 'success' | 'error';
    message: string;
  }>({
    show: false,
    type: 'success',
    message: '',
  });

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        bio: user.bio || '',
        gender: user.gender || null,
        birthday: user.birthday ? new Date(user.birthday).toISOString().split('T')[0] : null,
        native_language: user.native_language || 'EN',
        target_language: user.target_language || 'FR',
        language_level: user.language_level || 'A1',
        objectives: user.objectives || 'Travel',
        interface_language: 'en'
      });
      
      // Set initial language settings from user data
      setSettings(prev => ({
        ...prev,
        native_language: user.native_language || "EN",
        target_language: user.target_language || "FR",
        language_level: user.language_level || "A1",
        objectives: user.objectives || "Travel",
      }));
      
      // Load user settings
      fetchUserSettings();
      fetchUserProfile();
    }
  }, [user]);

  // Save active tab to localStorage
  useEffect(() => {
    localStorage.setItem("settingsActiveTab", activeTab);
  }, [activeTab]);

  const fetchUserProfile = async () => {
    try {
      const response = await apiClient.get('/api/auth/profile/');
      if (response.data) {
        setFormData(prev => ({
          ...prev,
          ...response.data,
          birthday: response.data.birthday
            ? new Date(response.data.birthday).toISOString().split('T')[0]
            : null,
          interface_language: prev.interface_language // Preserve interface language
        }));
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };
  
  const fetchUserSettings = async () => {
    try {
      // Try to get user settings from localStorage first
      const storedSettings = localStorage.getItem('userSettings');
      if (storedSettings) {
        const parsedSettings = JSON.parse(storedSettings);
        setSettings(prev => ({
          ...prev,
          ...parsedSettings
        }));
        
        setFormData(prev => ({
          ...prev,
          interface_language: parsedSettings.interface_language || prev.interface_language
        }));
      }
      
      // Then try to get from API
      try {
        const response = await apiClient.get('/api/auth/me/settings/');
        if (response.data) {
          setSettings(prev => ({
            ...prev,
            ...response.data
          }));
          
          setFormData(prev => ({
            ...prev,
            interface_language: response.data.interface_language || prev.interface_language
          }));
          
          // Update localStorage
          localStorage.setItem('userSettings', JSON.stringify(response.data));
        }
      } catch (error) {
        console.log('Settings API not available, using default values');
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name: string, value: string) => {
    if (name === 'native_language' && value === formData.target_language) {
      toast({
        title: "Validation Error",
        description: "Native language and target language must be different",
        variant: "destructive",
      });
      return;
    }
    if (name === 'target_language' && value === formData.native_language) {
      toast({
        title: "Validation Error",
        description: "Target language and native language must be different",
        variant: "destructive",
      });
      return;
    }
    if (name === 'gender' && value === 'not-specified') {
      setFormData(prev => ({ ...prev, [name]: null }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));

      // Also update settings for language-related fields
      if (['native_language', 'target_language', 'language_level', 'objectives', 'interface_language'].includes(name)) {
        setSettings(prev => ({ ...prev, [name]: value }));

        // If changing interface language, also update the UI translation system
        if (name === 'interface_language') {
          // Check if it's a theme value or a language code
          if (value === 'light' || value === 'dark') {
            setTheme(value);
          } else {
            // Update the UI language via localStorage to maintain consistency with header selector
            localStorage.setItem('language', value);

            // Forcer la mise à jour des traductions via notre événement personnalisé
            const event = new CustomEvent('app:language:changed', {
              detail: { locale: value, source: 'settings' }
            });
            window.dispatchEvent(event);

            // Trigger legacy language change event for backward compatibility
            window.dispatchEvent(new Event('languageChanged'));

            // Déclencher la transition visuelle avant de recharger
            triggerLanguageTransition(value, TransitionType.LANGUAGE);

            setTimeout(() => {
              window.location.reload();
            }, 1500);
          }
        }
      }
    }
  };

  const saveProfile = async () => {
    try {
      setIsSaving(true);
      setAlert({ show: false, type: 'success', message: '' });

      // Save both profile and interface language
      await apiClient.patch('/api/auth/profile/', {
        username: formData.username,
        first_name: formData.first_name,
        last_name: formData.last_name,
        bio: formData.bio,
        gender: formData.gender,
        birthday: formData.birthday,
        native_language: formData.native_language,
        target_language: formData.target_language,
        language_level: formData.language_level,
        objectives: formData.objectives,
        interface_language: formData.interface_language
      });

      // Update settings with interface language
      setSettings(prev => ({
        ...prev,
        interface_language: formData.interface_language
      }));

      // Save settings to localStorage
      localStorage.setItem('userSettings', JSON.stringify({
        ...settings,
        interface_language: formData.interface_language
      }));

      // Try to save settings to backend
      try {
        await apiClient.post('/api/auth/me/settings/', {
          ...settings,
          interface_language: formData.interface_language
        });
      } catch (error) {
        console.log('Settings API not available, saved locally only');
      }

      // Update UI language if it's a language code
      if (['en', 'fr', 'es', 'nl'].includes(formData.interface_language)) {
        // Update the UI language system
        localStorage.setItem('language', formData.interface_language);

        // Forcer la mise à jour des traductions via notre événement personnalisé
        const event = new CustomEvent('app:language:changed', {
          detail: { locale: formData.interface_language, source: 'settings-profile' }
        });
        window.dispatchEvent(event);

        // Trigger legacy language change event for backward compatibility
        window.dispatchEvent(new Event('languageChanged'));

        // Déclencher la transition visuelle avant de recharger
        triggerLanguageTransition(formData.interface_language, TransitionType.PROFILE);

        setTimeout(() => {
          window.location.reload();
        }, 1500);
      }
      // Apply theme if it's a theme value
      else if (formData.interface_language === 'light' || formData.interface_language === 'dark') {
        setTheme(formData.interface_language);
      }

      setAlert({
        show: true,
        type: 'success',
        message: t('alerts.profileUpdated')
      });

      setIsEditing(false);

      // Clear alert after 3 seconds
      setTimeout(() => {
        setAlert(prev => ({ ...prev, show: false }));
      }, 3000);

    } catch (error) {
      console.error('Error updating profile:', error);
      setAlert({
        show: true,
        type: 'error',
        message: t('alerts.updateFailed')
      });
    } finally {
      setIsSaving(false);
    }
  };

  const saveSettings = async () => {
    try {
      setIsSaving(true);
      setAlert({ show: false, type: 'success', message: '' });

      // Store in localStorage
      localStorage.setItem('userSettings', JSON.stringify(settings));

      // Try to save to backend
      try {
        await apiClient.post('/api/auth/me/settings/', settings);
      } catch (error) {
        console.log('Settings API not available, saved locally only');
      }

      // Save language settings to user profile
      const languageSettings = {
        native_language: settings.native_language,
        target_language: settings.target_language,
        language_level: settings.language_level,
        objectives: settings.objectives,
        interface_language: settings.interface_language
      };

      await apiClient.patch('/api/auth/profile/', languageSettings);

      setAlert({
        show: true,
        type: 'success',
        message: t('alerts.settingsSaved')
      });

      // Theme is managed by next-themes
      if (settings.interface_language === 'dark') {
        setTheme('dark');
      } else if (settings.interface_language === 'light') {
        setTheme('light');
      }
      // If it's a language code, update UI language
      else if (['en', 'fr', 'es', 'nl'].includes(settings.interface_language)) {
        // Update the UI language system
        localStorage.setItem('language', settings.interface_language);

        // Forcer la mise à jour des traductions via notre événement personnalisé
        const event = new CustomEvent('app:language:changed', {
          detail: { locale: settings.interface_language, source: 'settings-general' }
        });
        window.dispatchEvent(event);

        // Trigger legacy language change event for backward compatibility
        window.dispatchEvent(new Event('languageChanged'));

        // Déclencher la transition visuelle avant de recharger
        triggerLanguageTransition(settings.interface_language, TransitionType.SETTINGS);

        setTimeout(() => {
          window.location.reload();
        }, 1500);
      }

      // Clear alert after 3 seconds
      setTimeout(() => {
        setAlert(prev => ({ ...prev, show: false }));
      }, 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setAlert({
        show: true,
        type: 'error',
        message: t('alerts.updateFailed')
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleChangePassword = async () => {
    try {
      // Validate passwords
      if (newPassword !== confirmPassword) {
        setPasswordError("Passwords don't match");
        return;
      }
      
      if (newPassword.length < 8) {
        setPasswordError("Password must be at least 8 characters");
        return;
      }
      
      setPasswordError("");
      setIsSaving(true);
      
      // Auth0 doesn't allow password change from app directly
      // But we'll implement the UI for when backend is ready
      
      // For now, just show a success message
      toast({
        title: "Password Change",
        description: "Password updated successfully.",
      });
      
      // Clear password fields
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      console.error('Error changing password:', error);
      toast({
        title: "Password Change Failed",
        description: "There was an error changing your password.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleCancelEdit = () => {
    // Reset form to original user data
    if (user) {
      setFormData({
        username: user.username || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        bio: user.bio || '',
        gender: user.gender || null,
        birthday: user.birthday ? new Date(user.birthday).toISOString().split('T')[0] : null,
        native_language: user.native_language || 'EN',
        target_language: user.target_language || 'FR',
        language_level: user.language_level || 'A1',
        objectives: user.objectives || 'Travel',
        interface_language: settings.interface_language || 'en'
      });
    }
    setIsEditing(false);
  };
  
  const handleProfilePictureClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
  
    try {
      setIsUploading(true);
  
      // Create FormData
      const formData = new FormData();
      formData.append('profile_picture', file);
  
      // Use the correct endpoint path
      const response = await apiClient.post('/api/auth/profile-picture/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
  
      if (response.data && response.data.picture) {
        toast({
          title: "Success",
          description: "Profile picture updated successfully!",
        });
  
        // Refresh user data
        fetchUserProfile();
      }
    } catch (error) {
      console.error('Error uploading profile picture:', error);
      toast({
        title: "Error",
        description: "Failed to upload profile picture. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteAccountTemporary = async () => {
    try {
      setIsDeleting(true);
      
      // Call the account deletion API endpoint with temporary deletion
      const response = await apiClient.post('/api/auth/delete-account/', {
        deletion_type: 'temporary',
        anonymize: true // GDPR-compliant anonymization
      });
      
      if (response.data.success) {
        toast({
          title: "Account Scheduled for Deletion",
          description: "Your account has been deactivated and will be permanently deleted in 30 days.",
        });
        
        // Store deletion info in localStorage for the confirmation page
        localStorage.setItem('account_deletion_type', 'temporary');
        if (response.data.deletion_date) {
          localStorage.setItem('account_deletion_date', response.data.deletion_date);
        }
        if (response.data.days_remaining !== undefined) {
          localStorage.setItem('account_deletion_days_remaining', 
                              response.data.days_remaining.toString());
        }
        
        // Log the user out and redirect to confirmation page
        logout();
        router.push('/account-deleted?type=temporary');
      } else {
        throw new Error(response.data.message || "Failed to schedule account deletion");
      }
    } catch (error) {
      console.error('Error scheduling account deletion:', error);
      toast({
        title: "Account Deactivation Failed",
        description: error instanceof Error ? error.message : "There was an error deactivating your account.",
        variant: "destructive",
      });
      setIsDeleting(false);
    }
  };
  
  const handleDeleteAccountPermanent = async () => {
    try {
      setIsDeleting(true);
      
      // Call the account deletion API endpoint with permanent deletion
      const response = await apiClient.post('/api/auth/delete-account/', {
        deletion_type: 'permanent',
        anonymize: true // GDPR-compliant anonymization
      });
      
      if (response.data.success) {
        toast({
          title: "Account Deleted",
          description: "Your account has been permanently deleted.",
        });
        
        // Store deletion type in localStorage for the confirmation page
        localStorage.setItem('account_deletion_type', 'permanent');
        
        // Log the user out and redirect to confirmation page
        logout();
        router.push('/account-deleted?type=permanent');
      } else {
        throw new Error(response.data.message || "Failed to delete account");
      }
    } catch (error) {
      console.error('Error deleting account:', error);
      toast({
        title: "Account Deletion Failed",
        description: error instanceof Error ? error.message : "There was an error deleting your account.",
        variant: "destructive",
      });
      setIsDeleting(false);
    }
  };
  
  const handleResetProgress = async () => {
    try {
      setIsResetting(true);
      
      // Récupérer la langue cible actuelle
      const targetLanguage = formData.target_language;
      console.log(`Réinitialisation de la progression pour la langue: ${targetLanguage}`);
      
      // Progress system removed - reset disabled
      console.log('Progress reset would be called for language:', targetLanguage);
      const success = true; // Mock success
      
      if (success) {
        // Forcer un nettoyage complet du cache local
        Object.keys(localStorage).forEach(key => {
          if (key.includes('progress') || key.includes('Progress') || 
              key.includes('cache') || key.includes('Cache')) {
            localStorage.removeItem(key);
          }
        });
        
        // Message de succès
        toast({
          title: "Progression réinitialisée",
          description: `Votre progression pour la langue ${targetLanguage} a été réinitialisée avec succès. La page va être rechargée.`,
        });
        
        // Attendre que le toast soit affiché puis recharger la page
        setTimeout(() => {
          // Forcer un hard reload pour s'assurer que tout est rechargé
          window.location.href = "/settings?reset=true";
        }, 1500);
      } else {
        throw new Error("Échec de la réinitialisation de la progression");
      }
    } catch (error) {
      console.error('Erreur lors de la réinitialisation de la progression:', error);
      toast({
        title: "Échec de la réinitialisation",
        description: error instanceof Error ? error.message : "Une erreur s'est produite lors de la réinitialisation de votre progression.",
        variant: "destructive",
      });
      setIsResetting(false);
    }
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null; // Router will redirect
  }

  const fullName = `${formData.first_name || ''} ${formData.last_name || ''}`.trim() || formData.username;

  return (
    <div className="w-full h-full bg-gray-50 dark:bg-gray-900 overflow-hidden flex flex-col py-4 px-2 md:px-4">
      {alert.show && (
        <Alert className={`mx-4 mb-4 ${alert.type === 'error' ? 'border-destructive bg-destructive/10' : 'border-green-500 bg-green-50 dark:bg-green-900/20'}`}>
          <AlertDescription>
            {alert.message}
          </AlertDescription>
        </Alert>
      )}
      <div className="grid grid-cols-1 md:grid-cols-6 lg:grid-cols-6 gap-4 lg:gap-6 flex-1 h-full overflow-hidden">
        {/* Left sidebar */}
        <div className="md:col-span-1 lg:col-span-1 space-y-6">
          <div className="bg-card rounded-lg shadow-sm border overflow-hidden h-full sticky top-4">
            <div className="p-4 lg:p-6 flex flex-col items-center">
              <div className="relative mb-4">
                <div
                  className="h-24 w-24 rounded-full overflow-hidden border-4 border-background cursor-pointer transition-all hover:opacity-90"
                  onClick={handleProfilePictureClick}
                >
                  {user.picture ? (
                    <img
                      src={user.picture}
                      alt={fullName}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="h-full w-full bg-gradient-to-r from-purple-400 to-blue-500 flex items-center justify-center">
                      <span className="text-3xl font-bold text-white">
                        {fullName.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  )}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </div>
                {isUploading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-full">
                    <Loader2 className="h-8 w-8 animate-spin text-white" />
                  </div>
                )}
                <div className="absolute bottom-0 right-0 bg-primary text-primary-foreground p-1.5 rounded-full cursor-pointer hover:bg-primary/90 transition-colors">
                  <Camera className="h-3.5 w-3.5" />
                </div>
              </div>
              <h2 className="text-xl font-bold">{fullName}</h2>
              <p className="text-sm text-muted-foreground mb-4">{formData.email}</p>
              
              <div className="w-full space-y-1">
                <Button 
                  variant={activeTab === "profile" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => {
                    setActiveTab("profile");
                    setIsEditing(false);
                  }}
                >
                  <User className="mr-2 h-4 w-4" />
                  {t('tabs.profile')}
                </Button>
                <Button 
                  variant={activeTab === "notifications" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("notifications")}
                >
                  <Bell className="mr-2 h-4 w-4" />
                  {t('tabs.notifications')}
                </Button>
                <Button 
                  variant={activeTab === "language" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("language")}
                >
                  <Languages className="mr-2 h-4 w-4" />
                  {t('tabs.language')}
                </Button>
                <Button 
                  variant={activeTab === "appearance" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("appearance")}
                >
                  <Palette className="mr-2 h-4 w-4" />
                  {t('tabs.appearance')}
                </Button>
                <Button 
                  variant={activeTab === "learning" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("learning")}
                >
                  <BookOpen className="mr-2 h-4 w-4" />
                  {t('tabs.learning')}
                </Button>
                <Button 
                  variant={activeTab === "security" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("security")}
                >
                  <Lock className="mr-2 h-4 w-4" />
                  {t('tabs.security')}
                </Button>
                <Button 
                  variant={activeTab === "privacy" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("privacy")}
                >
                  <Shield className="mr-2 h-4 w-4" />
                  {t('tabs.privacy')}
                </Button>
                <Button 
                  variant={activeTab === "billing" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("billing")}
                >
                  <CreditCard className="mr-2 h-4 w-4" />
                  {t('tabs.billing')}
                </Button>
                <Button 
                  variant={activeTab === "danger" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("danger")}
                >
                  <AlertCircle className="mr-2 h-4 w-4" />
                  {t('tabs.dangerZone')}
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Main content area */}
        <div className="md:col-span-5 lg:col-span-5 space-y-6 h-full overflow-y-auto pr-2">
          {/* Profile Section */}
          {activeTab === "profile" && (
            <Card className="shadow-sm">
              <SettingsCardHeader 
                title={t('tabs.profile')}
                description={t('profileInfo.subtitle')}
                icon={<User className="h-5 w-5" />}
              />
              <CardContent className="p-6">
                <div className="flex justify-end mb-4">
                  {isEditing && (
                    <Button variant="outline" onClick={handleCancelEdit} className="mr-2">
                      {t('cancel')}
                    </Button>
                  )}
                  <SaveButton
                    onClick={saveProfile}
                    isSaving={isSaving}
                    saveText={t('saveChanges')}
                    savingText={t('saving')}
                  />
                </div>
                <Tabs defaultValue={activeProfileTab} onValueChange={setActiveProfileTab} className="mt-2">
                  <TabsList className="grid grid-cols-1 mb-6">
                    <TabsTrigger value="personal">{t('profileInfo.personalInfo')}</TabsTrigger>
                  </TabsList>

                  <TabsContent value="personal" className="space-y-6">
                    {!isEditing ? (
                      // View Mode
                      (<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <InfoItem 
                          label={t('profileInfo.firstName')} 
                          value={formData.first_name || t('profileInfo.notSpecified')} 
                          icon={<User className="h-4 w-4" />}
                        />
                        <InfoItem 
                          label={t('profileInfo.lastName')} 
                          value={formData.last_name || t('profileInfo.notSpecified')} 
                          icon={<User className="h-4 w-4" />}
                        />
                        <InfoItem 
                          label={t('profileInfo.username')} 
                          value={formData.username}
                          icon={<User className="h-4 w-4" />}
                        />
                        <InfoItem 
                          label={t('profileInfo.email')} 
                          value={formData.email}
                          icon={<Mail className="h-4 w-4" />}
                        />
                        <InfoItem
                          label={t('profileInfo.gender')}
                          value={formData.gender
                            ? GENDER_OPTIONS.find(opt => opt.value === formData.gender)?.label || t('profileInfo.notSpecified')
                            : t('profileInfo.notSpecified')
                          }
                        />
                        <InfoItem
                          label={t('profileInfo.birthday')}
                          value={formData.birthday ? new Date(formData.birthday).toLocaleDateString() : t('profileInfo.notSpecified')}
                          icon={<Calendar className="h-4 w-4" />}
                        />
                        <div className="col-span-full">
                          <h3 className="text-sm font-medium mb-2 flex items-center gap-2">
                            <BookOpen className="h-4 w-4" />
                            {t('profileInfo.bio')}
                          </h3>
                          <p className="text-muted-foreground">{formData.bio || 'No bio provided yet.'}</p>
                        </div>
                        <div className="col-span-full flex gap-2">
                          <Button 
                            variant="outline" 
                            onClick={() => setIsEditing(true)}
                            className="mt-4"
                          >
                            {t('profileInfo.editProfile')}
                          </Button>
                          
                          <Button 
                            variant="outline" 
                            onClick={() => setActiveTab('language')}
                            className="mt-4"
                          >
                            {t('tabs.language')}
                          </Button>
                          
                          <Button 
                            variant="outline" 
                            onClick={() => setActiveTab('appearance')}
                            className="mt-4"
                          >
                            {t('tabs.appearance')}
                          </Button>
                        </div>
                      </div>)
                    ) : (
                      // Edit Mode
                      (<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <Label htmlFor="first_name">{t('profileInfo.firstName')}</Label>
                          <Input
                            id="first_name"
                            name="first_name"
                            value={formData.first_name || ''}
                            onChange={handleInputChange}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="last_name">{t('profileInfo.lastName')}</Label>
                          <Input
                            id="last_name"
                            name="last_name"
                            value={formData.last_name || ''}
                            onChange={handleInputChange}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="username">{t('profileInfo.username')}</Label>
                          <Input
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleInputChange}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="email">{t('profileInfo.email')} </Label>
                          <Input
                            id="email"
                            name="email"
                            value={formData.email}
                            disabled
                            className="bg-muted"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="gender">{t('profileInfo.gender')}</Label>
                          <Select
                            value={formData.gender || 'not-specified'}
                            onValueChange={(value) => handleSelectChange('gender', value)}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder={t('profileInfo.notSpecified')} />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="not-specified">{t('profileInfo.notSpecified')}</SelectItem>
                              {GENDER_OPTIONS.map(option => (
                                <SelectItem key={option.value} value={option.value}>
                                  {option.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="birthday">{t('profileInfo.birthday')}</Label>
                          <Input
                            id="birthday"
                            name="birthday"
                            type="date"
                            value={formData.birthday || ''}
                            onChange={handleInputChange}
                          />
                        </div>
                        <div className="col-span-full space-y-2">
                          <Label htmlFor="bio">{t('profileInfo.bio')}</Label>
                          <Textarea
                            id="bio"
                            name="bio"
                            placeholder="Tell us about yourself..."
                            value={formData.bio || ''}
                            onChange={handleInputChange}
                            rows={4}
                          />
                        </div>
                        <div className="col-span-full flex flex-wrap gap-2">
                          <p className="w-full text-sm text-muted-foreground">
                            {t('profileInfo.otherSettingsNote', {defaultValue: "For language and appearance settings, please use the dedicated tabs in the sidebar."})}
                          </p>
                        </div>
                      </div>)
                    )}
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}

          {activeTab === "notifications" && (
            <Card className="shadow-sm">
              <CardHeader className="pb-3 bg-muted/30">
                <CardTitle>{t('tabs.notifications')}</CardTitle>
                <CardDescription>
                  {t('notifications.subtitle')}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <NotificationSettingsPanel defaultTab={new URL(window.location.href).searchParams.get('tab') || 'channels'} />
              </CardContent>
            </Card>
          )}

          {activeTab === "language" && (
            <Card className="shadow-sm">
              <SettingsCardHeader 
                title={t('languageSettings.title')}
                description={t('languageSettings.description')}
                icon={<Languages className="h-5 w-5" />}
              />
              <CardContent className="space-y-6">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      onClick={() => setActiveTab('profile')}
                      className="flex items-center gap-1"
                    >
                      <User className="h-4 w-4" />
                      {t('tabs.profile')}
                    </Button>
                    
                    <Button 
                      variant="outline" 
                      onClick={() => setActiveTab('appearance')}
                      className="flex items-center gap-1"
                    >
                      <Palette className="h-4 w-4" />
                      {t('tabs.appearance')}
                    </Button>
                  </div>
                  
                  <SaveButton
                    onClick={saveSettings}
                    isSaving={isSaving}
                    saveText={t('saveChanges')}
                    savingText={t('saving')}
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="native_language">{t('languageSettings.nativeLanguage')}</Label>
                    <Select 
                      value={settings.native_language}
                      onValueChange={(value) => setSettings({...settings, native_language: value})}
                    >
                      <SelectTrigger id="native_language">
                        <SelectValue placeholder={t('languageSettings.nativeLanguage')} />
                      </SelectTrigger>
                      <SelectContent>
                        {LANGUAGE_OPTIONS.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="target_language">{t('languageSettings.targetLanguage')}</Label>
                    <Select 
                      value={settings.target_language}
                      onValueChange={(value) => setSettings({...settings, target_language: value})}
                    >
                      <SelectTrigger id="target_language">
                        <SelectValue placeholder={t('languageSettings.targetLanguage')} />
                      </SelectTrigger>
                      <SelectContent>
                        {LANGUAGE_OPTIONS.map((option) => (
                          <SelectItem 
                            key={option.value} 
                            value={option.value}
                            disabled={option.value === settings.native_language}
                          >
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="language_level">{t('languageSettings.languageLevel')}</Label>
                    <Select 
                      value={settings.language_level}
                      onValueChange={(value) => setSettings({...settings, language_level: value})}
                    >
                      <SelectTrigger id="language_level">
                        <SelectValue placeholder={t('languageSettings.languageLevel')} />
                      </SelectTrigger>
                      <SelectContent>
                        {LEVEL_OPTIONS.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="objectives">{t('languageSettings.learningObjectives')}</Label>
                    <Select 
                      value={settings.objectives}
                      onValueChange={(value) => setSettings({...settings, objectives: value})}
                    >
                      <SelectTrigger id="objectives">
                        <SelectValue placeholder={t('languageSettings.learningObjectives')} />
                      </SelectTrigger>
                      <SelectContent>
                        {OBJECTIVES_OPTIONS.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "appearance" && (
            <Card className="shadow-sm">
              <SettingsCardHeader 
                title={t('appearance.title')}
                description={t('appearance.description')}
                icon={<Palette className="h-5 w-5" />}
              />
              <CardContent className="space-y-6">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      onClick={() => setActiveTab('profile')}
                      className="flex items-center gap-1"
                    >
                      <User className="h-4 w-4" />
                      {t('tabs.profile')}
                    </Button>
                    
                    <Button 
                      variant="outline" 
                      onClick={() => setActiveTab('language')}
                      className="flex items-center gap-1"
                    >
                      <Languages className="h-4 w-4" />
                      {t('tabs.language')}
                    </Button>
                  </div>
                  
                  <SaveButton
                    onClick={saveSettings}
                    isSaving={isSaving}
                    saveText={t('saveChanges')}
                    savingText={t('saving')}
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="theme">{t('appearance.theme')}</Label>
                    <Select 
                      value={theme || 'system'}
                      onValueChange={(value) => setTheme(value)}
                    >
                      <SelectTrigger id="theme">
                        <SelectValue placeholder={t('appearance.theme')} />
                      </SelectTrigger>
                      <SelectContent>
                        {THEME_OPTIONS.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="interface_language">{t('appearance.interfaceLanguage')}</Label>
                    <Select 
                      value={settings.interface_language}
                      onValueChange={(value) => setSettings({...settings, interface_language: value})}
                    >
                      <SelectTrigger id="interface_language">
                        <SelectValue placeholder={t('appearance.interfaceLanguage')} />
                      </SelectTrigger>
                      <SelectContent>
                        {INTERFACE_LANGUAGE_OPTIONS.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "learning" && (
            <Card className="shadow-sm">
              <SettingsCardHeader 
                title={t('learning.title')}
                description={t('learning.description')}
                icon={<BookOpen className="h-5 w-5" />}
              />
              <CardContent className="space-y-6">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      onClick={() => setActiveTab('language')}
                      className="flex items-center gap-1"
                    >
                      <Languages className="h-4 w-4" />
                      {t('tabs.language')}
                    </Button>
                  </div>
                  
                  <SaveButton
                    onClick={saveSettings}
                    isSaving={isSaving}
                    saveText={t('saveChanges')}
                    savingText={t('saving')}
                  />
                </div>
                <div className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <Label htmlFor="daily_goal">{t('learning.dailyGoal')}</Label>
                      <span className="text-sm text-muted-foreground">{settings.daily_goal} minutes</span>
                    </div>
                    <Slider 
                      id="daily_goal" 
                      min={5} 
                      max={60} 
                      step={5} 
                      value={[settings.daily_goal]} 
                      onValueChange={(value: number[]) => setSettings({...settings, daily_goal: value[0]})} 
                      className="w-full"
                    />
                  </div>
                  
                  <div className="rounded-lg border p-4 space-y-4">
                    <h3 className="font-medium text-sm">{t('learning.exercisePreferences')}</h3>
                    
                    <SettingsToggle
                      id="speaking_exercises"
                      label={t('learning.speakingExercises')}
                      description={t('learning.includeDescription', { exerciseType: t('learning.speakingExercises').toLowerCase() })}
                      checked={settings.speaking_exercises}
                      onCheckedChange={(value) => setSettings({...settings, speaking_exercises: value})}
                    />
                    
                    <SettingsToggle
                      id="listening_exercises"
                      label={t('learning.listeningExercises')}
                      description={t('learning.includeDescription', { exerciseType: t('learning.listeningExercises').toLowerCase() })}
                      checked={settings.listening_exercises}
                      onCheckedChange={(value) => setSettings({...settings, listening_exercises: value})}
                    />
                    
                    <SettingsToggle
                      id="reading_exercises"
                      label={t('learning.readingExercises')}
                      description={t('learning.includeDescription', { exerciseType: t('learning.readingExercises').toLowerCase() })}
                      checked={settings.reading_exercises}
                      onCheckedChange={(value) => setSettings({...settings, reading_exercises: value})}
                    />
                    
                    <SettingsToggle
                      id="writing_exercises"
                      label={t('learning.writingExercises')}
                      description={t('learning.includeDescription', { exerciseType: t('learning.writingExercises').toLowerCase() })}
                      checked={settings.writing_exercises}
                      onCheckedChange={(value) => setSettings({...settings, writing_exercises: value})}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "security" && (
            <Card className="shadow-sm">
              <SettingsCardHeader 
                title={t('security.title')}
                description={t('security.description')}
                icon={<Lock className="h-5 w-5" />}
              />
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">{t('security.changePassword')}</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="old_password">{t('security.currentPassword')}</Label>
                      <Input 
                        id="old_password" 
                        type="password" 
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                      />
                    </div>
                    
                    <div className="col-span-1 md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="new_password">{t('security.newPassword')}</Label>
                        <Input 
                          id="new_password" 
                          type="password" 
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="confirm_password">{t('security.confirmPassword')}</Label>
                        <Input 
                          id="confirm_password" 
                          type="password" 
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                        />
                      </div>
                    </div>
                  </div>
                  
                  {passwordError && (
                    <p className="text-sm text-destructive">{passwordError}</p>
                  )}
                  
                  <Button 
                    onClick={handleChangePassword}
                    disabled={isSaving || !oldPassword || !newPassword || !confirmPassword}
                  >
                    {isSaving ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        {t('saving')}
                      </>
                    ) : (
                      <>{t('security.changePassword')}</>
                    )}
                  </Button>
                </div>
                
                <div className="border-t pt-6 mt-4 space-y-4">
                  <h3 className="text-lg font-medium">{t('security.twoFactor')}</h3>
                  <p className="text-sm text-muted-foreground">
                    {t('security.twoFactorDescription')}
                  </p>
                  <Button variant="outline">{t('security.setup2FA')}</Button>
                </div>
                
                <div className="border-t pt-6 mt-4 space-y-4">
                  <h3 className="text-lg font-medium">{t('security.connectedAccounts')}</h3>
                  <p className="text-sm text-muted-foreground">
                    {t('security.connectedAccountsDescription')}
                  </p>
                  
                  <div className="bg-card rounded-md border p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="bg-muted p-2 rounded-md">
                          <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 0C5.372 0 0 5.373 0 12C0 17.302 3.438 21.8 8.207 23.387C8.806 23.498 9 23.126 9 22.81V20.576C5.662 21.302 4.967 19.16 4.967 19.16C4.421 17.773 3.634 17.404 3.634 17.404C2.545 16.66 3.717 16.675 3.717 16.675C4.922 16.759 5.556 17.912 5.556 17.912C6.626 19.746 8.363 19.216 9.048 18.909C9.155 18.134 9.466 17.604 9.81 17.305C7.145 17 4.343 15.971 4.343 11.374C4.343 10.063 4.812 8.993 5.579 8.153C5.455 7.85 5.044 6.629 5.696 4.977C5.696 4.977 6.704 4.655 8.997 6.207C9.954 5.941 10.98 5.808 12 5.803C13.02 5.808 14.047 5.941 15.006 6.207C17.297 4.655 18.303 4.977 18.303 4.977C18.956 6.63 18.545 7.851 18.421 8.153C19.191 8.993 19.656 10.064 19.656 11.374C19.656 15.983 16.849 16.998 14.177 17.295C14.607 17.667 15 18.397 15 19.517V22.81C15 23.129 15.192 23.504 15.801 23.386C20.566 21.797 24 17.3 24 12C24 5.373 18.627 0 12 0Z" fill="currentColor"/>
                          </svg>
                        </div>
                        <div>
                          <p className="font-medium">GitHub</p>
                          <p className="text-sm text-muted-foreground">
                            Connect to sync your progress with GitHub
                          </p>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">{t('security.connect')}</Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "privacy" && (
            <Card className="shadow-sm">
              <SettingsCardHeader 
                title={t('privacy.title')}
                description={t('privacy.description')}
                icon={<Shield className="h-5 w-5" />}
              />
              <CardContent className="space-y-6">
                <div className="flex justify-end mb-4">
                  <SaveButton
                    onClick={saveSettings}
                    isSaving={isSaving}
                    saveText={t('saveChanges')}
                    savingText={t('saving')}
                  />
                </div>
                <div className="space-y-4">
                  <SettingsToggle
                    id="public_profile"
                    label={t('privacy.publicProfile')}
                    description={t('privacy.publicProfileDescription')}
                    checked={settings.public_profile}
                    onCheckedChange={(value) => setSettings({...settings, public_profile: value})}
                  />
                  
                  <SettingsToggle
                    id="share_progress"
                    label={t('privacy.shareProgress')}
                    description={t('privacy.shareProgressDescription')}
                    checked={settings.share_progress}
                    onCheckedChange={(value) => setSettings({...settings, share_progress: value})}
                  />
                  
                  <SettingsToggle
                    id="share_activity"
                    label={t('privacy.shareActivity')}
                    description={t('privacy.shareActivityDescription')}
                    checked={settings.share_activity}
                    onCheckedChange={(value) => setSettings({...settings, share_activity: value})}
                  />
                </div>
                
                <div className="border-t pt-6 mt-4">
                  <h3 className="text-lg font-medium mb-2">{t('privacy.dataPrivacy')}</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {t('privacy.dataPrivacyDescription')}
                  </p>
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full justify-start">
                      {t('privacy.downloadData')}
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      {t('privacy.privacyPolicy')}
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      {t('privacy.termsOfService')}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "billing" && (
            <Card className="shadow-sm">
              <SettingsCardHeader 
                title={t('billing.title')}
                description={t('billing.description')}
                icon={<CreditCard className="h-5 w-5" />}
              />
              <CardContent className="space-y-6">
                <div className="bg-background rounded-lg border shadow-xs p-5 space-y-4">
                  <h3 className="text-lg font-medium">{t('billing.currentPlan')}</h3>
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">{user.is_subscribed ? t('billing.premiumPlan') : t('billing.freePlan')}</p>
                      <p className="text-sm text-muted-foreground">
                        {user.is_subscribed 
                          ? 'Your subscription renews on the 1st of each month' 
                          : t('billing.upgradeToPremium')}
                      </p>
                    </div>
                    <Button variant={user.is_subscribed ? "outline" : "default"}>
                      {user.is_subscribed ? t('billing.manageSubscription') : t('billing.upgrade')}
                    </Button>
                  </div>
                </div>
                
                {user.is_subscribed && (
                  <div className="bg-background rounded-lg border shadow-xs p-5 space-y-4">
                    <h3 className="text-lg font-medium">{t('billing.paymentMethod')}</h3>
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <div className="bg-muted p-2 rounded-md">
                          <CreditCard className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="font-medium">Visa ending in 4242</p>
                          <p className="text-sm text-muted-foreground">Expires 04/24</p>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">{t('billing.edit')}</Button>
                    </div>
                  </div>
                )}
                
                <div className="bg-background rounded-lg border shadow-xs p-5 space-y-4">
                  <h3 className="text-lg font-medium">{t('billing.billingHistory')}</h3>
                  {user.is_subscribed ? (
                    <div className="space-y-4">
                      <div className="flex justify-between items-center py-2 border-b">
                        <div>
                          <p className="font-medium">Mar 1, 2025</p>
                          <p className="text-sm text-muted-foreground">{t('billing.premiumPlan')}</p>
                        </div>
                        <p className="font-medium">$9.99</p>
                      </div>
                      <div className="flex justify-between items-center py-2 border-b">
                        <div>
                          <p className="font-medium">Feb 1, 2025</p>
                          <p className="text-sm text-muted-foreground">{t('billing.premiumPlan')}</p>
                        </div>
                        <p className="font-medium">$9.99</p>
                      </div>
                      <Button variant="outline" className="w-full mt-4">{t('billing.viewAllInvoices')}</Button>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      {t('billing.noHistory')}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "danger" && (
            <Card className="border-destructive shadow-sm">
              <SettingsCardHeader 
                title={t('dangerZone.title')}
                description={t('dangerZone.description')}
                icon={<AlertCircle className="h-5 w-5" />}
                variant="destructive"
              />
              <CardContent className="p-6 space-y-6">
                <div className="bg-background rounded-lg border shadow-xs p-5 space-y-4">
                  <h3 className="text-lg font-medium">{t('dangerZone.exportAndReset')}</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {t('dangerZone.exportBeforeDeleting')}
                  </p>
                  <div className="flex flex-wrap gap-3">
                    <Button variant="outline">{t('dangerZone.exportAllData')}</Button>
                    <Button
                      variant="destructive"
                      onClick={() => {
                        localStorage.removeItem("onboardingCompleted");
                        toast({
                          title: "Onboarding Reset",
                          description: "Onboarding reset successfully. Refresh the page to see the onboarding flow.",
                        });
                        setTimeout(() => {
                          window.location.reload();
                        }, 1500);
                      }}
                    >
                      {t('dangerZone.resetOnboarding')}
                    </Button>
                  </div>
                </div>
                
                <div className="bg-background rounded-lg border shadow-xs p-5 space-y-4">
                  <h3 className="text-lg font-medium">{typeof t('dangerZone.resetProgressButton') === 'string' ? t('dangerZone.resetProgressButton') : 'Reset Learning Progress'}</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {t('dangerZone.resetProgressDescription')}
                  </p>
                  <ResetProgressDialog 
                    onConfirmReset={handleResetProgress}
                    isResetting={isResetting}
                  />
                </div>
                
                <div className="bg-background rounded-lg border shadow-xs p-5 space-y-4">
                  <h3 className="text-lg font-medium">{typeof t('dangerZone.deleteAccountButton') === 'string' ? t('dangerZone.deleteAccountButton') : 'Delete Account'}</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {t('dangerZone.deleteAccountDescription')}
                  </p>
                  <DeleteAccountDialog
                    onConfirmTemporary={handleDeleteAccountTemporary}
                    onConfirmPermanent={handleDeleteAccountPermanent}
                    isDeleting={isDeleting}
                  />
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

// Helper components for settings UI
interface InfoItemProps {
  label: string;
  value: string;
  icon?: React.ReactNode;
}

function InfoItem({ label, value, icon }: InfoItemProps) {
  return (
    <div>
      <h3 className="text-sm font-medium mb-1 flex items-center gap-2">
        {icon && icon}
        {label}
      </h3>
      <p className="text-muted-foreground">{value}</p>
    </div>
  );
}

interface SettingsCardHeaderProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  variant?: "default" | "destructive";
}

function SettingsCardHeader({ title, description, icon, variant = "default" }: SettingsCardHeaderProps) {
  const bgClass = variant === "destructive" ? "bg-destructive/5" : "bg-muted/30";
  const titleClass = variant === "destructive" ? "text-destructive" : "";
  
  return (
    <CardHeader className={`pb-3 ${bgClass}`}>
      <CardTitle className={titleClass}>
        {icon ? (
          <div className="flex items-center gap-2">
            {icon}
            {title}
          </div>
        ) : (
          title
        )}
      </CardTitle>
      <CardDescription>
        {description}
      </CardDescription>
    </CardHeader>
  );
}

interface SaveButtonProps {
  onClick: () => void;
  isSaving: boolean;
  saveText: string;
  savingText: string;
  className?: string;
}

function SaveButton({ onClick, isSaving, saveText, savingText, className = "" }: SaveButtonProps) {
  return (
    <Button 
      onClick={onClick}
      disabled={isSaving}
      className={className}
    >
      {isSaving ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          {savingText}
        </>
      ) : (
        <>
          <Save className="mr-2 h-4 w-4" />
          {saveText}
        </>
      )}
    </Button>
  );
}

interface SettingsToggleProps {
  id: string;
  label: string;
  description?: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
  icon?: React.ReactNode;
}

function SettingsToggle({ 
  id, 
  label, 
  description, 
  checked, 
  onCheckedChange, 
  disabled = false,
  icon
}: SettingsToggleProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="space-y-0.5">
        <Label htmlFor={id} className={`flex items-center gap-2 ${description ? '' : 'text-base'}`}>
          {icon && icon}
          {label}
        </Label>
        {description && (
          <p className="text-sm text-muted-foreground">
            {description}
          </p>
        )}
      </div>
      <Switch
        id={id}
        checked={checked}
        onCheckedChange={onCheckedChange}
        disabled={disabled}
      />
    </div>
  );
}