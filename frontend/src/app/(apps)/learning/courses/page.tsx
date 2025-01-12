// src/app/(learning)/courses/page.tsx
"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/shared/components/ui/tabs";
import { Card } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { BookOpen, List, Grid } from "lucide-react";

// Types
interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}

// Main component
export default function CoursesPage() {
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchUnits = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/v1/course/units/');
        setUnits((response.data as { results: Unit[] }).results || []);
      } catch (err) {
        console.error("Error loading units:", err);
        setError("Unable to load units. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchUnits();
  }, []);

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600 mx-auto"/>
          <p className="text-gray-500">Loading courses...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="text-center text-red-500 p-4 rounded-lg bg-red-50">
        <p>{error}</p>
        <Button onClick={() => window.location.reload()} className="mt-4">
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-sky-700">Available Courses</h1>
      </div>

      <Tabs defaultValue="grid" className="space-y-4">
        <TabsList>
          <TabsTrigger value="grid">
            <Grid className="h-4 w-4 mr-2" />
            Grid View
          </TabsTrigger>
          <TabsTrigger value="list">
            <List className="h-4 w-4 mr-2" />
            List View
          </TabsTrigger>
        </TabsList>

        <TabsContent value="grid" className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {units.map((unit) => (
              <Card
                key={unit.id}
                className="p-4 hover:shadow-lg transition-all cursor-pointer group"
                onClick={() => router.push(`/units/${unit.id}`)}
              >
                <div className="flex flex-col h-full">
                  <h3 className="text-lg font-semibold mb-2 group-hover:text-sky-600 transition-colors">
                    {unit.title}
                  </h3>
                  <p className="text-sm text-gray-600 flex-grow">
                    {unit.description}
                  </p>
                  <div className="mt-4 flex items-center justify-between pt-4 border-t">
                    <span className="text-sm font-medium px-2 py-1 rounded-full bg-sky-100 text-sky-600">
                      Level {unit.level}
                    </span>
                    <Button size="sm" variant="ghost">
                      <BookOpen className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="list">
          <div className="space-y-2">
            {units.map((unit) => (
              <Card
                key={unit.id}
                className="p-4 hover:shadow-md transition-all cursor-pointer"
                onClick={() => router.push(`/units/${unit.id}`)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">{unit.title}</h3>
                    <p className="text-sm text-gray-600">{unit.description}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-500">
                      Level {unit.level}
                    </span>
                    <Button size="sm" variant="ghost">
                      <BookOpen className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}