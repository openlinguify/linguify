// src/addons/learning/components/Lessons/AllLessonsView.tsx
'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Lesson } from "@/addons/learning/types";
import courseAPI from "@/addons/learning/api/courseAPI";
import progressAPI from "@/addons/progress/api/progressAPI";
import { getUserTargetLanguage } from "@/core/utils/languageUtils";
import {
  Clock,
  BookOpen,
  GraduationCap,
  Video,
  FileText,
  CheckCircle,
  AlertCircle,
  ChevronRight,
  ChevronDown,
  Infinity,
  Mic,
  PencilLine,
  ArrowRightLeft,
  Loader2
} from "lucide-react";

// Helper function to get the appropriate icon for lesson type
const getLessonTypeIcon = (type: string): React.ReactNode => {
  switch (type.toLowerCase()) {
    case "video": return <Video className="h-5 w-5" />;
    case "quiz": return <GraduationCap className="h-5 w-5" />;
    case "reading": return <FileText className="h-5 w-5" />;
    case "vocabulary": return <BookOpen className="h-5 w-5" />;
    case "grammar": return <GraduationCap className="h-5 w-5" />;
    case "theory": return <BookOpen className="h-5 w-5" />;
    default: return <BookOpen className="h-5 w-5" />;
  }
};

// Helper function to get content type icon
const getContentTypeIcon = (type: string): React.ReactNode => {
  const contentType = type.toLowerCase();
  switch (contentType) {
    case "theory": return <BookOpen className="w-4 h-4" />;
    case "vocabulary": return <FileText className="w-4 h-4" />;
    case "vocabularylist": return <FileText className="w-4 h-4" />;
    case "multiple choice": return <GraduationCap className="w-4 h-4" />;
    case "matching": return <Infinity className="w-4 h-4" />;
    case "speaking": return <Mic className="w-4 h-4" />;
    case "fill_blank": return <PencilLine className="w-4 h-4" />;
    case "reordering": return <ArrowRightLeft className="w-4 h-4" />;
    default: return <BookOpen className="w-4 h-4" />;
  }
};

interface AllLessonsViewProps {
  levelFilter: string;
  contentTypeFilter: string;
  unitId?: number; // Optional unitId for filtering lessons by unit
  isCompactView?: boolean;
  layout?: "list" | "grid";
}

