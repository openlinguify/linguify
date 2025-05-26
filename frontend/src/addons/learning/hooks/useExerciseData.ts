import { useState, useEffect, useCallback, useRef } from 'react';

interface UseExerciseDataOptions<T> {
  lessonId: string | number;
  language?: string;
  fetchFunction: (lessonId: string | number, language?: string) => Promise<T>;
  dataValidator?: (data: T) => boolean;
  dataTransformer?: (data: T) => T;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

interface UseExerciseDataReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  retry: () => void;
  refresh: () => void;
}

/**
 * Hook personnalisé pour gérer le chargement, la validation et la transformation 
 * des données d'exercices de manière unifiée
 */
export function useExerciseData<T>({
  lessonId,
  language = 'fr',
  fetchFunction,
  dataValidator,
  dataTransformer,
  onSuccess,
  onError
}: UseExerciseDataOptions<T>): UseExerciseDataReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Use refs to store callbacks to avoid dependency issues
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  const dataValidatorRef = useRef(dataValidator);
  const dataTransformerRef = useRef(dataTransformer);

  // Update refs when callbacks change
  onSuccessRef.current = onSuccess;
  onErrorRef.current = onError;
  dataValidatorRef.current = dataValidator;
  dataTransformerRef.current = dataTransformer;

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log(`[useExerciseData] Fetching data for lesson ${lessonId} with language ${language}`);
      
      // Récupérer les données
      let result = await fetchFunction(lessonId, language);
      
      console.log(`[useExerciseData] Raw data received:`, result);
      
      // Transformer les données si nécessaire
      if (dataTransformerRef.current) {
        result = dataTransformerRef.current(result) as Awaited<T>;
        console.log(`[useExerciseData] Transformed data:`, result);
      }
      
      // Valider les données si un validateur est fourni
      if (dataValidatorRef.current && !dataValidatorRef.current(result)) {
        throw new Error('Les données reçues ne sont pas valides');
      }
      
      setData(result);
      onSuccessRef.current?.(result);
      
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Erreur lors du chargement des données');
      console.error(`[useExerciseData] Error:`, error);
      setError(error);
      onErrorRef.current?.(error);
    } finally {
      setLoading(false);
    }
  }, [lessonId, language, fetchFunction]);

  const retry = useCallback(() => {
    fetchData();
  }, [fetchData]);

  const refresh = useCallback(() => {
    setData(null);
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (lessonId) {
      fetchData();
    }
  }, [fetchData, lessonId]);

  return {
    data,
    loading,
    error,
    retry,
    refresh
  };
}

export default useExerciseData;