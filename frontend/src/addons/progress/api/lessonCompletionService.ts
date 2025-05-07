// src/services/lessonCompletionService.ts
import progressAPI from "@/addons/progress/api/progressAPI";

import { toast } from '@/components/ui/use-toast';

/**
 * Service pour gérer la progression des leçons et unités
 */
const lessonCompletionService = {
  /**
   * Met à jour la progression d'une leçon et actualise la progression de l'unité parente
   * @param lessonId - ID de la leçon complétée ou en progression
   * @param completionPercentage - Pourcentage de complétion (0-100)
   * @param timeSpent - Temps passé en secondes (optionnel)
   * @param complete - Marquer comme complété si true
   * @param contentLessonId - ID du contenu de leçon associé (optionnel)
   */
  async updateLessonProgress(
    lessonId: number,
    completionPercentage: number = 100,
    timeSpent?: number,
    complete: boolean = false,
    contentLessonId?: number
  ): Promise<void> {
    try {
      // Validation des paramètres
      if (!lessonId) {
        console.error('Erreur: lessonId est obligatoire');
        toast({
          title: "Erreur de paramètre",
          description: "Paramètres invalides pour la mise à jour de la progression de leçon.",
          variant: "destructive",
          duration: 4000
        });
        return;
      }

      // S'assurer que les IDs sont des nombres
      const lessonIdNum = typeof lessonId === 'string' ? parseInt(lessonId) : lessonId;
      const contentIdNum = contentLessonId ? 
        (typeof contentLessonId === 'string' ? parseInt(contentLessonId) : contentLessonId) : 0;
      
      // Assurer que le pourcentage est dans la plage 0-100
      const validPercentage = Math.max(0, Math.min(100, completionPercentage));
      
      // Log de debug pour faciliter le dépannage
      console.log(`Mise à jour de la progression de leçon: lessonId=${lessonIdNum}, contentId=${contentIdNum}, percentage=${validPercentage}, complete=${complete}`);
      
      // 1. Mettre à jour la progression de la leçon
      await progressAPI.updateLessonProgress({
        lesson_id: lessonIdNum,
        content_lesson_id: contentIdNum,
        completion_percentage: validPercentage,
        time_spent: timeSpent,
        mark_completed: complete
      });

      // 2. L'API backend met automatiquement à jour l'unité parente
      if (complete) {
        // Vider le cache de progression pour assurer des données fraîches
        progressAPI.clearCache();
        
        toast({
          title: "Leçon terminée !",
          description: "Votre progression a été enregistrée.",
          duration: 3000
        });
      }

    } catch (error) {
      console.error('Erreur lors de la mise à jour de la progression:', error);
      toast({
        title: "Erreur de sauvegarde",
        description: "Impossible d'enregistrer votre progression. Veuillez réessayer.",
        variant: "destructive",
        duration: 4000
      });
    }
  },

  /**
   * Met à jour la progression d'un contenu de leçon spécifique
   * @param contentLessonId - ID du contenu de leçon
   * @param lessonId - ID de la leçon parente
   * @param completionPercentage - Pourcentage de complétion (0-100)
   * @param timeSpent - Temps passé en secondes (optionnel)
   * @param xpEarned - Points d'expérience gagnés (optionnel)
   * @param complete - Marquer comme complété si true
   */
  async updateContentProgress(
    contentLessonId: number,
    lessonId: number,
    completionPercentage: number = 100,
    timeSpent?: number,
    xpEarned?: number,
    complete: boolean = false
  ): Promise<void> {
    let requestAttempts = 0;
    const maxAttempts = 3;
    let toastId: string | number | undefined;
    
    try {
      // Validation des paramètres obligatoires
      if (!contentLessonId || !lessonId) {
        console.error('Erreur: contentLessonId et lessonId sont obligatoires');
        toast({
          title: "Erreur de paramètre",
          description: "Paramètres invalides pour la mise à jour de la progression.",
          variant: "destructive",
          duration: 4000
        });
        return;
      }

      // S'assurer que les IDs sont des nombres
      const contentId = typeof contentLessonId === 'string' ? parseInt(contentLessonId) : contentLessonId;
      const parentLessonId = typeof lessonId === 'string' ? parseInt(lessonId) : lessonId;
      
      // Assurer que le pourcentage est dans la plage 0-100
      const validPercentage = Math.max(0, Math.min(100, completionPercentage));
      
      // Log de debug pour faciliter le dépannage
      console.log(`Mise à jour de la progression du contenu: contentId=${contentId}, lessonId=${parentLessonId}, percentage=${validPercentage}, complete=${complete}`);
      
      // Montrer un toast de progression si c'est une complétion
      if (complete) {
        toastId = toast({
          title: "Sauvegarde en cours...",
          description: "Enregistrement de votre progression...",
          duration: 10000
        }).id;
      }
      
      const makeRequest = async (): Promise<boolean> => {
        requestAttempts++;
        try {
          await progressAPI.updateContentLessonProgress({
            content_lesson_id: contentId,
            lesson_id: parentLessonId,
            completion_percentage: validPercentage,
            time_spent: timeSpent,
            xp_earned: xpEarned,
            mark_completed: complete
          }, {
            // Utiliser des options plus robustes
            maxRetries: 3,
            retryOnNetworkError: true,
            showErrorToast: false // On gérera les toasts nous-mêmes
          });
          return true;
        } catch (err) {
          console.error(`Tentative ${requestAttempts}/${maxAttempts} échouée:`, err);
          
          // Si on a encore des tentatives, réessayer
          if (requestAttempts < maxAttempts) {
            // Notification à l'utilisateur que nous réessayons
            toast({
              title: "Problème de connexion",
              description: `Tentative ${requestAttempts}/${maxAttempts} de sauvegarde...`,
              duration: 3000
            });
            
            // Attendre un peu avant de réessayer (backoff exponentiel)
            const delay = Math.min(2000 * Math.pow(2, requestAttempts - 1), 8000);
            await new Promise(resolve => setTimeout(resolve, delay));
            return makeRequest(); // Appel récursif
          }
          
          throw err; // Si plus de tentatives, propager l'erreur
        }
      };
      
      // Exécuter la requête avec tentatives
      const success = await makeRequest();
      
      if (success) {
        // Note: l'API backend mettra automatiquement à jour la leçon parent et l'unité

        if (complete) {
          // Vider le cache de progression pour assurer des données fraîches
          progressAPI.clearCache();
          
          // Mettre à jour le toast ou en créer un nouveau
          if (toastId) {
            toast({
              id: toastId,
              title: "Contenu terminé !",
              description: "Votre progression a été enregistrée avec succès.",
              duration: 3000
            });
          } else {
            toast({
              title: "Contenu terminé !",
              description: "Votre progression a été enregistrée avec succès.",
              duration: 3000
            });
          }
        }
      }
    } catch (error) {
      console.error('Erreur finale lors de la mise à jour de la progression du contenu:', error);
      
      // Si on avait un toast en cours, le mettre à jour
      if (toastId) {
        toast({
          id: toastId,
          title: "Erreur de sauvegarde",
          description: "Impossible d'enregistrer votre progression après plusieurs tentatives. Veuillez réessayer ultérieurement.",
          variant: "destructive",
          duration: 5000,
          action: {
            label: "Réessayer",
            onClick: () => this.updateContentProgress(
              contentLessonId,
              lessonId,
              completionPercentage,
              timeSpent,
              xpEarned,
              complete
            )
          }
        });
      } else {
        // Sinon créer un nouveau toast
        toast({
          title: "Erreur de sauvegarde",
          description: "Impossible d'enregistrer votre progression après plusieurs tentatives. Veuillez réessayer ultérieurement.",
          variant: "destructive",
          duration: 5000,
          action: {
            label: "Réessayer",
            onClick: () => this.updateContentProgress(
              contentLessonId,
              lessonId,
              completionPercentage,
              timeSpent,
              xpEarned,
              complete
            )
          }
        });
      }
      
      // Stocker la requête localement pour réessayer plus tard
      try {
        const pendingRequests = JSON.parse(localStorage.getItem('pendingContentProgressRequests') || '[]');
        pendingRequests.push({
          contentLessonId,
          lessonId,
          completionPercentage,
          timeSpent,
          xpEarned,
          complete,
          timestamp: Date.now()
        });
        localStorage.setItem('pendingContentProgressRequests', JSON.stringify(pendingRequests));
        console.log('Requête de progression stockée pour réessai ultérieur');
      } catch (storageError) {
        console.error('Erreur lors du stockage de la requête:', storageError);
      }
    }
  }
};

