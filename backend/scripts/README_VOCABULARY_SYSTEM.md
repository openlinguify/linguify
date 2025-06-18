# 🔤 Système de Vocabulaire Linguify

Ce document explique comment utiliser le système de vocabulaire de Linguify pour remplir et gérer le contenu pédagogique.

## 📋 Vue d'ensemble

Le système de vocabulaire Linguify permet de :
- Gérer du vocabulaire multilingue (EN, FR, ES, NL)
- Organiser le contenu par unités, leçons et leçons de contenu
- Ajouter du vocabulaire de manière interactive ou programmatique
- Effectuer des recherches et analyses sur le vocabulaire

## 🏗️ Architecture des données

```
Unit (Unité)
└── Lesson (Leçon)
    └── ContentLesson (Leçon de contenu)
        └── VocabularyList (Vocabulaire)
```

### Modèles principaux

- **Unit** : Représente une unité thématique (ex: "Family and Relationships")
- **Lesson** : Une leçon spécifique dans une unité (ex: "Family Members")
- **ContentLesson** : Le contenu d'une leçon (ex: "Basic Family Vocabulary")
- **VocabularyList** : Un mot de vocabulaire avec ses traductions et informations

## 🚀 Scripts disponibles

### 1. Test de connexion
```bash
poetry run python scripts/test_db_connection.py
```
- Teste la connexion à la base de données
- Affiche les statistiques du vocabulaire existant
- Montre des exemples de données

### 2. Création de données de test
```bash
poetry run python scripts/create_sample_data.py
```
- Crée une unité de test "Family and Relationships"
- Ajoute une leçon "Family Members"
- Insère 8 mots de vocabulaire famille

### 3. Script interactif (à compléter)
```bash
poetry run python scripts/fill_vocabulary_interactive.py
```
- Interface interactive pour ajouter du vocabulaire
- Sélection guidée par unité/leçon/contenu
- Modes d'ajout individuel ou en lot

### 4. Démonstration complète
```bash
poetry run python scripts/demo_vocabulary_system.py
```
- Démontre toutes les fonctionnalités
- Exemples de requêtes et méthodes
- Guide d'utilisation pratique

## 📝 Structure d'un mot de vocabulaire

Chaque mot de vocabulaire contient :

```python
{
    # Traductions (obligatoires)
    "word_en": "mother",
    "word_fr": "mère", 
    "word_es": "madre",
    "word_nl": "moeder",
    
    # Définitions (obligatoires)
    "definition_en": "Female parent",
    "definition_fr": "Parent de sexe féminin",
    "definition_es": "Progenitora femenina", 
    "definition_nl": "Vrouwelijke ouder",
    
    # Types de mots (obligatoires)
    "word_type_en": "noun",
    "word_type_fr": "nom",
    "word_type_es": "sustantivo",
    "word_type_nl": "zelfstandig naamwoord",
    
    # Phrases d'exemple (optionnelles)
    "example_sentence_en": "My mother is very kind.",
    "example_sentence_fr": "Ma mère est très gentille.",
    "example_sentence_es": "Mi madre es muy amable.",
    "example_sentence_nl": "Mijn moeder is erg aardig.",
    
    # Synonymes et antonymes (optionnels)
    "synonymous_en": "mom, mama",
    "antonymous_en": "father"
}
```

## 🔧 Utilisation programmatique

### Ajouter du vocabulaire via Python

```python
from apps.course.models import ContentLesson, VocabularyList

# Récupérer une leçon de contenu
content_lesson = ContentLesson.objects.get(title_en="Basic Family Vocabulary")

# Créer un nouveau mot
vocab = VocabularyList.objects.create(
    content_lesson=content_lesson,
    word_en="uncle",
    word_fr="oncle",
    word_es="tío", 
    word_nl="oom",
    definition_en="Brother of one's parent",
    definition_fr="Frère du parent",
    definition_es="Hermano del padre o madre",
    definition_nl="Broer van ouder",
    word_type_en="noun",
    word_type_fr="nom",
    word_type_es="sustantivo",
    word_type_nl="zelfstandig naamwoord"
)
```

### Rechercher du vocabulaire

```python
# Recherche par mot
words = VocabularyList.objects.filter(word_en__icontains="mother")

# Recherche par définition
words = VocabularyList.objects.filter(definition_en__icontains="parent")

# Recherche par type
nouns = VocabularyList.objects.filter(word_type_en="noun")

# Utiliser les méthodes du modèle
word = VocabularyList.objects.get(word_en="mother")
french_translation = word.get_translation('fr')  # "mère"
french_definition = word.get_definition('fr')    # "Parent de sexe féminin"
example = word.get_example_sentence('fr')        # "Ma mère est très gentille."
```

## 💾 Configuration de la base de données

