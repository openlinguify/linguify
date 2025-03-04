"use client";

import React, { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { useRouter } from "next/navigation";
import { UserProgress } from "./_components/user-progress";
import { Card } from "@/components/ui/card";
import { BookOpen, MessageCircle, Star, Trophy } from "lucide-react";
import Link from "next/link";
import { useAuthContext } from "@/services/AuthProvider";

export default function DashboardHome() {
  const { user, isAuthenticated, isLoading } = useAuthContext(); // Use the auth context instead
  const router = useRouter();
  const [userData, setUserData] = useState({
    nativeLanguage: "ENGLISH",
    level: "Intermediate",
    goals: "Improve speaking skills",
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }

    // If we have the user from context, use it
    if (user) {
      setUserData({
        nativeLanguage: user.native_language || "ENGLISH",
        level: user.language_level || "Intermediate",
        goals: user.objectives || "Improve speaking skills",
      });
    }
  }, [isAuthenticated, isLoading, user, router]);

  const quickActions = [
    { title: "Continue Learning", description: "Resume your last lesson", icon: BookOpen, href: "/learning" },
    { title: "Practice Speaking", description: "Start a conversation", icon: MessageCircle, href: "/chat" },
    { title: "Review Progress", description: "Check your achievements", icon: Trophy, href: "/progress" },
    { title: "Daily Tasks", description: "Complete your goals", icon: Star, href: "/task" },
  ];

  return (
    <div className="space-y-6">
      {/* Header avec bienvenue personnalisé */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Welcome back, {user?.name || "User"}!</h1>
        <div className="text-sm text-gray-500">Target Language: {user?.target_language || "ENGLISH"}</div>
      </div>

      {/* Progress Section */}
      <div className="w-full">
        <UserProgress />
      </div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((action) => (
          <Link key={action.href} href={action.href}>
            <Card className="p-4 hover:shadow-lg transition-transform transform hover:scale-105 cursor-pointer">
              <div className="flex items-start gap-4">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <action.icon className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                  <h3 className="font-medium">{action.title}</h3>
                  <p className="text-sm text-gray-500">{action.description}</p>
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>

      {/* User Profile Section */}
      <Card className="p-6">
        <div className="space-y-4">
          {/* Informations linguistiques */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Native Language</p>
              <p className="text-lg">{userData.nativeLanguage}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Current Level</p>
              <p className="text-lg">{userData.level}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Learning Goals</p>
              <p className="text-lg">{userData.goals}</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}