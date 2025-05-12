import React, { useEffect } from 'react';
import NotebookMain from './NotebookMain';
import './animations.css'; // Importer les styles d'animation
import { motion } from 'framer-motion'; // Utiliser framer-motion pour des animations fluides

/**
 * Composant d'application principal pour le carnet de notes
 * Ce composant s'intègre dans le layout existant avec le header
 */
const NotebookApp = () => {
  // Appliquer l'effet pour verrouiller le défilement
  React.useEffect(() => {
    // Désactiver le défilement du corps
    document.body.style.overflow = 'hidden';

    return () => {
      // Réactiver le défilement quand le composant est démonté
      document.body.style.overflow = '';
    };
  }, []);
  // Variantes d'animation pour l'ensemble de l'application
  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: 0.4,
        ease: "easeOut",
        when: "beforeChildren",
        staggerChildren: 0.1
      }
    },
    exit: { 
      opacity: 0,
      y: -20,
      transition: { 
        duration: 0.3,
        ease: "easeIn" 
      }
    }
  };

  return (
    <motion.div
      className="h-full w-full bg-gray-50 dark:bg-gray-900 overflow-hidden p-0 m-0"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
    >
      <NotebookMain />
    </motion.div>
  );
};

export default NotebookApp;