### Mode développement (SQLite)
```bash
# Pour les tests et développement
export TEST_MODE=True
poetry run python manage.py migrate
```

### Mode production (PostgreSQL)
```bash
# Vérifier que PostgreSQL est en marche
# Configurer les variables d'environnement dans .env :
# DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

poetry run python manage.py migrate
```

## 📊 Méthodes utiles

### Sur VocabularyList
```python
vocab = VocabularyList.objects.get(word_en="mother")

# Obtenir traductions
vocab.get_translation('fr')        # "mère"
vocab.get_definition('es')         # "Progenitora femenina"
vocab.get_word_type('nl')          # "zelfstandig naamwoord"
vocab.get_example_sentence('en')   # "My mother is very kind."
vocab.get_synonymous('fr')         # "maman"
vocab.get_antonymous('en')         # "father"
```

### Sur ContentLesson
```python
content_lesson = ContentLesson.objects.get(title_en="Basic Family Vocabulary")

# Obtenir tout le vocabulaire
vocabulary = content_lesson.vocabulary_lists.all()

# Compter les mots
count = content_lesson.vocabulary_lists.count()

# Recherche dans cette leçon
family_words = content_lesson.vocabulary_lists.filter(
    definition_en__icontains="family"
)
```

## 🎯 Exemples d'usage

### Créer une nouvelle unité thématique

```python
from apps.course.models import Unit, Lesson, ContentLesson

# Créer l'unité
unit = Unit.objects.create(
    title_en="Food and Drinks",
    title_fr="Nourriture et Boissons", 
    title_es="Comida y Bebidas",
    title_nl="Eten en Drinken",
    level="A1",
    order=2
)

# Créer la leçon
lesson = Lesson.objects.create(
    unit=unit,
    lesson_type="vocabulary",
    title_en="Basic Food Vocabulary",
    title_fr="Vocabulaire de Base de la Nourriture",
    order=1
)

# Créer le contenu
content_lesson = ContentLesson.objects.create(
    lesson=lesson,
    content_type="VocabularyList",
    title_en="Common Foods",
    title_fr="Aliments Courants",
    estimated_duration=20,
    order=1
)
```

### Ajouter du vocabulaire alimentaire

```python
food_vocabulary = [
    {
        "word_en": "apple", "word_fr": "pomme", 
        "word_es": "manzana", "word_nl": "appel",
        "definition_en": "A round fruit with red or green skin"
    },
    {
        "word_en": "bread", "word_fr": "pain",
        "word_es": "pan", "word_nl": "brood", 
        "definition_en": "Food made from flour and water"
    }
]

for vocab_data in food_vocabulary:
    VocabularyList.objects.create(
        content_lesson=content_lesson,
        word_type_en="noun",
        word_type_fr="nom",
        word_type_es="sustantivo", 
        word_type_nl="zelfstandig naamwoord",
        **vocab_data
    )
```

## 🔍 Requêtes avancées

```python
# Statistiques par langue
from django.db.models import Count

# Compter par type de mot
word_types = VocabularyList.objects.values('word_type_en').annotate(
    count=Count('id')
).order_by('-count')

# Mots les plus longs
long_words = VocabularyList.objects.extra(
    select={'word_length': 'LENGTH(word_en)'}
).order_by('-word_length')[:10]

# Mots avec synonymes
words_with_synonyms = VocabularyList.objects.exclude(
    synonymous_en__isnull=True
).exclude(synonymous_en__exact='')

# Recherche multi-langue
multilingual_search = VocabularyList.objects.filter(
    Q(word_en__icontains="family") |
    Q(word_fr__icontains="famille") |
    Q(word_es__icontains="familia")
)
```

## 📚 Bonnes pratiques

1. **Organisation thématique** : Grouper le vocabulaire par thèmes logiques
2. **Cohérence des traductions** : Vérifier que toutes les langues sont remplies
3. **Exemples contextuels** : Fournir des phrases d'exemple pertinentes
4. **Types de mots précis** : Utiliser les bons types grammaticaux
5. **Synonymes utiles** : Ajouter des synonymes courants pour enrichir
6. **Validation** : Tester les données avant import en production

## 🚧 Limitations actuelles

- Script interactif à compléter pour production
- Pas d'interface admin spécialisée pour le vocabulaire 
- Validation limitée des données multilingues
- Pas de système de tags ou catégories avancées

## 🎯 Prochaines étapes

1. Finaliser le script interactif
2. Créer des APIs REST pour le frontend
3. Ajouter validation et nettoyage des données
4. Intégrer avec le système d'exercices
5. Créer interface admin dédiée
6. Ajouter import/export CSV/JSON
7. Système de révision et niveaux de difficulté

---

*Ce système est conçu pour être extensible et s'adapter aux besoins pédagogiques de Linguify.*