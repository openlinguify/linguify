'use client';

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
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
import { useAuthContext } from "@/core/auth/AuthAdapter";
import { useLanguageSync } from "@/core/i18n/useLanguageSync";
import { useTranslation } from "@/core/i18n/useTranslations";
import { triggerLanguageTransition, TransitionType } from "@/core/i18n/LanguageTransition";
import { Alert, AlertDescription } from "@/components/ui/alert";
import apiClient from '@/core/api/apiClient';

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

// Helper function to safely convert user properties to strings
const safeString = (value: unknown): string => {
  if (typeof value === 'string') return value;
  if (value === null || value === undefined) return '';
  if (typeof value === 'object' && Object.keys(value).length === 0) return '';
  return String(value);
};

export default function SettingsPage() {
  const { user, isAuthenticated, isLoading, logout, refreshUser } = useAuthContext();
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const { t } = useTranslation();

  useLanguageSync();
  const [activeTab, setActiveTab] = useState(() => {
    return localStorage.getItem('settingsActiveTab') || 'profile';
  });
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [profilePictureKey, setProfilePictureKey] = useState(Date.now());
  const [currentProfilePicture, setCurrentProfilePicture] = useState<string | null>(null);
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
        username: safeString(user.username),
        first_name: safeString(user.first_name),
        last_name: safeString(user.last_name),
        email: safeString(user.email),
        bio: safeString(user.bio),
        gender: safeString(user.gender) || null,
        birthday: user.birthday && typeof user.birthday === 'string' ? new Date(user.birthday).toISOString().split('T')[0] : null,
        native_language: safeString(user.native_language) || 'EN',
        target_language: safeString(user.target_language) || 'FR',
        language_level: safeString(user.language_level) || 'A1',
        objectives: safeString(user.objectives) || 'Travel',
        interface_language: 'en'
      });
      
      // Initialize current profile picture
      setCurrentProfilePicture(user.picture || null);
      
      setSettings(prev => ({
        ...prev,
        native_language: safeString(user.native_language) || "EN",
        target_language: safeString(user.target_language) || "FR",
        language_level: safeString(user.language_level) || "A1",
        objectives: safeString(user.objectives) || "Travel",
      }));
      
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
          interface_language: prev.interface_language
        }));
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };
  
  const fetchUserSettings = async () => {
    try {
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
          
          localStorage.setItem('userSettings', JSON.stringify(response.data));
        }
      } catch {
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

      if (['native_language', 'target_language', 'language_level', 'objectives', 'interface_language'].includes(name)) {
        setSettings(prev => ({ ...prev, [name]: value }));

        if (name === 'interface_language') {
          if (value === 'light' || value === 'dark') {
            setTheme(value);
          } else {
            localStorage.setItem('language', value);

            const event = new CustomEvent('app:language:changed', {
              detail: { locale: value, source: 'settings' }
            });
            window.dispatchEvent(event);

            window.dispatchEvent(new Event('languageChanged'));

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

      setAlert({
        show: true,
        type: 'success',
        message: t('alerts.profileUpdated')
      });

      setIsEditing(false);

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
  
      const formData = new FormData();
      formData.append('profile_picture', file);
  
      const response = await apiClient.post('/api/auth/profile-picture/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Profile picture upload response:', response.data);
  
      if (response.data) {
        toast({
          title: "Success",
          description: "Profile picture updated successfully!",
        });
  
        // Fetch complete profile to update the UI
        console.log('Before fetchUserProfile - Current user picture:', user?.picture);
        await fetchUserProfile();
        console.log('After fetchUserProfile - Form data profile_picture:', formData.profile_picture);
        
        // Update the local formData and currentProfilePicture with the new picture URL
        if (response.data.picture) {
          setCurrentProfilePicture(response.data.picture);
          setFormData(prev => ({
            ...prev,
            profile_picture: response.data.picture
          }));
        }
        
        // Refresh the auth context to update user picture globally
        if (refreshUser) {
          console.log('Calling refreshUser...');
          await refreshUser();
          console.log('After refreshUser - Current user picture:', user?.picture);
          
          // Small delay to ensure state updates propagate
          setTimeout(() => {
            console.log('After delay - Current user picture:', user?.picture);
            // Force image refresh by updating the key
            setProfilePictureKey(Date.now());
          }, 100);
        } else {
          console.log('refreshUser is not available');
          // Force image refresh by updating the key
          setProfilePictureKey(Date.now());
        }
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

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  const fullName = `${formData.first_name || ''} ${formData.last_name || ''}`.trim() || formData.username;

  return (
    <div className="w-full h-full bg-gray-50 dark:bg-gray-900 overflow-hidden flex flex-col">
      {alert.show && (
        <Alert className={alert.type === 'error' ? 'mx-auto max-w-7xl w-full px-4 mb-4 border-destructive bg-destructive/10' : 'mx-auto max-w-7xl w-full px-4 mb-4 border-green-500 bg-green-50 dark:bg-green-900/20'}>
          <AlertDescription>
            {alert.message}
          </AlertDescription>
        </Alert>
      )}
      <div className="max-w-7xl w-full mx-auto px-4 py-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 lg:gap-8">
          {/* Left sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-card rounded-lg shadow-sm border overflow-hidden sticky top-6">
              <div className="p-4 lg:p-6 flex flex-col items-center">
                <div className="relative mb-4">
                  <div
                    className="h-24 w-24 rounded-full overflow-hidden border-4 border-background cursor-pointer transition-all hover:opacity-90"
                    onClick={handleProfilePictureClick}
                  >
                    {(currentProfilePicture || formData.profile_picture || user.picture) && typeof (currentProfilePicture || formData.profile_picture || user.picture) === 'string' ? (
                      <img
                        src={`${currentProfilePicture || formData.profile_picture || user.picture}${(currentProfilePicture || formData.profile_picture || user.picture).includes('?') ? '&' : '?'}t=${profilePictureKey}`}
                        alt={fullName}
                        className="h-full w-full object-cover"
                        key={`${currentProfilePicture || formData.profile_picture || user.picture}-${profilePictureKey}`} // Force re-render when URL or key changes
                        onError={() => {
                          console.log('Image failed to load, falling back to default');
                          // Don't clear currentProfilePicture to avoid infinite loop
                        }}
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
                    variant={activeTab === "notifications" ? "default" : "ghost"} 
                    className="w-full justify-start" 
                    onClick={() => setActiveTab("notifications")}
                  >
                    <Bell className="mr-2 h-4 w-4" />
                    {t('tabs.notifications')}
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
                    {t('tabs.danger')}
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Main content area */}
          <div className="lg:col-span-3 space-y-6">
            {/* Profile Section */}
            {activeTab === "profile" && (
              <Card className="shadow-sm">
                <CardHeader className="pb-3 bg-muted/30">
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    {t('tabs.profile')}
                  </CardTitle>
                  <CardDescription>
                    {t('profileInfo.subtitle')}
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="flex justify-end mb-4">
                    {isEditing && (
                      <Button variant="outline" onClick={() => setIsEditing(false)} className="mr-2">
                        {t('cancel')}
                      </Button>
                    )}
                    <Button
                      onClick={isEditing ? saveProfile : () => setIsEditing(true)}
                      disabled={isSaving}
                    >
                      {isSaving ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          {t('saving')}
                        </>
                      ) : (
                        <>
                          <Save className="mr-2 h-4 w-4" />
                          {isEditing ? t('saveChanges') : t('profileInfo.editProfile')}
                        </>
                      )}
                    </Button>
                  </div>
                  
                  {!isEditing ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      <div>
                        <h3 className="text-sm font-medium mb-1 flex items-center gap-2">
                          <User className="h-4 w-4" />
                          {t('profileInfo.firstName')}
                        </h3>
                        <p className="text-muted-foreground">{formData.first_name || t('profileInfo.notSpecified')}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium mb-1 flex items-center gap-2">
                          <User className="h-4 w-4" />
                          {t('profileInfo.lastName')}
                        </h3>
                        <p className="text-muted-foreground">{formData.last_name || t('profileInfo.notSpecified')}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium mb-1 flex items-center gap-2">
                          <User className="h-4 w-4" />
                          {t('profileInfo.username')}
                        </h3>
                        <p className="text-muted-foreground">{formData.username}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium mb-1 flex items-center gap-2">
                          <Mail className="h-4 w-4" />
                          {t('profileInfo.email')}
                        </h3>
                        <p className="text-muted-foreground">{formData.email}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium mb-1">
                          {t('profileInfo.gender')}
                        </h3>
                        <p className="text-muted-foreground">
                          {formData.gender
                            ? GENDER_OPTIONS.find(opt => opt.value === formData.gender)?.label || t('profileInfo.notSpecified')
                            : t('profileInfo.notSpecified')
                          }
                        </p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium mb-1 flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          {t('profileInfo.birthday')}
                        </h3>
                        <p className="text-muted-foreground">
                          {formData.birthday ? new Date(formData.birthday).toLocaleDateString() : t('profileInfo.notSpecified')}
                        </p>
                      </div>
                      <div className="col-span-full">
                        <h3 className="text-sm font-medium mb-2 flex items-center gap-2">
                          <BookOpen className="h-4 w-4" />
                          {t('profileInfo.bio')}
                        </h3>
                        <p className="text-muted-foreground">{formData.bio || 'No bio provided yet.'}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                        <Label htmlFor="email">{t('profileInfo.email')}</Label>
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
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {activeTab === "language" && (
              <Card className="shadow-sm">
                <CardHeader className="pb-3 bg-muted/30">
                  <CardTitle className="flex items-center gap-2">
                    <Languages className="h-5 w-5" />
                    {t('languageSettings.title')}
                  </CardTitle>
                  <CardDescription>
                    {t('languageSettings.description')}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
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
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === "appearance" && (
              <Card className="shadow-sm">
                <CardHeader className="pb-3 bg-muted/30">
                  <CardTitle className="flex items-center gap-2">
                    <Palette className="h-5 w-5" />
                    {t('appearance.title')}
                  </CardTitle>
                  <CardDescription>
                    {t('appearance.description')}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
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
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === "notifications" && (
              <Card className="shadow-sm">
                <CardHeader className="pb-3 bg-muted/30">
                  <CardTitle className="flex items-center gap-2">
                    <Bell className="h-5 w-5" />
                    Notifications
                  </CardTitle>
                  <CardDescription>
                    Manage your notification preferences
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Email notifications</Label>
                        <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                      </div>
                      <Switch />
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Push notifications</Label>
                        <p className="text-sm text-muted-foreground">Receive browser notifications</p>
                      </div>
                      <Switch />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === "learning" && (
              <Card className="shadow-sm">
                <CardHeader className="pb-3 bg-muted/30">
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5" />
                    Learning
                  </CardTitle>
                  <CardDescription>
                    Customize your learning experience
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="language_level">Current Level</Label>
                      <Select 
                        value={settings.language_level}
                        onValueChange={(value) => setSettings({...settings, language_level: value})}
                      >
                        <SelectTrigger id="language_level">
                          <SelectValue placeholder="Select your level" />
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
                      <Label htmlFor="objectives">Learning Objectives</Label>
                      <Select 
                        value={settings.objectives}
                        onValueChange={(value) => setSettings({...settings, objectives: value})}
                      >
                        <SelectTrigger id="objectives">
                          <SelectValue placeholder="Select your goal" />
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

            {activeTab === "security" && (
              <Card className="shadow-sm">
                <CardHeader className="pb-3 bg-muted/30">
                  <CardTitle className="flex items-center gap-2">
                    <Lock className="h-5 w-5" />
                    Security
                  </CardTitle>
                  <CardDescription>
                    Manage your account security settings
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="oldPassword">Current Password</Label>
                      <Input
                        id="oldPassword"
                        type="password"
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                        placeholder="Enter current password"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="newPassword">New Password</Label>
                      <Input
                        id="newPassword"
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="Enter new password"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword">Confirm New Password</Label>
                      <Input
                        id="confirmPassword"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm new password"
                      />
                    </div>
                    {passwordError && (
                      <Alert className="border-destructive bg-destructive/10">
                        <AlertDescription>{passwordError}</AlertDescription>
                      </Alert>
                    )}
                    <Button className="w-full" disabled={!oldPassword || !newPassword || !confirmPassword}>
                      Change Password
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === "privacy" && (
              <Card className="shadow-sm">
                <CardHeader className="pb-3 bg-muted/30">
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Privacy
                  </CardTitle>
                  <CardDescription>
                    Control your privacy settings
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Public profile</Label>
                        <p className="text-sm text-muted-foreground">Make your profile visible to other users</p>
                      </div>
                      <Switch />
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Analytics</Label>
                        <p className="text-sm text-muted-foreground">Help us improve by sharing usage data</p>
                      </div>
                      <Switch />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === "billing" && (
              <Card className="shadow-sm">
                <CardHeader className="pb-3 bg-muted/30">
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="h-5 w-5" />
                    Billing
                  </CardTitle>
                  <CardDescription>
                    Manage your subscription and billing
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="text-center py-8">
                    <CreditCard className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="text-lg font-medium mb-2">Free Plan</h3>
                    <p className="text-muted-foreground mb-4">You're currently on the free plan</p>
                    <Button>Upgrade to Pro</Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === "danger" && (
              <Card className="shadow-sm border-destructive">
                <CardHeader className="pb-3 bg-destructive/5">
                  <CardTitle className="flex items-center gap-2 text-destructive">
                    <AlertCircle className="h-5 w-5" />
                    Danger Zone
                  </CardTitle>
                  <CardDescription>
                    Irreversible actions that affect your account
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="p-4 border border-destructive/20 rounded-lg">
                      <h3 className="font-medium text-destructive mb-2">Delete Account</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Permanently delete your account and all associated data. This action cannot be undone.
                      </p>
                      <Button 
                        variant="destructive" 
                        disabled={isDeleting}
                        onClick={() => setIsDeleting(true)}
                      >
                        {isDeleting ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Deleting...
                          </>
                        ) : (
                          'Delete Account'
                        )}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}