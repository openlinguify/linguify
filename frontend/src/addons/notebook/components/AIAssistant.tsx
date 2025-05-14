import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Bot,
  BookTranslation,
  Languages,
  Mic,
  Volume2,
  CheckCircle,
  Sparkles,
  AlertCircle,
  Loader2,
  Plus,
  MessageSquare,
  X,
  Edit,
  RefreshCw,
  SendHorizontal,
  LucideIcon,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog';
import { aiHelperAPI } from '../api/aiHelperAPI';
import LoadingIndicator from './LoadingIndicator';

interface AIAssistantProps {
  noteContent: string;
  noteLanguage?: string;
  userNativeLanguage?: string;
  onApplyTranslation?: (translation: string) => void;
  onAddExampleSentence?: (sentence: string) => void;
  onApplyCorrection?: (correctedText: string) => void;
  onUpdatePronunciation?: (pronunciation: string) => void;
  className?: string;
}

interface FeatureCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  onClick: () => void;
  disabled?: boolean;
}

const LANGUAGE_NAMES: Record<string, string> = {
  'en': 'English',
  'fr': 'French',
  'es': 'Spanish',
  'de': 'German',
  'it': 'Italian',
  'pt': 'Portuguese',
  'ja': 'Japanese',
  'zh': 'Chinese',
  'ru': 'Russian',
  'ar': 'Arabic',
  'hi': 'Hindi',
  'ko': 'Korean',
};

