'use client';
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/services/AuthProvider";

interface UserData {
  id: string;
  public_id: string | null;
  email: string;
  name: string;
  username: string;
  first_name: string;
  last_name: string;
  picture: string | null;
  language_level: string;
  native_language: string;
  target_language: string;
  objectives: string;
  bio: string;
  is_coach: boolean;
  is_subscribed: boolean;
  is_active: boolean;
}

export default function LearningJourney() {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();
  const [userData, setUserData] = useState<UserData | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
    
    // If we have the user from context, use it
    if (user) {
      setUserData(user as UserData);
    }
  }, [isAuthenticated, isLoading, user, router]);

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Learning Journey Card */}
      <div className="rounded-lg bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 p-6 text-white shadow-md">

        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-semibold">Your Learning Journey</h1>
            <p className="text-white text-sm opacity-80">
              Follow the path to language mastery
            </p>
          </div>
        </div>

        {/* Progress Overview */}
        <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
          <div className="bg-white/15 hover:bg-white/20 transition-colors rounded-lg p-4 flex flex-col items-center shadow-inner">
          
            <div className="text-lg font-semibold mb-1">Current Level</div>
            <div className="text-white text-sm bg-white/10 px-3 py-1 rounded-full">
              {userData?.language_level || "Beginner"}
            </div>
          </div>
          
          <div className="bg-white/15 hover:bg-white/20 transition-colors rounded-lg p-4 flex flex-col items-center shadow-inner">

            <div className="text-lg font-semibold mb-1">Learning Language</div>
            <div className="text-white text-sm bg-white/10 px-3 py-1 rounded-full">
              {userData?.target_language || "Not set"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}