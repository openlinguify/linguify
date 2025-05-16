# Carnet de Notes Linguify

## Présentation

Cette version simplifiée du carnet de notes a été créée pour résoudre les problèmes de persistance des données qui survenaient avec la version précédente. L'application d'origine avait des problèmes lorsqu'un utilisateur entrait des données, puis rechargeait la page - les données n'étaient pas correctement sauvegardées ou récupérées du backend.

## Problèmes Résolus

1. **Persistance des données** : Les notes sont maintenant sauvegardées correctement dans la base de données et récupérées à chaque chargement de page.

2. **Gestion d'erreurs robuste** : Ajout d'une meilleure gestion des erreurs API, avec des messages clairs pour l'utilisateur.

3. **Simplicité de l'interface** : L'interface a été simplifiée pour se concentrer sur les fonctionnalités essentielles (titre, contenu, traduction).

4. **Validation des données** : Vérification systématique que les données sont complètes et bien formatées avant l'envoi à l'API.

## Structure des Fichiers

- `SimpleNotebook.tsx` : Composant principal qui intègre la liste et l'éditeur.
- `SimpleNoteList.tsx` : Liste des notes avec recherche et filtrage.
- `SimpleNoteEditor.tsx` : Éditeur de note simplifié avec onglets pour le contenu et la traduction.
- `simpleNotebookAPI.ts` : API client simplifié et robuste qui gère correctement les erreurs et les données malformées.

## Fonctionnalités Disponibles

- Création, édition et suppression de notes
- Recherche et filtrage de notes
- Sauvegarde automatique des modifications
- Affichage des notes par langue
- Interface simplifiée et intuitive
- Gestion des erreurs API avec feedback utilisateur

## Fonctionnalités Avancées (Temporairement Désactivées)

Pour garantir la fiabilité de l'application, certaines fonctionnalités avancées ont été temporairement désactivées :

- Gestion complète des catégories et tags
- Système de révision avec planification
- Phrases d'exemple avancées
- Mots associés et prononciation
- Mode d'apprentissage adaptatif

Ces fonctionnalités seront réintégrées progressivement une fois que la stabilité de base sera confirmée.

## Guide d'Utilisation

1. Depuis la page principale, cliquez sur "Créer une nouvelle note" pour ajouter une note.
2. Entrez un titre, sélectionnez une langue et cliquez sur "Créer".
3. Utilisez les onglets "Contenu" et "Traduction" pour ajouter du texte.
4. Cliquez sur "Enregistrer" pour sauvegarder vos modifications.
5. Pour rechercher des notes, utilisez le champ de recherche en haut de la liste.

## Développement Futur

La version simplifiée servira de base solide pour reconstruire progressivement les fonctionnalités plus avancées, tout en garantissant que la persistance des données et la fiabilité restent prioritaires.

---

Pour toute question ou suggestion, veuillez contacter l'équipe de développement.