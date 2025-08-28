# Linguify Commands Editor

Un éditeur riche basé sur Editor.js avec tous les outils nécessaires pour les descriptions de tâches.

## 📁 Structure

```
commands-editor/
├── README.md              # Cette documentation
├── index.js              # Point d'entrée principal
├── editor-cdn.js         # Gestionnaire des dépendances CDN
└── linguify-editor.js    # Configuration Editor.js personnalisée
```

## 🚀 Utilisation rapide

### Méthode 1: Auto-initialization

```html
<!-- Inclure seulement le script principal -->
<script src="{% static 'js/commands-editor/index.js' %}"></script>

<!-- L'éditeur dans le HTML -->
<div id="my-editor"></div>

<script>
// Initialisation simple
initLinguifyEditor('my-editor').then(editor => {
    console.log('Editor ready!', editor);
});

// Ou avec du contenu existant
initLinguifyEditorWithContent('my-editor', existingContent).then(editor => {
    console.log('Editor ready with content!', editor);
});
</script>
```

### Méthode 2: Event-based

```html
<script src="{% static 'js/commands-editor/index.js' %}"></script>

<script>
document.addEventListener('linguifyCommandsEditorReady', function() {
    const editor = new LinguifyEditor('my-editor', {
        placeholder: 'Commencez à taper...',
        autofocus: true
    });
});
</script>
```

## 🛠️ API

### LinguifyEditor

#### Constructeur
```javascript
new LinguifyEditor(holderId, options)
```

#### Options
- `placeholder`: Texte du placeholder (défaut: "Commencez à taper votre description...")
- `autofocus`: Focus automatique (défaut: true)

#### Méthodes

##### save()
```javascript
const data = await editor.save();
console.log(data); // JSON structuré
```

##### render(data)
```javascript
await editor.render(jsonData);
```

##### clear()
```javascript
await editor.clear();
```

##### destroy()
```javascript
editor.destroy();
```

#### Méthode statique

##### createFromContent(holderId, content, options)
```javascript
const editor = await LinguifyEditor.createFromContent('editor', existingContent);
```

## 🎯 Outils disponibles

### Format
- **Header** (H1-H6) - Raccourci: `CMD+SHIFT+H`
- **Paragraph** avec toolbar inline

### Structure
- **List** (ordonnée et non-ordonnée)
- **Checklist** interactive
- **Quote** avec auteur
- **Delimiter** (séparateur)
- **Table** éditable
- **Code** avec coloration syntaxique

### Médias/Navigation
- **LinkTool** avec prévisualisation
- **Image** (upload + URL)

### Bannières
- **Alert** (info, success, warning, danger) - Raccourci: `CMD+SHIFT+A`

### Inline Tools
- **Marker** (surlignage)
- **InlineCode** (`code`)

## 💾 Intégration avec formulaires

```html
<form id="myForm">
    <div id="editor"></div>
    <input type="hidden" name="content" id="content-field">
    <button type="submit">Sauvegarder</button>
</form>

<script>
initLinguifyEditor('editor').then(editor => {
    document.getElementById('myForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const data = await editor.save();
        document.getElementById('content-field').value = JSON.stringify(data);
        
        // Maintenant soumettre le formulaire
        this.submit();
    });
});
</script>
```

## 🎨 Styles

Tous les styles sont intégrés dans `tailwind-modals.css` avec le préfixe `.editor-js-linguify`.

Les couleurs utilisent les variables CSS Linguify :
- `var(--linguify-primary)` 
- `var(--linguify-gray-xxx)`
- `var(--linguify-success/danger/warning)`

## ⚠️ Endpoints requis

Pour le bon fonctionnement des médias, implémentez ces endpoints :

- `/api/link-preview` - Prévisualisation des liens
- `/api/upload-image` - Upload d'images
- `/api/image-by-url` - Images par URL