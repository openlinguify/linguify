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
      // Navigate to the correct learning route structure
      router.push(`/learning/content/vocabulary/${lessonId}`);
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
        <div className="text-center space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Leçon de Vocabulaire</h2>
            <Badge variant="outline" className="text-sm px-3 py-1">
              {currentIndex + 1} / {vocabularyItems.length}
            </Badge>
          </div>
          <Progress value={progress} className="h-3 bg-gray-200 dark:bg-gray-700" />
        </div>

        {/* Main Content Area */}
        <div className="flex flex-col items-center space-y-6">
          {/* Vocabulary Card */}
          {currentItem && (
            <motion.div
              key={currentIndex}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="w-full max-w-2xl"
            >
              <Card className="shadow-lg border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
                <CardHeader className="text-center pb-6">
                  {/* Word Type and Audio */}
                  <div className="flex items-center justify-center gap-3 mb-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => speak(currentItem.word)}
                      className="flex items-center gap-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                    >
                      <Volume2 className="h-4 w-4" />
                      Écouter
                    </Button>
                    <Badge variant={knownWords.has(currentItem.id) ? "default" : "secondary"} className="px-3 py-1">
                      {currentItem.word_type || 'Expression'}
                    </Badge>
                  </div>
                  
                  {/* Main Word */}
                  <CardTitle className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-4">
                    {currentItem.word}
                  </CardTitle>
                </CardHeader>

                <CardContent className="px-6 pb-6">
                  {/* Content Tabs */}
                  <Tabs value={currentTab} onValueChange={setCurrentTab} className="w-full">
                    <TabsList className="grid w-full grid-cols-3 mb-6">
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

                    <TabsContent value="definition" className="mt-0">
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center space-y-4 min-h-[100px] flex items-center justify-center"
                      >
                        <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed">
                          {getFieldByLanguage('definition') || 'Définition non disponible'}
                        </p>
                      </motion.div>
                    </TabsContent>

                    <TabsContent value="example" className="mt-0">
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center space-y-4 min-h-[100px] flex flex-col items-center justify-center"
                      >
                        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg w-full">
                          <p className="text-lg italic text-blue-800 dark:text-blue-200 mb-3">
                            "{getFieldByLanguage('example_sentence') || 'Exemple non disponible'}"
                          </p>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => speak(getFieldByLanguage('example_sentence'))}
                            className="text-blue-600 hover:text-blue-700"
                          >
                            <Volume2 className="h-4 w-4 mr-2" />
                            Écouter l'exemple
                          </Button>
                        </div>
                      </motion.div>
                    </TabsContent>

                    <TabsContent value="related" className="mt-0">
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-4 min-h-[100px]"
                      >
                        {currentItem.synonymous && (
                          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                            <h4 className="font-medium text-green-700 dark:text-green-400 mb-2">Synonymes:</h4>
                            <p className="text-gray-700 dark:text-gray-300">{currentItem.synonymous}</p>
                          </div>
                        )}
                        {currentItem.antonymous && (
                          <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
                            <h4 className="font-medium text-red-700 dark:text-red-400 mb-2">Antonymes:</h4>
                            <p className="text-gray-700 dark:text-gray-300">{currentItem.antonymous}</p>
                          </div>
                        )}
                        {!currentItem.synonymous && !currentItem.antonymous && (
                          <div className="text-center py-8">
                            <p className="text-gray-500 dark:text-gray-400">Aucune information supplémentaire disponible</p>
                          </div>
                        )}
                      </motion.div>
                    </TabsContent>
                  </Tabs>

                  {/* Learning Action Buttons */}
                  <div className="flex justify-center gap-4 mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
                    <Button
                      variant={knownWords.has(currentItem.id) ? "default" : "outline"}
                      onClick={handleMarkAsKnown}
                      className="flex items-center gap-2 px-6"
                      size="lg"
                    >
                      <CheckCircle className="h-5 w-5" />
                      Je connais
                    </Button>
                    <Button
                      variant={difficultWords.has(currentItem.id) ? "destructive" : "outline"}
                      onClick={handleMarkAsDifficult}
                      className="flex items-center gap-2 px-6"
                      size="lg"
                    >
                      <Heart className="h-5 w-5" />
                      Difficile
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Navigation Controls */}
          <div className="w-full max-w-2xl">
            <div className="flex justify-between items-center pt-4">
              <Button
                variant="outline"
                onClick={handlePreviousWord}
                disabled={currentIndex === 0}
                className="flex items-center gap-2 px-6"
                size="lg"
              >
                <ArrowLeft className="h-4 w-4" />
                Précédent
              </Button>

              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  onClick={() => router.push('/learning')}
                  className="flex items-center gap-2"
                  size="lg"
                >
                  <Home className="h-4 w-4" />
                  Accueil
                </Button>
                
                {currentIndex === vocabularyItems.length - 1 ? (
                  <Button 
                    onClick={handleComplete} 
                    className="flex items-center gap-2 px-6 bg-green-600 hover:bg-green-700"
                    size="lg"
                  >
                    <Trophy className="h-4 w-4" />
                    Terminer
                  </Button>
                ) : (
                  <Button
                    onClick={handleNextWord}
                    className="flex items-center gap-2 px-6"
                    size="lg"
                  >
                    Suivant
                    <ArrowLeft className="h-4 w-4 rotate-180" />
                  </Button>
                )}
              </div>
            </div>
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
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        {renderVocabularyContent()}
      </div>
    </BaseExerciseWrapper>
  );
};