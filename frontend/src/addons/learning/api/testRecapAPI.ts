import apiClient from '@/core/api/apiClient';
import { getUserTargetLanguage } from '@/core/utils/languageUtils';

// Define types for TestRecap data
export interface TestRecap {
  id: string;
  title: string;
  description?: string;
  time_limit?: number; // in minutes
  passing_score: number;
  question_count: number;
  lesson_id?: string;
}

export type QuestionType = 
  | 'multiple_choice'
  | 'fill_blank'
  | 'matching'
  | 'reordering'
  | 'vocabulary'
  | 'speaking'
  | 'true_false';

export interface TestRecapQuestion {
  id: string;
  question_type: QuestionType;
  order: number;
}

export interface TestRecapResult {
  id: string;
  test_recap_id: string;
  user_id: string;
  score: number;
  passed: boolean;
  answers: Record<string, any>; // Maps question ID to answer
  completed_at: string;
  time_taken: number; // in seconds
}

/**
 * Creates a demo TestRecap object for use when real data is not available
 */
export const createDemoTestRecap = (id: string | number, language: string = 'en'): TestRecap => {
  return {
    id: id.toString(),
    title: "Demo Test Recap",
    description: "This is a demo test to help you review what you've learned in this lesson.",
    passing_score: 70,
    time_limit: 600, // 10 minutes
    question_count: 6
  };
};

/**
 * Creates demo questions for a test recap
 */
export const createDemoQuestions = (language: string = 'en'): TestRecapQuestion[] => {
  console.log("Generating demo questions for language:", language);
  
  // Adapt content based on language
  const languageSpecificContent: Record<string, any> = {
    'en': {
      hello: "hello",
      wordGo: "go",
      sentence: "I _____ to the market.",
      options: ["go", "goes", "going", "went"],
      fruits: {
        apple: "apple",
        banana: "banana",
        orange: "orange",
        grape: "grape"
      },
      translations: {
        appel: "apple",
        banaan: "banana",
        sinaasappel: "orange",
        druif: "grape"
      },
      house: "house",
      houseDef: "a building for human habitation",
      houseSentence: "I live in a house.",
      colors: {
        blue: "blue",
        table: "table",
        book: "book",
        car: "car"
      },
      dutch: "Dutch is a Germanic language."
    },
    'nl': {
      hello: "hallo",
      wordGo: "ga",
      sentence: "Ik _____ naar de markt.",
      options: ["ga", "gaat", "gaan", "ging"],
      fruits: {
        apple: "appel",
        banana: "banaan",
        orange: "sinaasappel",
        grape: "druif"
      },
      translations: {
        apple: "appel",
        banana: "banaan",
        orange: "sinaasappel",
        grape: "druif"
      },
      house: "huis",
      houseDef: "een gebouw voor menselijke bewoning",
      houseSentence: "Ik woon in een huis.",
      colors: {
        blue: "blauw",
        table: "tafel",
        book: "boek",
        car: "auto"
      },
      dutch: "Nederlands is een Germaanse taal."
    },
    'fr': {
      hello: "bonjour",
      wordGo: "vais",
      sentence: "Je _____ au marché.",
      options: ["vais", "va", "aller", "allons"],
      fruits: {
        apple: "pomme",
        banana: "banane",
        orange: "orange",
        grape: "raisin"
      },
      translations: {
        pomme: "apple",
        banane: "banana",
        orange: "orange",
        raisin: "grape"
      },
      house: "maison",
      houseDef: "un bâtiment pour l'habitation humaine",
      houseSentence: "J'habite dans une maison.",
      colors: {
        blue: "bleu",
        table: "table",
        book: "livre",
        car: "voiture"
      },
      dutch: "Le néerlandais est une langue germanique."
    },
    'es': {
      hello: "hola",
      wordGo: "voy",
      sentence: "Yo _____ al mercado.",
      options: ["voy", "va", "vas", "vamos"],
      fruits: {
        apple: "manzana",
        banana: "plátano",
        orange: "naranja",
        grape: "uva"
      },
      translations: {
        manzana: "apple",
        plátano: "banana",
        naranja: "orange",
        uva: "grape"
      },
      house: "casa",
      houseDef: "un edificio para la habitación humana",
      houseSentence: "Vivo en una casa.",
      colors: {
        blue: "azul",
        table: "mesa",
        book: "libro",
        car: "coche"
      },
      dutch: "El neerlandés es una lengua germánica."
    }
  };
  
  // Default to English if the language isn't available
  const content = languageSpecificContent[language] || languageSpecificContent['en'];
  
  return [
    {
      id: '1',
      question_type: 'multiple_choice',
      order: 1,
      points: 10,
      is_demo: true,
      question: `What is the correct way to say 'hello' in ${language === 'en' ? 'Dutch' : 'English'}?`,
      options: ["Hallo", "Goedemorgen", "Tot ziens", "Dank je"],
      correct_answer: "Hallo"
    },
    {
      id: '2',
      question_type: 'fill_blank',
      order: 2,
      points: 15,
      is_demo: true,
      sentence: content.sentence,
      options: content.options,
      correct_answer: content.wordGo
    },
    {
      id: '3',
      question_type: 'matching',
      order: 3,
      points: 20,
      is_demo: true,
      target_words: Object.keys(content.fruits),
      native_words: Object.values(content.fruits),
      correct_pairs: content.translations
    },
    {
      id: '4',
      question_type: 'vocabulary',
      order: 4,
      points: 10,
      is_demo: true,
      word: content.house,
      definition: content.houseDef,
      example_sentence: content.houseSentence,
      correct_answer: language === 'en' ? "huis" : "house"
    },
    {
      id: '5',
      question_type: 'multiple_choice',
      order: 5,
      points: 10,
      is_demo: true,
      question: "Which of these is a color?",
      options: Object.values(content.colors),
      correct_answer: content.colors.blue
    },
    {
      id: '6',
      question_type: 'true_false',
      order: 6,
      points: 10,
      is_demo: true,
      question: content.dutch,
      options: ["True", "False"],
      correct_answer: "True"
    }
  ] as TestRecapQuestion[];
};

