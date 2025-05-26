/**
 * Utilitaires pour transformer et normaliser les données API
 * en formats standardisés pour les composants d'exercices
 * Inclut la détection automatique de contenu en maintenance
 */

import { createMaintenanceError } from './contentValidation';

// Types standardisés pour les exercices
export interface StandardizedPair {
  id: string;
  left: string;
  right: string;
  isMatched?: boolean;
}

export interface StandardizedVocabularyItem {
  id: string;
  target_word: string;
  native_word?: string;
  pronunciation?: string;
  example_sentence?: string;
  image_url?: string;
}

export interface StandardizedQuestion {
  id: string;
  type: 'multiple_choice' | 'fill_blank' | 'matching' | 'reordering' | 'vocabulary' | 'speaking';
  question: string;
  options?: string[];
  correct_answer?: string;
  points?: number;
  data?: Record<string, any>;
}

/**
 * Transformateur pour les données de matching exercises
 */
export const transformMatchingData = (rawData: any): StandardizedPair[] => {
  console.log('[transformMatchingData] Processing raw data:', rawData);
  
  // Gestion de différentes structures de données
  let exercises = [];
  
  if (Array.isArray(rawData)) {
    exercises = rawData;
  } else if (rawData?.results && Array.isArray(rawData.results)) {
    exercises = rawData.results;
  } else if (rawData?.data && Array.isArray(rawData.data)) {
    exercises = rawData.data;
  } else if (rawData && typeof rawData === 'object') {
    exercises = [rawData];
  }
  
  if (exercises.length === 0) {
    throw new Error('Aucun exercice de matching trouvé');
  }
  
  const firstExercise = exercises[0];
  let pairs: StandardizedPair[] = [];
  
  // Recherche des données de pairs dans différentes structures
  if (firstExercise.exercise_data?.target_words && firstExercise.exercise_data?.native_words) {
    const targetWords = firstExercise.exercise_data.target_words;
    const nativeWords = firstExercise.exercise_data.native_words;
    
    if (Array.isArray(targetWords) && Array.isArray(nativeWords) && 
        targetWords.length === nativeWords.length) {
      pairs = targetWords.map((target: string, index: number) => ({
        id: `pair-${index}`,
        left: target,
        right: nativeWords[index],
        isMatched: false
      }));
    }
  } else if (firstExercise.target_words && firstExercise.native_words) {
    const targetWords = firstExercise.target_words;
    const nativeWords = firstExercise.native_words;
    
    if (Array.isArray(targetWords) && Array.isArray(nativeWords) && 
        targetWords.length === nativeWords.length) {
      pairs = targetWords.map((target: string, index: number) => ({
        id: `pair-${index}`,
        left: target,
        right: nativeWords[index],
        isMatched: false
      }));
    }
  } else if (firstExercise.pairs && Array.isArray(firstExercise.pairs)) {
    pairs = firstExercise.pairs.map((pair: any, index: number) => ({
      id: `pair-${index}`,
      left: pair.left || pair.target || '',
      right: pair.right || pair.native || '',
      isMatched: false
    }));
  }
  
  if (pairs.length === 0) {
    throw createMaintenanceError('matching');
  }
  
  console.log('[transformMatchingData] Generated pairs:', pairs);
  return pairs;
};

/**
 * Transformateur pour les données de vocabulaire
 */
export const transformVocabularyData = (rawData: any): StandardizedVocabularyItem[] => {
  console.log('[transformVocabularyData] Processing raw data:', rawData);
  
  let items: StandardizedVocabularyItem[] = [];
  
  // Gestion de différentes structures de réponse
  if (rawData?.results && Array.isArray(rawData.results)) {
    items = rawData.results;
  } else if (Array.isArray(rawData)) {
    items = rawData;
  } else if (rawData?.vocabulary_items && Array.isArray(rawData.vocabulary_items)) {
    items = rawData.vocabulary_items;
  }
  
  // Normalisation des items
  const standardizedItems = items.map((item: any, index: number) => ({
    id: item.id?.toString() || `vocab-${index}`,
    target_word: item.target_word || item.word || item.term || '',
    native_word: item.native_word || item.translation || item.definition || '',
    pronunciation: item.pronunciation || '',
    example_sentence: item.example_sentence || item.example || '',
    image_url: item.image_url || item.image || ''
  })).filter(item => item.target_word); // Filtrer les items sans mot cible
  
  if (standardizedItems.length === 0) {
    throw createMaintenanceError('vocabulary');
  }
  
  console.log('[transformVocabularyData] Standardized items:', standardizedItems);
  return standardizedItems;
};

/**
 * Transformateur pour les données de speaking exercises
 */
export const transformSpeakingData = (rawData: any) => {
  console.log('[transformSpeakingData] Processing raw data:', rawData);
  
  const vocabularyItems = transformVocabularyData(rawData);
  
  return {
    vocabulary_items: vocabularyItems,
    title: 'Exercice de Prononciation',
    instructions: 'Pratiquez la prononciation des mots suivants'
  };
};

/**
 * Transformateur pour les données de test recap
 */
export const transformTestRecapData = (rawData: any): StandardizedQuestion[] => {
  console.log('[transformTestRecapData] Processing raw data:', rawData);
  
  let questions = [];
  
  if (rawData?.questions && Array.isArray(rawData.questions)) {
    questions = rawData.questions;
  } else if (Array.isArray(rawData)) {
    questions = rawData;
  }
  
  const standardizedQuestions = questions.map((question: any) => ({
    id: question.id?.toString() || Math.random().toString(36).substr(2, 9),
    type: question.question_type || question.type || 'multiple_choice',
    question: question.question || question.text || '',
    options: question.options || [],
    correct_answer: question.correct_answer || '',
    points: question.points || 1,
    data: question.question_data || question.data || {}
  }));
  
  if (standardizedQuestions.length === 0) {
    throw createMaintenanceError('test_recap');
  }
  
  console.log('[transformTestRecapData] Standardized questions:', standardizedQuestions);
  return standardizedQuestions;
};

/**
 * Validateurs de données
 */
export const validators = {
  matchingPairs: (data: StandardizedPair[]): boolean => {
    return Array.isArray(data) && data.length > 0 && 
           data.every(pair => pair.left && pair.right);
  },
  
  vocabularyItems: (data: StandardizedVocabularyItem[]): boolean => {
    return Array.isArray(data) && data.length > 0 && 
           data.every(item => item.target_word);
  },
  
  questions: (data: StandardizedQuestion[]): boolean => {
    return Array.isArray(data) && data.length > 0 && 
           data.every(q => q.id && q.type);
  }
};

export default {
  transformMatchingData,
  transformVocabularyData,
  transformSpeakingData,
  transformTestRecapData,
  validators
};