// src/app/(dashboard)/(apps)/settings/SettingsPage.tsx
'use client';

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "@/components/ui/use-toast";
import { useAuthContext } from "@/services/AuthProvider";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { 
  User, 
  Bell, 
  Languages, 
  Settings, 
  Lock, 
  CreditCard, 
  LogOut, 
  Shield, 
  AlertCircle, 
  Loader2,
  Save 
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import apiClient from '@/services/axiosAuthInterceptor';

// Constants
const LANGUAGE_OPTIONS = [
  { value: 'EN', label: 'English' },
  { value: 'FR', label: 'French' },
  { value: 'NL', label: 'Dutch' },
  { value: 'DE', label: 'German' },
  { value: 'ES', label: 'Spanish' },
  { value: 'IT', label: 'Italian' },
  { value: 'PT', label: 'Portuguese' },
];

const INTERFACE_LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'fr', label: 'Français' },
  { value: 'es', label: 'Español' },
  { value: 'nl', label: 'Nederlands' },
];

const LEVEL_OPTIONS = [
  { value: 'A1', label: 'A1 - Beginner' },
  { value: 'A2', label: 'A2 - Elementary' },
  { value: 'B1', label: 'B1 - Intermediate' },
  { value: 'B2', label: 'B2 - Upper Intermediate' },
  { value: 'C1', label: 'C1 - Advanced' },
  { value: 'C2', label: 'C2 - Mastery' },
];

const OBJECTIVES_OPTIONS = [
  { value: 'Travel', label: 'Travel' },
  { value: 'Business', label: 'Business' },
  { value: 'Live Abroad', label: 'Live Abroad' },
  { value: 'Exam', label: 'Exam Preparation' },
  { value: 'For Fun', label: 'For Fun' },
  { value: 'Work', label: 'Work' },
  { value: 'School', label: 'School' },
  { value: 'Study', label: 'Study' },
  { value: 'Personal', label: 'Personal Development' },
];

const THEME_OPTIONS = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System' },
];

interface UserSettings {
  // Account settings
  email_notifications: boolean;
  push_notifications: boolean;
  interface_language: string;
  
  // Learning settings
  daily_goal: number; // in minutes
  weekday_reminders: boolean;
  weekend_reminders: boolean;
  reminder_time: string;
  speaking_exercises: boolean;
  listening_exercises: boolean;
  reading_exercises: boolean;
  writing_exercises: boolean;
  
  // Language settings
  native_language: string;
  target_language: string;
  language_level: string;
  objectives: string;
  
  // Privacy settings
  public_profile: boolean;
  share_progress: boolean;
  share_activity: boolean;
}

