import React, { useEffect, useState } from 'react';
import { Progress } from '@/components/ui/progress';
import { BookOpen, CheckCircle, Clock } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface LessonProgressIndicatorProps {
  currentStep: number;
  totalSteps: number;
  lessonId?: number;
  lessonTitle?: string;
  unitId?: number;
  contentType?: string;
  isCompleted?: boolean;
  className?: string;
  showDetailsOnHover?: boolean;
  showBackButton?: boolean;
}

/**
 * Composant d'indicateur de progression persistant pour les leçons
 * Affiche une barre de progression, le titre et la position actuelle dans l'exercice
 */
const LessonProgressIndicator: React.FC<LessonProgressIndicatorProps> = ({
  currentStep,
  totalSteps,
  lessonId,
  lessonTitle,
  unitId,
  contentType,
  isCompleted = false,
  className = '',
  showDetailsOnHover = true,
  showBackButton = true
}) => {
  const router = useRouter();
  const [percentage, setPercentage] = useState<number>(0);
  const [isHovering, setIsHovering] = useState<boolean>(false);
  
  // Calculer le pourcentage de progression
  useEffect(() => {
    if (totalSteps > 0) {
      // Assurer que le pourcentage est entre 0 et 100
      const calculatedPercentage = Math.min(
        Math.max(Math.round((currentStep / totalSteps) * 100), 0),
        100
      );
      setPercentage(calculatedPercentage);
    } else if (isCompleted) {
      setPercentage(100);
    } else {
      setPercentage(0);
    }
  }, [currentStep, totalSteps, isCompleted]);
  
  // Fonction pour revenir à la liste des leçons
  const handleBackClick = () => {
    if (unitId) {
      router.push(`/learning/${unitId}`);
    } else {
      router.push('/learning');
    }
  };
  
  // Obtenir la couleur de la barre de progression en fonction du type de contenu
  const getProgressBarColor = () => {
    if (isCompleted) return 'bg-green-500';
    
    switch (contentType?.toLowerCase()) {
      case 'vocabulary':
      case 'vocabularylist':
        return '[&>div]:bg-blue-600';
      case 'matching':
        return '[&>div]:bg-purple-600';
      case 'speaking':
        return '[&>div]:bg-orange-500';
      case 'fill_blank':
        return '[&>div]:bg-emerald-500';
      case 'reordering':
        return '[&>div]:bg-pink-500';
      case 'multiple choice':
        return '[&>div]:bg-indigo-600';
      default:
        return '[&>div]:bg-gradient-to-r [&>div]:from-indigo-600 [&>div]:via-purple-600 [&>div]:to-pink-400';
    }
  };
  
  return (
    <div 
      className={`w-full p-1 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm shadow-sm border-b rounded-t-lg fixed top-0 left-0 z-40 transition-all duration-150 ${className}`}
      onMouseEnter={() => showDetailsOnHover && setIsHovering(true)}
      onMouseLeave={() => showDetailsOnHover && setIsHovering(false)}
    >
      <div className="container max-w-7xl mx-auto">
        <div className="flex flex-col space-y-1">
          {/* Lesson title (if provided) */}
          {lessonTitle && (
            <div className="flex items-center text-xs text-muted-foreground">
              <BookOpen className="h-3 w-3 mr-1" />
              <span className="truncate">{lessonTitle}</span>
            </div>
          )}
          
          {/* Progress indicator row */}
          <div className="flex items-center justify-between">
            {/* Left side (back button or step indicator) */}
            <div className="flex items-center">
              {showBackButton && (
                <button 
                  onClick={handleBackClick}
                  className="text-xs mr-2 text-muted-foreground hover:text-primary transition-colors"
                >
                  ← Retour
                </button>
              )}
              
              <div className={`text-xs font-medium ${isCompleted ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`}>
                {isCompleted ? (
                  <span className="flex items-center">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Terminé
                  </span>
                ) : (
                  `Étape ${currentStep}/${totalSteps || '?'}`
                )}
              </div>
            </div>
            
            {/* Right side (completion time or details) */}
            {isHovering && (
              <div className="text-xs text-muted-foreground flex items-center">
                <Clock className="h-3 w-3 mr-1" />
                <span>ID: {lessonId} • Type: {contentType || 'Inconnu'}</span>
              </div>
            )}
          </div>
          
          {/* Progress bar */}
          <Progress 
            value={percentage} 
            className={`h-1 ${getProgressBarColor()}`}
          />
        </div>
      </div>
    </div>
  );
};

export default LessonProgressIndicator;