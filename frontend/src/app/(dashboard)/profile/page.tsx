'use client';
import { useRouter } from 'next/navigation';
import { useAuthContext } from "@/services/AuthProvider";
import { useEffect, useState } from 'react';
import { Save, X, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PhotoUploader } from './photo-upload';
import authService from '@/services/authService';

export default function ProfilePage() {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState({
    show: false,
    isError: false,
    message: "",
  });
  
  // Form data state
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    bio: '',
    gender: '',
    native_language: '',
    target_language: '',
    language_level: '',
    objectives: ''
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
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        bio: user.bio || '',
        gender: user.gender || '',
        native_language: user.native_language || '',
        target_language: user.target_language || '',
        language_level: user.language_level || '',
        objectives: user.objectives || ''
      });
    }
  }, [user]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-150px)]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <Card className="max-w-2xl mx-auto mt-10">
        <CardHeader>
          <CardTitle>Authentication Required</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4">Please log in to view your profile.</p>
          <Button onClick={() => router.push('/login')}>Login</Button>
        </CardContent>
      </Card>
    );
  }

  // Format the full name
  const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;

  // Handle form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle profile photo upload success
  const handlePhotoSuccess = (newPhotoUrl: string) => {
    console.log("New photo URL:", newPhotoUrl);
    // You can update the local state here if needed
  };

  // Handle form submission - using the existing user_profile endpoint with PATCH method
  const handleSaveChanges = async () => {
    try {
      setIsSaving(true);
      setSaveStatus({ show: false, isError: false, message: "" });
      
      // Get auth token
      const token = authService.getAuthToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }
      
      // Prepare data for update
      const updateData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        bio: formData.bio,
        gender: formData.gender || null,
        native_language: formData.native_language,
        target_language: formData.target_language,
        language_level: formData.language_level,
        objectives: formData.objectives
      };
      
      console.log("Updating profile with data:", updateData);
      
      // Send update request using PATCH as per the existing backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/auth/profile/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updateData),
        credentials: 'include'
      });
      
      console.log("Update response status:", response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Profile update error details:", errorData);
        throw new Error(`HTTP Error: ${response.status} - ${errorData.error || 'Unknown error'}`);
      }
      
      const updatedUser = await response.json();
      console.log("Profile updated successfully:", updatedUser);
      
      // Update auth state by refreshing the page
      authService.storeAuthData(token, updatedUser);
      
      setSaveStatus({
        show: true,
        isError: false,
        message: "Profile updated successfully",
      });
      
      setIsEditing(false);
    } catch (error: any) {
      console.error('Error:', error);
      setSaveStatus({
        show: true, 
        isError: true,
        message: `Error: ${error.message || "An error occurred while updating your profile"}`,
      });
    } finally {
      setIsSaving(false);
      setTimeout(() => {
        setSaveStatus(prev => ({ ...prev, show: false }));
      }, 3000);
    }
  };

  // Options for selectors
  const languageOptions = [
    { value: "EN", label: "English" },
    { value: "FR", label: "French" },
    { value: "NL", label: "Dutch" },
    { value: "DE", label: "German" },
    { value: "ES", label: "Spanish" },
    { value: "IT", label: "Italian" },
    { value: "PT", label: "Portuguese" },
  ];

  const levelOptions = [
    { value: "A1", label: "A1 - Beginner" },
    { value: "A2", label: "A2 - Elementary" },
    { value: "B1", label: "B1 - Intermediate" },
    { value: "B2", label: "B2 - Upper Intermediate" },
    { value: "C1", label: "C1 - Advanced" },
    { value: "C2", label: "C2 - Mastery" },
  ];

  const genderOptions = [
    { value: "M", label: "Male" },
    { value: "F", label: "Female" },
  ];

  const objectivesOptions = [
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

  return (
    <Card className="max-w-3xl mx-auto shadow-md">
      <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
        <CardTitle className="text-2xl font-bold">My Profile</CardTitle>
        {!isEditing ? (
          <Button 
            onClick={() => setIsEditing(true)}
            variant="default"
          >
            Edit Profile
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button 
              variant="outline"
              onClick={() => setIsEditing(false)}
              className="flex items-center"
            >
              <X className="w-4 h-4 mr-1" /> Cancel
            </Button>
            <Button 
              variant="default"
              onClick={handleSaveChanges}
              disabled={isSaving}
              className="flex items-center"
            >
              {isSaving ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Save className="w-4 h-4 mr-1" />
              )}
              Save Changes
            </Button>
          </div>
        )}
      </CardHeader>

      <CardContent className="pt-6">
        {saveStatus.show && (
          <Alert
            variant={saveStatus.isError ? "destructive" : "default"}
            className="mb-6"
          >
            <AlertDescription>{saveStatus.message}</AlertDescription>
          </Alert>
        )}

        <div className="flex flex-col md:flex-row md:items-start gap-8 mb-8">
          {/* Profile Photo with improved uploader */}
          <PhotoUploader 
            currentUrl={user.picture || user.profile_picture} 
            username={user.username || fullName}
            onSuccess={handlePhotoSuccess}
          />
          
          <div className="flex-1">
            <h2 className="text-xl font-medium">{fullName}</h2>
            <p className="text-gray-600">{user.email}</p>
            
            {/* User stats */}
            <div className="mt-4 grid grid-cols-2 gap-2">
              <div className="bg-gray-50 p-2 rounded">
                <div className="text-sm text-gray-500">Learning</div>
                <div className="font-medium">
                  {languageOptions.find(opt => opt.value === user.target_language)?.label || 'Not set'}
                </div>
              </div>
              <div className="bg-gray-50 p-2 rounded">
                <div className="text-sm text-gray-500">Level</div>
                <div className="font-medium">
                  {levelOptions.find(opt => opt.value === user.language_level)?.label?.split(' ')[0] || 'Not set'}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {!isEditing ? (
          // Display mode
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <InfoItem label="Username" value={user.username || 'Not specified'} />
            <InfoItem label="First Name" value={user.first_name || 'Not specified'} />
            <InfoItem label="Last Name" value={user.last_name || 'Not specified'} />
            <InfoItem label="Email" value={user.email || 'Not specified'} />
            <InfoItem label="Gender" value={
              genderOptions.find(opt => opt.value === user.gender)?.label || 'Not specified'
            } />
            <InfoItem label="Native Language" value={
              languageOptions.find(opt => opt.value === user.native_language)?.label || 'Not specified'
            } />
            <InfoItem label="Target Language" value={
              languageOptions.find(opt => opt.value === user.target_language)?.label || 'Not specified'
            } />
            <InfoItem label="Language Level" value={
              levelOptions.find(opt => opt.value === user.language_level)?.label || 'Not specified'
            } />
            <InfoItem label="Learning Objective" value={
              objectivesOptions.find(opt => opt.value === user.objectives)?.label || 'Not specified'
            } />
            
            <div className="col-span-2">
              <h3 className="text-lg font-semibold mb-2">Biography</h3>
              <p className="text-gray-700">{user.bio || 'No biography available'}</p>
            </div>
          </div>
        ) : (
          // Edit mode
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="first_name">
                First Name
              </label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
                className="border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="last_name">
                Last Name
              </label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
                className="border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                disabled
                className="border rounded w-full py-2 px-3 bg-gray-50 text-gray-500 leading-tight"
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="gender">
                Gender
              </label>
              <select
                id="gender"
                name="gender"
                value={formData.gender}
                onChange={handleInputChange}
                className="border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                {genderOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="native_language">
                Native Language
              </label>
              <select
                id="native_language"
                name="native_language"
                value={formData.native_language}
                onChange={handleInputChange}
                className="border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                {languageOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="target_language">
                Target Language
              </label>
              <select
                id="target_language"
                name="target_language"
                value={formData.target_language}
                onChange={handleInputChange}
                className="border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                {languageOptions.map(option => (
                  <option 
                    key={option.value} 
                    value={option.value}
                    disabled={option.value === formData.native_language}
                  >
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="language_level">
                Language Level
              </label>
              <select
                id="language_level"
                name="language_level"
                value={formData.language_level}
                onChange={handleInputChange}
                className="border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                {levelOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="objectives">
                Learning Objective
              </label>
              <select
                id="objectives"
                name="objectives"
                value={formData.objectives}
                onChange={handleInputChange}
                className="border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                {objectivesOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="col-span-2 mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="bio">
                Biography
              </label>
              <textarea
                id="bio"
                name="bio"
                value={formData.bio || ''}
                onChange={handleInputChange}
                rows={4}
                className="border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Tell us about yourself..."
              ></textarea>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Component to display an information row
function InfoItem({ label, value }: { label: string, value: string }) {
  return (
    <div className="mb-4">
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="text-gray-800">{value}</p>
    </div>
  );
}