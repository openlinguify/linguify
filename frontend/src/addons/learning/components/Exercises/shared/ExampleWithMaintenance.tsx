import React from 'react';
import { useRouter } from 'next/navigation';
import {
  BaseExerciseWrapper,
  ExerciseHeader,
  ExerciseControls,
  useMaintenanceAwareData,
  useExerciseSession,
  transformVocabularyData,
  validators
} from './index';
import courseAPI from '../../../api/courseAPI';

interface ExampleExerciseProps {
  lessonId: string;
  language?: string;
  unitId?: string;
  onComplete?: () => void;
}

/**
 * EXEMPLE d'utilisation du système unifié avec maintenance automatique
 * 
 * Ce composant montre comment créer un exercice en quelques lignes
 * avec gestion automatique de la maintenance, erreurs, et états
 */
export const ExampleExercise: React.FC<ExampleExerciseProps> = ({
  lessonId,
  language = 'fr',
  unitId,
  onComplete
}) => {
  const router = useRouter();

  // 🚀 TOUT LE SYSTÈME EN 3 HOOKS !
  
  // 1. Chargement des données avec détection automatique de maintenance
  const {
    data,
    loading,
    error,
    isMaintenance,
    contentTypeName,
    retry
  } = useMaintenanceAwareData({
    lessonId,
    language,
    contentType: 'vocabulary', // Type pour les messages de maintenance
    fetchFunction: async (lessonId: string | number, language?: string) => {
      const response = await courseAPI.getVocabularyLesson(lessonId);
      return response.data.vocabulary_items || [];
    },
    dataValidator: validators.vocabularyItems,
    dataTransformer: transformVocabularyData,
    onSuccess: (data) => console.log('✅ Données chargées:', data.length, 'items'),
    onMaintenance: (type) => console.log('🔧 Maintenance détectée pour:', type)
  });

  // 2. Gestion de la session d'exercice (progression, score, timer)
  const session = useExerciseSession({
    totalItems: data?.length || 0,
    passingScore: 80,
    onComplete: (result) => {
      console.log('🎉 Exercice terminé:', result);
      onComplete?.();
    }
  });

  // 3. Rendu automatique avec tous les états gérés
  return (
    <BaseExerciseWrapper
      unitId={unitId}
      loading={loading}
      error={error}
      isMaintenance={isMaintenance}
      contentTypeName={contentTypeName}
      lessonId={lessonId}
      onRetry={retry}
      onBack={() => router.push('/learning')}
      className="bg-gradient-to-br from-purple-50 to-pink-100 dark:from-gray-900 dark:to-purple-900"
    >
      {/* En-tête avec progression automatique */}
      <ExerciseHeader
        title="Mon Exercice Exemple"
        instructions="Ceci est un exemple d'exercice avec maintenance automatique"
        currentStep={session.currentIndex + 1}
        totalSteps={data?.length || 0}
        progress={session.progress}
        timeSpent={session.timeSpent}
        score={session.score}
        accuracy={session.accuracy}
      />

      {/* Contenu principal de votre exercice */}
      <div className="flex-1 p-4">
        <div className="max-w-4xl mx-auto">
          {data && (
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-xl font-semibold mb-4">
                Item {session.currentIndex + 1}: {data[session.currentIndex]?.target_word}
              </h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                {data[session.currentIndex]?.native_word}
              </p>
              
              {/* Exemple d'action */}
              <button
                onClick={() => {
                  session.recordAnswer(true); // Marquer comme correct
                  session.nextItem(); // Passer au suivant
                }}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
              >
                J'ai appris ce mot
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Contrôles avec navigation automatique */}
      <ExerciseControls
        canGoBack={session.currentIndex > 0}
        canGoForward={session.currentIndex < (data?.length || 0) - 1}
        onPrevious={session.previousItem}
        onNext={session.nextItem}
        onComplete={session.complete}
        isValid={data !== null}
        isLastItem={session.currentIndex === (data?.length || 0) - 1}
      />
    </BaseExerciseWrapper>
  );
};

/*
🎯 RÉSULTAT DE CET EXEMPLE :

✅ Si les données existent → Exercice normal
🔧 Si pas de données → Maintenance automatique avec message approprié  
❌ Si erreur technique → Écran d'erreur avec retry
⏳ Pendant le chargement → Spinner animé

🚀 TOUT ÇA EN ~80 LIGNES AU LIEU DE ~200+ !

📊 AVANTAGES :
- Détection automatique de maintenance
- Messages d'erreur appropriés selon le contexte
- Interface cohérente et professionnelle
- Code réutilisable et maintenable
- TypeScript strict pour éviter les erreurs
*/

export default ExampleExercise;