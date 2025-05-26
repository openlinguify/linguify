'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Volume2, 
  BookOpen, 
  CheckCircle,
  Trophy,
  ArrowLeft,
  Home,
  Clock,
  Eye,
  Code,
  FileText,
  AlertTriangle,
  Lightbulb,
  AlertCircle
} from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import courseAPI from '@/addons/learning/api/courseAPI';
import { useSpeechSynthesis } from '@/core/speech/useSpeechSynthesis';
import { BaseExerciseWrapper } from './shared/BaseExerciseWrapper';
import { useMaintenanceAwareData } from '../../hooks/useMaintenanceAwareData';

interface TheoryWrapperProps {
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

interface TheoryContent {
  id: number;
  title?: Record<string, string>;
  content?: Record<string, string>;
  examples?: string[];
  using_json_format?: boolean;
  language_specific_content?: Record<string, Record<string, string>>;
  content_lesson?: {
    title: Record<string, string>;
    instruction: Record<string, string>;
  };
  // Support for old format fields
  content_en?: string;
  content_fr?: string;
  content_es?: string;
  content_nl?: string;
  explanation_en?: string;
  explanation_fr?: string;
  explanation_es?: string;
  explanation_nl?: string;
  formula_en?: string;
  formula_fr?: string;
  formula_es?: string;
  formula_nl?: string;
  example_en?: string;
  example_fr?: string;
  example_es?: string;
  example_nl?: string;
  exception_en?: string;
  exception_fr?: string;
  exception_es?: string;
  exception_nl?: string;
}

const ModernTheoryWrapper: React.FC<TheoryWrapperProps> = ({
  lessonId,
  language = 'en',
  unitId,
  onComplete,
  progressIndicator
}) => {
  const router = useRouter();
  const { speak } = useSpeechSynthesis('en');
  
  const [readingTime, setReadingTime] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [startTime] = useState(Date.now());
  const [currentTab, setCurrentTab] = useState('content');
  const [readSections, setReadSections] = useState<string[]>([]);
  const [progress, setProgress] = useState(0);

  // Create fetch function for theory data
  const fetchTheoryData = useCallback(async (fetchLessonId: string | number, language?: string) => {
    console.log(`[ModernTheoryWrapper] Fetching Theory data for lesson: ${fetchLessonId}`);
    
    const response = await courseAPI.getTheoryContent(fetchLessonId, language);
    console.log('[ModernTheoryWrapper] Raw API response:', response);
    
    // Handle different response structures
    if (response && Array.isArray(response) && response.length > 0) {
      return response[0];
    } else if (response && !Array.isArray(response)) {
      return response;
    } else {
      throw new Error('Aucun contenu théorique trouvé pour cette leçon');
    }
  }, []);

  // Use maintenance-aware data fetching
  const {
    data: theoryContent,
    loading,
    error,
    isMaintenance,
    contentTypeName,
    retry
  } = useMaintenanceAwareData<TheoryContent>({
    lessonId,
    language,
    contentType: 'theory',
    fetchFunction: fetchTheoryData
  });

  // Timer for reading time
  useEffect(() => {
    const timer = setInterval(() => {
      setReadingTime(Date.now() - startTime);
    }, 1000);

    return () => clearInterval(timer);
  }, [startTime]);

  // Helper to get content in current language (same as original TheoryContent)
  const getLanguageContent = (field: string, defaultValue: string = ''): string => {
    if (!theoryContent) return defaultValue;

    // Try using new JSON format first
    if (theoryContent.using_json_format &&
      theoryContent.language_specific_content &&
      theoryContent.language_specific_content[language]) {
      return theoryContent.language_specific_content[language][field] || defaultValue;
    }

    // Fall back to old format if needed
    const oldFormatField = `${field}_${language}` as keyof TheoryContent;
    return (theoryContent[oldFormatField] as string) || defaultValue;
  };

  const getContentByLanguage = (content: Record<string, string> | null | undefined): string => {
    if (!content || typeof content !== 'object') return '';
    return content[language] || content['en'] || Object.values(content)[0] || '';
  };

  const handleSpeak = (text: string) => {
    if (text) {
      speak(text);
    }
  };

  // Determine available sections
  const getAvailableSections = () => {
    if (!theoryContent) return ['content'];

    const sections = ['content'];

    // Add formula section if available
    if (getLanguageContent('formula')) sections.push('formula');

    // Add examples section if available
    if (getLanguageContent('example')) sections.push('examples');

    // Add exceptions section if available
    if (getLanguageContent('exception')) sections.push('exceptions');

    return sections;
  };

  // Mark a section as read
  const markAsRead = (section: string) => {
    setReadSections(prev => {
      if (!prev.includes(section)) {
        return [...prev, section];
      }
      return prev;
    });
  };

  // Update progress when sections are read
  useEffect(() => {
    if (readSections.length > 0 && theoryContent) {
      const availableSections = getAvailableSections();
      const newProgress = Math.round((readSections.length / availableSections.length) * 100);
      setProgress(newProgress);

      // Set completed if all sections are read
      if (newProgress === 100 && !isComplete) {
        setIsComplete(true);
      }
    }
  }, [readSections, theoryContent, isComplete]);

  const handleComplete = () => {
    setIsComplete(true);
    setTimeout(() => {
      onComplete?.();
    }, 1000);
  };

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    return minutes > 0 ? `${minutes}m ${seconds % 60}s` : `${seconds}s`;
  };

