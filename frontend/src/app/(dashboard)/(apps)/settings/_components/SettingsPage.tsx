'use client';

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Globe, User, BookOpen, Save, Loader2 } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAuth } from "@/providers/AuthProvider";
import { apiGet, apiPatch } from "@/lib/api-client";
import { storeAuthData, getUserProfile } from "@/lib/auth";

// Constants matching backend choices
const LANGUAGE_CHOICES = [
  { value: "EN", label: "English" },
  { value: "FR", label: "French" },
  { value: "NL", label: "Dutch" },
  { value: "DE", label: "German" },
  { value: "ES", label: "Spanish" },
  { value: "IT", label: "Italian" },
  { value: "PT", label: "Portuguese" },
];

const LEVEL_CHOICES = [
  { value: "A1", label: "A1 - Beginner" },
  { value: "A2", label: "A2 - Elementary" },
  { value: "B1", label: "B1 - Intermediate" },
  { value: "B2", label: "B2 - Upper Intermediate" },
  { value: "C1", label: "C1 - Advanced" },
  { value: "C2", label: "C2 - Mastery" },
];

const OBJECTIVES_CHOICES = [
  { value: "Travel", label: "Travel" },
  { value: "Business", label: "Business" },
  { value: "Live Abroad", label: "Live Abroad" },
  { value: "Exam", label: "Exam" },
  { value: "For Fun", label: "For Fun" },
  { value: "Work", label: "Work" },
  { value: "School", label: "School" },
  { value: "Study", label: "Study" },
  { value: "Personal", label: "Personal" },
];

const GENDER_CHOICES = [
  { value: "M", label: "Male" },
  { value: "F", label: "Female" },
];

interface UserSettings {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  birthday: string | null;
  gender: string | null;
  bio: string | null;
  native_language: string;
  target_language: string;
  language_level: string;
  objectives: string;
  is_coach: boolean;
  is_subscribed: boolean;
  profile_picture: string | null;
}

