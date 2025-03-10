// src/app/(dashboard)/profile/ProfilePage.tsx
'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from "@/components/ui/use-toast";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { 
  User, 
  Calendar, 
  MapPin, 
  Mail, 
  BookOpen, 
  Loader2,
  Save,
  Camera
} from "lucide-react";
import { useAuthContext } from "@/services/AuthProvider";
import { Alert, AlertDescription } from "@/components/ui/alert";
import apiClient from '@/services/axiosAuthInterceptor';

// Constants for select options
const LANGUAGE_OPTIONS = [
  { value: 'EN', label: 'English' },
  { value: 'FR', label: 'French' },
  { value: 'NL', label: 'Dutch' },
  { value: 'DE', label: 'German' },
  { value: 'ES', label: 'Spanish' },
  { value: 'IT', label: 'Italian' },
  { value: 'PT', label: 'Portuguese' },
];

const LEVEL_OPTIONS = [
  { value: 'A1', label: 'A1 - Beginner' },
  { value: 'A2', label: 'A2 - Elementary' },
  { value: 'B1', label: 'B1 - Intermediate' },
  { value: 'B2', label: 'B2 - Upper Intermediate' },
  { value: 'C1', label: 'C1 - Advanced' },
  { value: 'C2', label: 'C2 - Mastery' },
];

