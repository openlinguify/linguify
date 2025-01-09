// src/app/(dashboard)/_components/settings/_components/settings-form.tsx
import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/components/ui/select";
import { Label } from "@/shared/components/ui/label";
import { Textarea } from "@/shared/components/ui/textarea";
import { Switch } from "@/shared/components/ui/switch";
import { Globe, User, BookOpen, Crown, AlertCircle, Save } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";

// Types and Constants
interface FormState {
  firstName: string;
  lastName: string;
  email: string;
  bio: string;
  nativeLanguage: string;
  targetLanguage: string;
  level: string;
  objectives: string[];
  notifications: {
    email: boolean;
    push: boolean;
  };
  premium: boolean;
  coach: boolean;
}

// Language options
const LANGUAGES = [
  { value: "EN", label: "English" },
  { value: "FR", label: "French" },
  { value: "DE", label: "German" },
  { value: "ES", label: "Spanish" },
  { value: "IT", label: "Italian" },
];

// Level options
const LEVELS = [
  { value: "A1", label: "A1 (Beginner)" },
  { value: "A2", label: "A2 (Elementary)" },
  { value: "B1", label: "B1 (Intermediate)" },
  { value: "B2", label: "B2 (Upper Intermediate)" },
  { value: "C1", label: "C1 (Advanced)" },
  { value: "C2", label: "C2 (Mastery)" },
];

// Objective options
const OBJECTIVES = [
  "Travel",
  "Business",
  "Academic",
  "Social",
  "Culture",
  "Other",
];

// Initial form state
const initialFormState: FormState = {
  firstName: "",
  lastName: "",
  email: "",
  bio: "",
  nativeLanguage: "",
  targetLanguage: "",
  level: "",
  objectives: [],
  notifications: {
    email: true,
    push: true,
  },
  premium: false,
  coach: false,
};

// Profile form component
const ProfileForm = ({
  formState,
  errors,
  handleInputChange,
}: {
  formState: FormState;
  errors: Record<string, string>;
  handleInputChange: (field: string, value: any) => void;
}) => (
  <Card>
    <CardHeader>
      <CardTitle>Personal Information</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="firstName">
            First Name
            <span className="text-red-500">*</span>
          </Label>
          <Input
            id="firstName"
            value={formState.firstName}
            onChange={(e) => handleInputChange("firstName", e.target.value)}
            placeholder="First Name"
            className={errors.firstName ? "border-red-500" : ""}
          />
          {errors.firstName && (
            <span className="text-sm text-red-500">{errors.firstName}</span>
          )}
        </div>
        <div className="space-y-2">
          <Label htmlFor="lastName">
            Last Name
            <span className="text-red-500">*</span>
          </Label>
          <Input
            id="lastName"
            value={formState.lastName}
            onChange={(e) => handleInputChange("lastName", e.target.value)}
            placeholder="Last Name"
            className={errors.lastName ? "border-red-500" : ""}
          />
          {errors.lastName && (
            <span className="text-sm text-red-500">{errors.lastName}</span>
          )}
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="email">
          Email
          <span className="text-red-500">*</span>
        </Label>
        <Input
          id="email"
          type="email"
          value={formState.email}
          onChange={(e) => handleInputChange("email", e.target.value)}
          placeholder="Email"
          className={errors.email ? "border-red-500" : ""}
        />
        {errors.email && (
          <span className="text-sm text-red-500">{errors.email}</span>
        )}
      </div>
      <div className="space-y-2">
        <Label htmlFor="bio">Bio</Label>
        <Textarea
          id="bio"
          value={formState.bio}
          onChange={(e) => handleInputChange("bio", e.target.value)}
          placeholder="Tell us about yourself"
          className="min-h-32"
        />
      </div>
    </CardContent>
  </Card>
);

// Main settings form
const SettingsForm = () => {
  const [activeTab, setActiveTab] = useState("profile");
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);

  const isValidEmail = (email: string): boolean => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const validateForm = useCallback(() => {
    const newErrors: Record<string, string> = {};

    if (!formState.firstName?.trim()) {
      newErrors.firstName = "First name is required";
    }
    if (!formState.lastName?.trim()) {
      newErrors.lastName = "Last name is required";
    }
    if (!formState.email?.trim()) {
      newErrors.email = "Email is required";
    } else if (!isValidEmail(formState.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formState]);

  const handleInputChange = (field: string, value: any) => {
    setFormState((prev) => ({
      ...prev,
      [field]: value,
    }));
    setHasChanges(true);

    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleSave = async (isAutoSave = false) => {
    if (!isAutoSave && !validateForm()) {
      setActiveTab("profile");
      return;
    }

    setIsSaving(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      if (!isAutoSave) {
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
      setHasChanges(false);
    } catch (error) {
      setErrors((prev) => ({
        ...prev,
        submit: "Failed to save changes. Please try again.",
      }));
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    if (!hasChanges || !autoSaveEnabled) return;

    const timer = setTimeout(() => {
      handleSave(true);
    }, 1000);

    return () => clearTimeout(timer);
  }, [formState, hasChanges, autoSaveEnabled]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          {hasChanges && (
            <p className="text-sm text-gray-500 mt-1">
              You have unsaved changes
            </p>
          )}
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Switch
              checked={autoSaveEnabled}
              onCheckedChange={setAutoSaveEnabled}
              id="auto-save"
            />
            <Label htmlFor="auto-save" className="text-sm">
              Auto-save
            </Label>
          </div>
          <Button
            onClick={() => handleSave(false)}
            disabled={isSaving || !hasChanges}
            className="bg-sky-600 hover:bg-sky-700"
          >
            <Save className="w-4 h-4 mr-2" />
            {isSaving ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </div>

      {saveSuccess && (
        <Alert className="bg-green-50 border-green-200">
          <AlertCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-600">
            Settings saved successfully!
          </AlertDescription>
        </Alert>
      )}

      {errors.submit && (
        <Alert className="bg-red-50 border-red-200">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-600">
            {errors.submit}
          </AlertDescription>
        </Alert>
      )}

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="space-y-6"
      >
        <TabsList className="gap-2">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="language" className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
            Language
          </TabsTrigger>
          <TabsTrigger value="learning" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Learning
          </TabsTrigger>
          <TabsTrigger value="subscription" className="flex items-center gap-2">
            <Crown className="h-4 w-4" />
            Subscription
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
          <ProfileForm
            formState={formState}
            errors={errors}
            handleInputChange={handleInputChange}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SettingsForm;