const AllLessonsView: React.FC<AllLessonsViewProps> = ({
  levelFilter,
  contentTypeFilter,
  unitId,
  isCompactView = false,
  layout = "list"
}) => {
  const router = useRouter();
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [progressData, setProgressData] = useState<Record<number, any>>({});
  const [expandedLessonId, setExpandedLessonId] = useState<number | null>(null);
  const [contentMap, setContentMap] = useState<Record<number, any[]>>({});
  const [loadingContentMap, setLoadingContentMap] = useState<Record<number, boolean>>({});
  const [targetLanguage, setTargetLanguage] = useState<string>(getUserTargetLanguage());

  useEffect(() => {
    // Get user's target language
    const userLang = getUserTargetLanguage();
    setTargetLanguage(userLang);
  }, []);

  useEffect(() => {
    const fetchLessons = async () => {
      setLoading(true);
      try {
        console.log(`Fetching lessons with contentType=${contentTypeFilter}, level=${levelFilter}${unitId ? `, unitId=${unitId}` : ''}`);

        let response;
        
        // If unitId is provided, fetch lessons for that unit
        if (unitId) {
          response = await courseAPI.getLessons(unitId, targetLanguage);
          // For unitId queries, we already get the array directly
          if (Array.isArray(response)) {
            setLessons(response);
            // Fetch progress data for all lessons
            const lessonIds = response.map(lesson => lesson.id);
            fetchLessonProgressData(lessonIds);
          } else {
            // Handle unexpected response format
            console.error("Unexpected response format:", response);
            setLessons([]);
          }
        } else {
          // Otherwise get lessons by content type and level
          let apiContentType = contentTypeFilter;
          if (apiContentType === "all") {
            apiContentType = ""; // Empty string for "all" content types
          }

          response = await courseAPI.getLessonsByContentType(apiContentType, levelFilter);

          // For content type queries, we get a response with results array
          if (response.results && response.results.length > 0) {
            setLessons(response.results);
            // Fetch progress data for all lessons
            const lessonIds = response.results.map(lesson => lesson.id);
            fetchLessonProgressData(lessonIds);
          } else {
            console.log(`No lessons found for content type "${contentTypeFilter}"`);
            setLessons([]);
          }
        }

        setError(null);
      } catch (err) {
        console.error("Failed to fetch lessons:", err);
        setError("Failed to load lessons. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchLessons();
  }, [levelFilter, contentTypeFilter, unitId, targetLanguage]);

  const fetchLessonProgressData = async (lessonIds: number[]) => {
    if (!lessonIds.length) return;

    try {
      // Fetch progress for all lessons
      const progressMap: Record<number, any> = {};

      // In a real implementation, you'd fetch all progress at once
      for (const lessonId of lessonIds) {
        const progress = await progressAPI.getLessonProgressByUnit(lessonId);
        if (progress && progress.length > 0) {
          progressMap[lessonId] = progress[0];
        }
      }

      setProgressData(progressMap);
    } catch (err) {
      console.error("Failed to fetch lesson progress:", err);
    }
  };

  const handleLessonClick = (lessonId: number) => {
    if (expandedLessonId === lessonId) {
      // If lesson is already expanded, collapse it
      setExpandedLessonId(null);
    } else {
      // Otherwise expand the new lesson
      setExpandedLessonId(lessonId);

      // Load content if not already loaded
      if (!contentMap[lessonId] && !loadingContentMap[lessonId]) {
        loadLessonContents(lessonId);
      }
    }
  };

  const loadLessonContents = async (lessonId: number) => {
    // Mark as loading
    setLoadingContentMap(prev => ({ ...prev, [lessonId]: true }));

    try {
      const contents = await courseAPI.getContentLessons(lessonId, targetLanguage);
      if (Array.isArray(contents)) {
        // Sort by order if available
        const sortedContents = contents.sort((a, b) => (a.order || 0) - (b.order || 0));
        setContentMap(prev => ({ ...prev, [lessonId]: sortedContents }));
      }
    } catch (error) {
      console.error(`Error loading contents for lesson ${lessonId}:`, error);
    } finally {
      setLoadingContentMap(prev => ({ ...prev, [lessonId]: false }));
    }
  };

  const handleContentClick = (unitId: number, lessonId: number, contentId: number, contentType: string) => {
    router.push(
      `/learning/content/${contentType.toLowerCase()}/${contentId}?language=${targetLanguage}&parentLessonId=${lessonId}&unitId=${unitId}`
    );
  };

  const navigateToLesson = (unitId: number, lessonId: number) => {
    router.push(`/learning/${unitId}/${lessonId}`);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-8 space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-purple-600" />
        <p className="text-purple-600 font-medium">Loading lessons...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="m-6">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (lessons.length === 0 && !loading && !error) {
    return (
      <div className="p-6 bg-gray-50 rounded-lg border border-gray-200 text-gray-700">
        <p className="text-center">No lessons found matching your filters.</p>
        <div className="flex justify-center mt-4">
          <Button
            variant="default"
            className="bg-purple-600 hover:bg-purple-700"
            onClick={() => {
              console.log("Manual refresh triggered");
              // Re-run the query manually
              setLoading(true);
              if (unitId) {
                courseAPI.getLessons(unitId, targetLanguage)
                  .then(response => {
                    console.log("Manual refresh response:", response);
                    if (Array.isArray(response)) {
                      setLessons(response);
                      if (response.length > 0) {
                        const lessonIds = response.map(lesson => lesson.id);
                        fetchLessonProgressData(lessonIds);
                      }
                    }
                    setLoading(false);
                  })
                  .catch(err => {
                    console.error("Manual refresh error:", err);
                    setLoading(false);
                    setError("Failed to load lessons. Please try again.");
                  });
              } else {
                courseAPI.getLessonsByContentType(contentTypeFilter, levelFilter)
                  .then(response => {
                    console.log("Manual refresh response:", response);
                    if (response.results) {
                      setLessons(response.results);
                      if (response.results.length > 0) {
                        const lessonIds = response.results.map(lesson => lesson.id);
                        fetchLessonProgressData(lessonIds);
                      }
                    }
                    setLoading(false);
                  })
                  .catch(err => {
                    console.error("Manual refresh error:", err);
                    setLoading(false);
                    setError("Failed to load lessons. Please try again.");
                  });
              }
            }}
          >
            Refresh Lessons
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={layout === "grid"
      ? `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`
      : "space-y-4"
    }>
      {lessons.map((lesson) => {
        const progress = progressData[lesson.id];
        const completionPercentage = progress ? progress.completion_percentage : 0;
        const status = progress ? progress.status : 'not_started';
        const isExpanded = expandedLessonId === lesson.id;
        const contents = contentMap[lesson.id] || [];
        const isLoadingContents = loadingContentMap[lesson.id] || false;

        return (
          <div key={lesson.id} className="space-y-1">
            <Card
              className={`transform transition-all duration-300 hover:shadow-md cursor-pointer
                ${status === 'completed' ? 'border-l-4 border-green-500' :
                  status === 'in_progress' ? 'border-l-4 border-amber-500' : ''}`}
              onClick={() => handleLessonClick(lesson.id)}
            >
              <CardContent className={isCompactView ? "p-3" : "p-6"}>
                {isCompactView ? (
                  // Compact view
                  <div className="flex items-center gap-2">
                    <div className={`flex items-center justify-center w-8 h-8 rounded-full shrink-0 
                      ${status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-purple-100 text-purple-600'}`}>
                      {status === 'completed' ? <CheckCircle className="h-4 w-4" /> : getLessonTypeIcon(lesson.lesson_type)}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1">
                        <h3 className="text-sm font-medium text-gray-900 truncate">{lesson.title}</h3>
                        {lesson.unit_level && (
                          <Badge className="whitespace-nowrap bg-gray-300 text-gray-800">
                            {lesson.unit_level}
                          </Badge>
                        )}
                      </div>

                      {lesson.unit_title && (
                        <p className="text-xs text-gray-600 truncate mt-1">
                          {lesson.unit_title}
                        </p>
                      )}
                    </div>
                    {isExpanded ?
                      <ChevronDown className="h-4 w-4 text-purple-600" /> :
                      <ChevronRight className="h-4 w-4 text-gray-400" />
                    }
                  </div>
                ) : (
                  // Full view
                  <div className="flex items-start gap-4">
                    <div className={`flex items-center justify-center w-12 h-12 rounded-full shrink-0 
                      ${status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-purple-100 text-purple-600'}`}>
                      {status === 'completed' ? <CheckCircle className="h-5 w-5" /> : getLessonTypeIcon(lesson.lesson_type)}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-xl font-bold text-gray-900">{lesson.title}</h3>
                            {lesson.unit_level && (
                              <Badge className="whitespace-nowrap bg-gray-300 text-gray-800">
                                Level {lesson.unit_level}
                              </Badge>
                            )}
                          </div>

                          <p className="text-gray-600 mt-1 line-clamp-2">{lesson.description}</p>

                          {lesson.unit_title && (
                            <p className="text-sm text-purple-600 mt-1">
                              Unit: {lesson.unit_title}
                            </p>
                          )}

                          {completionPercentage > 0 && (
                            <div className="mt-2">
                              <Progress
                                className="h-1.5"
                                value={completionPercentage}
                              />
                            </div>
                          )}
                        </div>
                        {isExpanded ?
                          <ChevronDown className="h-5 w-5 text-purple-600" /> :
                          <ChevronRight className="h-5 w-5 text-gray-400" />
                        }
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

                        {status === 'in_progress' && (
                          <span className="flex items-center gap-1 text-sm font-medium px-3 py-1 rounded-full bg-amber-50 text-amber-700">
                            In Progress
                          </span>
                        )}

                        {status === 'completed' && (
                          <span className="flex items-center gap-1 text-sm font-medium px-3 py-1 rounded-full bg-green-50 text-green-700">
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Completed
                          </span>
                        )}

                        {/* Add button to go to lesson detail page */}
                        <Button
                          variant="ghost"
                          size="sm"
                          className="ml-auto text-purple-600"
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent accordion toggle
                            navigateToLesson(lesson.unit_id || 0, lesson.id);
                          }}
                        >
                          Open Lesson <ChevronRight className="h-4 w-4 ml-1" />
                        </Button>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Lesson contents (visible only when expanded) */}
            {isExpanded && (
              <div className="border-2 border-purple-200 rounded-lg overflow-hidden bg-white p-2">
                {isLoadingContents ? (
                  <div className="p-4 flex justify-center">
                    <Loader2 className="h-5 w-5 animate-spin text-purple-500" />
                  </div>
                ) : contents.length === 0 ? (
                  <div className="p-4 text-center text-gray-500">
                    No content available for this lesson
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 p-2">
                    {contents.map(content => {
                      // Extract title in the appropriate language
                      const title = typeof content.title === 'object'
                        ? (content.title[targetLanguage] || content.title.en || Object.values(content.title)[0] || 'Content')
                        : content.title || 'Content';

                      return (
                        <div
                          key={content.id}
                          className="border border-purple-300 p-2 rounded-md hover:bg-purple-50 cursor-pointer flex items-center justify-between"
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent accordion toggle
                            handleContentClick(lesson.unit_id || 0, lesson.id, content.id, content.content_type);
                          }}
                        >
                          <div className="flex items-center gap-2">
                            <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center">
                              {getContentTypeIcon(content.content_type)}
                            </div>
                            <span className="text-purple-700 font-medium text-sm">{title}</span>
                          </div>
                          <ChevronRight className="h-4 w-4 text-purple-400" />
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default AllLessonsView;