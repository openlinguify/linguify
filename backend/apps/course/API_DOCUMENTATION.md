# 📚 Course API Documentation

## 🚀 Overview

L'API REST Course fournit un accès complet aux fonctionnalités d'apprentissage de Linguify, incluant la gestion des cours, le suivi de progression, les exercices et l'analytics.

## 🔗 Base URL

```
/api/v1/course/
```

## 🔑 Authentication

Toutes les endpoints nécessitent une authentification. Utilisez la session Django ou les tokens DRF.

```bash
# Exemple avec curl
curl -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     https://your-domain.com/api/v1/course/units/
```

## 📋 Endpoints Principaux

### 🏗️ Core Content

#### Units (Unités)
- `GET /units/` - Liste toutes les unités avec progression utilisateur
- `GET /units/{id}/` - Détails d'une unité spécifique
- `GET /units/recommended/` - Unités recommandées pour l'utilisateur
- `GET /units/{id}/progress/` - Progression détaillée d'une unité
- `POST /units/{id}/reset_progress/` - Remet à zéro la progression

#### Chapters (Chapitres)
- `GET /chapters/` - Liste tous les chapitres
- `GET /chapters/{id}/` - Détails d'un chapitre
- `GET /chapters/by_unit/?unit_id={id}` - Chapitres d'une unité
- `GET /chapters/{id}/progress/` - Progression d'un chapitre

#### Lessons (Leçons)
- `GET /lessons/` - Liste toutes les leçons
- `GET /lessons/{id}/` - Détails d'une leçon
- `GET /lessons/by_chapter/?chapter_id={id}` - Leçons d'un chapitre
- `GET /lessons/recent/` - Leçons récemment consultées
- `POST /lessons/{id}/complete/` - Marquer une leçon comme terminée
- `GET /lessons/{id}/content/` - Contenu complet d'une leçon

### 📚 Content & Exercises

#### Vocabulary (Vocabulaire)
- `GET /vocabulary/` - Liste du vocabulaire
- `GET /vocabulary/random/?count=10` - Vocabulaire aléatoire pour la pratique
- `GET /vocabulary/by_lesson/?lesson_id={id}` - Vocabulaire d'une leçon

#### Exercises (Exercices)
- `POST /exercises/submit/` - Soumettre une réponse d'exercice

### 📊 Progress & Analytics

#### User Progress (Progression Utilisateur)
- `GET /progress/` - Progression globale de l'utilisateur
- `GET /progress/dashboard/` - Données pour le dashboard
- `GET /progress/statistics/` - Statistiques détaillées

#### Analytics (Analytics)
- `GET /analytics/` - Analytics d'apprentissage de l'utilisateur
- `GET /analytics/daily_stats/?days=30` - Statistiques quotidiennes

### 🎓 Course Management

#### Enrollments (Inscriptions)
- `GET /enrollments/` - Cours où l'utilisateur est inscrit
- `POST /enrollments/enroll/` - S'inscrire à un cours
- `POST /enrollments/{id}/unenroll/` - Se désinscrire d'un cours

#### Reviews (Avis)
- `GET /reviews/` - Avis de l'utilisateur
- `POST /reviews/` - Créer un nouvel avis

## 📝 Exemples d'Utilisation

### Obtenir le Dashboard Utilisateur

```bash
curl -X GET \
  "https://your-domain.com/api/v1/course/progress/dashboard/" \
  -H "Authorization: Token YOUR_TOKEN"
```

**Réponse:**
```json
{
  "user_progress": {
    "overall_progress": 45,
    "completed_lessons": 23,
    "total_lessons": 51,
    "streak_days": 7,
    "total_xp": 1250,
    "level": "A2"
  },
  "recent_lessons": [...],
  "unit_progress": [...],
  "recommended_lessons": [...]
}
```

### Compléter une Leçon

```bash
curl -X POST \
  "https://your-domain.com/api/v1/course/lessons/123/complete/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": 123,
    "time_spent": 1800,
    "score": 85.5,
    "exercises_completed": [
      {"type": "multiple_choice", "correct": true},
      {"type": "vocabulary", "score": 90}
    ]
  }'
```

### Soumettre un Exercice

```bash
curl -X POST \
  "https://your-domain.com/api/v1/course/exercises/submit/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_type": "multiple_choice",
    "exercise_id": 456,
    "answer": {"selected_option": "B"},
    "time_spent": 30
  }'
```

### Obtenir du Vocabulaire Aléatoire

```bash
curl -X GET \
  "https://your-domain.com/api/v1/course/vocabulary/random/?count=5&difficulty=beginner" \
  -H "Authorization: Token YOUR_TOKEN"
```

## 🔍 Filtres et Paramètres

### Vocabulary Filters
- `difficulty`: `beginner`, `intermediate`, `advanced`
- `word_type`: `noun`, `verb`, `adjective`, `adverb`
- `search`: Recherche textuelle
- `lesson_id`: Filtrer par leçon

### Pagination
Toutes les listes supportent la pagination Django REST Framework:
- `?page=2`
- `?page_size=20`

### Formats
Tous les endpoints supportent JSON et API browsable:
- `?format=json`
- `?format=api`

## 🎯 Types d'Exercices Supportés

1. **multiple_choice** - Questions à choix multiples
2. **matching** - Exercices d'association
3. **fill_blank** - Exercices à trous
4. **grammar_reordering** - Réorganisation grammaticale
5. **speaking** - Exercices de prononciation

## 📈 Codes de Statut

- `200 OK` - Succès
- `201 Created` - Ressource créée
- `400 Bad Request` - Données invalides
- `401 Unauthorized` - Authentification requise
- `403 Forbidden` - Permissions insuffisantes
- `404 Not Found` - Ressource introuvable
- `500 Internal Server Error` - Erreur serveur

## 🔧 Headers Requis

```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
Accept: application/json
```

## 📊 Structure des Réponses

### Réponse de Succès
```json
{
  "id": 1,
  "title": "Introduction au Français",
  "description": "Leçon d'introduction",
  "user_progress": {
    "is_completed": false,
    "score": null
  }
}
```

### Réponse d'Erreur
```json
{
  "error": "Validation failed",
  "details": {
    "field_name": ["This field is required."]
  }
}
```

## 🚦 Rate Limiting

L'API implémente un rate limiting pour éviter les abus:
- 1000 requêtes par heure pour les utilisateurs authentifiés
- 100 requêtes par heure pour les utilisateurs anonymes

## 📱 Exemples Frontend

### JavaScript/Fetch
```javascript
// Obtenir les unités recommandées
const response = await fetch('/api/v1/course/units/recommended/', {
  headers: {
    'Authorization': `Token ${userToken}`,
    'Content-Type': 'application/json'
  }
});
const units = await response.json();
```

### Python/Requests
```python
import requests

headers = {
    'Authorization': f'Token {user_token}',
    'Content-Type': 'application/json'
}

# Obtenir le dashboard
response = requests.get(
    'https://your-domain.com/api/v1/course/progress/dashboard/',
    headers=headers
)
dashboard_data = response.json()
```

## 🔮 Endpoints Futurs (Roadmap)

- `/api/v1/course/gamification/` - Système de badges et XP
- `/api/v1/course/recommendations/` - IA de recommandations
- `/api/v1/course/social/` - Fonctionnalités sociales
- `/api/v1/course/offline/` - Support hors-ligne

---

**Note:** Cette API est en développement actif. Consultez régulièrement cette documentation pour les mises à jour.