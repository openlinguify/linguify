import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Mic, MicOff, Volume2, Check, RotateCcw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
// import ExerciseNavBar from '../Navigation/ExerciseNavBar'; // Removed unused import
import courseAPI from '../../api/courseAPI';
import { useSpeechSynthesis } from '@/core/speech/useSpeechSynthesis';
import { useSpeechRecognition } from '@/core/speech/useSpeechRecognition';
import { BaseExerciseWrapper } from './shared/BaseExerciseWrapper';
import { useMaintenanceAwareData } from '../../hooks/useMaintenanceAwareData';
import { LessonCompletionModal } from '../shared/LessonCompletionModal';

interface VocabularyItem {
  id: string;
  word: string;
  word_en?: string;
  word_fr?: string;
  word_es?: string;
  word_nl?: string;
  pronunciation?: string;
  example_sentence?: string;
  example_sentence_en?: string;
  example_sentence_fr?: string;
  example_sentence_es?: string;
  example_sentence_nl?: string;
}

// interface SpeakingExerciseData {
//   vocabulary_items: VocabularyItem[];
//   title: string;
//   instructions: string;
// } // Removed unused interface

interface SpeakingWrapperProps {
  lessonId: string;
  language?: string;
  unitId?: string;
  onComplete?: () => void;
  progressIndicator?: {
    currentStep: number;
    totalSteps: number;
    contentType: string;
    lessonId: string;
    unitId?: string;
    lessonTitle: string;
  };
}

