/**
 * Utilitaires pour calculer la progression localement
 */

// Types simplifiés pour les calculs de progression
interface ProgressItem {
  id: number;
  completion_percentage: number;
  is_completed?: boolean;
}

/**
 * Calcule le pourcentage de progression moyen pour une collection d'éléments
 * @param items - Les éléments avec des pourcentages de progression
 * @returns Le pourcentage moyen (0-100)
 */
export const calculateAveragePercentage = (items: ProgressItem[]): number => {
  if (!items || items.length === 0) {
    return 0;
  }

  // Calculer le total des pourcentages
  const totalPercentage = items.reduce(
    (sum, item) => sum + (item.completion_percentage || 0),
    0
  );

  // Calculer la moyenne avec précision décimale (pas de division entière)
  return Math.round(totalPercentage / items.length);
};

/**
 * Vérifie si tous les éléments sont complets (100%)
 * @param items - Les éléments à vérifier
 * @returns true si tous les éléments sont à 100%, false sinon
 */
export const areAllItemsComplete = (items: ProgressItem[]): boolean => {
  if (!items || items.length === 0) {
    return false;
  }
  
  return items.every(item => 
    (item.completion_percentage === 100 || item.is_completed === true)
  );
};

/**
 * Recalcule la progression d'une leçon en fonction de ses contenus
 * @param contentProgressItems - Progression des contenus de la leçon
 * @returns Objet avec le pourcentage et l'état de complétion
 */
export const calculateLessonProgress = (contentProgressItems: ProgressItem[]): { 
  percentage: number; 
  completed: boolean;
} => {
  if (!contentProgressItems || contentProgressItems.length === 0) {
    return { percentage: 0, completed: false };
  }

  // Une leçon est complète uniquement si tous ses contenus sont complets
  const completed = areAllItemsComplete(contentProgressItems);
  
  // Si tous les éléments sont complets, la leçon est à 100%
  const percentage = completed 
    ? 100 
    : calculateAveragePercentage(contentProgressItems);
  
  return { percentage, completed };
};

/**
 * Recalcule la progression d'une unité en fonction de ses leçons
 * @param lessonProgressItems - Progression des leçons de l'unité
 * @returns Objet avec le pourcentage et l'état de complétion
 */
export const calculateUnitProgress = (lessonProgressItems: ProgressItem[]): {
  percentage: number;
  completed: boolean;
} => {
  if (!lessonProgressItems || lessonProgressItems.length === 0) {
    return { percentage: 0, completed: false };
  }
  
  // Une unité est complète uniquement si toutes ses leçons sont complètes
  const completed = areAllItemsComplete(lessonProgressItems);
  
  // Si toutes les leçons sont complètes, l'unité est à 100%
  const percentage = completed 
    ? 100 
    : calculateAveragePercentage(lessonProgressItems);
  
  return { percentage, completed };
};

/**
 * Structure des données de progression dans le localStorage
 */
interface LocalProgressData {
  id: number;
  parentId?: number; // ID de l'élément parent (unitId pour leçons, lessonId pour contenus)
  completion_percentage: number;
  is_completed: boolean;
  timestamp: number;
}

/**
 * Met à jour le localStorage pour la progression d'une leçon
 * @param lessonId - ID de la leçon
 * @param unitId - ID de l'unité parente
 * @param percentage - Nouveau pourcentage
 * @param completed - Si la leçon est complète
 */
export const updateLocalLessonProgress = (
  lessonId: number,
  unitId: number | null,
  percentage: number,
  completed: boolean
): void => {
  try {
    const key = `local_lesson_progress_${lessonId}`;
    
    const progressData: LocalProgressData = {
      id: lessonId,
      parentId: unitId || undefined,
      completion_percentage: percentage,
      is_completed: completed,
      timestamp: Date.now()
    };
    
    localStorage.setItem(key, JSON.stringify(progressData));
    
    console.log(`Progression de leçon mise à jour localement: ${lessonId} -> ${percentage}% (${completed ? 'complète' : 'en cours'})`);
  } catch (error) {
    console.error('Erreur lors de la mise à jour locale de la progression de la leçon', error);
  }
};

