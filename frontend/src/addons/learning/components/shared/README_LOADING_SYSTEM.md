# Système de Chargement Harmonisé - Guide d'utilisation

## Vue d'ensemble

Ce système permet d'avoir un chargement unifié et élégant dans toute l'application d'apprentissage, éliminant les multiples indicateurs de chargement qui se superposent.

## Composants principaux

### 1. GlobalLoadingProvider
Fournit le contexte global de chargement pour toute l'application.

### 2. useSmoothTransition
Hook pour gérer les transitions et navigations avec chargement harmonisé.

### 3. useExerciseLoading
Hook spécialisé pour les exercices.

## Utilisation

### Dans une page principale :
```tsx
import { GlobalLoadingProvider } from '@/addons/learning/components/shared/GlobalLoadingProvider';

export default function LearningPage() {
  return (
    <GlobalLoadingProvider>
      <YourContent />
    </GlobalLoadingProvider>
  );
}
```

### Pour les navigations :
```tsx
import { useSmoothTransition } from '@/addons/learning/hooks/useSmoothTransition';

function MyComponent() {
  const { navigateWithTransition } = useSmoothTransition();

  const handleClick = () => {
    navigateWithTransition('/learning/exercise/123', {
      loadingText: 'Chargement de l\'exercice...',
      stage: 'exercise',
      minDuration: 600
    });
  };

  return <button onClick={handleClick}>Aller à l'exercice</button>;
}
```

### Pour les exercices :
```tsx
import { useExerciseLoading } from '@/addons/learning/components/shared/ExerciseLoadingWrapper';

function MyExercise() {
  const { startExerciseLoading, finishExerciseLoading, updateExerciseProgress } = useExerciseLoading();

  useEffect(() => {
    const loadExercise = async () => {
      startExerciseLoading('matching');
      
      updateExerciseProgress(30, 'Chargement des données...');
      await loadData();
      
      updateExerciseProgress(70, 'Préparation de l\'interface...');
      await setupUI();
      
      finishExerciseLoading();
    };

    loadExercise();
  }, []);

  return <div>Mon exercice</div>;
}
```

### Pour des opérations asynchrones :
```tsx
import { useSmoothTransition } from '@/addons/learning/hooks/useSmoothTransition';

function MyComponent() {
  const { executeWithTransition } = useSmoothTransition();

  const handleSave = async () => {
    await executeWithTransition(
      () => saveProgress(),
      {
        loadingText: 'Sauvegarde en cours...',
        stage: 'saving',
        minDuration: 500
      }
    );
  };

  return <button onClick={handleSave}>Sauvegarder</button>;
}
```

## Avantages

1. **Chargement unifié** : Plus de superposition d'indicateurs
2. **Transitions fluides** : Durée minimale pour éviter les flashes
3. **Feedback riche** : Progression et étapes détaillées
4. **Performance** : Préchargement et optimisations intégrées
5. **Expérience utilisateur** : Interface cohérente et professionnelle

## Stages disponibles

- `init` : Initialisation de l'application
- `units` : Chargement des unités
- `lessons` : Chargement des leçons
- `progress` : Récupération de la progression
- `content` : Préparation du contenu
- `exercise` : Préparation d'un exercice
- `navigation` : Navigation en cours
- `saving` : Sauvegarde en cours

## Migration des composants existants

1. Supprimer les `useState([loading, setLoading])` locaux
2. Supprimer les indicateurs de chargement personnalisés
3. Remplacer `router.push()` par `navigateWithTransition()`
4. Utiliser `executeWithTransition()` pour les opérations async
5. Wrapper les exercices avec `useExerciseLoading()`