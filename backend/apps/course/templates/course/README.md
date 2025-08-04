# 📚 Course App - Dashboard d'Apprentissage

Interface principale de l'application Course avec système d'onglets pour l'apprentissage des langues.

## 📁 Structure des fichiers

```
course/templates/course/
├── dashboard.html               # Template principal du dashboard avec onglets
└── README.md                    # Cette documentation
```

## 🔧 Fonctionnalités

### Template principal (`dashboard.html`)
- Étend `saas_web/base.html` (header système Linguify)
- Interface à onglets avec Bootstrap 5
- Contient 3 onglets principaux :
  - **Mon apprentissage** : Progression utilisateur, cours inscrits, leçons à continuer
  - **Marketplace** : Cours disponibles organisés par niveau (A1-C2)
  - **Parcourir** : Navigation par catégories (langues, types de cours)

## ✨ Fonctionnalités des onglets

### 📖 Mon apprentissage
- Section de bienvenue avec stats utilisateur (XP, niveau, série)
- Carte "Reprendre l'apprentissage" pour continuer les leçons
- Grille des cours inscrits avec progression
- Filtre par statut (tous, en cours, terminés, pas commencés)

### 🏪 Marketplace
- Statistiques du marketplace (cours disponibles, gratuits, professeurs)
- Cours organisés par niveau (A1, A2, B1, B2, C1, C2)
- Cartes de cours avec prix, évaluations, nombre d'étudiants
- Actions d'inscription/achat selon le statut

### 🗂️ Parcourir
- Catégories par langue (Français, Anglais, Espagnol, etc.)
- Types de cours (Vocabulaire, Grammaire, Conversation, Culture, Professionnel, Examens)
- Navigation rapide vers le marketplace avec filtres

## 🎨 Styles et CSS

Le template utilise :
- Bootstrap 5 pour la structure responsive
- Font Awesome pour les icônes
- CSS custom pour les cartes de cours et animations
- Style fixes pour l'affichage correct des onglets

## 🔧 Fonctionnalités JavaScript

- Gestion des onglets Bootstrap
- Recherche en temps réel dans les cours
- Filtres et animations
- Raccourcis clavier (Ctrl+K pour recherche, flèches pour navigation)

## 📊 Données affichées

Le dashboard affiche des données depuis le backend :
- `user_stats` : Statistiques de progression utilisateur
- `marketplace_courses` : Cours disponibles groupés par niveau
- `marketplace_stats` : Statistiques générales du marketplace
- `my_courses` : Cours auxquels l'utilisateur est inscrit
- `continue_learning` : Leçons à reprendre

## 🌐 URLs

- `/learning/` : Dashboard principal
- `/learning/demo/` : Version de démonstration
- `/learning/test-data/` : Endpoint pour tester les données

---

Interface d'apprentissage complète et responsive pour la plateforme Linguify ! 🚀