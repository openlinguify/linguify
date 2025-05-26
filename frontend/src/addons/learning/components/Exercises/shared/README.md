# Système d'Exercices Unifié

Ce système fournit une architecture modulaire et réutilisable pour tous les types d'exercices dans l'application Linguify.

## 🏗️ Architecture

### Composants de Base

#### `BaseExerciseWrapper`
- **Responsabilité** : Structure commune pour tous les exercices
- **Fonctionnalités** :
  - Gestion des états (chargement, erreur, succès)
  - Navigation avec ExerciseNavBar
  - Animations standardisées
  - Gestion des erreurs avec retry

#### `ExerciseHeader`
- **Responsabilité** : En-tête standardisé avec progression et statistiques
- **Fonctionnalités** :
  - Barre de progression visuelle
  - Affichage du temps et du score
  - Support pour timer et limite de temps
  - Design responsive

#### `ExerciseControls`
- **Responsabilité** : Contrôles de navigation et actions
- **Fonctionnalités** :
  - Navigation (précédent/suivant)
  - Actions principales (soumettre, recommencer)
  - Contrôles de timer
  - Validation et messages d'erreur

### Hooks Personnalisés

#### `useExerciseData`
- **Responsabilité** : Chargement et transformation des données d'exercices
- **Fonctionnalités** :
  - Appel API avec gestion d'erreurs
  - Validation des données
  - Transformation automatique
  - Support pour retry et refresh

#### `useExerciseSession`
- **Responsabilité** : Gestion d'une session d'exercice
- **Fonctionnalités** :
  - Progression et navigation
  - Scoring et statistiques
  - Timer avec limite de temps
  - Calculs automatiques (précision, score)

### Utilitaires

#### `dataTransformers`
- **Responsabilité** : Normalisation des données API
- **Fonctionnalités** :
  - Transformateurs spécialisés par type d'exercice
  - Validation des structures de données
  - Gestion des formats multiples
  - Types TypeScript standardisés

## 🚀 Utilisation

### Exemple de Base

```tsx
import React from 'react';
import {
  BaseExerciseWrapper,
  ExerciseHeader,
  ExerciseControls,
  useExerciseData,
  useExerciseSession
} from './shared';

export const MyExerciseWrapper = ({ lessonId, onComplete }) => {
  // Chargement des données
  const { data, loading, error, retry } = useExerciseData({
    lessonId,
    fetchFunction: myAPI.getData,
    dataValidator: myValidator,
    dataTransformer: myTransformer
  });

  // Gestion de la session
  const session = useExerciseSession({
    totalItems: data?.length || 0,
    onComplete
  });

  return (
    <BaseExerciseWrapper
      loading={loading}
      error={error}
      onRetry={retry}
    >
      <ExerciseHeader
        title="Mon Exercice"
        currentStep={session.currentIndex + 1}
        totalSteps={data?.length || 0}
        progress={session.progress}
        score={session.score}
      />
      
      {/* Votre contenu d'exercice ici */}
      
      <ExerciseControls
        onNext={session.nextItem}
        onPrevious={session.previousItem}
        onComplete={session.complete}
      />
    </BaseExerciseWrapper>
  );
};
```

### Transformateur de Données

```tsx
import { transformMatchingData, validators } from './shared';

const { data } = useExerciseData({
  lessonId,
  fetchFunction: courseAPI.getMatchingExercises,
  dataValidator: validators.matchingPairs,
  dataTransformer: transformMatchingData
});
```

## 📊 Avantages

### 1. **Réutilisabilité**
- Composants modulaires réutilisables
- Hooks partagés pour la logique commune
- Moins de duplication de code

### 2. **Maintenabilité**
- Architecture claire et séparée
- Types TypeScript stricts
- Documentation intégrée

### 3. **Consistance**
- Interface utilisateur unifiée
- Comportements standardisés
- Animations cohérentes

### 4. **Extensibilité**
- Facilité d'ajout de nouveaux types d'exercices
- Système de hooks composables
- Transformateurs de données flexibles

### 5. **Performance**
- Chargement optimisé des données
- Gestion d'erreurs robuste
- Timer précis et performant

## 🔧 Migration

Pour migrer un exercice existant vers le nouveau système :

1. **Identifier les données** : Créer un transformateur approprié
2. **Extraire la logique** : Utiliser les hooks fournis
3. **Remplacer les composants** : Utiliser BaseExerciseWrapper, ExerciseHeader, ExerciseControls
4. **Tester** : Vérifier que toutes les fonctionnalités sont préservées

## 🎯 Types d'Exercices Supportés

- ✅ **Matching** : Association de mots/phrases
- ✅ **Vocabulary** : Étude de vocabulaire
- 🔄 **Speaking** : Exercices de prononciation
- 🔄 **Multiple Choice** : Questions à choix multiples
- 🔄 **Fill Blank** : Textes à trous
- 🔄 **Reordering** : Remise en ordre
- 🔄 **Test Recap** : Tests récapitulatifs

## 📝 Bonnes Pratiques

1. **Toujours utiliser les hooks fournis** pour la logique commune
2. **Créer des transformateurs spécifiques** pour chaque type de données
3. **Respecter les interfaces TypeScript** pour la cohérence
4. **Tester les états d'erreur** et de chargement
5. **Documenter les nouvelles fonctionnalités** ajoutées