// Fonction pour traiter les requêtes en attente au démarrage de l'application
if (typeof window !== 'undefined') {
  // Exécuter après un court délai pour laisser l'application se charger
  setTimeout(() => {
    try {
      const pendingRequests = JSON.parse(localStorage.getItem('pendingContentProgressRequests') || '[]');
      
      if (pendingRequests.length > 0) {
        console.log(`Traitement de ${pendingRequests.length} requêtes de progression en attente...`);
        
        // Créer une copie des requêtes pour pouvoir les supprimer de manière sûre
        const requestsCopy = [...pendingRequests];
        
        // Vider la liste des requêtes en attente
        localStorage.setItem('pendingContentProgressRequests', JSON.stringify([]));
        
        // Traiter chaque requête
        requestsCopy.forEach(request => {
          if (navigator.onLine) {
            lessonCompletionService.updateContentProgress(
              request.contentLessonId,
              request.lessonId,
              request.completionPercentage,
              request.timeSpent,
              request.xpEarned,
              request.complete
            );
          } else {
            // Si hors ligne, remettre dans la file d'attente
            const currentRequests = JSON.parse(localStorage.getItem('pendingContentProgressRequests') || '[]');
            currentRequests.push(request);
            localStorage.setItem('pendingContentProgressRequests', JSON.stringify(currentRequests));
          }
        });
      }
    } catch (error) {
      console.error('Erreur lors du traitement des requêtes de progression en attente:', error);
    }
  }, 3000);
  
  // Écouter l'événement "online" pour traiter les requêtes en attente quand la connexion est rétablie
  window.addEventListener('online', () => {
    setTimeout(() => {
      try {
        const pendingRequests = JSON.parse(localStorage.getItem('pendingContentProgressRequests') || '[]');
        
        if (pendingRequests.length > 0) {
          console.log(`Connexion rétablie: traitement de ${pendingRequests.length} requêtes de progression en attente...`);
          
          // Traitement similaire à celui du chargement initial
          const requestsCopy = [...pendingRequests];
          localStorage.setItem('pendingContentProgressRequests', JSON.stringify([]));
          
          requestsCopy.forEach(request => {
            lessonCompletionService.updateContentProgress(
              request.contentLessonId,
              request.lessonId,
              request.completionPercentage,
              request.timeSpent,
              request.xpEarned,
              request.complete
            );
          });
          
          // Notification à l'utilisateur
          toast({
            title: "Synchronisation en cours",
            description: "Reprise de la synchronisation de vos progrès...",
            duration: 3000
          });
        }
      } catch (error) {
        console.error('Erreur lors du traitement des requêtes de progression en attente (événement online):', error);
      }
    }, 2000);
  });
}

export default lessonCompletionService;