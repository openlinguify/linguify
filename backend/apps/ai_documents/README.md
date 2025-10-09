# AI Documents - Génération Intelligente de Flashcards

Application Django pour générer automatiquement des flashcards à partir de documents (PDF, images, texte) en utilisant des **bibliothèques NLP open-source** (scikit-learn, spaCy, Naive Bayes).

## 🚀 Fonctionnalités

- **Upload de documents** : PDF, images (PNG, JPG), fichiers texte
- **Extraction de texte** :
  - PyMuPDF pour les PDF
  - OCR (pytesseract) pour les images et PDF scannés
  - Lecture directe pour les fichiers texte
- **Génération NLP Open-Source** :
  - **TF-IDF** (scikit-learn) : Extraction des concepts clés
  - **spaCy** : Analyse syntaxique, entités nommées, découpage en phrases
  - **Naive Bayes** : Classification et scoring de pertinence
  - **Pattern matching** : Détection automatique de définitions
- **Classification intelligente** : Scoring et tri des flashcards par pertinence
- **Interface HTMX** : Upload drag & drop et affichage dynamique sans rechargement

## 🔬 Techniques NLP utilisées

### 1. Extraction de définitions (Pattern Matching)
Détecte automatiquement les patterns de définition :
- "X est Y"
- "On appelle X ..."
- "X : définition"
- "X, c'est-à-dire Y"

### 2. Extraction d'entités nommées (spaCy)
Identifie les personnes, lieux, organisations, dates et génère des questions contextuelles.

### 3. Extraction de concepts (TF-IDF)
Utilise TF-IDF (Term Frequency - Inverse Document Frequency) pour identifier les termes les plus importants du document.

### 4. Classification Naive Bayes
Score et classe les flashcards par pertinence en combinant :
- Type de carte (définition, concept, entité, raisonnement)
- Qualité de la question
- Longueur et complexité
- Présence de mots interrogatifs

### 5. Niveaux de difficulté
Assignation automatique (facile/moyen/difficile) basée sur :
- Longueur de la réponse
- Complexité de la question
- Type de contenu

## 📦 Installation

### 1. Ajouter l'app dans `INSTALLED_APPS`

Dans `settings.py` :

```python
INSTALLED_APPS = [
    # ...
    'apps.ai_documents',
    'apps.revision',  # Dépendance requise
    # ...
]
```

### 2. Installer les dépendances

```bash
# Bibliothèques NLP essentielles
pip install scikit-learn spacy PyMuPDF pytesseract Pillow langdetect

# Télécharger les modèles spaCy
python -m spacy download fr_core_news_sm  # Pour le français
python -m spacy download en_core_web_sm   # Pour l'anglais
```

**Note** : Pour l'OCR, vous devez aussi installer Tesseract-OCR sur votre système :
- **Ubuntu/Debian** : `sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng`
- **macOS** : `brew install tesseract tesseract-lang`
- **Windows** : Télécharger depuis [GitHub Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### 3. Configurer les URLs

Dans votre `urls.py` principal :

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('ai-documents/', include('apps.ai_documents.urls')),
    # ...
]
```

### 4. Appliquer les migrations

```bash
python manage.py makemigrations ai_documents
python manage.py migrate
```

### 5. Configurer les fichiers média

Dans `settings.py` :

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 🎯 Utilisation

### Interface Web

Accédez à `/ai-documents/` pour :

1. **Uploader un document** (PDF, image, texte)
2. **Choisir un deck** existant ou créer un nouveau
3. **Configurer** le nombre de flashcards à générer
4. **Lancer** la génération automatique

### Utilisation programmatique

```python
from apps.ai_documents.services import FlashcardGeneratorService
from apps.ai_documents.utils import extract_text_from_file

# Extraire le texte d'un document
text, method = extract_text_from_file('/path/to/document.pdf', 'application/pdf')

# Générer des flashcards avec NLP open-source
generator = FlashcardGeneratorService(language='french')
flashcards = generator.generate_flashcards(
    text=text,
    max_cards=10,
    difficulty_levels=True,
    language='fr'
)

