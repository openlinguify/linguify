# Linguify Command Palette

Un système d'édition riche inspiré de Notion avec commandes slash et blocs éditables visuels.

## 📁 Structure des fichiers

```
command-palette/
├── README.md                           # Cette documentation
├── linguify-command-palette.js         # Command palette basique (textarea)
├── linguify-rich-editor.js            # Éditeur riche avec blocs visuels
├── linguify-command-palette-demo.html  # Démo command palette simple
└── rich-editor-demo.html              # Démo éditeur riche complet
```

## 🚀 Utilisation rapide

### Command Palette Simple (Textarea)

Pour ajouter le command palette à un textarea existant :

```html
<!-- Include le script -->
<script src="{% static 'js/command-palette/linguify-command-palette.js' %}"></script>

<!-- Ajouter l'attribut au textarea -->
<textarea data-command-palette="true" placeholder="Tapez / pour les commandes..."></textarea>
```

**Initialisation automatique** : Tous les textareas avec `data-command-palette="true"` sont automatiquement initialisés.

**Initialisation manuelle** :
```javascript
const palette = new LinguifyCommandPalette(textareaElement);
```

### Rich Editor (Blocs visuels)

Pour un éditeur riche avec blocs éditables :

```html
<!-- Include les scripts -->
<script src="{% static 'js/command-palette/linguify-command-palette.js' %}"></script>
<script src="{% static 'js/command-palette/linguify-rich-editor.js' %}"></script>

<!-- Container pour l'éditeur -->
<div id="rich-editor" data-rich-editor="true"></div>
<input type="hidden" name="content" id="content-field">

<script>
// Initialisation manuelle avec sauvegarde
const editor = new LinguifyRichEditor(document.getElementById('rich-editor'));

// Synchroniser avec un champ hidden pour sauvegarde
document.getElementById('form').addEventListener('submit', function() {
    document.getElementById('content-field').value = editor.getHTML();
});
</script>
```

## 📝 Types de blocs disponibles

### Format
- **Texte** : Paragraphe normal
- **Titre 1-3** : Titres de différentes tailles

### Éléments  
- **Citation** : Bloc de citation avec barre latérale
- **Code** : Bloc de code avec syntaxe
- **Séparateur** : Ligne horizontale
- **Listes** : À puces ou numérotées

### Mise en page
- **2 colonnes** : Layout en 2 colonnes visuelles
- **3 colonnes** : Layout en 3 colonnes visuelles

### Bannières
- **Info** : Bannière bleue avec icône info
- **Succès** : Bannière verte avec icône check
- **Attention** : Bannière orange avec icône warning  
- **Danger** : Bannière rouge avec icône erreur

## 🎮 Contrôles utilisateur

### Command Palette (/)
- Tapez `/` au début d'une ligne ou après un espace
- Utilisez ↑↓ pour naviguer
- Appuyez sur Entrée ou Tab pour sélectionner
- Échap pour fermer

### Rich Editor
- **Entrée** : Nouveau bloc
- **Backspace** sur bloc vide : Supprimer le bloc
- **Hover** sur un bloc : Afficher les contrôles (dupliquer/supprimer)
- **/** : Transformer le bloc actuel

## 🔧 API Rich Editor

### Méthodes principales

```javascript
const editor = new LinguifyRichEditor(container, options);

// Ajouter un bloc
editor.addBlock('heading1', 'Mon titre');
editor.addBlock('paragraph', 'Mon paragraphe');
editor.addBlock('quote', 'Ma citation');

// Exporter le contenu
const html = editor.getHTML();

// Nettoyer
editor.destroy();
```

### Options disponibles

```javascript
const options = {
    placeholder: 'Votre placeholder personnalisé...'
};
```

### Types de blocs supportés

- `paragraph` : Paragraphe normal
- `heading1`, `heading2`, `heading3` : Titres
- `quote` : Citation
- `code` : Code
- `separator` : Séparateur
- `columns2`, `columns3` : Colonnes
- `banner-info`, `banner-success`, `banner-warning`, `banner-danger` : Bannières
- `list-bulleted`, `list-numbered` : Listes

## 🎨 Styles CSS

Tous les styles sont centralisés dans `tailwind-modals.css` :

- `.linguify-command-palette` : Styles du command palette
- `.linguify-rich-editor` : Styles de l'éditeur riche
- `.rich-block` : Styles des blocs individuels
- `.block-*` : Styles spécifiques par type de bloc

## 🔄 Intégration avec les formulaires

### Exemple complet Todo

```html
<!-- Description avec éditeur riche -->
<div class="form-group-linguify">
    <label for="description" class="form-label-linguify">Description</label>
    <div id="description-editor" data-rich-editor="true"></div>
    <input type="hidden" id="description" name="description">
</div>

<script>
// Initialisation
const editor = new LinguifyRichEditor(document.getElementById('description-editor'));

// Charger contenu existant
const existingContent = document.getElementById('description').value;
if (existingContent) {
    editor.addBlock('paragraph', existingContent);
}

// Synchroniser avant soumission
document.getElementById('form').addEventListener('submit', function() {
    document.getElementById('description').value = editor.getHTML();
});
</script>
```

## 🧪 Testing

Utilisez les fichiers de démo pour tester :

- **linguify-command-palette-demo.html** : Test du command palette simple
- **rich-editor-demo.html** : Test de l'éditeur riche complet

## 📱 Responsive

Les composants sont responsive par défaut :
- Colonnes passent en 1 colonne sur mobile
- Command palette s'adapte à la taille d'écran
- Contrôles mobiles optimisés

## 🎯 Utilisation dans d'autres apps

Le système est conçu pour être réutilisé dans toute l'application Linguify :

1. **Include les scripts** dans votre template
2. **Ajoutez les attributs** `data-command-palette` ou `data-rich-editor`
3. **Les styles sont automatiquement** disponibles via tailwind-modals.css

Perfect pour : descriptions, commentaires, contenu riche, documentation, etc.