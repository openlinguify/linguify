'use client';

import React, { useState, useRef } from 'react';
import { Camera, Loader2, UserIcon } from 'lucide-react';
import authService from '@/services/authService';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

interface PhotoUploaderProps {
  currentUrl?: string | null;
  username: string;
  onSuccess?: (newPhotoUrl: string) => void;
}

// Utiliser le même nom de composant que celui utilisé dans l'importation
export function PhotoUploader({ currentUrl, username, onSuccess }: PhotoUploaderProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleProfilePictureClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    try {
      setUploading(true);
      setError(null);
      
      // Create form data for file upload
      const formData = new FormData();
      formData.append('profile_picture', file);
      
      // Get auth token
      const token = authService.getAuthToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }
      
      console.log("Uploading profile picture...");
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/auth/profile-picture/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          // Don't set Content-Type when using FormData
        },
        body: formData,
      });
      
      console.log("Upload response status:", response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Server error: ${response.status}`);
      }
      
      const result = await response.json();
      console.log("Upload successful:", result);
      
      if (result.profile_picture && onSuccess) {
        onSuccess(result.profile_picture);
      }
      
      // Refresh the page to show the new profile picture
      setTimeout(() => {
        window.location.reload();
      }, 1000);
      
    } catch (error: any) {
      console.error('Error:', error);
      setError(error.message || "An error occurred while uploading your profile picture");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-3">
      {/* Profile picture with upload overlay */}
      <div 
        className="relative w-32 h-32 rounded-full overflow-hidden border-2 border-gray-200 cursor-pointer"
        onClick={handleProfilePictureClick}
      >
        {currentUrl ? (
          <img 
            src={currentUrl} 
            alt="Profile"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full bg-gray-100 flex items-center justify-center">
            <UserIcon className="w-16 h-16 text-gray-400" />
          </div>
        )}
        
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40 opacity-0 hover:opacity-100 transition-opacity">
          <Camera className="w-8 h-8 text-white" />
        </div>
        
        {uploading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-60">
            <Loader2 className="w-8 h-8 text-white animate-spin" />
          </div>
        )}
      </div>
      
      {/* Hidden file input */}
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        className="hidden" 
        accept="image/*"
      />
      
      {/* Upload button */}
      <Button 
        variant="outline" 
        size="sm"
        onClick={handleProfilePictureClick}
        disabled={uploading}
      >
        {uploading ? 'Uploading...' : 'Upload Photo'}
      </Button>
      
      {error && (
        <Alert 
          variant="destructive" 
          className="mt-2"
        >
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
}