// API service for TestRecap
const testRecapAPI = {
  // Get test details with error handling
  getTest: async (testId: string, language?: string) => {
    try {
      const lang = language || getUserTargetLanguage();
      console.log(`Attempting to fetch TestRecap ${testId} with language ${lang}`);
      
      return await apiClient.get(`/api/v1/course/test-recap/${testId}/?language=${lang}`);
    } catch (error: any) {
      console.warn(`Error fetching TestRecap ${testId}:`, error?.status || error?.message);
      // Re-throw errors so they can be properly handled by the caller
      throw error;
    }
  },

  // Get all questions for a test
  getQuestions: async (testId: string, language?: string) => {
    try {
      const lang = language || getUserTargetLanguage();
      console.log(`Attempting to fetch questions for TestRecap ${testId} with language ${lang}`);
      
      // Use v1 endpoint directly with language parameter
      const url = `/api/v1/course/test-recap/${testId}/questions/?language=${lang}`;
      return await apiClient.get(url);
    } catch (error: any) {
      console.warn(`Error fetching questions for TestRecap ${testId}:`, error?.status || error?.message);
      // Re-throw errors so they can be properly handled by the caller
      throw error;
    }
  },

  // Get specific question data
  getQuestionData: async (questionId: string, language?: string) => {
    try {
      const lang = language || getUserTargetLanguage();
      return await apiClient.get(`/api/v1/course/test-recap/question/${questionId}/?language=${lang}`);
    } catch (error: any) {
      console.warn(`Error fetching question ${questionId}:`, error?.status || error?.message);
      throw error;
    }
  },

  // Submit test answers
  submitTest: async (testId: string, answers: Record<string, any>, timeTaken: number) => {
    try {
      // Use the API to submit answers
      return await apiClient.post(`/api/v1/course/test-recap/${testId}/submit/`, {
        answers,
        time_taken: timeTaken,
      });
    } catch (error: any) {
      console.warn(`Error submitting TestRecap ${testId}:`, error?.status || error?.message);
      // Re-throw errors so they can be properly handled by the caller
      throw error;
    }
  },

  // Get test results
  getResults: async (testId: string) => {
    try {
      return await apiClient.get(`/api/v1/course/test-recap/${testId}/results/`);
    } catch (error: any) {
      console.warn(`Error fetching results for TestRecap ${testId}:`, error?.status || error?.message);
      throw error;
    }
  },

  // Get user's most recent result for a test
  getLatestResult: async (testId: string) => {
    try {
      return await apiClient.get(`/api/v1/course/test-recap/${testId}/latest-result/`);
    } catch (error: any) {
      console.warn(`Error fetching latest result for TestRecap ${testId}:`, error?.status || error?.message);
      throw error;
    }
  },
  
  // Check if a TestRecap exists
  checkExists: async (testId: string): Promise<boolean> => {
    try {
      // Use HEAD request to check if resource exists without fetching full content
      await apiClient.head(`/api/v1/course/test-recap/${testId}/`);
      return true;
    } catch (error: any) {
      // If 404, resource doesn't exist
      if (error?.status === 404) {
        return false;
      }
      
      // For other errors, also indicate it doesn't exist for simplicity
      console.warn(`Error checking if TestRecap ${testId} exists:`, error?.status || error?.message);
      return false;
    }
  },
  
  // Get all TestRecaps for a lesson
  getTestRecapsForLesson: async (lessonId: string | number): Promise<any> => {
    try {
      const response = await apiClient.get(`/api/v1/course/test-recap/?lesson_id=${lessonId}`);
      return response;
    } catch (error: any) {
      console.warn(`Error fetching TestRecaps for lesson ${lessonId}:`, error?.status || error?.message);
      throw error;
    }
  }
};

export default testRecapAPI;