const GENDER_OPTIONS = [
  { value: 'M', label: 'Male' },
  { value: 'F', label: 'Female' },
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

interface ProfileFormData {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  bio: string | null;
  gender: string | null;
  birthday: string | null;
  native_language: string;
  target_language: string;
  language_level: string;
  objectives: string;
}

export default function ProfilePage() {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
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
    objectives: 'Travel'
  });

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
        objectives: user.objectives || 'Travel'
      });
      
      // Fetch more detailed profile info
      fetchUserProfile();
    }
  }, [user]);

  const fetchUserProfile = async () => {
    try {
      const response = await apiClient.get('/api/auth/me/');
      if (response.data) {
        setFormData(prev => ({
          ...prev,
          ...response.data,
          birthday: response.data.birthday 
            ? new Date(response.data.birthday).toISOString().split('T')[0] 
            : null
        }));
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = async () => {
    try {
      setIsSaving(true);
      setAlert({ show: false, type: 'success', message: '' });

      const response = await apiClient.patch('/api/auth/me/', {
        username: formData.username,
        first_name: formData.first_name,
        last_name: formData.last_name,
        bio: formData.bio,
        gender: formData.gender,
        birthday: formData.birthday,
        native_language: formData.native_language,
        target_language: formData.target_language,
        language_level: formData.language_level,
        objectives: formData.objectives
      });

      setAlert({
        show: true,
        type: 'success',
        message: 'Profile updated successfully!'
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
        message: 'Failed to update profile. Please try again.'
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
        objectives: user.objectives || 'Travel'
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
      
      const response = await apiClient.post('/api/auth/me/profile-picture/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (response.data && response.data.profile_picture) {
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
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Your Profile</h1>
        {!isEditing ? (
          <Button onClick={() => setIsEditing(true)}>
            Edit Profile
          </Button>
        ) : (
          <div className="flex space-x-2">
            <Button variant="outline" onClick={handleCancelEdit}>
              Cancel
            </Button>
            <Button onClick={handleSaveProfile} disabled={isSaving}>
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
        )}
      </div>

      {alert.show && (
        <Alert className={`mb-6 ${alert.type === 'error' ? 'bg-destructive/15' : 'bg-green-100'}`}>
          <AlertDescription>
            {alert.message}
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column - Profile Summary */}
        <div className="md:col-span-1">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center mb-6">
                <div className="relative">
                  <div 
                    className="h-32 w-32 rounded-full overflow-hidden border-4 border-purple-100 cursor-pointer"
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
                      <Loader2 className="h-10 w-10 animate-spin text-white" />
                    </div>
                  )}
                  <div className="absolute bottom-0 right-0 bg-primary text-white p-2 rounded-full cursor-pointer hover:bg-primary/80 transition-colors">
                    <Camera className="h-4 w-4" />
                  </div>
                </div>
                <h2 className="text-xl font-semibold mt-4">{fullName}</h2>
                <p className="text-sm text-gray-500">{formData.email}</p>
              </div>

              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <User className="h-5 w-5 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Username</p>
                    <p className="text-gray-600">{formData.username}</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Mail className="h-5 w-5 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Email</p>
                    <p className="text-gray-600">{formData.email}</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Calendar className="h-5 w-5 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Birthday</p>
                    <p className="text-gray-600">
                      {formData.birthday ? new Date(formData.birthday).toLocaleDateString() : 'Not specified'}
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <MapPin className="h-5 w-5 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Native Language</p>
                    <p className="text-gray-600">
                      {LANGUAGE_OPTIONS.find(opt => opt.value === formData.native_language)?.label || 'Not specified'}
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <BookOpen className="h-5 w-5 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Learning</p>
                    <p className="text-gray-600">
                      {LANGUAGE_OPTIONS.find(opt => opt.value === formData.target_language)?.label || 'Not specified'} - 
                      {LEVEL_OPTIONS.find(opt => opt.value === formData.language_level)?.label || 'Not specified'}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Profile Details / Edit Form */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>
                {isEditing ? "Edit Your Profile" : "Profile Information"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid grid-cols-3 mb-6">
                  <TabsTrigger value="profile">Personal Info</TabsTrigger>
                  <TabsTrigger value="languages">Languages</TabsTrigger>
                  <TabsTrigger value="learning">Learning Goals</TabsTrigger>
                </TabsList>

                <TabsContent value="profile" className="space-y-6">
                  {!isEditing ? (
                    // View Mode
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <InfoItem label="First Name" value={formData.first_name || 'Not specified'} />
                      <InfoItem label="Last Name" value={formData.last_name || 'Not specified'} />
                      <InfoItem label="Username" value={formData.username} />
                      <InfoItem label="Email" value={formData.email} />
                      <InfoItem 
                        label="Gender" 
                        value={GENDER_OPTIONS.find(opt => opt.value === formData.gender)?.label || 'Not specified'} 
                      />
                      <InfoItem 
                        label="Birthday" 
                        value={formData.birthday ? new Date(formData.birthday).toLocaleDateString() : 'Not specified'} 
                      />
                      
                      <div className="col-span-full">
                        <h3 className="text-sm font-medium mb-2">Bio</h3>
                        <p className="text-gray-600">{formData.bio || 'No bio provided yet.'}</p>
                      </div>
                    </div>
                  ) : (
                    // Edit Mode
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="first_name">First Name</Label>
                        <Input
                          id="first_name"
                          name="first_name"
                          value={formData.first_name || ''}
                          onChange={handleInputChange}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="last_name">Last Name</Label>
                        <Input
                          id="last_name"
                          name="last_name"
                          value={formData.last_name || ''}
                          onChange={handleInputChange}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="username">Username</Label>
                        <Input
                          id="username"
                          name="username"
                          value={formData.username}
                          onChange={handleInputChange}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="email">Email (Read-only)</Label>
                        <Input
                          id="email"
                          name="email"
                          value={formData.email}
                          disabled
                          className="bg-gray-50"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="gender">Gender</Label>
                        <Select 
                          value={formData.gender || ''} 
                          onValueChange={(value) => handleSelectChange('gender', value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select gender" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">Not specified</SelectItem>
                            {GENDER_OPTIONS.map(option => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="birthday">Birthday</Label>
                        <Input
                          id="birthday"
                          name="birthday"
                          type="date"
                          value={formData.birthday || ''}
                          onChange={handleInputChange}
                        />
                      </div>
                      
                      <div className="col-span-full space-y-2">
                        <Label htmlFor="bio">Bio</Label>
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
                </TabsContent>

                <TabsContent value="languages" className="space-y-6">
                  {!isEditing ? (
                    // View Mode
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <InfoItem 
                        label="Native Language" 
                        value={LANGUAGE_OPTIONS.find(opt => opt.value === formData.native_language)?.label || 'Not specified'} 
                      />
                      <InfoItem 
                        label="Target Language" 
                        value={LANGUAGE_OPTIONS.find(opt => opt.value === formData.target_language)?.label || 'Not specified'} 
                      />
                      <InfoItem 
                        label="Language Level" 
                        value={LEVEL_OPTIONS.find(opt => opt.value === formData.language_level)?.label || 'Not specified'} 
                      />
                    </div>
                  ) : (
                    // Edit Mode
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="native_language">Native Language</Label>
                        <Select 
                          value={formData.native_language} 
                          onValueChange={(value) => handleSelectChange('native_language', value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select language" />
                          </SelectTrigger>
                          <SelectContent>
                            {LANGUAGE_OPTIONS.map(option => (
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
                          value={formData.target_language} 
                          onValueChange={(value) => handleSelectChange('target_language', value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select language" />
                          </SelectTrigger>
                          <SelectContent>
                            {LANGUAGE_OPTIONS.map(option => (
                              <SelectItem 
                                key={option.value} 
                                value={option.value}
                                disabled={option.value === formData.native_language}
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
                          value={formData.language_level} 
                          onValueChange={(value) => handleSelectChange('language_level', value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select level" />
                          </SelectTrigger>
                          <SelectContent>
                            {LEVEL_OPTIONS.map(option => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="learning" className="space-y-6">
                  {!isEditing ? (
                    // View Mode
                    <div className="grid grid-cols-1 gap-6">
                      <InfoItem 
                        label="Learning Objectives" 
                        value={OBJECTIVES_OPTIONS.find(opt => opt.value === formData.objectives)?.label || 'Not specified'} 
                      />
                      
                      {user.is_coach && (
                        <InfoItem 
                          label="Coach Status" 
                          value="You are registered as a language coach"
                        />
                      )}
                    </div>
                  ) : (
                    // Edit Mode
                    <div className="grid grid-cols-1 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="objectives">Learning Objectives</Label>
                        <Select 
                          value={formData.objectives} 
                          onValueChange={(value) => handleSelectChange('objectives', value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select objectives" />
                          </SelectTrigger>
                          <SelectContent>
                            {OBJECTIVES_OPTIONS.map(option => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

// Helper component for displaying information in view mode
function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <h3 className="text-sm font-medium mb-1">{label}</h3>
      <p className="text-gray-600">{value}</p>
    </div>
  );
}