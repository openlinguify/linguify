'use client';

import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Volume2, 
  Heart, 
  BookOpen, 
  CheckCircle,
  Trophy,
  RotateCcw,
  Star,
  Eye,
  Home,
  ArrowLeft
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import courseAPI from '@/addons/learning/api/courseAPI';
import { VocabularyItem, VocabularyLessonProps } from '@/addons/learning/types';
import { useSpeechSynthesis } from '@/core/speech/useSpeechSynthesis';
import { BaseExerciseWrapper } from './shared/BaseExerciseWrapper';
import { useMaintenanceAwareData } from '../../hooks/useMaintenanceAwareData';
import ExerciseNavBar from '../Navigation/ExerciseNavBar';

export const ModernVocabularyWrapper: React.FC<VocabularyLessonProps> = ({
  lessonId,
  language = 'en',
  unitId,
  onComplete,
  progressIndicator
}) => {
  const router = useRouter();
  const { speak } = useSpeechSynthesis('en');
  
  // Exercise state
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentTab, setCurrentTab] = useState('definition');
  const [knownWords, setKnownWords] = useState<Set<number>>(new Set());
  const [difficultWords, setDifficultWords] = useState<Set<number>>(new Set());

  // Create a data fetcher for vocabulary
  const fetchVocabularyData = useCallback(async (fetchLessonId: string | number, language?: string) => {
    console.log(`[ModernVocabularyWrapper] Fetching vocabulary for lesson: ${fetchLessonId}`);
    
    const response = await courseAPI.getVocabularyLesson(fetchLessonId);
    console.log('[ModernVocabularyWrapper] Vocabulary response:', response);
    
    if (response?.data?.vocabulary_items?.length > 0) {
      return {
        vocabulary_items: response.data.vocabulary_items,
        lesson_data: response.data
      };
    } else {
      console.log('[ModernVocabularyWrapper] No vocabulary found, triggering maintenance');
      throw new Error('MAINTENANCE: No vocabulary content found for this lesson');
    }
  }, []);

  // Use the maintenance-aware data hook
  const { data, loading: isLoading, error } = useMaintenanceAwareData({
    lessonId,
    contentType: 'vocabulary',
    fetchFunction: fetchVocabularyData
  });

  const vocabularyItems = data?.vocabulary_items || [];
  const currentItem = vocabularyItems[currentIndex];
  const progress = vocabularyItems.length > 0 ? ((currentIndex + 1) / vocabularyItems.length) * 100 : 0;

  const handleNextWord = () => {
    if (currentIndex < vocabularyItems.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setCurrentTab('definition');
    }
  };

  const handlePreviousWord = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setCurrentTab('definition');
    }
  };

  const handleMarkAsKnown = () => {
    if (currentItem) {
      setKnownWords(prev => new Set([...prev, currentItem.id]));
    }
  };

  const handleMarkAsDifficult = () => {
    if (currentItem) {
      setDifficultWords(prev => new Set([...prev, currentItem.id]));
    }
  };

  const handleComplete = () => {
    if (onComplete) {
      onComplete();
    } else {
      router.push(`/learn/lesson/${lessonId}`);
    }
  };

  const getFieldByLanguage = (field: string) => {
    return currentItem?.[`${field}_${language}`] || currentItem?.[field] || '';
  };

  // Render the vocabulary content
  const renderVocabularyContent = () => {
    if (vocabularyItems.length === 0) {
      return (
        <div className="text-center p-8">
          <p className="text-muted-foreground">Aucun vocabulaire disponible pour cette leçon.</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Progress Header */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Leçon de Vocabulaire</h2>
            <Badge variant="outline" className="text-sm">
              {currentIndex + 1} / {vocabularyItems.length}
            </Badge>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

          {/* Vocabulary Card */}
          {currentItem && (
            <Card className="w-full max-w-2xl mx-auto mb-6">
              <CardHeader className="text-center pb-4">
                <div className="flex items-center justify-center gap-3 mb-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => speak(currentItem.word)}
                    className="flex items-center gap-2"
                  >
                    <Volume2 className="h-4 w-4" />
                    Écouter
                  </Button>
                  <Badge variant={knownWords.has(currentItem.id) ? "default" : "secondary"}>
                    {currentItem.word_type || 'mot'}
                  </Badge>
                </div>
                <CardTitle className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {currentItem.word}
                </CardTitle>
              </CardHeader>

              <CardContent>
                <Tabs value={currentTab} onValueChange={setCurrentTab} className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="definition" className="flex items-center gap-2">
                      <BookOpen className="h-4 w-4" />
                      Définition
                    </TabsTrigger>
                    <TabsTrigger value="example" className="flex items-center gap-2">
                      <Eye className="h-4 w-4" />
                      Exemple
                    </TabsTrigger>
                    <TabsTrigger value="related" className="flex items-center gap-2">
                      <Star className="h-4 w-4" />
                      Lié
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="definition" className="mt-6">
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-center space-y-4"
                    >
                      <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed">
                        {getFieldByLanguage('definition')}
                      </p>
                    </motion.div>
                  </TabsContent>

                  <TabsContent value="example" className="mt-6">
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-center space-y-4"
                    >
                      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                        <p className="text-lg italic text-blue-800 dark:text-blue-200">
                          "{getFieldByLanguage('example_sentence')}"
                        </p>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => speak(getFieldByLanguage('example_sentence'))}
                          className="mt-2"
                        >
                          <Volume2 className="h-4 w-4 mr-2" />
                          Écouter l'exemple
                        </Button>
                      </div>
                    </motion.div>
                  </TabsContent>

                  <TabsContent value="related" className="mt-6">
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="space-y-4"
                    >
                      {currentItem.synonymous && (
                        <div>
                          <h4 className="font-medium text-green-600 dark:text-green-400 mb-2">Synonymes:</h4>
                          <p className="text-gray-700 dark:text-gray-300">{currentItem.synonymous}</p>
                        </div>
                      )}
                      {currentItem.antonymous && (
                        <div>
                          <h4 className="font-medium text-red-600 dark:text-red-400 mb-2">Antonymes:</h4>
                          <p className="text-gray-700 dark:text-gray-300">{currentItem.antonymous}</p>
                        </div>
                      )}
                    </motion.div>
                  </TabsContent>
                </Tabs>

                {/* Action Buttons */}
                <div className="flex justify-center gap-3 mt-6">
                  <Button
                    variant={knownWords.has(currentItem.id) ? "default" : "outline"}
                    onClick={handleMarkAsKnown}
                    className="flex items-center gap-2"
                  >
                    <CheckCircle className="h-4 w-4" />
                    Je connais
                  </Button>
                  <Button
                    variant={difficultWords.has(currentItem.id) ? "destructive" : "outline"}
                    onClick={handleMarkAsDifficult}
                    className="flex items-center gap-2"
                  >
                    <Heart className="h-4 w-4" />
                    Difficile
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

        {/* Navigation */}
        <div className="flex justify-between items-center pt-4">
          <Button
            variant="outline"
            onClick={handlePreviousWord}
            disabled={currentIndex === 0}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Précédent
          </Button>

          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => router.push('/learning')}
              className="flex items-center gap-2"
            >
              <Home className="h-4 w-4" />
              Accueil
            </Button>
            
            {currentIndex === vocabularyItems.length - 1 ? (
              <Button onClick={handleComplete} className="flex items-center gap-2">
                <Trophy className="h-4 w-4" />
                Terminer
              </Button>
            ) : (
              <Button
                onClick={handleNextWord}
                className="flex items-center gap-2"
              >
                Suivant
                <ArrowLeft className="h-4 w-4 rotate-180" />
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <BaseExerciseWrapper
      loading={isLoading}
      error={error}
      unitId={unitId}
      onBack={onComplete}
    >
      {renderVocabularyContent()}
    </BaseExerciseWrapper>
  );
};