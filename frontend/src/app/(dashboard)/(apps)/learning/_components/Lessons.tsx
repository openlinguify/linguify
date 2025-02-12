'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from "next/navigation";
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  ArrowLeft, 
  Clock, 
  BookOpen, 
  CheckCircle, 
  AlertCircle,
  ChevronRight,
  GraduationCap,
  Video,
  FileText
} from 'lucide-react';

interface Lesson {
  id: number;
  title: string;
  description: string;
  lesson_type: string;
  estimated_duration: number;
  order: number;
}

interface LessonsProps {
  unitId: string;
}

const getLessonTypeIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'video':
      return <Video className="w-5 h-5" />;
    case 'quiz':
      return <GraduationCap className="w-5 h-5" />;
    case 'reading':
      return <FileText className="w-5 h-5" />;
    default:
      return <BookOpen className="w-5 h-5" />;
  }
};

export default function EnhancedLessons({ unitId }: LessonsProps) {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(30);
  const router = useRouter();

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:8000/api/v1/course/lesson/?unit=${unitId}`,
          { credentials: "omit" }
        );

        if (!response.ok) throw new Error("Failed to fetch lessons");

        const data = await response.json();
        const sortedLessons = Array.isArray(data) 
          ? data.sort((a: Lesson, b: Lesson) => a.order - b.order)
          : (data.results || []).sort((a: Lesson, b: Lesson) => a.order - b.order);
        
        setLessons(sortedLessons);
        setError(null);
      } catch (err) {
        setError("Failed to load lessons");
        console.error("Error fetching lessons:", err);
      } finally {
        setLoading(false);
      }
    };

    if (unitId) fetchLessons();
  }, [unitId]);

  const handleBack = () => {
    router.push("/learning");
  };

  const handleLessonClick = (lessonId: number) => {
    router.push(`/learning/${unitId}/${lessonId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen w-full bg-purple-50 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <p className="text-purple-600 font-medium">Loading your learning journey...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen w-full bg-purple-50 p-4">
        <Alert variant="destructive" className="max-w-2xl mx-auto">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full bg-purple-50">
      <div className="px-8 py-6 max-w-7xl mx-auto">
        {/* Header Section */}
        <Button
          variant="ghost"
          className="flex items-center gap-2 text-purple-600 hover:text-purple-700 mb-8"
          onClick={handleBack}
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Units
        </Button>
        
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-amber-500 text-transparent bg-clip-text">
            Course Progress
          </h1>
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-purple-600" />
            <span className="text-gray-600">
              {lessons.reduce((acc, lesson) => acc + lesson.estimated_duration, 0)} min total
            </span>
          </div>
        </div>
        
        <div className="bg-white rounded-lg p-4 mb-8 shadow-sm">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-600">Overall Progress</span>
            <span className="text-sm font-medium text-purple-600">{progress}%</span>
          </div>
          <Progress value={progress} className="h-2 bg-purple-100" />
        </div>

        {/* Lessons Grid */}
        <div className="space-y-4">
          {lessons.length === 0 ? (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>No lessons available yet.</AlertDescription>
            </Alert>
          ) : (
            lessons.map((lesson, index) => (
              <Card
                key={lesson.id}
                className="transform transition-all duration-300 hover:scale-[1.01] cursor-pointer hover:shadow-md bg-white"
                onClick={() => handleLessonClick(lesson.id)}
              >
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-12 h-12 rounded-full bg-purple-100 text-purple-600 shrink-0">
                      {getLessonTypeIcon(lesson.lesson_type)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <h3 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-amber-500 text-transparent bg-clip-text">
                            {lesson.title}
                          </h3>
                          <p className="text-gray-600 mt-1">{lesson.description}</p>
                        </div>
                        <ChevronRight className="h-5 w-5 text-gray-400 shrink-0" />
                      </div>
                      
                      <div className="flex flex-wrap items-center gap-3 mt-4">
                        <span className="flex items-center gap-2 text-sm text-gray-600">
                          <Clock className="h-4 w-4" />
                          {lesson.estimated_duration} min
                        </span>
                        <span className="flex items-center gap-2 text-sm font-medium px-3 py-1 rounded-full bg-purple-50 text-purple-700">
                          {getLessonTypeIcon(lesson.lesson_type)}
                          {lesson.lesson_type}
                        </span>
                        {index === 0 && (
                          <span className="flex items-center gap-1 text-sm font-medium px-3 py-1 rounded-full bg-green-50 text-green-700">
                            <CheckCircle className="h-4 w-4" />
                            Start Here
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}