const SettingsPage = () => {
  // Get auth context
  const { isAuthenticated, user, getAccessToken } = useAuth();
  
  const [settings, setSettings] = useState<UserSettings>({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    birthday: null,
    gender: null,
    bio: null,
    native_language: "EN",
    target_language: "EN",
    language_level: "A1",
    objectives: "Travel",
    is_coach: false,
    is_subscribed: false,
    profile_picture: null,
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState("profile");
  const [saveStatus, setSaveStatus] = useState({
    show: false,
    isError: false,
    message: "",
  });

  // Try both user endpoints to get user data
  const loadUserSettings = async () => {
    try {
      setIsLoading(true);
      
      // Initialize with data from Auth provider if available
      if (user) {
        setSettings(prev => ({
          ...prev,
          email: user.email || '',
          first_name: user.name?.split(' ')[0] || '',
          last_name: user.name?.split(' ').slice(1).join(' ') || '',
          native_language: user.native_language || 'EN',
          target_language: user.target_language || 'EN',
          language_level: user.language_level || 'A1',
        }));
      }
      
      // Try /me endpoint first
      try {
        const userData = await apiGet<any>('/api/auth/me/');
        updateSettingsFromUserData(userData);
        return;
      } catch (meError) {
        console.log("Failed to fetch from /me endpoint, trying /user/...");
        // Fall back to /user/ endpoint
        try {
          const userData = await apiGet<any>('/api/auth/user/');
          updateSettingsFromUserData(userData);
          return;
        } catch (userError) {
          // If both fail, fallback to local storage
          const localProfile = getUserProfile();
          if (localProfile) {
            updateSettingsFromUserData(localProfile);
            return;
          }
          throw userError;
        }
      }
    } catch (error) {
      setSaveStatus({
        show: true,
        isError: true,
        message: error instanceof Error ? error.message : "Failed to load settings",
      });
      console.error("Load settings error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateSettingsFromUserData = (data: any) => {
    if (!data) return;
    
    // Check for required fields
    if (!data.email) {
      console.warn("Invalid user data received:", data);
      return;
    }

    setSettings({
      username: data.username || "",
      first_name: data.first_name || "",
      last_name: data.last_name || "",
      email: data.email || "",
      birthday: data.birthday || null,
      gender: data.gender || null,
      bio: data.bio || null,
      native_language: data.native_language || "EN",
      target_language: data.target_language || "EN",
      language_level: data.language_level || "A1",
      objectives: data.objectives || "Travel",
      is_coach: !!data.is_coach,
      is_subscribed: !!data.is_subscribed,
      profile_picture: data.profile_picture || null,
    });
    
    // Also update local storage for offline access
    const token = getAccessToken ? getAccessToken() : null;
    if (token) {
      storeAuthData(token, data);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadUserSettings();
    } else {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  const handleInputChange = (field: keyof UserSettings, value: any) => {
    setSettings(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setSaveStatus({ show: false, isError: false, message: "" });
      
      // Match the exact fields from ProfileUpdateSerializer
      const updateData = {
        first_name: settings.first_name,
        last_name: settings.last_name,
        username: settings.username,
        bio: settings.bio,
        native_language: settings.native_language,
        target_language: settings.target_language,
        language_level: settings.language_level,
        objectives: settings.objectives,
        gender: settings.gender,
      };
      
      // Use our API client for consistent auth handling
      const updatedData = await apiPatch<any>('/api/auth/user/', updateData);
      
      // Update settings with response data
      updateSettingsFromUserData(updatedData);
      
      // Save user preferences to localStorage for quick access
      localStorage.setItem('userSettings', JSON.stringify({
        native_language: settings.native_language,
        target_language: settings.target_language,
        language_level: settings.language_level,
        objectives: settings.objectives
      }));
      
      setSaveStatus({
        show: true,
        isError: false,
        message: "Settings saved successfully",
      });
    } catch (error) {
      setSaveStatus({
        show: true,
        isError: true,
        message: error instanceof Error ? error.message : "Failed to save settings",
      });
      console.error("Save settings error:", error);
    } finally {
      setIsSaving(false);
      setTimeout(() => {
        setSaveStatus(prev => ({ ...prev, show: false }));
      }, 3000);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  // Check if user is not authenticated
  if (!isAuthenticated) {
    return (
      <div className="container mx-auto p-6 max-w-4xl">
        <Card>
          <CardHeader>
            <CardTitle>Authentication Required</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">You need to be logged in to view and edit your settings.</p>
            <Button onClick={() => window.location.href = "/login"}>
              Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        <Button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center gap-2"
        >
          {isSaving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          Save Changes
        </Button>
      </div>

      {saveStatus.show && (
        <Alert
          variant={saveStatus.isError ? "destructive" : "default"}
          className="mb-6"
        >
          <AlertDescription>{saveStatus.message}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="w-4 h-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="language" className="flex items-center gap-2">
            <Globe className="w-4 h-4" />
            Language
          </TabsTrigger>
          <TabsTrigger value="learning" className="flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            Learning
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    value={settings.first_name}
                    onChange={(e) => handleInputChange("first_name", e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    value={settings.last_name}
                    onChange={(e) => handleInputChange("last_name", e.target.value)}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  value={settings.username}
                  onChange={(e) => handleInputChange("username", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  value={settings.email}
                  disabled
                  className="bg-gray-50"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="gender">Gender</Label>
                <Select
                  value={settings.gender || ""}
                  onValueChange={(value) => handleInputChange("gender", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select your gender" />
                  </SelectTrigger>
                  <SelectContent>
                    {GENDER_CHOICES.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea
                  id="bio"
                  value={settings.bio || ""}
                  onChange={(e) => handleInputChange("bio", e.target.value)}
                  placeholder="Tell us about yourself"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="language">
          <Card>
            <CardHeader>
              <CardTitle>Language Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="native_language">Native Language</Label>
                <Select
                  value={settings.native_language}
                  onValueChange={(value) => handleInputChange("native_language", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select your native language" />
                  </SelectTrigger>
                  <SelectContent>
                    {LANGUAGE_CHOICES.map((option) => (
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
                  onValueChange={(value) => handleInputChange("target_language", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select language to learn" />
                  </SelectTrigger>
                  <SelectContent>
                    {LANGUAGE_CHOICES.map((option) => (
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
                <Label htmlFor="language_level">Current Level</Label>
                <Select
                  value={settings.language_level}
                  onValueChange={(value) => handleInputChange("language_level", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select your level" />
                  </SelectTrigger>
                  <SelectContent>
                    {LEVEL_CHOICES.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="learning">
          <Card>
            <CardHeader>
              <CardTitle>Learning Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="objectives">Learning Objectives</Label>
                <Select
                  value={settings.objectives}
                  onValueChange={(value) => handleInputChange("objectives", value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select your objectives" />
                  </SelectTrigger>
                  <SelectContent>
                    {OBJECTIVES_CHOICES.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SettingsPage;