/**
 * Met à jour le localStorage pour la progression d'une unité
 * @param unitId - ID de l'unité
 * @param percentage - Nouveau pourcentage
 * @param completed - Si l'unité est complète
 */
export const updateLocalUnitProgress = (
  unitId: number,
  percentage: number,
  completed: boolean
): void => {
  try {
    const key = `local_unit_progress_${unitId}`;
    
    const progressData: LocalProgressData = {
      id: unitId,
      completion_percentage: percentage,
      is_completed: completed,
      timestamp: Date.now()
    };
    
    localStorage.setItem(key, JSON.stringify(progressData));
    
    console.log(`Progression d'unité mise à jour localement: ${unitId} -> ${percentage}% (${completed ? 'complète' : 'en cours'})`);
  } catch (error) {
    console.error('Erreur lors de la mise à jour locale de la progression de l\'unité', error);
  }
};

/**
 * Met à jour le localStorage pour la progression d'un contenu de leçon
 * @param contentId - ID du contenu
 * @param lessonId - ID de la leçon parente
 * @param percentage - Nouveau pourcentage
 * @param completed - Si le contenu est complet
 */
export const updateLocalContentProgress = (
  contentId: number,
  lessonId: number,
  percentage: number,
  completed: boolean
): void => {
  try {
    const key = `progress_data_${contentId}`;
    
    localStorage.setItem(key, JSON.stringify({
      data: {
        content_lesson_id: contentId,
        lesson_id: lessonId,
        completion_percentage: percentage,
        mark_completed: completed
      },
      timestamp: Date.now()
    }));
    
    console.log(`Progression de contenu mise à jour localement: ${contentId} -> ${percentage}% (${completed ? 'complet' : 'en cours'})`);
  } catch (error) {
    console.error('Erreur lors de la mise à jour locale de la progression du contenu', error);
  }
};

/**
 * Récupère la progression locale d'une leçon
 * @param lessonId - ID de la leçon
 * @returns Les données de progression locales ou null
 */
export const getLocalLessonProgress = (lessonId: number): ProgressItem | null => {
  try {
    const key = `local_lesson_progress_${lessonId}`;
    const data = localStorage.getItem(key);
    if (!data) return null;
    return JSON.parse(data) as ProgressItem;
  } catch (error) {
    console.error('Erreur lors de la récupération de la progression locale de la leçon', error);
    return null;
  }
};

/**
 * Récupère la progression locale d'une unité
 * @param unitId - ID de l'unité
 * @returns Les données de progression locales ou null
 */
export const getLocalUnitProgress = (unitId: number): ProgressItem | null => {
  try {
    const key = `local_unit_progress_${unitId}`;
    const data = localStorage.getItem(key);
    if (!data) return null;
    return JSON.parse(data) as ProgressItem;
  } catch (error) {
    console.error('Erreur lors de la récupération de la progression locale de l\'unité', error);
    return null;
  }
};

/**
 * Récupère toutes les progressions de contenu pour une leçon donnée
 * @param lessonId - ID de la leçon
 * @returns Tableau de progressions de contenus associés à cette leçon
 */
export const getAllContentProgressForLesson = (lessonId: number): ProgressItem[] => {
  try {
    const contentProgresses: ProgressItem[] = [];
    
    // Parcourir l'ensemble du localStorage pour trouver les entrées pertinentes
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('progress_data_')) {
        try {
          const data = JSON.parse(localStorage.getItem(key) || '');
          if (data && data.data && data.data.lesson_id === lessonId) {
            contentProgresses.push({
              id: data.data.content_lesson_id,
              completion_percentage: data.data.completion_percentage,
              is_completed: data.data.mark_completed
            });
          }
        } catch {
          // Ignorer les entrées invalides
        }
      }
    }
    
    return contentProgresses;
  } catch (error) {
    console.error('Erreur lors de la récupération des progressions de contenu', error);
    return [];
  }
};

/**
 * Récupère toutes les progressions de leçon pour une unité donnée
 * @param unitId - ID de l'unité
 * @returns Tableau de progressions de leçons associées à cette unité
 */
