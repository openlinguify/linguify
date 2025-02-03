// src/app/(dashboard)/page.tsx
"use client";

import { UserProgress } from "./_components/user-progress";
import { Card } from "@/components/ui/card";
import { BookOpen, MessageCircle, Star, Trophy } from "lucide-react";
import Link from "next/link";

export default function DashboardHome() {
  const quickActions = [
    {
      title: "Continue Learning",
      description: "Resume your last lesson",
      icon: BookOpen,
      href: "/learning",
    },
    {
      title: "Practice Speaking",
      description: "Start a conversation",
      icon: MessageCircle,
      href: "/chat",
    },
    {
      title: "Review Progress",
      description: "Check your achievements",
      icon: Trophy,
      href: "/progress",
    },
    {
      title: "Daily Tasks",
      description: "Complete your goals",
      icon: Star,
      href: "/task",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header avec bienvenue personnalisé */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Welcome back!</h1>
        <div className="text-sm text-gray-500">Target Language: ENGLISH</div>
      </div>

      {/* Progress Section */}
      <div className="w-full">
        <UserProgress />
      </div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((action) => (
          <Link key={action.href} href={action.href}>
            <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer">
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
              <p className="text-sm font-medium text-gray-500">
                Native Language
              </p>
              <p className="text-lg">ENGLISH</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Current Level</p>
              <p className="text-lg">Intermediate</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">
                Learning Goals
              </p>
              <p className="text-lg">Improve speaking skills</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
