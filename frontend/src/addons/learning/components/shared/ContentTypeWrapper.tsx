'use client';

import React, { useState, useEffect } from 'react';
import courseAPI from '@/addons/learning/api/courseAPI';
import { ContentTypeWrapperProps } from '@/addons/learning/types';
import LessonProgressIndicator from '../Navigation/LessonProgressIndicator';

export function ContentTypeWrapper({
  children,
  lessonId,
  contentType,
  currentStep,
  totalSteps,
  unitId,
  language = 'en'
}: ContentTypeWrapperProps) {
  const [lessonTitle, setLessonTitle] = useState<string>('');
  const [isCompleted, setIsCompleted] = useState<boolean>(false);

  const numericLessonId = typeof lessonId === 'string' ? parseInt(lessonId) : lessonId;
  const numericUnitId = unitId ? (typeof unitId === 'string' ? parseInt(unitId) : unitId) : undefined;

  // Fetch lesson title if available
  useEffect(() => {
    if (lessonId && unitId) {
      // Try to get lesson details from the content lessons
      courseAPI.getContentLessons(lessonId, language)
        .then(contentLessons => {
          if (contentLessons && contentLessons.length > 0) {
            // Content lessons may have multilingual titles
            const contentLesson = contentLessons[0];
            const title = typeof contentLesson.title === 'object'
              ? contentLesson.title[language || 'en'] || contentLesson.title.en
              : contentLesson.title;

            if (title) {
              setLessonTitle(title);
            }
          }
        })
        .catch(error => {
          console.warn(`Could not fetch content lessons: ${error.message}`);

          // Fallback: try to get the lesson info from the unit's lessons
          courseAPI.getLessons(unitId, language)
            .then(lessons => {
              if (lessons && lessons.length > 0) {
                const lesson = lessons.find(l => l.id === parseInt(String(lessonId)));
                if (lesson) {
                  setLessonTitle(lesson.title);
                }
              }
            })
            .catch(err => {
              console.warn(`Could not fetch lessons from unit: ${err.message}`);
            });
        });
    } else if (lessonId) {
      // For standalone content types, we'll use a generic title
      setLessonTitle(`${contentType.charAt(0).toUpperCase() + contentType.slice(1)} ${lessonId}`);
    }
  }, [lessonId, unitId, contentType, language]);

  // Check if the lesson is completed
  useEffect(() => {
    const checkCompletion = async () => {
      try {
        if (numericLessonId) {
          // First check if we have completion data in localStorage
          const localStorageKey = `progress_data_${numericLessonId}`;
          const storedData = localStorage.getItem(localStorageKey);

          if (storedData) {
            try {
              const parsedData = JSON.parse(storedData);
              if (parsedData?.data?.mark_completed) {
                setIsCompleted(true);
                return;
              }
            } catch (err) {
              console.warn('Error parsing localStorage data:', err);
            }
          }

          // If not found in localStorage, we could check with the API
          // But we'll leave this commented out to avoid extra API calls
          // This can be uncommented if API performance improves
          /*
          const contentProgress = await progressAPI.getContentLessonProgress(numericLessonId);
          if (contentProgress && contentProgress.length > 0) {
            setIsCompleted(contentProgress[0].status === 'completed');
          }
          */
        }
      } catch (error) {
        console.warn('Error checking lesson completion:', error);
      }
    };

    checkCompletion();
  }, [numericLessonId]);

  return (
    <div className="relative pt-16">
      {/* Progress Indicator - fixed at top */}
      <LessonProgressIndicator
        currentStep={currentStep || 1}
        totalSteps={totalSteps || 1}
        lessonId={numericLessonId}
        lessonTitle={lessonTitle}
        unitId={numericUnitId}
        contentType={contentType}
        isCompleted={isCompleted}
        showBackButton={true}
      />

      {/* Content */}
      <div className="container mx-auto pt-4 pb-16">
        {children}
      </div>
    </div>
  );
}