const FeatureCard: React.FC<FeatureCardProps> = ({ 
  title, 
  description, 
  icon: Icon, 
  onClick,
  disabled = false
}) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card 
        className={`cursor-pointer transition-all ${disabled ? 'opacity-60' : 'hover:shadow-md'}`}
        onClick={disabled ? undefined : onClick}
      >
        <CardHeader className="p-4 pb-2">
          <div className="flex justify-between items-center">
            <CardTitle className="text-sm font-medium">{title}</CardTitle>
            <Icon className="h-4 w-4 text-indigo-500" />
          </div>
        </CardHeader>
        <CardContent className="p-4 pt-0">
          <CardDescription className="text-xs">
            {description}
          </CardDescription>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const AIAssistant: React.FC<AIAssistantProps> = ({
  noteContent,
  noteLanguage = 'en',
  userNativeLanguage = 'en',
  onApplyTranslation,
  onAddExampleSentence,
  onApplyCorrection,
  onUpdatePronunciation,
  className = '',
}) => {
  const [isAvailable, setIsAvailable] = useState<boolean | null>(null);
  const [activeTab, setActiveTab] = useState('features');
  const [showDialog, setShowDialog] = useState(false);
  
  // Translation state
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationResult, setTranslationResult] = useState<string | null>(null);
  const [translationError, setTranslationError] = useState<string | null>(null);
  
  // Pronunciation state
  const [isPronouncing, setIsPronouncing] = useState(false);
  const [pronunciationResult, setPronunciationResult] = useState<{
    pronunciation: string;
    phonetic: string;
    audio_url?: string;
  } | null>(null);
  const [pronunciationError, setPronunciationError] = useState<string | null>(null);
  
  // Example sentences state
  const [isGeneratingExamples, setIsGeneratingExamples] = useState(false);
  const [exampleWord, setExampleWord] = useState('');
  const [exampleSentences, setExampleSentences] = useState<string[]>([]);
  const [exampleSentencesError, setExampleSentencesError] = useState<string | null>(null);
  
  // Grammar check state
  const [isCheckingGrammar, setIsCheckingGrammar] = useState(false);
  const [grammarResult, setGrammarResult] = useState<{
    corrected_text: string;
    corrections: {
      original: string;
      corrected: string;
      explanation: string;
      position: {
        start: number;
        end: number;
      };
    }[];
  } | null>(null);
  const [grammarError, setGrammarError] = useState<string | null>(null);
  
  // Check if AI features are available
  useEffect(() => {
    let isMounted = true;
    
    const checkAvailability = async () => {
      try {
        // If the component is unmounted before the async operation completes,
        // we shouldn't update the state
        const available = await aiHelperAPI.checkAvailability();
        if (isMounted) {
          console.log('AI service availability check result:', available);
          setIsAvailable(available);
        }
      } catch (error) {
        if (isMounted) {
          console.error('Error checking AI availability:', error);
          // Even if there's an error checking availability, we'll default to false
          // but not crash the component
          setIsAvailable(false);
        }
      }
    };
    
    // Start with a small delay to prevent rapid API calls during component mounting/unmounting cycles
    const timeoutId = setTimeout(() => {
      checkAvailability();
    }, 100);
    
    // Return cleanup function to prevent memory leaks and state updates after unmount
    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
    };
  }, []);
  
  // Clear active feature state when the dialog is closed
  useEffect(() => {
    if (!showDialog) {
      setActiveTab('features');
      setTranslationResult(null);
      setTranslationError(null);
      setPronunciationResult(null);
      setPronunciationError(null);
      setExampleSentences([]);
      setExampleSentencesError(null);
      setGrammarResult(null);
      setGrammarError(null);
    }
  }, [showDialog]);
  
  // Translate the note content
  const handleTranslate = async () => {
    if (!noteContent.trim()) {
      setTranslationError('No content to translate');
      return;
    }
    
    try {
      setIsTranslating(true);
      setTranslationError(null);
      setTranslationResult(null);
      
      const result = await aiHelperAPI.translate({
        text: noteContent,
        sourceLanguage: noteLanguage,
        targetLanguage: userNativeLanguage !== noteLanguage ? userNativeLanguage : 'en',
      });
      
      setTranslationResult(result.translation);
    } catch (error) {
      console.error('Translation error:', error);
      setTranslationError(
        error instanceof Error ? error.message : 'Translation failed'
      );
    } finally {
      setIsTranslating(false);
    }
  };
  
  // Get pronunciation for selected text or first sentence
  const handleGetPronunciation = async () => {
    // Use the first sentence if no content is selected
    let textToProcess = noteContent.split('.')[0].trim();
    
    if (!textToProcess) {
      setPronunciationError('No content to pronounce');
      return;
    }
    
    try {
      setIsPronouncing(true);
      setPronunciationError(null);
      setPronunciationResult(null);
      
      const result = await aiHelperAPI.getPronunciation({
        text: textToProcess,
        language: noteLanguage,
      });
      
      setPronunciationResult(result);
    } catch (error) {
      console.error('Pronunciation error:', error);
      setPronunciationError(
        error instanceof Error ? error.message : 'Pronunciation request failed'
      );
    } finally {
      setIsPronouncing(false);
    }
  };
  
  // Generate example sentences
  const handleGenerateExamples = async () => {
    if (!exampleWord.trim()) {
      setExampleSentencesError('Please enter a word or phrase');
      return;
    }
    
    try {
      setIsGeneratingExamples(true);
      setExampleSentencesError(null);
      setExampleSentences([]);
      
      const result = await aiHelperAPI.getExampleSentences({
        word: exampleWord,
        language: noteLanguage,
        count: 3,
      });
      
      setExampleSentences(result.sentences);
    } catch (error) {
      console.error('Example sentences error:', error);
      setExampleSentencesError(
        error instanceof Error ? error.message : 'Failed to generate example sentences'
      );
    } finally {
      setIsGeneratingExamples(false);
    }
  };
  
  // Check grammar
  const handleCheckGrammar = async () => {
    if (!noteContent.trim()) {
      setGrammarError('No content to check');
      return;
    }
    
    try {
      setIsCheckingGrammar(true);
      setGrammarError(null);
      setGrammarResult(null);
      
      const result = await aiHelperAPI.checkGrammar({
        text: noteContent,
        language: noteLanguage,
      });
      
      setGrammarResult(result);
    } catch (error) {
      console.error('Grammar check error:', error);
      setGrammarError(
        error instanceof Error ? error.message : 'Grammar check failed'
      );
    } finally {
      setIsCheckingGrammar(false);
    }
  };
  
  // Apply translation to the note
  const handleApplyTranslation = () => {
    if (translationResult && onApplyTranslation) {
      onApplyTranslation(translationResult);
      setShowDialog(false);
    }
  };
  
  // Add example sentence to the note
  const handleAddExampleSentence = (sentence: string) => {
    if (onAddExampleSentence) {
      onAddExampleSentence(sentence);
    }
  };
  
  // Apply grammar corrections
  const handleApplyCorrection = () => {
    if (grammarResult && onApplyCorrection) {
      onApplyCorrection(grammarResult.corrected_text);
      setShowDialog(false);
    }
  };
  
  // Update pronunciation in the note
  const handleUpdatePronunciation = () => {
    if (pronunciationResult && onUpdatePronunciation) {
      onUpdatePronunciation(pronunciationResult.phonetic);
      setShowDialog(false);
    }
  };
  
  // Play pronunciation audio if available
  const handlePlayAudio = () => {
    if (pronunciationResult?.audio_url) {
      const audio = new Audio(pronunciationResult.audio_url);
      audio.play();
    }
  };
  
  // Render AI features grid
  const renderFeatures = () => (
    <div className="grid grid-cols-2 gap-3 p-4">
      <FeatureCard
        title="Translation"
        description={`Translate from ${LANGUAGE_NAMES[noteLanguage] || noteLanguage} to your native language`}
        icon={BookTranslation}
        onClick={() => {
          setActiveTab('translate');
          handleTranslate();
        }}
        disabled={!isAvailable}
      />
      
      <FeatureCard
        title="Pronunciation"
        description="Get pronunciation help and audio examples"
        icon={Volume2}
        onClick={() => {
          setActiveTab('pronunciation');
          handleGetPronunciation();
        }}
        disabled={!isAvailable}
      />
      
      <FeatureCard
        title="Example Sentences"
        description="Generate example sentences for words or phrases"
        icon={MessageSquare}
        onClick={() => {
          setActiveTab('examples');
        }}
        disabled={!isAvailable}
      />
      
      <FeatureCard
        title="Grammar Check"
        description="Check grammar and get correction suggestions"
        icon={CheckCircle}
        onClick={() => {
          setActiveTab('grammar');
          handleCheckGrammar();
        }}
        disabled={!isAvailable}
      />
    </div>
  );
  
  // Render translation feature
  const renderTranslation = () => (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Translation</h3>
        <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
          {LANGUAGE_NAMES[noteLanguage] || noteLanguage} → {LANGUAGE_NAMES[userNativeLanguage] || userNativeLanguage}
        </Badge>
      </div>
      
      {isTranslating ? (
        <LoadingIndicator message="Translating..." size="small" />
      ) : translationError ? (
        <div className="text-sm text-red-500 flex items-center">
          <AlertCircle className="h-4 w-4 mr-2" />
          {translationError}
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto h-8"
            onClick={handleTranslate}
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Retry
          </Button>
        </div>
      ) : translationResult ? (
        <div className="space-y-3">
          <div className="text-sm border rounded-md p-3 bg-gray-50 dark:bg-gray-900">
            {translationResult}
          </div>
          
          <div className="flex justify-end">
            <Button
              size="sm"
              className="h-8"
              onClick={handleApplyTranslation}
            >
              <Edit className="h-4 w-4 mr-1" />
              Apply as Translation
            </Button>
          </div>
        </div>
      ) : (
        <div className="text-sm text-gray-500 dark:text-gray-400 flex flex-col items-center py-4">
          <Sparkles className="h-8 w-8 mb-2 text-indigo-500" />
          <p>Click translate to see the translation</p>
        </div>
      )}
      
      <div className="flex justify-between">
        <Button
          variant="outline"
          size="sm"
          className="h-8"
          onClick={() => setActiveTab('features')}
        >
          Back to Features
        </Button>
        
        {!translationResult && !isTranslating && (
          <Button
            size="sm"
            className="h-8"
            onClick={handleTranslate}
            disabled={isTranslating || !noteContent.trim()}
          >
            {isTranslating ? (
              <Loader2 className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <BookTranslation className="h-4 w-4 mr-1" />
            )}
            Translate
          </Button>
        )}
      </div>
    </div>
  );
  
  // Render pronunciation feature
  const renderPronunciation = () => (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Pronunciation</h3>
        <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
          {LANGUAGE_NAMES[noteLanguage] || noteLanguage}
        </Badge>
      </div>
      
      {isPronouncing ? (
        <LoadingIndicator message="Getting pronunciation..." size="small" />
      ) : pronunciationError ? (
        <div className="text-sm text-red-500 flex items-center">
          <AlertCircle className="h-4 w-4 mr-2" />
          {pronunciationError}
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto h-8"
            onClick={handleGetPronunciation}
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Retry
          </Button>
        </div>
      ) : pronunciationResult ? (
        <div className="space-y-4">
          <div className="border rounded-md p-3 bg-gray-50 dark:bg-gray-900">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-xs font-medium text-gray-500">Phonetic</h4>
              {pronunciationResult.audio_url && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={handlePlayAudio}
                >
                  <Volume2 className="h-4 w-4" />
                </Button>
              )}
            </div>
            <p className="text-sm font-mono">{pronunciationResult.phonetic}</p>
          </div>
          
          <div className="border rounded-md p-3 bg-gray-50 dark:bg-gray-900">
            <h4 className="text-xs font-medium text-gray-500 mb-2">Tips</h4>
            <p className="text-sm">{pronunciationResult.pronunciation}</p>
          </div>
          
          <div className="flex justify-end">
            <Button
              size="sm"
              className="h-8"
              onClick={handleUpdatePronunciation}
            >
              <Edit className="h-4 w-4 mr-1" />
              Add to Note
            </Button>
          </div>
        </div>
      ) : (
        <div className="text-sm text-gray-500 dark:text-gray-400 flex flex-col items-center py-4">
          <Volume2 className="h-8 w-8 mb-2 text-indigo-500" />
          <p>Get pronunciation help for your text</p>
        </div>
      )}
      
      <div className="flex justify-between">
        <Button
          variant="outline"
          size="sm"
          className="h-8"
          onClick={() => setActiveTab('features')}
        >
          Back to Features
        </Button>
        
        {!pronunciationResult && !isPronouncing && (
          <Button
            size="sm"
            className="h-8"
            onClick={handleGetPronunciation}
            disabled={isPronouncing || !noteContent.trim()}
          >
            {isPronouncing ? (
              <Loader2 className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <Volume2 className="h-4 w-4 mr-1" />
            )}
            Get Pronunciation
          </Button>
        )}
      </div>
    </div>
  );
  
  // Render example sentences feature
  const renderExampleSentences = () => (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Example Sentences</h3>
        <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
          {LANGUAGE_NAMES[noteLanguage] || noteLanguage}
        </Badge>
      </div>
      
      <div className="flex gap-2">
        <Input
          placeholder="Enter a word or phrase"
          value={exampleWord}
          onChange={(e) => setExampleWord(e.target.value)}
          className="text-sm"
        />
        <Button
          size="sm"
          className="shrink-0"
          onClick={handleGenerateExamples}
          disabled={isGeneratingExamples || !exampleWord.trim()}
        >
          {isGeneratingExamples ? (
            <Loader2 className="h-4 w-4 animate-spin mr-1" />
          ) : (
            <SendHorizontal className="h-4 w-4 mr-1" />
          )}
          Generate
        </Button>
      </div>
      
      {isGeneratingExamples ? (
        <LoadingIndicator message="Generating examples..." size="small" />
      ) : exampleSentencesError ? (
        <div className="text-sm text-red-500 flex items-center">
          <AlertCircle className="h-4 w-4 mr-2" />
          {exampleSentencesError}
        </div>
      ) : exampleSentences.length > 0 ? (
        <div className="space-y-3">
          {exampleSentences.map((sentence, index) => (
            <div 
              key={index} 
              className="border rounded-md p-3 bg-gray-50 dark:bg-gray-900 flex justify-between items-start"
            >
              <p className="text-sm">{sentence}</p>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 ml-2 shrink-0 text-green-600"
                onClick={() => handleAddExampleSentence(sentence)}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-sm text-gray-500 dark:text-gray-400 flex flex-col items-center py-4">
          <MessageSquare className="h-8 w-8 mb-2 text-indigo-500" />
          <p>Enter a word to generate example sentences</p>
        </div>
      )}
      
      <div className="flex justify-between">
        <Button
          variant="outline"
          size="sm"
          className="h-8"
          onClick={() => setActiveTab('features')}
        >
          Back to Features
        </Button>
      </div>
    </div>
  );
  
  // Render grammar check feature
  const renderGrammarCheck = () => (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Grammar Check</h3>
        <Badge className="bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
          {LANGUAGE_NAMES[noteLanguage] || noteLanguage}
        </Badge>
      </div>
      
      {isCheckingGrammar ? (
        <LoadingIndicator message="Checking grammar..." size="small" />
      ) : grammarError ? (
        <div className="text-sm text-red-500 flex items-center">
          <AlertCircle className="h-4 w-4 mr-2" />
          {grammarError}
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto h-8"
            onClick={handleCheckGrammar}
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Retry
          </Button>
        </div>
      ) : grammarResult ? (
        <div className="space-y-4">
          {grammarResult.corrections.length === 0 ? (
            <div className="flex items-center text-green-600 text-sm">
              <CheckCircle className="h-4 w-4 mr-2" />
              No grammar issues found
            </div>
          ) : (
            <>
              <div className="border rounded-md p-3 bg-gray-50 dark:bg-gray-900">
                <h4 className="text-xs font-medium text-gray-500 mb-2">Corrected Text</h4>
                <p className="text-sm">{grammarResult.corrected_text}</p>
              </div>
              
              <div>
                <h4 className="text-xs font-medium text-gray-500 mb-2">Corrections ({grammarResult.corrections.length})</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {grammarResult.corrections.map((correction, index) => (
                    <div key={index} className="border rounded-md p-2 text-xs">
                      <div className="flex gap-1 mb-1">
                        <span className="text-red-500 line-through">{correction.original}</span>
                        <span className="text-gray-500">→</span>
                        <span className="text-green-500">{correction.corrected}</span>
                      </div>
                      <p className="text-gray-600 dark:text-gray-400">{correction.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex justify-end">
                <Button
                  size="sm"
                  className="h-8"
                  onClick={handleApplyCorrection}
                >
                  <Edit className="h-4 w-4 mr-1" />
                  Apply Corrections
                </Button>
              </div>
            </>
          )}
        </div>
      ) : (
        <div className="text-sm text-gray-500 dark:text-gray-400 flex flex-col items-center py-4">
          <CheckCircle className="h-8 w-8 mb-2 text-indigo-500" />
          <p>Check your text for grammar issues</p>
        </div>
      )}
      
      <div className="flex justify-between">
        <Button
          variant="outline"
          size="sm"
          className="h-8"
          onClick={() => setActiveTab('features')}
        >
          Back to Features
        </Button>
        
        {!grammarResult && !isCheckingGrammar && (
          <Button
            size="sm"
            className="h-8"
            onClick={handleCheckGrammar}
            disabled={isCheckingGrammar || !noteContent.trim()}
          >
            {isCheckingGrammar ? (
              <Loader2 className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <CheckCircle className="h-4 w-4 mr-1" />
            )}
            Check Grammar
          </Button>
        )}
      </div>
    </div>
  );
  
  // Render content based on active tab
  const renderContent = () => {
    switch (activeTab) {
      case 'translate':
        return renderTranslation();
      case 'pronunciation':
        return renderPronunciation();
      case 'examples':
        return renderExampleSentences();
      case 'grammar':
        return renderGrammarCheck();
      default:
        return renderFeatures();
    }
  };
  
  // Loading state
  if (isAvailable === null) {
    return (
      <Button
        variant="outline"
        size="sm"
        className={`h-8 ${className}`}
        disabled
      >
        <Loader2 className="h-4 w-4 mr-1 animate-spin" />
        AI Assistant
      </Button>
    );
  }
  
  // AI not available
  if (isAvailable === false) {
    return (
      <Button
        variant="outline"
        size="sm"
        className={`h-8 ${className}`}
        disabled
      >
        <Bot className="h-4 w-4 mr-1 text-gray-400" />
        AI Unavailable
      </Button>
    );
  }
  
  return (
    <Dialog open={showDialog} onOpenChange={setShowDialog}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={`h-8 ${className}`}
        >
          <Bot className="h-4 w-4 mr-1 text-indigo-500" />
          AI Assistant
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Bot className="h-5 w-5 mr-2 text-indigo-500" />
            Language Learning Assistant
          </DialogTitle>
          <DialogDescription>
            AI-powered tools to help you learn {LANGUAGE_NAMES[noteLanguage] || noteLanguage}
          </DialogDescription>
        </DialogHeader>
        
        {renderContent()}
      </DialogContent>
    </Dialog>
  );
};

export default AIAssistant;