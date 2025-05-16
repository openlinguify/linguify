# Refactoring pour la logique TestRecap

## Problème identifié

Après analyse du code, nous avons identifié plusieurs problèmes liés à la duplication de la logique métier entre le frontend et le backend pour les fonctionnalités TestRecap :

1. Duplication de fonctionnalités entre `courseAPI.ts` et `testRecapAPI.ts`
2. Logique métier complexe implémentée côté client qui devrait être côté serveur
3. Fallbacks et gestion d'erreurs dupliqués

## Améliorations apportées

1. **Simplification de la méthode `getTestRecapIdFromContentLesson` dans courseAPI.ts** :
   - Réutilisation de `testRecapAPI.getTestRecapForContentLesson` pour éviter la duplication de code
   - Suppression de la logique de fallback côté client qui est maintenant gérée par le backend
   - Import dynamique de testRecapAPI pour éviter les problèmes de dépendances circulaires

## Recommandations pour la suite

Pour une refactorisation complète, nous recommandons les actions suivantes :

1. **Dépréciez les méthodes TestRecap dans courseAPI** :
   - Marquez-les comme obsolètes
   - Ajoutez un commentaire dirigeant vers testRecapAPI.ts
   - À terme, supprimez-les complètement

2. **Centralisez toute la logique TestRecap dans testRecapAPI.ts** :
   - Déplacez les types et interfaces
   - Assurez une API cohérente
   - Documentez clairement l'utilisation recommandée

3. **Éliminez la duplication de code dans les composants** :
   - Mettez à jour les composants pour utiliser uniquement testRecapAPI
   - Simplifiez la gestion des erreurs et des cas par défaut

4. **Standardisez la réponse d'erreur côté backend** :
   - Utilisez un format d'erreur cohérent
   - Ajoutez des codes d'erreur spécifiques
   - Incluez suffisamment de contexte pour le débogage

## Implémentation actuelle

Le schéma actuel a été simplifié comme suit :

1. Le backend (`TestRecapViewSet.for_content_lesson`) implémente maintenant une logique complète pour trouver un TestRecap associé à un ContentLesson, avec plusieurs stratégies :
   - Recherche par correspondance de titre
   - Recherche via la leçon parente
   - Recherche via les leçons de contenu "sœurs"
   - Recherche dans l'unité parente
   - Fallback vers le premier TestRecap disponible

2. Le frontend utilise désormais une approche plus simple :
   - Appel à l'endpoint `/api/v1/course/test-recap/for_content_lesson/?content_lesson_id=X`
   - Gestion simple des réponses
   - Génération de contenu démo uniquement en dernier recours

Ce changement améliore la maintenabilité en centralisant la logique dans le backend et en simplifiant le code frontend.