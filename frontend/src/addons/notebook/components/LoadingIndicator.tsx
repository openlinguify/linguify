import React from 'react';
import { Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface LoadingIndicatorProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
  fullHeight?: boolean;
  inline?: boolean;
  className?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  message = 'Chargement en cours...',
  size = 'medium',
  fullHeight = false,
  inline = false,
  className = '',
}) => {
  // Déterminer la taille de l'icône
  const getIconSize = () => {
    switch (size) {
      case 'small':
        return 'h-4 w-4';
      case 'large':
        return 'h-12 w-12';
      case 'medium':
      default:
        return 'h-8 w-8';
    }
  };

  // Déterminer la taille du texte
  const getTextSize = () => {
    switch (size) {
      case 'small':
        return 'text-xs';
      case 'large':
        return 'text-lg';
      case 'medium':
      default:
        return 'text-sm';
    }
  };

  // Déterminer la hauteur du conteneur
  const getContainerHeight = () => {
    if (fullHeight) return 'h-full';
    return inline ? '' : 'py-6';
  };

  // Utiliser une mise en page en ligne ou centrée
  if (inline) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Loader2 className={`${getIconSize()} animate-spin text-blue-500`} />
        <span className={`${getTextSize()} text-gray-600 dark:text-gray-300`}>
          {message}
        </span>
      </div>
    );
  }

  // Animation avec Framer Motion
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className={`${getContainerHeight()} flex flex-col items-center justify-center ${className}`}
    >
      <motion.div
        animate={{ 
          rotate: 360,
          transition: { 
            duration: 1.5, 
            ease: "linear", 
            repeat: Infinity 
          }
        }}
      >
        <Loader2 className={`${getIconSize()} text-blue-500`} />
      </motion.div>
      
      {message && (
        <motion.p 
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className={`${getTextSize()} mt-2 text-gray-600 dark:text-gray-300`}
        >
          {message}
        </motion.p>
      )}
    </motion.div>
  );
};

export default LoadingIndicator;