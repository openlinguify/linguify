# Linguify Editor

Universal text editor component for the Linguify platform with slash commands and formatting toolbar.

## Features

### ✨ Slash Commands
- Type `/` at the beginning of a line or after a space
- Navigate with arrow keys (↑↓)
- Select with Enter or click
- Escape with Esc or Space

Available commands:
- **Note** - `**Note:** `
- **Tâche** - `☐ `
- **Idée** - `**Idée:** `
- **Question** - `**Question:** `
- **Traduction** - `**FR:** \n**EN:** `
- **Vocabulaire** - `**Mot:** définition`
- **Rappel** - `**Rappel:** `

### 🎨 Formatting Toolbar
- Appears when text is selected
- Supports bold, italic, highlight, code
- Headers (H1, H2, H3, H4)
- Mobile responsive

## Usage

### 1. Include Files
```html
<!-- CSS -->
<link rel="stylesheet" href="{% static 'editor-linguify/editor.css' %}">

<!-- JavaScript -->
<script src="{% static 'editor-linguify/editor.js' %}"></script>
```

### 2. HTML Structure
```html
<div x-data="linguifyEditor()" @click.away="hideCommandMenu()">
    <textarea
        @keydown="handleKeydown($event)"
        @mouseup="handleSelection($event)"
        @keyup="handleSelection($event)"
        class="content-textarea"
        placeholder="Start typing... Press / for commands">
    </textarea>
</div>
```

## Compatible Modules

- ✅ **Notebook** - Note taking and organization
- 📝 **Flashcards** - Card content creation
- 📚 **Lessons** - Educational content
- 💬 **Forums** - Discussion posts
- 📋 **Assignments** - Exercise creation
- 🎯 **Any text input** in Linguify

## Technical Details

### Dependencies
- Alpine.js (for reactivity)
- Font Awesome (for toolbar icons)

### Browser Support
- Modern browsers (ES6+)
- Mobile responsive
- Touch-friendly

### Performance
- Lightweight (~3KB JS + 2KB CSS)
- No external dependencies beyond Alpine.js
- Efficient positioning calculations

## Customization

### Adding New Commands
```javascript
commands: [
    { name: 'Custom', text: 'Custom text: ' },
    // ... existing commands
]
```

### Styling
All styles are in `editor.css` and use CSS variables for easy theming.

## Version
1.0.0

## License
Part of the Linguify platform