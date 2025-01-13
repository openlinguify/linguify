'use client';
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Label } from "@/shared/components/ui/label";
import { Textarea } from "@/shared/components/ui/textarea";
import { Switch } from "@/shared/components/ui/switch";
import { Globe, User, BookOpen, Crown, Save } from 'lucide-react';
import { Alert, AlertDescription } from "@/shared/components/ui/alert";

interface FormState {
  profile: {
    firstName: string;
    lastName: string;
    email: string;
    bio: string;
  };
  language: {
    nativeLanguage: string;
    targetLanguage: string;
  };
  learning: {
    level: string;
    objectives: string;
  };
  subscription: {
    isPremium: boolean;
    isCoach: boolean;
  };
}

interface SaveStatus {
  show: boolean;
  success: boolean;
}

type FormSection = keyof FormState;
type FormField<T extends FormSection> = keyof FormState[T];
type FormValue = string | boolean;


const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState<FormSection>("profile");
  const [formState, setFormState] = useState<FormState>({
    profile: {
      firstName: "",
      lastName: "",
      email: "",
      bio: ""
    },
    language: {
      nativeLanguage: "",
      targetLanguage: ""
    },
    learning: {
      level: "",
      objectives: ""
    },
    subscription: {
      isPremium: false,
      isCoach: false
    }
  });
  const [saveStatus, setSaveStatus] = useState({ show: false, success: false });

  const handleInputChange = (section: FormSection, field: string, value: FormValue) => {
    setFormState(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleSave = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSaveStatus({ show: true, success: true });
      setTimeout(() => setSaveStatus({ show: false, success: false }), 3000);
    } catch (error) {
      setSaveStatus({ show: true, success: false });
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Settings</h1>
        <Button 
          onClick={handleSave}
          className="flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          Save Changes
        </Button>
      </div>

      {saveStatus.show && (
        <Alert className={saveStatus.success ? "bg-green-50" : "bg-red-50"}>
          <AlertDescription>
            {saveStatus.success 
              ? "Settings saved successfully!"
              : "Error saving settings. Please try again."}
          </AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={(value: string) => setActiveTab(value as FormSection)} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="profile" className="space-x-2">
            <User className="w-4 h-4" />
            <span>Profile</span>
          </TabsTrigger>
          <TabsTrigger value="language" className="space-x-2">
            <Globe className="w-4 h-4" />
            <span>Language</span>
          </TabsTrigger>
          <TabsTrigger value="learning" className="space-x-2">
            <BookOpen className="w-4 h-4" />
            <span>Learning</span>
          </TabsTrigger>
          <TabsTrigger value="subscription" className="space-x-2">
            <Crown className="w-4 h-4" />
            <span>Subscription</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
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
                    value={formState.profile.firstName}
                    onChange={(e) => handleInputChange('profile', 'firstName', e.target.value)}
                    placeholder="First Name" 
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input 
                    id="lastName" 
                    value={formState.profile.lastName}
                    onChange={(e) => handleInputChange('profile', 'lastName', e.target.value)}
                    placeholder="Last Name" 
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input 
                  id="email" 
                  type="email" 
                  value={formState.profile.email}
                  onChange={(e) => handleInputChange('profile', 'email', e.target.value)}
                  placeholder="Email" 
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea 
                  id="bio" 
                  value={formState.profile.bio}
                  onChange={(e) => handleInputChange('profile', 'bio', e.target.value)}
                  placeholder="Tell us about yourself" 
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="language" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Language Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="nativeLanguage">Native Language</Label>
                <Select 
                  value={formState.language.nativeLanguage}
                  onValueChange={(value) => handleInputChange('language', 'nativeLanguage', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select language" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EN">English</SelectItem>
                    <SelectItem value="FR">French</SelectItem>
                    <SelectItem value="DE">German</SelectItem>
                    <SelectItem value="ES">Spanish</SelectItem>
                    <SelectItem value="IT">Italian</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="targetLanguage">Target Language</Label>
                <Select
                  value={formState.language.targetLanguage}
                  onValueChange={(value) => handleInputChange('language', 'targetLanguage', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select language" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EN">English</SelectItem>
                    <SelectItem value="FR">French</SelectItem>
                    <SelectItem value="DE">German</SelectItem>
                    <SelectItem value="ES">Spanish</SelectItem>
                    <SelectItem value="IT">Italian</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="learning" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Learning Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="level">Current Level</Label>
                <Select
                  value={formState.learning.level}
                  onValueChange={(value) => handleInputChange('learning', 'level', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="A1">A1 (Beginner)</SelectItem>
                    <SelectItem value="A2">A2 (Elementary)</SelectItem>
                    <SelectItem value="B1">B1 (Intermediate)</SelectItem>
                    <SelectItem value="B2">B2 (Upper Intermediate)</SelectItem>
                    <SelectItem value="C1">C1 (Advanced)</SelectItem>
                    <SelectItem value="C2">C2 (Mastery)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="objectives">Learning Objectives</Label>
                <Select
                  value={formState.learning.objectives}
                  onValueChange={(value) => handleInputChange('learning', 'objectives', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select objective" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Travel">Travel</SelectItem>
                    <SelectItem value="Business">Business</SelectItem>
                    <SelectItem value="Live Abroad">Live Abroad</SelectItem>
                    <SelectItem value="Exam">Exam</SelectItem>
                    <SelectItem value="For Fun">For Fun</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="subscription" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Subscription Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Premium Subscription</Label>
                  <div className="text-sm text-muted-foreground">
                    Access premium features and content
                  </div>
                </div>
                <Switch
                  checked={formState.subscription.isPremium}
                  onCheckedChange={(checked) => 
                    handleInputChange('subscription', 'isPremium', checked)
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Coach Profile</Label>
                  <div className="text-sm text-muted-foreground">
                    Enable coaching features
                  </div>
                </div>
                <Switch
                  checked={formState.subscription.isCoach}
                  onCheckedChange={(checked) => 
                    handleInputChange('subscription', 'isCoach', checked)
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SettingsPage;