import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { 
  AlertCircle, 
  WifiOff, 
  Lock, 
  FileQuestion, 
  ShieldAlert, 
  AlertTriangle, 
  ServerCrash, 
  X, 
  RefreshCcw 
} from 'lucide-react';
import { ErrorType, ErrorResponse } from '../utils/errorHandling';
import { motion } from 'framer-motion';

interface ErrorDisplayProps {
  error: ErrorResponse;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ 
  error, 
  onRetry, 
  onDismiss,
  className = ''
}) => {
  // Déterminer l'icône en fonction du type d'erreur
  const getErrorIcon = () => {
    switch (error.type) {
      case ErrorType.NETWORK:
        return <WifiOff className="h-5 w-5" />;
      case ErrorType.AUTHENTICATION:
        return <Lock className="h-5 w-5" />;
      case ErrorType.NOT_FOUND:
        return <FileQuestion className="h-5 w-5" />;
      case ErrorType.PERMISSION:
        return <ShieldAlert className="h-5 w-5" />;
      case ErrorType.VALIDATION:
        return <AlertTriangle className="h-5 w-5" />;
      case ErrorType.SERVER:
        return <ServerCrash className="h-5 w-5" />;
      case ErrorType.UNKNOWN:
      default:
        return <AlertCircle className="h-5 w-5" />;
    }
  };

  // Déterminer la couleur en fonction du type d'erreur
  const getAlertVariant = (): 'default' | 'destructive' => {
    switch (error.type) {
      case ErrorType.VALIDATION:
        return 'default';
      case ErrorType.NETWORK:
      case ErrorType.AUTHENTICATION:
      case ErrorType.PERMISSION:
      case ErrorType.SERVER:
      case ErrorType.NOT_FOUND:
      case ErrorType.UNKNOWN:
      default:
        return 'destructive';
    }
  };

  // Déterminer le titre en fonction du type d'erreur
  const getErrorTitle = (): string => {
    switch (error.type) {
      case ErrorType.NETWORK:
        return 'Problème de connexion';
      case ErrorType.AUTHENTICATION:
        return 'Authentification requise';
      case ErrorType.NOT_FOUND:
        return 'Ressource introuvable';
      case ErrorType.PERMISSION:
        return 'Accès refusé';
      case ErrorType.VALIDATION:
        return 'Données invalides';
      case ErrorType.SERVER:
        return 'Erreur serveur';
      case ErrorType.UNKNOWN:
      default:
        return 'Erreur inattendue';
    }
  };

  // Version compacte dans une alerte
  if (className.includes('compact')) {
    return (
      <Alert variant={getAlertVariant()} className={`mb-4 ${className}`}>
        <div className="flex items-start">
          {getErrorIcon()}
          <div className="ml-3 flex-1">
            <AlertTitle>{getErrorTitle()}</AlertTitle>
            <AlertDescription className="mt-1">{error.message}</AlertDescription>
          </div>
          {onDismiss && (
            <Button 
              variant="ghost" 
              size="icon" 
              className="ml-2 -my-1 h-8 w-8 shrink-0" 
              onClick={onDismiss}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        {error.retry && onRetry && (
          <div className="mt-3 flex justify-end">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onRetry}
              className="text-xs"
            >
              <RefreshCcw className="mr-1 h-3 w-3" />
              Réessayer
            </Button>
          </div>
        )}
      </Alert>
    );
  }

  // Version complète dans une carte
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={className}
    >
      <Card className="border-2 border-dashed border-red-100 dark:border-red-800">
        <CardContent className="p-8 flex flex-col items-center justify-center space-y-4">
          <div className="bg-red-100 dark:bg-red-900/20 rounded-full p-4">
            {getErrorIcon()}
          </div>
          
          <h3 className="text-lg font-semibold">{getErrorTitle()}</h3>
          
          <p className="text-center text-gray-600 dark:text-gray-400">
            {error.message}
          </p>
          
          {error.details && typeof error.details === 'string' && (
            <div className="text-sm text-gray-500 dark:text-gray-500 mt-2 max-w-full overflow-hidden">
              <p className="truncate">{error.details}</p>
            </div>
          )}
          
          <div className="flex gap-2 mt-2">
            {onDismiss && (
              <Button 
                variant="outline" 
                onClick={onDismiss}
              >
                Fermer
              </Button>
            )}
            
            {error.retry && onRetry && (
              <Button 
                onClick={onRetry} 
                className="gap-1"
              >
                <RefreshCcw className="h-4 w-4" />
                Réessayer
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ErrorDisplay;