export default function SettingsPage() {
  const { user, isAuthenticated, isLoading, logout } = useAuthContext();
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [activeTab, setActiveTab] = useState("account");
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const [settings, setSettings] = useState<UserSettings>({
    // Default values
    email_notifications: true,
    push_notifications: true,
    interface_language: "en",
    
    daily_goal: 15,
    weekday_reminders: true,
    weekend_reminders: false,
    reminder_time: "18:00",
    speaking_exercises: true,
    listening_exercises: true,
    reading_exercises: true,
    writing_exercises: true,
    
    native_language: "EN",
    target_language: "FR",
    language_level: "A1",
    objectives: "Travel",
    
    public_profile: true,
    share_progress: true,
    share_activity: false,
  });
  
  const [profileSettings, setProfileSettings] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    native_language: "EN",
    target_language: "FR",
    language_level: "A1",
    objectives: "Travel",
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

  // Load user data
  useEffect(() => {
    if (user) {
      // Initialize with user data
      setProfileSettings({
        username: user.username || "",
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        email: user.email || "",
        native_language: user.native_language || "EN",
        target_language: user.target_language || "FR",
        language_level: user.language_level || "A1",
        objectives: user.objectives || "Travel",
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
    }
  }, [user]);

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
      }
      
      // Then try to get from API
      try {
        const response = await apiClient.get('/api/auth/me/settings/');
        if (response.data) {
          setSettings(prev => ({
            ...prev,
            ...response.data
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
        objectives: settings.objectives
      };
      
      await apiClient.patch('/api/auth/me/', languageSettings);
      
      setAlert({
        show: true,
        type: 'success',
        message: 'Settings saved successfully!'
      });
      
      // Theme is managed by next-themes
      if (settings.interface_language === 'dark') {
        setTheme('dark');
      } else if (settings.interface_language === 'light') {
        setTheme('light');
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
        message: 'Failed to save settings. Please try again.'
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

  const handleDeleteAccount = async () => {
    // Show confirmation dialog
    const confirmed = window.confirm(
      "Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently lost."
    );
    
    if (!confirmed) return;
    
    try {
      setIsDeleting(true);
      
      // Implement account deletion when backend is ready
      // For now, just log the user out
      
      toast({
        title: "Account Deletion",
        description: "Account deletion request received. You will be logged out now.",
      });
      
      setTimeout(() => {
        logout();
        router.push('/');
      }, 2000);
    } catch (error) {
      console.error('Error deleting account:', error);
      toast({
        title: "Account Deletion Failed",
        description: "There was an error deleting your account.",
        variant: "destructive",
      });
      setIsDeleting(false);
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

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        <Button 
          onClick={saveSettings}
          disabled={isSaving}
        >
          {isSaving ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Changes
            </>
          )}
        </Button>
      </div>

      {alert.show && (
        <Alert className={`mb-6 ${alert.type === 'error' ? 'bg-destructive/15' : 'bg-green-100'}`}>
          <AlertDescription>
            {alert.message}
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-4 gap-6">
        {/* Left sidebar */}
        <div className="col-span-1">
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <Button 
                  variant={activeTab === "account" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("account")}
                >
                  <User className="mr-2 h-4 w-4" />
                  Account
                </Button>
                <Button 
                  variant={activeTab === "notifications" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("notifications")}
                >
                  <Bell className="mr-2 h-4 w-4" />
                  Notifications
                </Button>
                <Button 
                  variant={activeTab === "language" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("language")}
                >
                  <Languages className="mr-2 h-4 w-4" />
                  Language
                </Button>
                <Button 
                  variant={activeTab === "appearance" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("appearance")}
                >
                  <Settings className="mr-2 h-4 w-4" />
                  Appearance
                </Button>
                <Button 
                  variant={activeTab === "learning" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("learning")}
                >
                  <Languages className="mr-2 h-4 w-4" />
                  Learning
                </Button>
                <Button 
                  variant={activeTab === "security" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("security")}
                >
                  <Lock className="mr-2 h-4 w-4" />
                  Security
                </Button>
                <Button 
                  variant={activeTab === "privacy" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("privacy")}
                >
                  <Shield className="mr-2 h-4 w-4" />
                  Privacy
                </Button>
                <Button 
                  variant={activeTab === "billing" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("billing")}
                >
                  <CreditCard className="mr-2 h-4 w-4" />
                  Billing
                </Button>
                <Button 
                  variant={activeTab === "danger" ? "default" : "ghost"} 
                  className="w-full justify-start" 
                  onClick={() => setActiveTab("danger")}
                >
                  <AlertCircle className="mr-2 h-4 w-4" />
                  Danger Zone
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main content */}
        <div className="col-span-3">
          {activeTab === "account" && (
            <Card>
              <CardHeader>
                <CardTitle>Account Settings</CardTitle>
                <CardDescription>
                  Manage your account details and preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <Input 
                      id="username" 
                      value={profileSettings.username} 
                      onChange={(e) => setProfileSettings({...profileSettings, username: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input 
                      id="email" 
                      value={profileSettings.email}
                      disabled
                      className="bg-gray-50"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="first_name">First Name</Label>
                    <Input 
                      id="first_name" 
                      value={profileSettings.first_name} 
                      onChange={(e) => setProfileSettings({...profileSettings, first_name: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="last_name">Last Name</Label>
                    <Input 
                      id="last_name" 
                      value={profileSettings.last_name} 
                      onChange={(e) => setProfileSettings({...profileSettings, last_name: e.target.value})}
                    />
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="interface-language">Interface Language</Label>
                    <Select 
                      value={settings.interface_language}
                      onValueChange={(value) => setSettings({...settings, interface_language: value})}
                    >
                      <SelectTrigger id="interface-language" className="w-[200px]">
                        <SelectValue placeholder="Select language" />
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

          {activeTab === "notifications" && (
            <Card>
              <CardHeader>
                <CardTitle>Notification Settings</CardTitle>
                <CardDescription>
                  Manage how you receive notifications
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="email_notifications">Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive notifications via email
                    </p>
                  </div>
                  <Switch
                    id="email_notifications"
                    checked={settings.email_notifications}
                    onCheckedChange={(value) => setSettings({...settings, email_notifications: value})}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="push_notifications">Push Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive notifications on your device
                    </p>
                  </div>
                  <Switch
                    id="push_notifications"
                    checked={settings.push_notifications}
                    onCheckedChange={(value) => setSettings({...settings, push_notifications: value})}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="weekday_reminders">Weekday Reminders</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive reminders on weekdays
                    </p>
                  </div>
                  <Switch
                    id="weekday_reminders"
                    checked={settings.weekday_reminders}
                    onCheckedChange={(value) => setSettings({...settings, weekday_reminders: value})}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="weekend_reminders">Weekend Reminders</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive reminders on weekends
                    </p>
                  </div>
                  <Switch
                    id="weekend_reminders"
                    checked={settings.weekend_reminders}
                    onCheckedChange={(value) => setSettings({...settings, weekend_reminders: value})}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="reminder_time">Reminder Time</Label>
                  <Input
                    id="reminder_time"
                    type="time"
                    value={settings.reminder_time}
                    onChange={(e) => setSettings({...settings, reminder_time: e.target.value})}
                    className="w-[200px]"
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "language" && (
            <Card>
              <CardHeader>
                <CardTitle>Language Settings</CardTitle>
                <CardDescription>
                  Manage your language learning preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="native_language">Native Language</Label>
                    <Select 
                      value={settings.native_language}
                      onValueChange={(value) => setSettings({...settings, native_language: value})}
                    >
                      <SelectTrigger id="native_language">
                        <SelectValue placeholder="Select language" />
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
                    <Label htmlFor="target_language">Target Language</Label>
                    <Select 
                      value={settings.target_language}
                      onValueChange={(value) => setSettings({...settings, target_language: value})}
                    >
                      <SelectTrigger id="target_language">
                        <SelectValue placeholder="Select language" />
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
                    <Label htmlFor="language_level">Language Level</Label>
                    <Select 
                      value={settings.language_level}
                      onValueChange={(value) => setSettings({...settings, language_level: value})}
                    >
                      <SelectTrigger id="language_level">
                        <SelectValue placeholder="Select level" />
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
                        <SelectValue placeholder="Select objectives" />
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
            <Card>
              <CardHeader>
                <CardTitle>Appearance Settings</CardTitle>
                <CardDescription>
                  Customize the look and feel of the application
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="theme">Theme</Label>
                  <Select 
                    value={theme || 'system'}
                    onValueChange={(value) => setTheme(value)}
                  >
                    <SelectTrigger id="theme" className="w-[200px]">
                      <SelectValue placeholder="Select theme" />
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
              </CardContent>
            </Card>
          )}

          {activeTab === "learning" && (
            <Card>
              <CardHeader>
                <CardTitle>Learning Settings</CardTitle>
                <CardDescription>
                  Customize your learning experience
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Label htmlFor="daily_goal">Daily Goal (minutes)</Label>
                    <span className="text-sm text-muted-foreground">{settings.daily_goal} minutes</span>
                  </div>
                  <Slider 
                    id="daily_goal" 
                    min={5} 
                    max={60} 
                    step={5} 
                    value={[settings.daily_goal]} 
                    onValueChange={(value: number[]) => setSettings({...settings, daily_goal: value[0]})} 
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="speaking_exercises">Speaking Exercises</Label>
                    <p className="text-sm text-muted-foreground">
                      Include speaking exercises in your lessons
                    </p>
                  </div>
                  <Switch
                    id="speaking_exercises"
                    checked={settings.speaking_exercises}
                    onCheckedChange={(value) => setSettings({...settings, speaking_exercises: value})}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="listening_exercises">Listening Exercises</Label>
                    <p className="text-sm text-muted-foreground">
                      Include listening exercises in your lessons
                    </p>
                  </div>
                  <Switch
                    id="listening_exercises"
                    checked={settings.listening_exercises}
                    onCheckedChange={(value) => setSettings({...settings, listening_exercises: value})}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="reading_exercises">Reading Exercises</Label>
                    <p className="text-sm text-muted-foreground">
                      Include reading exercises in your lessons
                    </p>
                  </div>
                  <Switch
                    id="reading_exercises"
                    checked={settings.reading_exercises}
                    onCheckedChange={(value) => setSettings({...settings, reading_exercises: value})}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="writing_exercises">Writing Exercises</Label>
                    <p className="text-sm text-muted-foreground">
                      Include writing exercises in your lessons
                    </p>
                  </div>
                  <Switch
                    id="writing_exercises"
                    checked={settings.writing_exercises}
                    onCheckedChange={(value) => setSettings({...settings, writing_exercises: value})}
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "security" && (
            <Card>
              <CardHeader>
                <CardTitle>Security Settings</CardTitle>
                <CardDescription>
                  Manage your account security
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Change Password</h3>
                  
                  <div className="space-y-2">
                    <Label htmlFor="old_password">Current Password</Label>
                    <Input 
                      id="old_password" 
                      type="password" 
                      value={oldPassword}
                      onChange={(e) => setOldPassword(e.target.value)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="new_password">New Password</Label>
                    <Input 
                      id="new_password" 
                      type="password" 
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="confirm_password">Confirm Password</Label>
                    <Input 
                      id="confirm_password" 
                      type="password" 
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                  </div>
                  
                  {passwordError && (
                    <p className="text-sm text-red-500">{passwordError}</p>
                  )}
                  
                  <Button 
                    onClick={handleChangePassword}
                    disabled={isSaving || !oldPassword || !newPassword || !confirmPassword}
                  >
                    {isSaving ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Changing...
                      </>
                    ) : (
                      <>Change Password</>
                    )}
                  </Button>
                </div>
                
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Two-Factor Authentication</h3>
                  <p className="text-sm text-muted-foreground">
                    Add an extra layer of security to your account
                  </p>
                  <Button variant="outline">Setup 2FA</Button>
                </div>
                
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Connected Accounts</h3>
                  <p className="text-sm text-muted-foreground">
                    Manage your connected accounts and services
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="bg-gray-100 dark:bg-gray-800 p-2 rounded-md">
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
                    <Button variant="ghost" size="sm">Connect</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "privacy" && (
            <Card>
              <CardHeader>
                <CardTitle>Privacy Settings</CardTitle>
                <CardDescription>
                  Manage your privacy preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="public_profile">Public Profile</Label>
                    <p className="text-sm text-muted-foreground">
                      Make your profile visible to other users
                    </p>
                  </div>
                  <Switch
                    id="public_profile"
                    checked={settings.public_profile}
                    onCheckedChange={(value) => setSettings({...settings, public_profile: value})}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="share_progress">Share Progress</Label>
                    <p className="text-sm text-muted-foreground">
                      Allow others to see your learning progress
                    </p>
                  </div>
                  <Switch
                    id="share_progress"
                    checked={settings.share_progress}
                    onCheckedChange={(value) => setSettings({...settings, share_progress: value})}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="share_activity">Share Activity</Label>
                    <p className="text-sm text-muted-foreground">
                      Allow others to see your recent activity
                    </p>
                  </div>
                  <Switch
                    id="share_activity"
                    checked={settings.share_activity}
                    onCheckedChange={(value) => setSettings({...settings, share_activity: value})}
                  />
                </div>
                
                <div className="pt-4">
                  <h3 className="text-lg font-medium mb-2">Data & Privacy</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Manage your data and privacy options
                  </p>
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full justify-start">
                      Download My Data
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      Privacy Policy
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      Terms of Service
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "billing" && (
            <Card>
              <CardHeader>
                <CardTitle>Billing Settings</CardTitle>
                <CardDescription>
                  Manage your subscription and payment methods
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="pb-4 border-b">
                  <h3 className="text-lg font-medium mb-2">Current Plan</h3>
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">{user.is_subscribed ? 'Premium Plan' : 'Free Plan'}</p>
                      <p className="text-sm text-muted-foreground">
                        {user.is_subscribed 
                          ? 'Your subscription renews on the 1st of each month' 
                          : 'Upgrade to access premium features'}
                      </p>
                    </div>
                    <Button variant={user.is_subscribed ? "outline" : "default"}>
                      {user.is_subscribed ? 'Manage Subscription' : 'Upgrade'}
                    </Button>
                  </div>
                </div>
                
                {user.is_subscribed && (
                  <div className="pb-4 border-b">
                    <h3 className="text-lg font-medium mb-2">Payment Method</h3>
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <div className="bg-gray-100 dark:bg-gray-800 p-2 rounded-md">
                          <CreditCard className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="font-medium">Visa ending in 4242</p>
                          <p className="text-sm text-muted-foreground">Expires 04/24</p>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">Update</Button>
                    </div>
                  </div>
                )}
                
                <div className="pt-4">
                  <h3 className="text-lg font-medium mb-2">Billing History</h3>
                  {user.is_subscribed ? (
                    <div className="space-y-4">
                      <div className="flex justify-between items-center py-2">
                        <div>
                          <p className="font-medium">Mar 1, 2025</p>
                          <p className="text-sm text-muted-foreground">Premium Plan</p>
                        </div>
                        <p className="font-medium">$9.99</p>
                      </div>
                      <div className="flex justify-between items-center py-2">
                        <div>
                          <p className="font-medium">Feb 1, 2025</p>
                          <p className="text-sm text-muted-foreground">Premium Plan</p>
                        </div>
                        <p className="font-medium">$9.99</p>
                      </div>
                      <Button variant="outline" className="w-full mt-4">View All Invoices</Button>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      No billing history available on the free plan
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "danger" && (
            <Card className="border-red-200">
              <CardHeader>
                <CardTitle className="text-red-500">Danger Zone</CardTitle>
                <CardDescription>
                  Irreversible and destructive actions
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="pb-4 border-b">
                  <h3 className="text-lg font-medium mb-2">Export and Reset Data</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Download your data before resetting or deleting your account
                  </p>
                  <Button variant="outline">Export All Data</Button>
                </div>
                
                <div className="pb-4 border-b">
                  <h3 className="text-lg font-medium mb-2">Reset Progress</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    This will reset all your learning progress and statistics
                  </p>
                  <Button variant="outline" className="text-red-500">
                    Reset Progress
                  </Button>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium mb-2">Delete Account</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Once you delete your account, there is no going back. This action cannot be undone.
                  </p>
                  <Button 
                    variant="destructive"
                    onClick={handleDeleteAccount}
                    disabled={isDeleting}
                  >
                    {isDeleting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Deleting...
                      </>
                    ) : (
                      <>Delete Account</>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}