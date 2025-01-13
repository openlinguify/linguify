'use client';

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { AxiosError } from "axios";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/shared/components/ui/tabs";
import { Card } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { BookOpen, List, Grid, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Skeleton } from "@/shared/components/ui/skeleton";

// Types
interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Loading skeleton component
const LoadingSkeleton = () => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
    {[...Array(6)].map((_, i) => (
      <Card key={i} className="p-6">
        <Skeleton className="h-6 w-3/4 mb-4" />
        <Skeleton className="h-20 w-full mb-4" />
        <div className="flex justify-between items-center">
          <Skeleton className="h-6 w-20" />
          <Skeleton className="h-6 w-6 rounded-full" />
        </div>
      </Card>
    ))}
  </div>
);

export default function CoursesPage() {
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchUnits = async () => {
      try {
        const { data } = await axios.get<{ results: Unit[] }>(`${apiUrl}/api/v1/course/units/`, {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          withCredentials: false
        });
        setUnits(data.results || []);
      } catch (err) {
        console.error('Error fetching units:', err);
        if (axios.isAxiosError(err)) {
          const axiosError = err as AxiosError;
          setError(axiosError.response?.data?.message || "Unable to load units.");
        } else {
          setError("An unexpected error occurred.");
        }
      } finally {
        setLoading(false);
      }
    };
    fetchUnits();
  }, []);

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-48" />
        </div>
        <LoadingSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
          <Button 
            onClick={() => window.location.reload()} 
            variant="outline" 
            size="sm"
            className="mt-2"
          >
            Try Again
          </Button>
        </Alert>
      </div>
    );
  }

  if (units.length === 0) {
    return (
      <div className="p-6">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>No courses available at the moment.</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
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

        <TabsContent value="grid">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {units.map((unit) => (
              <Card
                key={unit.id}
                className="p-6 hover:shadow-lg transition-all cursor-pointer group"
                onClick={() => router.push(`/units/${unit.id}`)}
              >
                <div className="flex flex-col h-full">
                  <h3 className="text-lg font-semibold mb-2 group-hover:text-sky-600 transition-colors">
                    {unit.title}
                  </h3>
                  <p className="text-sm text-gray-600 flex-grow">{unit.description}</p>
                  <div className="mt-4 flex items-center justify-between pt-4 border-t">
                    <span className="text-sm font-medium px-2 py-1 rounded-full bg-sky-100 text-sky-600">
                      Level {unit.level}
                    </span>
                    <Button variant="ghost" size="icon">
                      <BookOpen className="h-4 w-4 text-sky-600" />
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
                    <span className="text-sm text-gray-500">Level {unit.level}</span>
                    <BookOpen className="h-4 w-4 text-sky-600" />
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