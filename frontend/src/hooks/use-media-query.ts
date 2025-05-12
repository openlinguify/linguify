import { useEffect, useState } from 'react';

/**
 * Custom hook to manage media queries
 * @param query CSS media query string
 * @returns Boolean indicating whether the media query matches
 */
export function useMediaQuery(query: string): boolean {
  // Vérifier si window est disponible (éviter les erreurs SSR)
  const getMatches = (query: string): boolean => {
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  };

  const [matches, setMatches] = useState<boolean>(getMatches(query));

  useEffect(() => {
    // Éviter d'exécuter durant le rendu SSR
    if (typeof window === 'undefined') {
      return;
    }

    // Fonction pour mettre à jour l'état
    const handleChange = () => {
      setMatches(getMatches(query));
    };

    // Ajouter un listener pour les changements de taille d'écran
    const matchMedia = window.matchMedia(query);
    
    // Initialiser avec la valeur actuelle
    handleChange();
    
    // Utiliser la méthode moderne si disponible (addEventListener), sinon utiliser addListener
    if (matchMedia.addEventListener) {
      matchMedia.addEventListener('change', handleChange);
    } else {
      matchMedia.addListener(handleChange);
    }

    // Nettoyage
    return () => {
      if (matchMedia.removeEventListener) {
        matchMedia.removeEventListener('change', handleChange);
      } else {
        matchMedia.removeListener(handleChange);
      }
    };
  }, [query]);

  return matches;
}