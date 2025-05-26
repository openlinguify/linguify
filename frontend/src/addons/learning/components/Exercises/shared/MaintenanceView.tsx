import React from 'react';
import { motion } from 'framer-motion';
import { Construction, ArrowLeft, RefreshCw } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface MaintenanceViewProps {
  contentTypeName: string;
  onBack?: () => void;
  onRetry?: () => void;
  lessonId?: string | number;
  className?: string;
  customMessage?: string;
}

/**
 * Composant de maintenance standardisé pour les contenus non disponibles
 */
export const MaintenanceView: React.FC<MaintenanceViewProps> = ({
  contentTypeName,
  onBack,
  onRetry,
  lessonId,
  className = '',
  customMessage
}) => {
  const defaultMessage = `Cette ${contentTypeName} est temporairement en maintenance et sera bientôt disponible.`;
  
  return (
    <div className={`flex items-center justify-center min-h-[60vh] p-4 ${className}`}>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-md"
      >
        <Card className="shadow-lg border-orange-200 dark:border-orange-800">
          <CardContent className="p-8 text-center">
            {/* Icône de maintenance */}
            <motion.div
              animate={{ 
                rotate: [0, 5, -5, 0],
                scale: [1, 1.05, 1]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="mb-6"
            >
              <div className="w-16 h-16 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center mx-auto">
                <Construction className="h-8 w-8 text-orange-600 dark:text-orange-400" />
              </div>
            </motion.div>

            {/* Badge de statut */}
            <Badge 
              variant="outline" 
              className="mb-4 bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-900/20 dark:text-orange-300 dark:border-orange-800"
            >
              En Maintenance
            </Badge>

            {/* Titre */}
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
              Contenu Temporairement Indisponible
            </h3>

            {/* Message principal */}
            <p className="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
              {customMessage || defaultMessage}
            </p>

            {/* Informations additionnelles */}
            <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 mb-6">
              <div className="text-sm text-orange-800 dark:text-orange-200">
                <p className="font-medium mb-2">Que pouvez-vous faire ?</p>
                <ul className="text-left space-y-1">
                  <li>• Essayer un autre exercice</li>
                  <li>• Revenir plus tard</li>
                  <li>• Contacter le support si le problème persiste</li>
                </ul>
              </div>
            </div>

            {/* Informations techniques (optionnel) */}
            {lessonId && (
              <div className="text-xs text-gray-400 dark:text-gray-500 mb-4">
                Référence: Leçon {lessonId} - {contentTypeName}
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              {onBack && (
                <Button
                  onClick={onBack}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Retour
                </Button>
              )}
              
              {onRetry && (
                <Button
                  onClick={onRetry}
                  variant="default"
                  className="flex items-center gap-2 bg-orange-600 hover:bg-orange-700"
                >
                  <RefreshCw className="h-4 w-4" />
                  Réessayer
                </Button>
              )}
            </div>

            {/* Message d'encouragement */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.3 }}
              className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700"
            >
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Merci de votre patience ! 🚀
              </p>
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default MaintenanceView;