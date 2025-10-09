# 📄 Import de Documents - Génération Automatique de Flashcards

## 🎯 Utilisation dans l'app Revision

L'app **revision** intègre maintenant la fonctionnalité de génération automatique de flashcards à partir de documents (PDF, images, texte) grâce à l'app **ai_documents**.

### 📍 Où trouver cette fonctionnalité ?

Dans l'interface **Revision → Liste de cartes**, lors de l'import dans un deck :

1. Cliquez sur "**Importer**" sur un deck
2. Vous avez maintenant 2 options :
   - **Excel / CSV** : Import classique depuis tableur
   - **Document / PDF / Image** : Import avec génération IA ✨

### 🚀 Comment ça marche ?

#### API Endpoint

```
POST /revision/api/decks/{deck_id}/import-document/
```

**Paramètres** :
- `document` (file) : Fichier à uploader (PDF, PNG, JPG, TXT)
- `max_cards` (int, optionnel) : Nombre max de flashcards à générer (défaut: 10)

**Exemple de requête** :

```javascript
const formData = new FormData();
formData.append('document', fileInput.files[0]);
formData.append('max_cards', 15);

fetch(`/revision/api/decks/${deckId}/import-document/`, {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
    },
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log(`${data.cards_created} flashcards créées !`);
    console.log('Aperçu:', data.preview);
});
```

**Réponse JSON** :

```json
{
    "success": true,
    "message": "12 flashcards générées avec succès",
    "cards_created": 12,
    "deck_id": 42,
    "deck_name": "Histoire - Révolution française",
    "preview": [
        {
            "id": 123,
            "front_text": "Qu'est-ce que la Révolution française ?",
            "back_text": "La Révolution française est une période...",
            "difficulty": "medium",
            "relevance_score": 0.95
        }
    ],
    "extraction_method": "PyMuPDF",
    "detected_language": "fr"
}
```

### 🔬 Techniques NLP utilisées

1. **Extraction de texte** :
   - PDF → PyMuPDF
   - Images → OCR (pytesseract)
   - Texte → Lecture directe

2. **Génération de flashcards** (100% open-source) :
   - **TF-IDF** : Identification des concepts clés
   - **spaCy** : Entités nommées, parsing syntaxique
   - **Naive Bayes** : Scoring de pertinence
   - **Pattern matching** : Détection de définitions

3. **Types de flashcards générées** :
   - ✅ Définitions (`Qu'est-ce que X ?`)
   - ✅ Entités (`Qui est...?`, `Où se trouve...?`)
   - ✅ Concepts clés (`Que dit le texte à propos de X ?`)
   - ✅ Raisonnement (`Pourquoi...?`)

### 📦 Dépendances requises

```bash
pip install scikit-learn spacy PyMuPDF pytesseract Pillow langdetect
python -m spacy download fr_core_news_sm  # Français
python -m spacy download en_core_web_sm   # Anglais
```

**Tesseract-OCR** (pour images) :
- Ubuntu/Debian : `sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng`
- macOS : `brew install tesseract tesseract-lang`
- Windows : [GitHub Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### ⚙️ Configuration

Assurez-vous que `apps.ai_documents` est dans `INSTALLED_APPS` :

```python
INSTALLED_APPS = [
    # ...
    'apps.ai_documents',
    'apps.revision',
    # ...
]
```

### 📊 Exemple d'utilisation frontend

```javascript
// Quand l'utilisateur sélectionne "Document / PDF / Image"
document.getElementById('importTypeDocument').addEventListener('change', function() {
    if (this.checked) {
        // Afficher l'interface d'upload de document
        showDocumentUploadInterface();
    }
});

function uploadDocument(deckId, file, maxCards = 10) {
    const formData = new FormData();
    formData.append('document', file);
    formData.append('max_cards', maxCards);

    return fetch(`/revision/api/decks/${deckId}/import-document/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(`${data.cards_created} flashcards créées !`);
            reloadDeck(deckId);
        } else {
            showErrorMessage(data.error);
        }
        return data;
    });
}
```

### 🎨 Interface utilisateur suggérée

```html
<!-- Sélecteur de type d'import -->
<div class="btn-group w-100" role="group">
    <input type="radio" class="btn-check" name="importType" id="importTypeExcel" value="excel" checked>
    <label class="btn btn-outline-primary" for="importTypeExcel">
        <i class="bi bi-file-earmark-excel me-2"></i>
        Excel / CSV
    </label>

    <input type="radio" class="btn-check" name="importType" id="importTypeDocument" value="document">
    <label class="btn btn-outline-primary" for="importTypeDocument">
        <i class="bi bi-file-earmark-pdf me-2"></i>
        Document / PDF / Image
        <span class="badge bg-success ms-1">NLP</span>
    </label>
</div>

<!-- Section upload document -->
<div id="documentImportSection" class="d-none">
    <div class="mb-3">
        <label class="form-label">Document à analyser</label>
        <input type="file" id="documentFile" accept=".pdf,.png,.jpg,.jpeg,.txt">
    </div>

    <div class="mb-3">
        <label class="form-label">Nombre de flashcards à générer</label>
        <input type="number" id="maxCards" value="10" min="1" max="50">
    </div>

    <button onclick="generateFlashcards()" class="btn btn-primary">
        🚀 Générer les Flashcards
    </button>
</div>
```

### ✅ Avantages

| Critère | Valeur |
|---------|--------|
| **Coût** | Gratuit (pas d'API payante) |
| **Confidentialité** | 100% local |
| **Rapidité** | Traitement instantané |
| **Formats supportés** | PDF, PNG, JPG, TXT |
| **Langues** | Français, Anglais (extensible) |
| **Personnalisation** | Complète (code open-source) |

### 🔧 Dépannage

**Erreur "Aucun texte extrait"** :
- Vérifier que le PDF contient du texte (pas seulement des images)
- Pour les PDF scannés, installer Tesseract-OCR

**Erreur "spaCy model not found"** :
```bash
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm
```

**Faible qualité des flashcards** :
- Augmenter `max_cards` pour avoir plus de choix
- Utiliser des documents plus structurés (cours, définitions claires)
- Vérifier la qualité de l'OCR si c'est une image

### 📝 Notes techniques

- **Limite de texte** : 8000 caractères par défaut (configurable)
- **Scoring** : Les flashcards sont triées par pertinence (0-1)
- **Difficulté** : Assignée automatiquement (easy/medium/hard)
- **Stockage** : Les documents uploadés sont conservés dans `DocumentUpload`

### 🆚 Comparaison avec import Excel

| Critère | Excel/CSV | Document/PDF |
|---------|-----------|--------------|
| **Source** | Tableur préparé | Document brut |
| **Effort** | Manuel | Automatique |
| **Rapidité** | Rapide si déjà préparé | Instantané |
| **Flexibilité** | Structure imposée | Adaptatif |
| **Cas d'usage** | Listes de vocabulaire | Cours, articles, notes |

---

**Générez des flashcards intelligentes en un clic ! 🎉**
