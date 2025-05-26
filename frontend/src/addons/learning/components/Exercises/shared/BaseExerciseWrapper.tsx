import React, { ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, RefreshCw, ArrowLeft } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import ExerciseNavBar from '../../Navigation/ExerciseNavBar';
import MaintenanceView from './MaintenanceView';

interface BaseExerciseWrapperProps {
  unitId?: string;
  loading: boolean;
  error: Error | null;
  isMaintenance?: boolean;
  contentTypeName?: string;
  lessonId?: string | number;
  onRetry?: () => void;
  onBack?: () => void;
  children: ReactNode;
  className?: string;
}

/**
 * Wrapper de base pour tous les exercices - fournit une structure commune
 * avec gestion d'états de chargement, d'erreur et navigation
 */
export const BaseExerciseWrapper: React.FC<BaseExerciseWrapperProps> = ({
  unitId,
  loading,
  error,
  isMaintenance = false,
  contentTypeName = 'contenu',
  lessonId,
  onRetry,
  onBack,
  children,
  className = ''
}) => {
  // État de chargement
  if (loading) {
    return (
      <div className="flex flex-col min-h-screen">
        <ExerciseNavBar unitId={unitId} />
        <div className={`flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-blue-900 flex items-center justify-center ${className}`}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="w-full max-w-md">
              <CardContent className="p-6">
                <div className="text-center">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="inline-block"
                  >
                    <RefreshCw className="h-8 w-8 text-blue-600 mx-auto mb-4" />
                  </motion.div>
                  <p className="text-gray-600 dark:text-gray-300">Chargement de l'exercice...</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    );
  }

  // État de maintenance
  if (isMaintenance) {
    return (
      <div className="flex flex-col min-h-screen">
        <ExerciseNavBar unitId={unitId} />
        <div className={`flex-1 bg-gradient-to-br from-orange-50 to-yellow-100 dark:from-gray-900 dark:to-orange-900 ${className}`}>
          <MaintenanceView
            contentTypeName={contentTypeName}
            lessonId={lessonId}
            onBack={onBack}
            onRetry={onRetry}
          />
        </div>
      </div>
    );
  }

  // État d'erreur (non-maintenance)
  if (error) {
    return (
      <div className="flex flex-col min-h-screen">
        <ExerciseNavBar unitId={unitId} />
        <div className={`flex-1 bg-gradient-to-br from-red-50 to-pink-100 dark:from-gray-900 dark:to-red-900 flex items-center justify-center ${className}`}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="w-full max-w-md">
              <CardContent className="p-6">
                <Alert variant="destructive" className="mb-4">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    {error.message || 'Une erreur est survenue lors du chargement de l\'exercice'}
                  </AlertDescription>
                </Alert>
                <div className="flex gap-2 justify-center">
                  {onBack && (
                    <Button onClick={onBack} variant="outline" className="flex items-center gap-2">
                      <ArrowLeft className="h-4 w-4" />
                      Retour
                    </Button>
                  )}
                  {onRetry && (
                    <Button onClick={onRetry} className="flex items-center gap-2">
                      <RefreshCw className="h-4 w-4" />
                      Réessayer
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    );
  }

  // Contenu principal
  return (
    <div className="flex flex-col min-h-screen">
      <ExerciseNavBar unitId={unitId} />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        className={`flex-1 ${className}`}
      >
        {children}
      </motion.div>
    </div>
  );
};

export default BaseExerciseWrapper;