// src/app/(dashboard)/(routes)/page.tsx
"use client";

import { useAuth } from "@/providers/AuthProvider";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BookOpen, Star, Trophy, Clock } from "lucide-react";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const { isAuthenticated, user } = useAuth();
  const router = useRouter();

  const stats = [
    {
      label: "Current Progress",
      value: "32%",
      description: "Keep going!",
      icon: BookOpen,
      color: "text-blue-600",
    },
    {
      label: "Achievements",
      value: "12",
      description: "Earned so far",
      icon: Trophy,
      color: "text-amber-600",
    },
    {
      label: "Streak",
      value: "7 days",
      description: "Your current streak",
      icon: Star,
      color: "text-green-600",
    },
    {
      label: "Time Spent",
      value: "4.5h",
      description: "This week",
      icon: Clock,
      color: "text-purple-600",
    },
  ];

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-gray-50 to-white px-4">
        <div className="text-center space-y-6 max-w-2xl">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
            Welcome to Linguify
          </h1>

          <p className="text-lg text-gray-600">
            Start your language learning journey today with personalized
            lessons, interactive exercises, and real-time progress tracking.
          </p>

          <div className="mt-8">
            <p className="text-gray-500 mb-4">
              Sign in to access your personalized dashboard
            </p>
            <Button
              onClick={() => router.push("/login")}
              className="bg-gradient-to-r from-sky-500 to-blue-600"
            >
              Get Started
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
          Welcome back, {user?.name}!
        </h1>
        <p className="text-gray-600 mt-2">
          Ready to continue your language learning journey?
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Card key={stat.label} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                {stat.label}
              </CardTitle>
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-gray-600 mt-1">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Continue Learning</CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              onClick={() => router.push("/courses")}
              className="w-full bg-gradient-to-r from-sky-500 to-blue-600"
            >
              <BookOpen className="mr-2 h-4 w-4" />
              Go to Courses
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Daily Challenge</CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              onClick={() => router.push("/challenges")}
              className="w-full border-sky-500 text-sky-600 hover:bg-sky-50"
            >
              <Trophy className="mr-2 h-4 w-4" />
              Start Challenge
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
