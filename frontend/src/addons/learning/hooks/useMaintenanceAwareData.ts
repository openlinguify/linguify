import { useMemo, useCallback, useRef } from 'react';
import { useExerciseData } from './useExerciseData';
import { useMaintenanceCheck } from './useMaintenanceCheck';
import { isMaintenanceError, isEmptyContent, createMaintenanceError } from '../utils/contentValidation';

interface UseMaintenanceAwareDataOptions<T> {
  lessonId: string | number;
  language?: string;
  contentType: string;
  fetchFunction: (lessonId: string | number, language?: string) => Promise<T>;
  dataValidator?: (data: T) => boolean;
  dataTransformer?: (data: T) => T;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  onMaintenance?: (contentType: string) => void;
}

interface UseMaintenanceAwareDataReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  isMaintenance: boolean;
  contentTypeName: string;
  retry: () => void;
  refresh: () => void;
}

/**
 * Hook qui combine useExerciseData avec la détection de maintenance
 * Gère automatiquement les contenus non disponibles avec des messages appropriés
 */
export function useMaintenanceAwareData<T>({
  lessonId,
  language = 'fr',
  contentType,
  fetchFunction,
  dataValidator,
  dataTransformer,
  onSuccess,
  onError,
  onMaintenance
}: UseMaintenanceAwareDataOptions<T>): UseMaintenanceAwareDataReturn<T> {

  // Use refs to store callbacks to avoid dependency issues
  const onMaintenanceRef = useRef(onMaintenance);
  const dataTransformerRef = useRef(dataTransformer);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  
  // Update refs when callbacks change
  onMaintenanceRef.current = onMaintenance;
  dataTransformerRef.current = dataTransformer;
  onSuccessRef.current = onSuccess;
  onErrorRef.current = onError;

  // Wrapper pour la fonction de fetch qui gère la maintenance
  const maintenanceAwareFetch = useCallback(async (lessonId: string | number, language?: string): Promise<T> => {
    try {
      const result = await fetchFunction(lessonId, language);
      
      // Vérifier si les données sont vides après transformation
      let transformedResult = result;
      if (dataTransformerRef.current) {
        transformedResult = dataTransformerRef.current(result);
      }
      
      // Si les données sont vides, considérer comme maintenance
      if (isEmptyContent(transformedResult)) {
        console.log(`[useMaintenanceAwareData] Empty content detected for ${contentType} lesson ${lessonId}`);
        throw createMaintenanceError(contentType, lessonId);
      }
      
      return result;
    } catch (error) {
      // Si c'est une erreur de maintenance, on la propage telle quelle
      if (isMaintenanceError(error)) {
        throw error;
      }
      
      // Pour les autres erreurs, vérifier si elles indiquent une maintenance
      if (error instanceof Error) {
        if (isMaintenanceError(error)) {
          throw createMaintenanceError(contentType, lessonId);
        }
      }
      
      // Sinon, propager l'erreur originale
      throw error;
    }
  }, [fetchFunction, contentType]);

  // Memoize the error handler to avoid infinite re-renders
  const handleError = useCallback((error: Error) => {
    if (isMaintenanceError(error)) {
      onMaintenanceRef.current?.(contentType);
    } else {
      onErrorRef.current?.(error);
    }
  }, [contentType]);

  // Utiliser useExerciseData avec notre wrapper
  const {
    data,
    loading,
    error,
    retry,
    refresh
  } = useExerciseData({
    lessonId,
    language,
    fetchFunction: maintenanceAwareFetch,
    dataValidator,
    dataTransformer,
    onSuccess: onSuccessRef.current,
    onError: handleError
  });

  // Utiliser useMaintenanceCheck pour déterminer l'état de maintenance
  const maintenanceCheck = useMaintenanceCheck({
    error,
    data,
    contentType
  });

  return useMemo(() => ({
    data,
    loading,
    error,
    isMaintenance: maintenanceCheck.shouldShowMaintenance,
    contentTypeName: maintenanceCheck.contentTypeName,
    retry,
    refresh
  }), [
    data,
    loading,
    error,
    maintenanceCheck.shouldShowMaintenance,
    maintenanceCheck.contentTypeName,
    retry,
    refresh
  ]);
}

export default useMaintenanceAwareData;