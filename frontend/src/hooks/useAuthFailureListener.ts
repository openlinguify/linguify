// hooks/useAuthFailureListener.ts
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { clearAuthData } from '@/lib/auth';
import { useToast } from '@/components/ui/use-toast';

/**
 * Hook pour écouter les événements d'échec d'authentification et rediriger vers la page de login
 */
export const useAuthFailureListener = () => {
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    const handleAuthFailure = () => {
      console.log('🔒 Événement auth:failed détecté - redirection vers login');
      
      // Afficher une notification à l'utilisateur
      toast({
        title: "Session expirée",
        description: "Votre session a expiré, veuillez vous reconnecter.",
        variant: "destructive",
      });
      
      // Effacer les données d'authentification
      clearAuthData();
      
      // Sauvegarder l'URL actuelle pour y revenir après connexion
      const currentPath = window.location.pathname;
      
      // Rediriger vers la page de login
      setTimeout(() => {
        router.push(`/login?returnTo=${encodeURIComponent(currentPath)}`);
      }, 1000);
    };

    // Ajouter l'écouteur d'événement
    window.addEventListener('auth:failed', handleAuthFailure);

    // Nettoyer l'écouteur
    return () => {
      window.removeEventListener('auth:failed', handleAuthFailure);
    };
  }, [router, toast]);

  return null;
};

export default useAuthFailureListener;