export const getAllLessonProgressForUnit = (unitId: number): ProgressItem[] => {
  try {
    const lessonProgresses: ProgressItem[] = [];
    
    // Parcourir l'ensemble du localStorage pour trouver les entrées pertinentes
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('local_lesson_progress_')) {
        try {
          const data = JSON.parse(localStorage.getItem(key) || '');
          if (data && data.parentId === unitId) {
            lessonProgresses.push({
              id: data.id,
              completion_percentage: data.completion_percentage,
              is_completed: data.is_completed
            });
          }
        } catch {
          // Ignorer les entrées invalides
        }
      }
    }
    
    return lessonProgresses;
  } catch (error) {
    console.error('Erreur lors de la récupération des progressions de leçon', error);
    return [];
  }
};

/**
 * Met à jour la progression en cascade pour un contenu de leçon
 * @param contentId - ID du contenu
 * @param lessonId - ID de la leçon parente
 * @param unitId - ID de l'unité parente
 * @param percentage - Pourcentage de progression du contenu
 * @param completed - Si le contenu est complet
 */
export const updateProgressCascade = (
  contentId: number,
  lessonId: number,
  unitId: number | null,
  percentage: number,
  completed: boolean
): void => {
  try {
    // Handle invalid parameters
    if (contentId === undefined || contentId === null) {
      console.warn('Content ID is missing for progress cascade update, using default');
      contentId = 0;
    }

    if (lessonId === undefined || lessonId === null) {
      console.warn('Lesson ID is missing for progress cascade update, using default');
      lessonId = 0;
    }

    console.log(`Début de la mise à jour en cascade: Content=${contentId}, Lesson=${lessonId}, Unit=${unitId}`);

    // 1. Mettre à jour la progression du contenu
    updateLocalContentProgress(contentId, lessonId, percentage, completed);

    // 2. Récupérer tous les contenus pour cette leçon et recalculer
    const contentProgresses = getAllContentProgressForLesson(lessonId);
    console.log(`Trouvé ${contentProgresses.length} contenus pour la leçon ${lessonId}`);

    // If we have no content progresses but this is a completion, create a fake one
    if (contentProgresses.length === 0 && completed) {
      contentProgresses.push({
        id: contentId,
        completion_percentage: 100,
        is_completed: true
      });
    }

    const lessonProgress = calculateLessonProgress(contentProgresses);
    console.log(`Progression de leçon calculée: ${lessonProgress.percentage}% (${lessonProgress.completed ? 'complète' : 'en cours'})`);

    // 3. Mettre à jour la progression de la leçon
    updateLocalLessonProgress(lessonId, unitId, lessonProgress.percentage, lessonProgress.completed);

    // 4. Si l'unitId est fourni, mettre à jour l'unité
    if (unitId) {
      // 5. Récupérer toutes les leçons pour cette unité et recalculer
      const lessonProgresses = getAllLessonProgressForUnit(unitId);
      console.log(`Trouvé ${lessonProgresses.length} leçons pour l'unité ${unitId}`);

      // If we have no lesson progresses but this is a completion, create a fake one
      if (lessonProgresses.length === 0) {
        lessonProgresses.push({
          id: lessonId,
          completion_percentage: lessonProgress.percentage,
          is_completed: lessonProgress.completed
        });
      }

      const unitProgress = calculateUnitProgress(lessonProgresses);
      console.log(`Progression d'unité calculée: ${unitProgress.percentage}% (${unitProgress.completed ? 'complète' : 'en cours'})`);

      // 6. Mettre à jour la progression de l'unité
      updateLocalUnitProgress(unitId, unitProgress.percentage, unitProgress.completed);
    }

    console.log("✅ Mise à jour en cascade de la progression terminée avec succès");
  } catch (error) {
    console.error('Erreur lors de la mise à jour en cascade de la progression', error);

    // Try to save minimal progress data even in error case
    try {
      const safeContentId = contentId || 0;
      const safeLessonId = lessonId || 0;

      // Just save direct content progress
      if (safeContentId > 0) {
        updateLocalContentProgress(safeContentId, safeLessonId, percentage, completed);
      }

      // And lesson progress
      if (safeLessonId > 0) {
        updateLocalLessonProgress(safeLessonId, unitId, percentage, completed);
      }
    } catch (fallbackError) {
      console.error('Critical error in progress cascade fallback', fallbackError);
    }
  }
};