# Résultat
# [
#   {
#     "question": "Qu'est-ce que...",
#     "answer": "C'est...",
#     "difficulty": "medium",
#     "type": "definition",
#     "relevance_score": 0.95
#   },
#   ...
# ]
```

## 🔧 Architecture du générateur

### Pipeline de génération

```
Texte brut
    ↓
Découpage en phrases (spaCy)
    ↓
Extraction parallèle:
    ├─ Définitions (regex patterns)
    ├─ Entités nommées (spaCy NER)
    ├─ Concepts clés (TF-IDF)
    └─ Questions causales (pattern matching)
    ↓
Classification Naive Bayes
    ↓
Scoring de pertinence
    ↓
Tri et sélection (top N)
    ↓
Assignation de difficulté
    ↓
Flashcards finales
```

### Types de flashcards générées

1. **Définitions** (score: 0.9)
   - Détecte les patterns définitionnels
   - Question: "Qu'est-ce que X ?"

2. **Entités** (score: 0.7)
   - Basé sur spaCy NER
   - Questions contextuelles (Qui? Où? Quand?)

3. **Concepts** (score: 0.6)
   - Identifie via TF-IDF
   - Question: "Que dit le texte à propos de X ?"

4. **Raisonnement** (score: 0.5)
   - Détecte les liens causaux
   - Question: "Pourquoi..."

## 🛠️ Dépendances

| Bibliothèque | Usage | Licence |
|-------------|-------|---------|
| **scikit-learn** | TF-IDF, Naive Bayes, vectorisation | BSD-3 |
| **spaCy** | NLP, NER, parsing syntaxique | MIT |
| **PyMuPDF** | Extraction PDF | AGPL-3.0 |
| **pytesseract** | OCR | Apache 2.0 |
| **Pillow** | Traitement d'images | HPND |
| **langdetect** | Détection de langue | Apache 2.0 |

**100% Open-Source, pas d'API payante !**

## 📊 Modèles de données

### DocumentUpload

- `user` : Utilisateur propriétaire
- `deck` : Deck cible (optionnel)
- `file` : Fichier uploadé
- `document_type` : Type (pdf, image, text)
- `status` : Statut (pending, processing, completed, failed)
- `extracted_text` : Texte extrait
- `flashcards_generated_count` : Nombre de flashcards créées
- `generation_params` : Paramètres utilisés (JSON)

## 🎓 Algorithmes utilisés

### TF-IDF (Term Frequency - Inverse Document Frequency)

Mesure l'importance d'un terme dans un document par rapport à un corpus :

```
TF-IDF(t,d) = TF(t,d) × IDF(t)
```

Utilisé pour identifier les concepts clés.

### Naive Bayes

Classificateur probabiliste basé sur le théorème de Bayes :

```
P(classe|features) = P(features|classe) × P(classe) / P(features)
```

Utilisé pour scorer la pertinence des flashcards.

### Named Entity Recognition (spaCy)

Identifie et classifie les entités nommées (personnes, lieux, dates, etc.) via des modèles de deep learning pré-entraînés.

## 🔐 Sécurité

- Authentification requise pour toutes les vues
- Validation des types de fichiers
- Limite de taille configurable
- Isolation des fichiers par utilisateur
- **Pas de transfert de données vers des APIs tierces**

## 📝 Améliorations futures

- [ ] Support NLTK en fallback si spaCy non installé
- [ ] Fine-tuning des patterns de définition par domaine
- [ ] Support de plus de formats (DOCX, PPTX, EPUB)
- [ ] Clustering des flashcards par thème
- [ ] Export Anki/Quizlet
- [ ] Mode asynchrone (Celery) pour gros documents
- [ ] Support multilingue avancé

## 🆚 Comparaison Open-Source vs API IA

| Critère | Open-Source (ce projet) | API OpenAI |
|---------|------------------------|------------|
| **Coût** | Gratuit | ~0.002$/1k tokens |
| **Confidentialité** | 100% local | Données envoyées |
| **Contrôle** | Total | Limité |
| **Personnalisation** | Complète | Limitée |
| **Dépendance** | Aucune | Internet + quota |
| **Qualité** | Bonne (patterns) | Excellente |
| **Rapidité** | Rapide (local) | Variable (API) |

## 📄 Licence

Propriétaire - Linguify 2025

---

**Générez des flashcards intelligentes sans dépendre d'APIs externes !** 🎉
