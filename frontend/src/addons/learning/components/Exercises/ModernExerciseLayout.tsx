'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  MessageSquare, 
  Shuffle, 
  PenTool,
  Mic,
  ArrowLeft,
  RotateCcw,
  Trophy,
  Sparkles,
  ChevronRight,
  Home
} from 'lucide-react';
import { useRouter } from 'next/navigation';

interface ModernExerciseLayoutProps {
  children: React.ReactNode;
  title: string;
  exerciseType: 'vocabulary' | 'theory' | 'matching' | 'grammar' | 'speaking';
  currentStep: number;
  totalSteps: number;
  progress?: number;
  onReset?: () => void;
  showCelebration?: boolean;
  unitTitle?: string;
  description?: string;
}

const exerciseIcons = {
  vocabulary: BookOpen,
  theory: MessageSquare,
  matching: Shuffle,
  grammar: PenTool,
  speaking: Mic
};

const exerciseColors = {
  vocabulary: 'from-blue-500 to-blue-600',
  theory: 'from-green-500 to-green-600',
  matching: 'from-purple-500 to-purple-600',
  grammar: 'from-orange-500 to-orange-600',
  speaking: 'from-red-500 to-red-600'
};

const ModernExerciseLayout: React.FC<ModernExerciseLayoutProps> = ({
  children,
  title,
  exerciseType,
  currentStep,
  totalSteps,
  progress,
  onReset,
  showCelebration = false,
  unitTitle,
  description
}) => {
  const router = useRouter();
  const IconComponent = exerciseIcons[exerciseType];
  const gradientClass = exerciseColors[exerciseType];
  const calculatedProgress = progress !== undefined ? progress : (currentStep / totalSteps) * 100;

  const handleBack = () => {
    router.back();
  };

  const handleHome = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="sticky top-0 z-50 bg-white border-b shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Left side - Back button and breadcrumb */}
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBack}
                className="flex items-center gap-1"
              >
                <ArrowLeft className="w-4 h-4" />
                Retour
              </Button>
              
              {unitTitle && (
                <>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600 truncate max-w-32">
                    {unitTitle}
                  </span>
                </>
              )}
            </div>

            {/* Right side - Action buttons */}
            <div className="flex items-center gap-2">
              {onReset && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onReset}
                  className="flex items-center gap-1"
                >
                  <RotateCcw className="w-4 h-4" />
                  Reset
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={handleHome}
                className="flex items-center gap-1"
              >
                <Home className="w-4 h-4" />
                Accueil
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Exercise Header */}
      <div className={`bg-gradient-to-r ${gradientClass} text-white`}>
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-white/20 rounded-lg">
              <IconComponent className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h1 className="text-2xl font-bold">{title}</h1>
                <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
                  {exerciseType}
                </Badge>
              </div>
              {description && (
                <p className="text-white/90">{description}</p>
              )}
            </div>
          </div>

          {/* Progress */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span>Progression</span>
              <span>{currentStep} / {totalSteps}</span>
            </div>
            <Progress 
              value={calculatedProgress} 
              className="h-2 bg-white/20" 
            />
            <div className="text-right text-sm text-white/80">
              {Math.round(calculatedProgress)}% terminé
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {children}
        </motion.div>
      </div>

      {/* Celebration Overlay */}
      <AnimatePresence>
        {showCelebration && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.5, opacity: 0 }}
              transition={{ type: "spring", damping: 15 }}
              className="bg-white rounded-xl p-8 max-w-md mx-4 text-center shadow-2xl"
            >
              <motion.div
                animate={{ 
                  rotate: [0, 10, -10, 0],
                  scale: [1, 1.1, 1]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  repeatType: "loop"
                }}
              >
                <Trophy className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
              </motion.div>
              
              <h3 className="text-2xl font-bold text-gray-800 mb-2">
                Félicitations ! 🎉
              </h3>
              <p className="text-gray-600">
                Vous avez terminé cet exercice avec succès !
              </p>
              
              <div className="flex items-center justify-center gap-1 mt-4">
                {[...Array(5)].map((_, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <Sparkles className="w-5 h-5 text-yellow-400" />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ModernExerciseLayout;