  // Create renderTheoryContent function
  const renderTheoryContent = () => {
    if (!theoryContent) return null;

    const title = getContentByLanguage(theoryContent?.content_lesson?.title) || getContentByLanguage(theoryContent?.title);
    const availableSections = getAvailableSections();

    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
        {/* Exercise Header */}
        <div className="bg-gradient-to-r from-green-500 to-green-600 text-white">
          <div className="max-w-4xl mx-auto px-4 py-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-white/20 rounded-lg">
                <BookOpen className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h1 className="text-2xl font-bold">Théorie</h1>
                  <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
                    Lecture
                  </Badge>
                </div>
                <p className="text-white/90">Apprenez les concepts fondamentaux</p>
              </div>
            </div>

            {/* Progress */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span>Temps de lecture</span>
                <span>{formatTime(readingTime)}</span>
              </div>
              <Progress value={isComplete ? 100 : 50} className="h-2 bg-white/20" />
            </div>
          </div>
        </div>
        {/* Main Content */}
        <div className="max-w-4xl mx-auto px-4 py-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
          >
            {/* Title Card */}
            <Card className="border-green-200">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-bold text-green-600 flex items-center justify-center gap-3">
                  {title}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleSpeak(title)}
                    className="p-2"
                  >
                    <Volume2 className="w-4 h-4" />
                  </Button>
                </CardTitle>
              </CardHeader>
            </Card>

            {/* Content Card with Tabs */}
            <Card className="overflow-hidden border border-gray-100 shadow-sm">
              <div className="p-4 space-y-4">
                {/* Section tabs */}
                <Tabs defaultValue="content" value={currentTab} onValueChange={(value) => {
                  setCurrentTab(value);
                  markAsRead(value);
                }}>
                  <TabsList className="w-full grid grid-cols-4 bg-gray-50 rounded-lg p-1">
                    <TabsTrigger value="content" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md text-xs py-1">
                      <div className="flex items-center">
                        <FileText className="h-3 w-3 mr-1" />
                        <span>Contenu</span>
                        {readSections.includes('content') && (
                          <CheckCircle className="h-2 w-2 ml-1 text-green-500" />
                        )}
                      </div>
                    </TabsTrigger>

                    <TabsTrigger value="formula" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md text-xs py-1">
                      <div className="flex items-center">
                        <Code className="h-3 w-3 mr-1" />
                        <span>Formule</span>
                        {readSections.includes('formula') && (
                          <CheckCircle className="h-2 w-2 ml-1 text-green-500" />
                        )}
                      </div>
                    </TabsTrigger>

                    <TabsTrigger value="examples" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md text-xs py-1">
                      <div className="flex items-center">
                        <BookOpen className="h-3 w-3 mr-1" />
                        <span>Exemples</span>
                        {readSections.includes('examples') && (
                          <CheckCircle className="h-2 w-2 ml-1 text-green-500" />
                        )}
                      </div>
                    </TabsTrigger>

                    <TabsTrigger value="exceptions" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md text-xs py-1">
                      <div className="flex items-center">
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        <span>Exceptions</span>
                        {readSections.includes('exceptions') && (
                          <CheckCircle className="h-2 w-2 ml-1 text-green-500" />
                        )}
                      </div>
                    </TabsTrigger>
                  </TabsList>

                  <AnimatePresence mode="wait">
                    <motion.div
                      key={currentTab}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.3 }}
                      className="mt-3"
                    >
                      <TabsContent value="content" className="focus:outline-none mt-0">
                        <div className="bg-white rounded-lg overflow-hidden">
                          {/* Title */}
                          <div className="border-b border-gray-100 p-3 flex justify-between items-center">
                            <h2 className="text-sm font-semibold text-gray-800">
                              Règle grammaticale : {title}
                            </h2>
                            <button
                              onClick={() => handleSpeak(getLanguageContent('content'))}
                              className="text-green-600 hover:text-green-800 focus:outline-none"
                              aria-label="Écouter le contenu"
                            >
                              <Volume2 className="h-3 w-3" />
                            </button>
                          </div>

                          {/* Content */}
                          <div className="p-3">
                            {getLanguageContent('content') ? (
                              <div className="space-y-2">
                                {getLanguageContent('content')
                                  .split(/\r?\n/)
                                  .filter(line => line.trim() !== '')
                                  .map((line: string, index: number) => (
                                    <p key={index} className="text-sm text-gray-700">{line}</p>
                                  ))}
                              </div>
                            ) : (
                              <p className="text-xs text-gray-500 italic">Aucun contenu disponible</p>
                            )}
                          </div>

                          {/* Explanation */}
                          <div className="bg-gray-50 p-3 mt-2 rounded-lg">
                            <h3 className="text-sm font-semibold mb-2">Explication</h3>
                            {getLanguageContent('explanation') ? (
                              <div className="space-y-2">
                                {getLanguageContent('explanation')
                                  .split(/\r?\n/)
                                  .filter(line => line.trim() !== '')
                                  .map((line: string, index: number) => (
                                    <p key={index} className="text-xs text-gray-700">{line}</p>
                                  ))}
                              </div>
                            ) : (
                              <p className="text-xs text-gray-500 italic">Aucune explication disponible</p>
                            )}
                          </div>
                        </div>
                      </TabsContent>

                      <TabsContent value="formula" className="focus:outline-none mt-0">
                        <div className="bg-white rounded-lg overflow-hidden">
                          <div className="border-b border-gray-100 p-3 flex justify-between items-center">
                            <h2 className="text-sm font-semibold text-gray-800">Formule</h2>
                            <button
                              onClick={() => handleSpeak(getLanguageContent('formula'))}
                              className="text-green-600 hover:text-green-800 focus:outline-none"
                            >
                              <Volume2 className="h-3 w-3" />
                            </button>
                          </div>
                          <div className="p-3">
                            {getLanguageContent('formula') ? (
                              <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                                {getLanguageContent('formula')
                                  .split(/\r?\n/)
                                  .filter(line => line.trim() !== '')
                                  .map((line: string, index: number) => (
                                    <p key={index} className="text-sm text-gray-800 mb-1">{line}</p>
                                  ))}
                              </div>
                            ) : (
                              <Alert className="p-2">
                                <AlertCircle className="h-3 w-3" />
                                <AlertDescription className="text-xs">Aucune formule disponible pour ce sujet.</AlertDescription>
                              </Alert>
                            )}
                          </div>
                        </div>
                      </TabsContent>

                      <TabsContent value="examples" className="focus:outline-none mt-0">
                        <div className="bg-white rounded-lg overflow-hidden">
                          <div className="border-b border-gray-100 p-3 flex justify-between items-center">
                            <h2 className="text-sm font-semibold text-gray-800">Exemples</h2>
                            <button
                              onClick={() => handleSpeak(getLanguageContent('example'))}
                              className="text-green-600 hover:text-green-800 focus:outline-none"
                            >
                              <Volume2 className="h-3 w-3" />
                            </button>
                          </div>
                          <div className="p-3">
                            {getLanguageContent('example') ? (
                              <div className="p-3 bg-green-50 rounded-lg border border-green-100">
                                {getLanguageContent('example')
                                  .split(/\r?\n/)
                                  .filter(line => line.trim() !== '')
                                  .map((line: string, index: number) => (
                                    <p key={index} className="text-sm text-gray-800 mb-1">{line}</p>
                                  ))}
                              </div>
                            ) : (
                              <Alert className="p-2">
                                <AlertCircle className="h-3 w-3" />
                                <AlertDescription className="text-xs">Aucun exemple disponible pour ce sujet.</AlertDescription>
                              </Alert>
                            )}
                          </div>
                        </div>
                      </TabsContent>

                      <TabsContent value="exceptions" className="focus:outline-none mt-0">
                        <div className="bg-white rounded-lg overflow-hidden">
                          <div className="border-b border-gray-100 p-3 flex justify-between items-center">
                            <h2 className="text-sm font-semibold text-gray-800">Exceptions</h2>
                            <button
                              onClick={() => handleSpeak(getLanguageContent('exception'))}
                              className="text-green-600 hover:text-green-800 focus:outline-none"
                            >
                              <Volume2 className="h-3 w-3" />
                            </button>
                          </div>
                          <div className="p-3">
                            {getLanguageContent('exception') ? (
                              <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
                                {getLanguageContent('exception')
                                  .split(/\r?\n/)
                                  .filter(line => line.trim() !== '')
                                  .map((line: string, index: number) => (
                                    <p key={index} className="text-sm text-gray-800 mb-1">{line}</p>
                                  ))}
                              </div>
                            ) : (
                              <Alert className="p-2">
                                <AlertCircle className="h-3 w-3" />
                                <AlertDescription className="text-xs">Aucune exception notée pour ce sujet.</AlertDescription>
                              </Alert>
                            )}
                          </div>
                        </div>
                      </TabsContent>
                    </motion.div>
                  </AnimatePresence>
                </Tabs>
              </div>
            </Card>

            {/* Completion */}
            {!isComplete ? (
              <div className="text-center">
                <Button
                  size="lg"
                  onClick={handleComplete}
                  className="px-8 bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle className="w-5 h-5 mr-2" />
                  J'ai terminé la lecture
                </Button>
              </div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center p-6 bg-green-50 border border-green-200 rounded-lg"
              >
                <Trophy className="w-12 h-12 text-green-500 mx-auto mb-3" />
                <h3 className="text-lg font-semibold text-green-800 mb-2">Excellent travail !</h3>
                <p className="text-green-700">
                  Vous avez terminé cette leçon de théorie en {formatTime(readingTime)}.
                </p>
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    );
  };

  return (
    <BaseExerciseWrapper
      unitId={unitId}
      loading={loading}
      error={error}
      isMaintenance={isMaintenance}
      contentTypeName={contentTypeName}
      lessonId={lessonId}
      onRetry={retry}
      onBack={() => router.back()}
      className="bg-gradient-to-br from-green-50 to-emerald-100"
    >
      {renderTheoryContent()}
    </BaseExerciseWrapper>
  );
};

export default ModernTheoryWrapper;