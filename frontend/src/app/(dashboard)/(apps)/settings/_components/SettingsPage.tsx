// src/app/(dashboard)/settings/_components/SettingsPage.tsx
"use client";

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
import {
  userSettingsService,
  UserSettings,
} from "@/services/userSettingsService";

const LANGUAGE_OPTIONS = [
  { value: "EN", label: "English" },
  { value: "FR", label: "French" },
  { value: "DE", label: "German" },
  { value: "ES", label: "Spanish" },
  { value: "IT", label: "Italian" },
  { value: "PT", label: "Portuguese" },
];

const LEVEL_OPTIONS = [
  { value: "A1", label: "A1 - Beginner" },
  { value: "A2", label: "A2 - Elementary" },
  { value: "B1", label: "B1 - Intermediate" },
  { value: "B2", label: "B2 - Upper Intermediate" },
  { value: "C1", label: "C1 - Advanced" },
  { value: "C2", label: "C2 - Mastery" },
];

const OBJECTIVES_OPTIONS = [
  { value: "Travel", label: "Travel" },
  { value: "Business", label: "Business" },
  { value: "Live Abroad", label: "Live Abroad" },
  { value: "Exam", label: "Exam" },
  { value: "For Fun", label: "For Fun" },
];

const SettingsPage = () => {
  const [settings, setSettings] = useState<UserSettings>({
    profile: {
      firstName: "",
      lastName: "",
      email: "",
      bio: null,
    },
    language: {
      nativeLanguage: "",
      targetLanguage: "",
      level: "",
    },
    learning: {
      objectives: "",
    },
    account: {
      isCoach: false,
      isSubscribed: false,
    },
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState("profile");
  const [saveStatus, setSaveStatus] = useState<{
    show: boolean;
    isError: boolean;
    message: string;
  }>({
    show: false,
    isError: false,
    message: "",
  });

  useEffect(() => {
    loadUserSettings();
  }, []);

  const loadUserSettings = async () => {
    try {
      const data = await userSettingsService.getUserSettings();
      setSettings(data);
    } catch (error) {
      setSaveStatus({
        show: true,
        isError: true,
        message: "Failed to load settings",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (
    section: keyof UserSettings,
    field: string,
    value: any
  ) => {
    setSettings((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await userSettingsService.updateUserSettings(settings);
      setSaveStatus({
        show: true,
        isError: false,
        message: "Settings saved successfully",
      });
    } catch (error) {
      setSaveStatus({
        show: true,
        isError: true,
        message: "Failed to save settings",
      });
    } finally {
      setIsSaving(false);
      setTimeout(() => {
        setSaveStatus((prev) => ({ ...prev, show: false }));
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

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="space-y-6"
      >
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
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    value={settings.profile.firstName}
                    onChange={(e) =>
                      handleInputChange("profile", "firstName", e.target.value)
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    value={settings.profile.lastName}
                    onChange={(e) =>
                      handleInputChange("profile", "lastName", e.target.value)
                    }
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  value={settings.profile.email}
                  disabled
                  className="bg-gray-50"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea
                  id="bio"
                  value={settings.profile.bio || ""}
                  onChange={(e) =>
                    handleInputChange("profile", "bio", e.target.value)
                  }
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
                <Label htmlFor="nativeLanguage">Native Language</Label>
                <Select
                  value={settings.language.nativeLanguage}
                  onValueChange={(value) =>
                    handleInputChange("language", "nativeLanguage", value)
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select your native language" />
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
                <Label htmlFor="targetLanguage">Target Language</Label>
                <Select
                  value={settings.language.targetLanguage}
                  onValueChange={(value) =>
                    handleInputChange("language", "targetLanguage", value)
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select language to learn" />
                  </SelectTrigger>
                  <SelectContent>
                    {LANGUAGE_OPTIONS.map((option) => (
                      <SelectItem
                        key={option.value}
                        value={option.value}
                        disabled={
                          option.value === settings.language.nativeLanguage
                        }
                      >
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="level">Current Level</Label>
                <Select
                  value={settings.language.level}
                  onValueChange={(value) =>
                    handleInputChange("language", "level", value)
                  }
                >
                  <SelectTrigger>
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
                  value={settings.learning.objectives}
                  onValueChange={(value) =>
                    handleInputChange("learning", "objectives", value)
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select your objectives" />
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
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SettingsPage;