export const ModernSpeakingWrapper: React.FC<SpeakingWrapperProps> = ({
  lessonId,
  // language = 'fr', // Removed unused parameter
  unitId,
  onComplete
  // progressIndicator // Removed unused prop
}) => {
  const router = useRouter();
  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  const [userRecording, setUserRecording] = useState<string>('');
  const [completedItems, setCompletedItems] = useState<Set<number>>(new Set());
  const [isRecording, setIsRecording] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  // const [practiceMode, setPracticeMode] = useState<'listen' | 'speak'>('speak'); // Removed unused state

  // Create a data fetcher for speaking exercise
  const fetchSpeakingData = useCallback(async (fetchLessonId: string | number) => {
    console.log(`[ModernSpeakingWrapper] Fetching speaking exercise for lesson: ${fetchLessonId}`);
    
    const response = await courseAPI.getSpeakingExercise(fetchLessonId);
    console.log('[ModernSpeakingWrapper] Speaking exercise response:', response);
    
    if (response?.data?.vocabulary_items?.length > 0) {
      return response.data;
    } else {
      console.log('[ModernSpeakingWrapper] No speaking exercise found, triggering maintenance');
      throw new Error('MAINTENANCE: No speaking exercise content found for this lesson');
    }
  }, []);

  // Use the maintenance-aware data hook
  const { data: exerciseData, loading, error } = useMaintenanceAwareData({
    lessonId,
    contentType: 'speaking',
    fetchFunction: fetchSpeakingData
  });

  // Speech hooks
  const { speak, isSpeaking } = useSpeechSynthesis('fr'); // Fixed language parameter
  const { 
    transcript, 
    isRecording: isListening, 
    startRecording: startListening, 
    stopRecording: stopListening, 
    error: speechRecognitionError,
    resetTranscript
  } = useSpeechRecognition({ language: language === 'fr' ? 'fr-FR' : 'en-US' });
  
  const speechRecognitionSupported = !speechRecognitionError;

  // Update recording state when speech recognition transcript changes
  React.useEffect(() => {
    if (transcript) {
      setUserRecording(transcript);
    }
  }, [transcript]);

  const currentItem = exerciseData?.vocabulary_items[currentItemIndex];
  // Calculate progress including current item if it's the last one
  const totalItems = exerciseData?.vocabulary_items.length || 0;
  const completedCount = completedItems.size;
  const isLastItem = currentItemIndex === totalItems - 1;
  const progress = totalItems > 0 ? ((completedCount + (isLastItem ? 1 : 0)) / totalItems) * 100 : 0;

  // Helper functions to get the correct word and example based on language
  const getWordByLanguage = (item: VocabularyItem) => {
    switch (language) {
      case 'en': return item.word_en || item.word;
      case 'fr': return item.word_fr || item.word;
      case 'es': return item.word_es || item.word;
      case 'nl': return item.word_nl || item.word;
      default: return item.word;
    }
  };

  const getExampleByLanguage = (item: VocabularyItem) => {
    switch (language) {
      case 'en': return item.example_sentence_en || item.example_sentence;
      case 'fr': return item.example_sentence_fr || item.example_sentence;
      case 'es': return item.example_sentence_es || item.example_sentence;
      case 'nl': return item.example_sentence_nl || item.example_sentence;
      default: return item.example_sentence;
    }
  };

  const getNativeTranslation = (item: VocabularyItem) => {
    // Return English translation if current language is not English, otherwise return French
    if (language === 'en') {
      return item.word_fr || item.word;
    }
    return item.word_en || item.word;
  };

  const playTargetAudio = () => {
    if (currentItem) {
      const wordToSpeak = getWordByLanguage(currentItem);
      speak(wordToSpeak);
    }
  };

  const playExampleSentence = () => {
    if (currentItem) {
      const exampleToSpeak = getExampleByLanguage(currentItem);
      if (exampleToSpeak) {
        speak(exampleToSpeak);
      }
    }
  };

  const startRecording = async () => {
    setUserRecording('');
    setShowFeedback(false);
    resetTranscript();
    setIsRecording(true);
    startListening();
  };

  // Function to check if pronunciation is correct
  const checkPronunciation = (spokenText: string, expectedWord: string) => {
    const spoken = spokenText.toLowerCase().trim();
    const expected = expectedWord.toLowerCase().trim();
    
    // Simple similarity check - you can make this more sophisticated
    const similarity = calculateSimilarity(spoken, expected);
    return similarity > 0.6; // 60% similarity threshold
  };

  // Simple similarity calculation (Levenshtein distance based)
  const calculateSimilarity = (str1: string, str2: string) => {
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1;
    
    const distance = levenshteinDistance(longer, shorter);
    return (longer.length - distance) / longer.length;
  };

  // Levenshtein distance calculation
  const levenshteinDistance = (str1: string, str2: string) => {
    const matrix = [];
    
    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i];
    }
    
    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j;
    }
    
    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    
    return matrix[str2.length][str1.length];
  };

  const [pronunciationResult, setPronunciationResult] = useState<'correct' | 'incorrect' | null>(null);
  const [showCompletionModal, setShowCompletionModal] = useState(false);

  // Function to play success sound
  const playSuccessSound = () => {
    try {
      const audio = new Audio('/success.mp3');
      audio.volume = 0.5; // Set volume to 50%
      audio.play().catch(error => {
        console.log('Could not play success sound:', error);
      });
    } catch (error) {
      console.log('Error creating audio:', error);
    }
  };

  // Function to play fail sound
  const playFailSound = () => {
    try {
      const audio = new Audio('/fail.mp3');
      audio.volume = 0.5; // Set volume to 50%
      audio.play().catch(error => {
        console.log('Could not play fail sound:', error);
      });
    } catch (error) {
      console.log('Error creating audio:', error);
    }
  };

  const stopRecording = async () => {
    setIsRecording(false);
    stopListening();
    if (transcript.trim() && currentItem) {
      const expectedWord = getWordByLanguage(currentItem);
      const isCorrect = checkPronunciation(transcript, expectedWord);
      setPronunciationResult(isCorrect ? 'correct' : 'incorrect');
      setShowFeedback(true);
      
      // Play appropriate sound based on pronunciation result
      if (isCorrect) {
        playSuccessSound();
      } else {
        playFailSound();
      }
    }
  };

  const markAsCompleted = () => {
    const newCompleted = new Set(completedItems);
    newCompleted.add(currentItemIndex);
    setCompletedItems(newCompleted);
    setShowFeedback(false);
    setUserRecording('');
    setPronunciationResult(null);
    resetTranscript();
    
    // Move to next item or complete the exercise
    if (currentItemIndex < (exerciseData?.vocabulary_items.length || 0) - 1) {
      setCurrentItemIndex(currentItemIndex + 1);
    } else {
      // All items completed - show completion modal
      setShowCompletionModal(true);
    }
  };

  const retryCurrentItem = () => {
    setUserRecording('');
    setShowFeedback(false);
    setPronunciationResult(null);
    resetTranscript();
  };

  const goToNextItem = () => {
    if (currentItemIndex < (exerciseData?.vocabulary_items.length || 0) - 1) {
      setCurrentItemIndex(currentItemIndex + 1);
      setUserRecording('');
      setShowFeedback(false);
      setPronunciationResult(null);
      resetTranscript();
    }
  };

  const goToPreviousItem = () => {
    if (currentItemIndex > 0) {
      setCurrentItemIndex(currentItemIndex - 1);
      setUserRecording('');
      setShowFeedback(false);
      setPronunciationResult(null);
      resetTranscript();
    }
  };

  const renderSpeakingContent = () => {
    if (!exerciseData || !currentItem) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <Card className="w-full max-w-md">
            <CardContent className="p-6">
              <div className="text-center">
                <p className="text-gray-600 dark:text-gray-300">Aucun contenu d&apos;exercice trouvé.</p>
                <Button onClick={() => router.push('/learning')} variant="outline" className="mt-4">
                  Retour à l&apos;apprentissage
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    const isItemCompleted = completedItems.has(currentItemIndex);
    const allItemsCompleted = completedItems.size === exerciseData.vocabulary_items.length;

    return (
      <div className="w-full max-w-2xl mx-auto">
        {/* Main Exercise Card */}
        <Card className="w-full">
          <CardHeader>
            {/* Compact progress info */}
            <div className="text-center text-xs text-gray-500 mb-2 space-y-1">
              <div className="flex items-center justify-center gap-2">
                <span>Mot {currentItemIndex + 1}/{exerciseData.vocabulary_items.length}</span>
                <Progress value={progress} className="w-16 h-1" />
                <span>{Math.round(progress)}%</span>
              </div>
            </div>
            <CardTitle className="flex items-center justify-between">
              <span>Prononciation</span>
              {isItemCompleted && (
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  <Check className="h-4 w-4 mr-1" />
                  Complété
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          
          <CardContent className="space-y-2 pb-4">
            {/* Current Word Display */}
            <div className="text-center p-3 border-2 border-blue-200 dark:border-blue-700 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 shadow-lg">
              <motion.div
                key={currentItem.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="text-3xl font-black text-blue-900 dark:text-blue-100 mb-2 tracking-wide">
                  {getWordByLanguage(currentItem)}
                </h2>
                <p className="text-lg font-semibold text-blue-700 dark:text-blue-300 mb-2">
                  {getNativeTranslation(currentItem)}
                </p>
                {currentItem.pronunciation && (
                  <p className="text-sm text-blue-600 dark:text-blue-400 font-mono bg-white dark:bg-blue-800 px-2 py-1 rounded inline-block shadow-sm border border-blue-200 dark:border-blue-600">
                    [{currentItem.pronunciation}]
                  </p>
                )}
              </motion.div>
            </div>

            {/* Instructions */}
            <div className="text-center">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Prononcez le mot ci-dessus
              </p>
              <div className="flex justify-center gap-2">
                <Button
                  onClick={playTargetAudio}
                  disabled={isSpeaking}
                  variant="outline"
                  size="sm"
                >
                  <Volume2 className="h-3 w-3 mr-1" />
                  Écouter
                </Button>
                {getExampleByLanguage(currentItem) && (
                  <Button
                    onClick={playExampleSentence}
                    disabled={isSpeaking}
                    variant="outline"
                    size="sm"
                  >
                    <Volume2 className="h-3 w-3 mr-1" />
                    Exemple
                  </Button>
                )}
              </div>
            </div>

            {/* Example Sentence Display */}
            {getExampleByLanguage(currentItem) && (
              <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-700 dark:text-gray-300 text-center">
                  <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Exemple : </span>
                  <span className="italic">{getExampleByLanguage(currentItem)}</span>
                </p>
              </div>
            )}

            {/* Speaking Practice */}
            <div className="space-y-2">
              {!speechRecognitionSupported ? (
                <Alert>
                  <AlertDescription>
                    La reconnaissance vocale n&apos;est pas supportée par votre navigateur.
                  </AlertDescription>
                </Alert>
              ) : (
                <>
                  <div className="text-center">
                    <Button
                      onClick={isRecording ? stopRecording : startRecording}
                      disabled={isListening && !isRecording}
                      variant={isRecording ? "destructive" : "default"}
                      size="default"
                      className="mb-2"
                    >
                      {isRecording ? (
                        <>
                          <MicOff className="h-4 w-4 mr-2" />
                          Arrêter
                        </>
                      ) : (
                        <>
                          <Mic className="h-4 w-4 mr-2" />
                          Enregistrer
                        </>
                      )}
                    </Button>
                    
                    {isRecording && (
                      <div className="flex items-center justify-center gap-2 text-red-600 text-xs">
                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                        <span>En cours...</span>
                      </div>
                    )}
                  </div>

                  {userRecording && (
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <p className="text-xs text-gray-600 dark:text-gray-300 mb-1">
                        <strong>Votre prononciation:</strong>
                      </p>
                      <p className="text-sm">{userRecording}</p>
                    </div>
                  )}

                  {showFeedback && userRecording && pronunciationResult && (
                    <div className={`p-3 rounded-lg border text-center text-sm ${
                      pronunciationResult === 'correct' 
                        ? 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200'
                        : 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200'
                    }`}>
                      {pronunciationResult === 'correct' ? (
                        <p>✓ Bonne prononciation !</p>
                      ) : (
                        <div>
                          <p>❌ Prononciation incorrecte</p>
                          <p className="text-xs mt-1">Attendu: &quot;{getWordByLanguage(currentItem)}&quot;</p>
                          <p className="text-xs">Prononcé: &quot;{userRecording}&quot;</p>
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>

              {/* Action Buttons */}
              <div className="flex justify-between items-center pt-2 border-t">
                <Button
                  onClick={goToPreviousItem}
                  disabled={currentItemIndex === 0}
                  variant="outline"
                >
                  Précédent
                </Button>

                <div className="flex gap-2">
                  <Button
                    onClick={retryCurrentItem}
                    variant="outline"
                    size="sm"
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Recommencer
                  </Button>
                  
                  {showFeedback && userRecording && pronunciationResult === 'correct' ? (
                    <Button onClick={markAsCompleted}>
                      <Check className="h-4 w-4 mr-2" />
                      {currentItemIndex === exerciseData.vocabulary_items.length - 1 ? 'Terminer' : 'Suivant'}
                    </Button>
                  ) : (
                    <Button
                      onClick={goToNextItem}
                      disabled={currentItemIndex === exerciseData.vocabulary_items.length - 1}
                      variant="outline"
                    >
                      Passer
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Completion Message */}
          <AnimatePresence>
            {allItemsCompleted && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="mt-6"
              >
                <Card className="max-w-md mx-auto bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                  <CardContent className="p-6 text-center">
                    <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Check className="h-8 w-8 text-green-600 dark:text-green-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 mb-2">
                      Exercice terminé !
                    </h3>
                    <p className="text-green-600 dark:text-green-300 mb-4">
                      Félicitations ! Vous avez pratiqué tous les mots de prononciation.
                    </p>
                    <Button onClick={onComplete} className="bg-green-600 hover:bg-green-700">
                      Continuer
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
      </div>
    );
  };

  return (
    <>
      <BaseExerciseWrapper
        unitId={unitId}
        loading={loading}
        error={error}
        onBack={onComplete}
      >
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          {renderSpeakingContent()}
        </div>
      </BaseExerciseWrapper>

      <LessonCompletionModal
        show={showCompletionModal}
        title="Exercice terminé !"
        completionMessage="Félicitations ! Vous avez terminé tous les exercices de prononciation."
        score={`${completedItems.size}/${exerciseData?.vocabulary_items.length || 0}`}
        type="exercise"
        onComplete={() => {
          setShowCompletionModal(false);
          onComplete?.();
        }}
      />
    </>
  );
};