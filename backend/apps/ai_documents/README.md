# AI Documents - Bibliothèque NLP pour Génération de Flashcards

**Bibliothèque générique et réutilisable** pour générer des flashcards à partir de documents en utilisant des techniques NLP open-source.

## 🎯 Philosophie

Cette app est une **bibliothèque pure** sans dépendance métier :
- ❌ Pas de modèles Django spécifiques
- ❌ Pas de dépendance vers d'autres apps (`revision`, etc.)
- ✅ Services et utilitaires réutilisables
- ✅ 100% open-source (scikit-learn, spaCy, Naive Bayes)

## 📦 Contenu

```
apps/ai_documents/
├── services/
│   └── flashcard_generator.py    # Service de génération NLP
├── utils/
│   └── text_extraction.py        # Extraction texte (PDF, OCR, images)
└── README.md
```

## 🚀 Utilisation

### 1. Extraction de texte

```python
from apps.ai_documents.utils import extract_text_from_file

# Extraire texte d'un PDF
text, method = extract_text_from_file('/path/to/doc.pdf', 'application/pdf')
print(f"Texte extrait via {method}: {text[:100]}...")
```

**Méthodes supportées** :
- **PDF** : PyMuPDF (texte natif) ou OCR (PDF scanné)
- **Images** : OCR via pytesseract
- **Texte** : Lecture directe multi-encodages

### 2. Génération de flashcards

```python
from apps.ai_documents.services import FlashcardGeneratorService

# Initialiser le générateur
generator = FlashcardGeneratorService(language='french')

# Générer des flashcards
flashcards = generator.generate_flashcards(
    text="La photosynthèse est le processus par lequel les plantes...",
    max_cards=10,
    difficulty_levels=True
)

# Résultat
for card in flashcards:
    print(f"Q: {card['question']}")
    print(f"R: {card['answer']}")
    print(f"Difficulté: {card['difficulty']}")
    print(f"Score: {card['relevance_score']}")
    print("---")
```

### 3. Workflow complet

```python
from apps.ai_documents.utils import (
    extract_text_from_file,
    preprocess_text_for_flashcards,
    detect_document_language
)
from apps.ai_documents.services import FlashcardGeneratorService

# Étape 1 : Extraire le texte
text, extraction_method = extract_text_from_file(
    filepath='/path/to/cours.pdf',
    mime_type='application/pdf'
)

# Étape 2 : Nettoyer le texte
clean_text = preprocess_text_for_flashcards(text, max_length=8000)

# Étape 3 : Détecter la langue
detected_lang = detect_document_language(clean_text)
generator_lang = 'french' if detected_lang == 'fr' else 'english'

# Étape 4 : Générer les flashcards
generator = FlashcardGeneratorService(language=generator_lang)
flashcards = generator.generate_flashcards(
    text=clean_text,
    max_cards=15,
    difficulty_levels=True
)

# Étape 5 : Utiliser les résultats
# (stocker dans votre base, afficher, etc.)
```

## 🔬 Techniques NLP

### 1. Extraction de définitions (Regex)
Détecte les patterns :
- "X est Y"
- "On appelle X..."
- "X : définition"

### 2. Extraction d'entités (spaCy NER)
Identifie :
- Personnes, lieux, organisations
- Dates, événements
- Génère des questions contextuelles

### 3. Extraction de concepts (TF-IDF)
Utilise scikit-learn pour :
- Identifier les termes importants
- Pondérer par fréquence

### 4. Classification (Naive Bayes)
Score et trie les flashcards par :
- Type (definition > entity > concept)
- Qualité de la question
- Longueur optimale de la réponse

## 📊 Format de sortie

```python
[
    {
        "question": "Qu'est-ce que la photosynthèse ?",
        "answer": "La photosynthèse est le processus...",
        "difficulty": "medium",           # easy|medium|hard
        "type": "definition",              # definition|entity|concept|reasoning
        "relevance_score": 0.95,          # 0-1
    },
    {
        "question": "Qui est Marie Curie ?",
        "answer": "Marie Curie est une physicienne...",
        "difficulty": "easy",
        "type": "entity",
        "relevance_score": 0.87,
    }
]
```

