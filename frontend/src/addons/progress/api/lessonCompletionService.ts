// src/services/lessonCompletionService.ts
import progressAPI from "@/addons/progress/api/progressAPI";
import { updateProgressCascade } from "@/addons/progress/utils/progressCalculator";

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
    contentLessonId?: number,
    unitId?: number
  ): Promise<void> {
    try {
      // Accept undefined/null lessonId but log a warning
      if (!lessonId) {
        console.warn('Warning: lessonId manquant, utilisation de valeur par défaut');

        // Use fallback ID
        lessonId = 0;

        // Don't show toast error to user, just continue with fallback
      }

      // S'assurer que les IDs sont des nombres
      const lessonIdNum = typeof lessonId === 'string' ? parseInt(lessonId) : lessonId;
      const contentIdNum = contentLessonId ?
        (typeof contentLessonId === 'string' ? parseInt(contentLessonId) : contentLessonId) : 0;
      const unitIdNum = unitId ? (typeof unitId === 'string' ? parseInt(unitId) : unitId) : undefined;

      // Assurer que le pourcentage est dans la plage 0-100
      const validPercentage = Math.max(0, Math.min(100, completionPercentage));

      // Log de debug pour faciliter le dépannage
      console.log(`Mise à jour de la progression de leçon: lessonId=${lessonIdNum}, contentId=${contentIdNum}, percentage=${validPercentage}, complete=${complete}`);

      // Approche hybride : Mise à jour locale pour UI immédiate ET appel API

      // 1. Mettre à jour la progression locale pour UI immédiate
      const localStorageKey = `local_lesson_progress_${lessonIdNum}`;
      const progressData = {
        id: lessonIdNum,
        parentId: unitIdNum,
        completion_percentage: validPercentage,
        is_completed: complete === true, // Ensure boolean value
        timestamp: Date.now()
      };

      // Store the progress data in localStorage
      localStorage.setItem(localStorageKey, JSON.stringify(progressData));

      // 2. If we have content lesson ID, update content lesson storage
      if (contentIdNum && contentIdNum > 0) {
        const contentStorageKey = `progress_data_${contentIdNum}`;
        localStorage.setItem(contentStorageKey, JSON.stringify({
          data: {
            content_lesson_id: contentIdNum,
            lesson_id: lessonIdNum,
            completion_percentage: validPercentage,
            mark_completed: complete
          },
          timestamp: Date.now()
        }));
      }

      // 3. If we have a unit ID, update unit progress too
      if (unitIdNum) {
        // Get all lessons for this unit from local storage
        const lessonKeys = [];
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && key.startsWith('local_lesson_progress_')) {
            try {
              const lessonData = JSON.parse(localStorage.getItem(key) || '{}');
              if (lessonData.parentId === unitIdNum) {
                lessonKeys.push(key);
              }
            } catch (err) {
              // Ignore invalid localStorage entries
            }
          }
        }

        // Calculate unit completion percentage based on lessons
        const lessonProgresses = lessonKeys.map(key => {
          const data = JSON.parse(localStorage.getItem(key) || '{}');
          return {
            id: data.id,
            completion_percentage: data.completion_percentage || 0,
            is_completed: data.is_completed || false
          };
        });

        // Only mark unit complete if ALL lessons are complete
        const allLessonsComplete = lessonProgresses.length > 0 &&
          lessonProgresses.every(lesson => lesson.is_completed || lesson.completion_percentage === 100);

        // Calculate average progress
        const totalProgress = lessonProgresses.reduce((sum, item) => sum + item.completion_percentage, 0);
        const avgProgress = lessonProgresses.length > 0 ? Math.round(totalProgress / lessonProgresses.length) : 0;

        // Update unit progress in localStorage
        const unitStorageKey = `local_unit_progress_${unitIdNum}`;
        localStorage.setItem(unitStorageKey, JSON.stringify({
          id: unitIdNum,
          completion_percentage: allLessonsComplete ? 100 : avgProgress,
          is_completed: allLessonsComplete,
          timestamp: Date.now()
        }));
      }

      // 4. IMPORTANT: Réactiver l'appel API pour que les données soient dans l'ORM
      try {
        // Log détaillé pour débogage
        console.log("Envoi des données de progression de leçon au backend:", {
          lesson_id: lessonIdNum,
          content_lesson_id: contentIdNum,
          completion_percentage: validPercentage,
          time_spent: timeSpent || 0,
          mark_completed: complete
        });

        // Obtenir le code langue de l'utilisateur depuis localStorage ou utiliser 'en' par défaut
        const userLang = localStorage.getItem('userTargetLanguage') || 'en';

        // Envoi de la requête au serveur avec le code langue
        await progressAPI.updateLessonProgress({
          lesson_id: lessonIdNum,
          content_lesson_id: contentIdNum,
          completion_percentage: validPercentage,
          time_spent: timeSpent || 0,
          mark_completed: complete,
          language_code: userLang // Ajouter le code langue
        }, {
          // Options robustes
          maxRetries: 3,
          retryOnNetworkError: true,
          showErrorToast: false
        });

        console.log("✅ Progression de leçon synchronisée avec le backend avec succès");
      } catch (serverError) {
        // En cas d'erreur, continuer avec localStorage uniquement
        console.warn("⚠️ Erreur lors de la mise à jour de la progression de leçon via API:", serverError);

        // Stocker la requête pour une synchronisation ultérieure
        const pendingRequests = JSON.parse(localStorage.getItem('pendingLessonProgressRequests') || '[]');
        pendingRequests.push({
          lessonId: lessonIdNum,
          contentLessonId: contentIdNum,
          completionPercentage: validPercentage,
          timeSpent: timeSpent || 0,
          complete: complete,
          unitId: unitIdNum,
          timestamp: Date.now()
        });
        localStorage.setItem('pendingLessonProgressRequests', JSON.stringify(pendingRequests));
      }

      // Notification uniquement pour les complétions pour éviter trop de notifications
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

      // Still try to update local storage even if there's an error
      try {
        const localStorageKey = `local_lesson_progress_${lessonId}`;
        localStorage.setItem(localStorageKey, JSON.stringify({
          id: lessonId,
          completion_percentage: completionPercentage,
          is_completed: complete,
          timestamp: Date.now(),
          error: true,
          errorMessage: error instanceof Error ? error.message : 'Unknown error'
        }));
      } catch (storageError) {
        console.error('Failed to save to localStorage:', storageError);
      }

      toast({
        title: "Erreur de sauvegarde",
        description: "Impossible d'enregistrer votre progression. Utilisation du mode hors ligne.",
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
   * @param unitId - ID de l'unité parente (optionnel) pour mise à jour en cascade
   */
  async updateContentProgress(
    contentLessonId: number,
    lessonId: number,
    completionPercentage: number = 100,
    timeSpent?: number,
    xpEarned?: number,
    complete: boolean = false,
    unitId?: number
  ): Promise<void> {
    let toastId: string | number | undefined;

    try {
      // Accept undefined/null IDs but log a warning
      if (!contentLessonId || !lessonId) {
        console.warn('Warning: contentLessonId ou lessonId manquants, utilisation de valeurs par défaut', {
          contentLessonId,
          lessonId
        });

        // Use fallback IDs if needed
        contentLessonId = contentLessonId || 0;
        lessonId = lessonId || 0;

        // Don't show the error toast to the user, just log it
      }

      // S'assurer que les IDs sont des nombres
      const contentId = typeof contentLessonId === 'string' ? parseInt(contentLessonId) : contentLessonId;
      const parentLessonId = typeof lessonId === 'string' ? parseInt(lessonId) : lessonId;
      const parentUnitId = unitId ? (typeof unitId === 'string' ? parseInt(unitId) : unitId) : null;

      // Assurer que le pourcentage est dans la plage 0-100
      const validPercentage = Math.max(0, Math.min(100, completionPercentage));

      // Log de debug pour faciliter le dépannage
      console.log(`Mise à jour de la progression du contenu: contentId=${contentId}, lessonId=${parentLessonId}, unitId=${parentUnitId}, percentage=${validPercentage}, complete=${complete}`);

      // Montrer un toast de progression si c'est une complétion
      if (complete) {
        toastId = toast({
          title: "Sauvegarde en cours...",
          description: "Enregistrement de votre progression...",
          duration: 3000
        }).id;
      }

      // Approche hybride: Utiliser à la fois le localStorage pour UI immédiat ET l'API

      // 1. D'abord mettre à jour immédiatement la progression en local pour l'UI
      updateProgressCascade(
        contentId,
        parentLessonId,
        parentUnitId,
        validPercentage,
        complete
      );

      // 2. Store content progress data in localStorage
      const contentStorageKey = `progress_data_${contentId}`;
      localStorage.setItem(contentStorageKey, JSON.stringify({
        data: {
          content_lesson_id: contentId,
          lesson_id: parentLessonId,
          completion_percentage: validPercentage,
          time_spent: timeSpent || 0,
          xp_earned: xpEarned || 0,
          mark_completed: complete === true // Ensure boolean value
        },
        timestamp: Date.now()
      }));

      // 3. Try to update progress with the API (RÉACTIVÉ)
      try {
        // Log détaillé pour le débogage
        console.log("Envoi des données de progression au backend:", {
          content_lesson_id: contentId,
          lesson_id: parentLessonId,
          completion_percentage: validPercentage,
          time_spent: timeSpent || 0,
          xp_earned: xpEarned || 0,
          mark_completed: complete
        });

        // Obtenir le code langue de l'utilisateur depuis localStorage ou utiliser 'en' par défaut
        const userLang = localStorage.getItem('userTargetLanguage') || 'en';

        // IMPORTANT: Réactiver l'appel API avec le code langue
        await progressAPI.updateContentLessonProgress({
          content_lesson_id: contentId,
          lesson_id: parentLessonId,
          completion_percentage: validPercentage,
          time_spent: timeSpent || 0,
          xp_earned: xpEarned || 10, // Valeur par défaut non-nulle
          mark_completed: complete,
          language_code: userLang // Ajouter le code langue
        }, {
          // Options robustes
          maxRetries: 3,
          retryOnNetworkError: true,
          showErrorToast: false
        });

        console.log("✅ Progression synchronisée avec le backend avec succès");
      } catch (serverError) {
        // Si nous obtenons une erreur du serveur, continuer avec le localStorage
        console.warn("⚠️ Erreur serveur lors de la mise à jour de la progression. Utilisation du fallback localStorage:", serverError);

        // Stocker la requête pour une synchronisation ultérieure
        const pendingRequests = JSON.parse(localStorage.getItem('pendingContentProgressRequests') || '[]');
        pendingRequests.push({
          contentLessonId: contentId,
          lessonId: parentLessonId,
          completionPercentage: validPercentage,
          timeSpent: timeSpent || 0,
          xpEarned: xpEarned || 10,
          complete: complete,
          timestamp: Date.now()
        });
        localStorage.setItem('pendingContentProgressRequests', JSON.stringify(pendingRequests));
      }

      // 4. Update lesson progress (internally this will also update unit progress)
      await this.updateLessonProgress(
        parentLessonId,
        validPercentage,
        timeSpent,
        complete,
        contentId,
        parentUnitId || undefined
      );

      // Show completion toast
      if (complete) {
        // Clear cache
        progressAPI.clearCache();

        // Update toast to success
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
    } catch (error) {
      console.error('Erreur finale lors de la mise à jour de la progression du contenu:', error);

      // Fallback for error case: still try to save to localStorage
      try {
        const contentStorageKey = `progress_data_${contentLessonId}`;
        localStorage.setItem(contentStorageKey, JSON.stringify({
          data: {
            content_lesson_id: contentLessonId,
            lesson_id: lessonId,
            completion_percentage: completionPercentage,
            time_spent: timeSpent || 0,
            xp_earned: xpEarned || 0,
            mark_completed: complete === true, // Ensure boolean value
            error: true
          },
          timestamp: Date.now()
        }));
      } catch (storageError) {
        console.error('Failed to save progress to localStorage:', storageError);
      }

      // Si on avait un toast en cours, le mettre à jour
      if (toastId) {
        toast({
          id: toastId,
          title: "Mode hors ligne activé",
          description: "Progression enregistrée localement. Synchronisation reportée.",
          variant: "warning",
          duration: 3000
        });
      } else {
        // Sinon créer un nouveau toast
        toast({
          title: "Mode hors ligne activé",
          description: "Progression enregistrée localement. Synchronisation reportée.",
          variant: "warning",
          duration: 3000
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
          complete: complete === true, // Ensure boolean value
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
      // Traiter les requêtes de contenus en attente
      const pendingContentRequests = JSON.parse(localStorage.getItem('pendingContentProgressRequests') || '[]');

      if (pendingContentRequests.length > 0) {
        console.log(`Traitement de ${pendingContentRequests.length} requêtes de progression de contenu en attente...`);

        // Créer une copie des requêtes pour pouvoir les supprimer de manière sûre
        const contentRequestsCopy = [...pendingContentRequests];

        // Vider la liste des requêtes en attente
        localStorage.setItem('pendingContentProgressRequests', JSON.stringify([]));

        // Traiter chaque requête
        contentRequestsCopy.forEach(request => {
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

      // Traiter les requêtes de leçons en attente
      const pendingLessonRequests = JSON.parse(localStorage.getItem('pendingLessonProgressRequests') || '[]');

      if (pendingLessonRequests.length > 0) {
        console.log(`Traitement de ${pendingLessonRequests.length} requêtes de progression de leçon en attente...`);

        // Créer une copie des requêtes pour pouvoir les supprimer de manière sûre
        const lessonRequestsCopy = [...pendingLessonRequests];

        // Vider la liste des requêtes en attente
        localStorage.setItem('pendingLessonProgressRequests', JSON.stringify([]));

        // Traiter chaque requête
        lessonRequestsCopy.forEach(request => {
          if (navigator.onLine) {
            lessonCompletionService.updateLessonProgress(
              request.lessonId,
              request.completionPercentage,
              request.timeSpent,
              request.complete,
              request.contentLessonId,
              request.unitId
            );
          } else {
            // Si hors ligne, remettre dans la file d'attente
            const currentRequests = JSON.parse(localStorage.getItem('pendingLessonProgressRequests') || '[]');
            currentRequests.push(request);
            localStorage.setItem('pendingLessonProgressRequests', JSON.stringify(currentRequests));
          }
        });
      }
    } catch (error) {
      console.error('Erreur lors du traitement des requêtes de progression en attente:', error);
    }
  }, 3000);

  // Fonction réutilisable pour traiter les requêtes en attente
  const processAllPendingRequests = () => {
    setTimeout(() => {
      try {
        // Traiter les requêtes de contenus en attente
        const pendingContentRequests = JSON.parse(localStorage.getItem('pendingContentProgressRequests') || '[]');

        if (pendingContentRequests.length > 0) {
          console.log(`Connexion rétablie: traitement de ${pendingContentRequests.length} requêtes de progression de contenu en attente...`);

          // Traitement similaire à celui du chargement initial
          const contentRequestsCopy = [...pendingContentRequests];
          localStorage.setItem('pendingContentProgressRequests', JSON.stringify([]));

          contentRequestsCopy.forEach(request => {
            lessonCompletionService.updateContentProgress(
              request.contentLessonId,
              request.lessonId,
              request.completionPercentage,
              request.timeSpent,
              request.xpEarned,
              request.complete
            );
          });
        }

        // Traiter les requêtes de leçons en attente
        const pendingLessonRequests = JSON.parse(localStorage.getItem('pendingLessonProgressRequests') || '[]');

        if (pendingLessonRequests.length > 0) {
          console.log(`Connexion rétablie: traitement de ${pendingLessonRequests.length} requêtes de progression de leçon en attente...`);

          // Traitement similaire à celui du chargement initial
          const lessonRequestsCopy = [...pendingLessonRequests];
          localStorage.setItem('pendingLessonProgressRequests', JSON.stringify([]));

          lessonRequestsCopy.forEach(request => {
            lessonCompletionService.updateLessonProgress(
              request.lessonId,
              request.completionPercentage,
              request.timeSpent,
              request.complete,
              request.contentLessonId,
              request.unitId
            );
          });
        }

        // Notification à l'utilisateur seulement s'il y avait des requêtes en attente
        if (pendingContentRequests.length > 0 || pendingLessonRequests.length > 0) {
          toast({
            title: "Synchronisation en cours",
            description: "Reprise de la synchronisation de vos progrès...",
            duration: 3000
          });
        }
      } catch (error) {
        console.error('Erreur lors du traitement des requêtes de progression en attente:', error);
      }
    }, 2000);
  };

  // Écouter l'événement "online" pour traiter les requêtes en attente quand la connexion est rétablie
  window.addEventListener('online', processAllPendingRequests);

  // Lancer également un traitement toutes les minutes quand on est en ligne
  // pour gérer les cas où des requêtes n'ont pas été traitées à cause d'une erreur temporaire
  const intervalId = setInterval(() => {
    if (navigator.onLine) {
      processAllPendingRequests();
    }
  }, 60000); // Toutes les minutes

  // Nettoyer l'intervalle si la page est déchargée
  window.addEventListener('unload', () => {
    clearInterval(intervalId);
  });
}

export default lessonCompletionService;