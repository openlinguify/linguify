// src/addons/learning/components/Lessons/LessonAccordion.tsx
'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import courseAPI from "@/addons/learning/api/courseAPI";
import { ContentLesson, Lesson } from "@/addons/learning/types";
import {
  ChevronRight,
  ChevronDown,
  BookOpen,
  FileText,
  Infinity,
  Mic,
  GraduationCap
} from "lucide-react";

interface LessonAccordionProps {
  lessons: Lesson[];
  expandedLessonId: number | null;
  onLessonClick: (lessonId: number) => void;
  onContentClick: (unitId: number, lessonId: number, contentId: number) => void;
}

const getContentTypeIcon = (type: string) => {
  const contentType = type.toLowerCase();
  switch (contentType) {
    case "vocabulary": return <FileText className="w-4 h-4" />;
    case "matching": return <Infinity className="w-4 h-4" />;
    case "speaking": return <Mic className="w-4 h-4" />;
    case "reordering": return <GraduationCap className="w-4 h-4" />;
    default: return <BookOpen className="w-4 h-4" />;
  }
};

const LessonAccordion: React.FC<LessonAccordionProps> = ({
  lessons,
  expandedLessonId,
  onLessonClick,
  onContentClick
}) => {
  const [contentMap, setContentMap] = useState<Record<number, ContentLesson[]>>({});
  const [loadingMap, setLoadingMap] = useState<Record<number, boolean>>({});

  useEffect(() => {
    // Si une leçon est développée et qu'on n'a pas encore chargé ses contenus
    if (expandedLessonId && !contentMap[expandedLessonId]) {
      loadLessonContents(expandedLessonId);
    }
  }, [expandedLessonId]);

  const loadLessonContents = async (lessonId: number) => {
    // Marquer comme en chargement
    setLoadingMap(prev => ({ ...prev, [lessonId]: true }));
    
    try {
      const contents = await courseAPI.getContentLessons(lessonId);
      if (Array.isArray(contents)) {
        // Trier par ordre si disponible
        const sortedContents = contents.sort((a, b) => (a.order || 0) - (b.order || 0));
        setContentMap(prev => ({ ...prev, [lessonId]: sortedContents }));
      }
    } catch (error) {
      console.error(`Error loading contents for lesson ${lessonId}:`, error);
    } finally {
      setLoadingMap(prev => ({ ...prev, [lessonId]: false }));
    }
  };

  return (
    <div className="space-y-4">
      {lessons.map(lesson => {
        const isExpanded = lesson.id === expandedLessonId;
        const contents = contentMap[lesson.id] || [];
        const isLoading = loadingMap[lesson.id] || false;
        
        return (
          <div key={lesson.id} className="rounded-lg overflow-hidden">
            {/* Entête de la leçon */}
            <div 
              className={`flex items-center justify-between p-4 cursor-pointer ${
                isExpanded ? 'bg-purple-100 border-l-4 border-purple-500' : 'bg-white hover:bg-gray-50'
              }`}
              onClick={() => onLessonClick(lesson.id)}
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                  <BookOpen className="w-4 h-4 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-medium">{lesson.title}</h3>
                  {lesson.description && (
                    <p className="text-xs text-gray-500">{lesson.description}</p>
                  )}
                </div>
              </div>
              <div>
                {isExpanded ? (
                  <ChevronDown className="w-5 h-5 text-purple-600" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                )}
              </div>
            </div>
            
            {/* Contenus de la leçon (visible seulement si développé) */}
            {isExpanded && (
              <div className="bg-purple-50 border-l border-r border-b rounded-b-lg">
                {isLoading ? (
                  <div className="p-4 flex justify-center">
                    <div className="animate-spin h-5 w-5 border-2 border-purple-500 rounded-full border-t-transparent"></div>
                  </div>
                ) : contents.length === 0 ? (
                  <div className="p-4 text-center text-gray-500">
                    No content available for this lesson
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-4">
                    {contents.map(content => {
                      // Extraire le titre dans la langue appropriée
                      const title = typeof content.title === 'object' 
                        ? (content.title.en || Object.values(content.title)[0] || 'Content')
                        : content.title || 'Content';
                        
                      return (
                        <div 
                          key={content.id}
                          className="bg-white p-3 rounded-md shadow-sm hover:shadow-md cursor-pointer flex items-center"
                          onClick={() => onContentClick(lesson.unit_id || 0, lesson.id, content.id)}
                        >
                          <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                            {getContentTypeIcon(content.content_type)}
                          </div>
                          <span className="font-medium text-sm">{title}</span>
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

export default LessonAccordion;