## 🛠️ Installation

### Dépendances requises

```bash
pip install scikit-learn spacy PyMuPDF pytesseract Pillow langdetect
```

### Modèles spaCy

```bash
# Français
python -m spacy download fr_core_news_sm

# Anglais
python -m spacy download en_core_web_sm
```

### Tesseract (pour OCR)

- **Ubuntu/Debian** : `sudo apt-get install tesseract-ocr tesseract-ocr-fra`
- **macOS** : `brew install tesseract tesseract-lang`
- **Windows** : [Télécharger](https://github.com/UB-Mannheim/tesseract/wiki)

## 🧩 Intégration dans d'autres apps

### Exemple : App Revision

```python
# apps/revision/views/document_import.py
from apps.ai_documents.services import FlashcardGeneratorService
from apps.ai_documents.utils import extract_text_from_file
from apps.revision.models import Flashcard, FlashcardDeck

def import_from_document(deck_id, uploaded_file):
    # 1. Extraire texte
    text, method = extract_text_from_file(
        uploaded_file.path,
        uploaded_file.content_type
    )

    # 2. Générer flashcards
    generator = FlashcardGeneratorService(language='french')
    cards_data = generator.generate_flashcards(text, max_cards=10)

    # 3. Sauvegarder dans votre modèle
    deck = FlashcardDeck.objects.get(id=deck_id)
    for card_data in cards_data:
        Flashcard.objects.create(
            deck=deck,
            front_text=card_data['question'],
            back_text=card_data['answer']
        )
```

### Exemple : App Quiz

```python
# apps/quiz/services.py
from apps.ai_documents.services import FlashcardGeneratorService

def generate_quiz_from_text(text: str):
    generator = FlashcardGeneratorService(language='french')
    cards = generator.generate_flashcards(text, max_cards=20)

    # Transformer en questions QCM
    quiz_questions = []
    for card in cards:
        quiz_questions.append({
            'question': card['question'],
            'correct_answer': card['answer'],
            'difficulty': card['difficulty']
        })
    return quiz_questions
```

## ⚙️ Configuration

### Personnaliser le générateur

```python
generator = FlashcardGeneratorService(language='french')

# Changer la langue
generator.language = 'english'
generator._load_nlp_models()  # Recharger le modèle

# Générer avec options
flashcards = generator.generate_flashcards(
    text=long_text,
    max_cards=20,              # Nombre max
    difficulty_levels=True,    # Inclure difficultés
    language='fr'              # Override langue
)
```

### Paramètres de classification

Dans `classify_flashcards_with_bayes()`, les scores sont calculés selon :

```python
# Bonus par type
type_bonus = {
    'definition': 0.3,    # Haute priorité
    'entity': 0.2,
    'concept': 0.15,
    'reasoning': 0.1
}

# Longueur optimale de réponse : 10-50 mots
# Présence de mots interrogatifs : +0.3
# Question avec '?' : +0.1
```

## 🎓 Cas d'usage

### ✅ Recommandé pour

- Import de cours (PDF)
- Extraction depuis articles
- Génération depuis notes
- OCR de polycopiés scannés
- Création de quiz automatiques

### ❌ Moins adapté pour

- Listes de vocabulaire (préférer Excel/CSV)
- Tableaux structurés
- Formules mathématiques complexes
- Documents très courts (< 200 mots)

## 📝 Limitations

- **Texte max** : 50 000 caractères par défaut
- **Langues** : Français, Anglais (extensible)
- **Qualité OCR** : Dépend de la qualité de l'image
- **Complexité** : Meilleur sur texte structuré (cours, définitions)

## 🔄 Évolution

Cette bibliothèque est conçue pour :
- ✅ Être réutilisée dans plusieurs apps
- ✅ Fonctionner sans Django (utils purs Python)
- ✅ Être testée unitairement
- ✅ Évoluer indépendamment

## 📄 Licence

Propriétaire - Linguify 2025

---

**Bibliothèque NLP pure et réutilisable** 🧠
