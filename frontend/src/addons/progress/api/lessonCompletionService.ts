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
      
      await progressAPI.updateContentLessonProgress({
        content_lesson_id: contentId,
        lesson_id: parentLessonId,
        completion_percentage: validPercentage,
        time_spent: timeSpent,
        xp_earned: xpEarned,
        mark_completed: complete
      });

      // Note: l'API backend mettra automatiquement à jour la leçon parent et l'unité

      if (complete) {
        // Vider le cache de progression pour assurer des données fraîches
        progressAPI.clearCache();
        
        toast({
          title: "Contenu terminé !",
          description: "Votre progression a été enregistrée.",
          duration: 3000
        });
      }
    } catch (error) {
      console.error('Erreur lors de la mise à jour de la progression du contenu:', error);
      toast({
        title: "Erreur de sauvegarde",
        description: "Impossible d'enregistrer votre progression. Veuillez réessayer.",
        variant: "destructive",
        duration: 4000
      });
    }
  }
};

export default lessonCompletionService;