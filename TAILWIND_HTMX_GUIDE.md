# 🎨 Guide Tailwind CSS + HTMX pour Linguify

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Installation et Configuration](#installation-et-configuration)
3. [Utilisation dans l'App Revision](#utilisation-dans-lapp-revision)
4. [Composants Disponibles](#composants-disponibles)
5. [Patterns HTMX](#patterns-htmx)
6. [Exemples Pratiques](#exemples-pratiques)
7. [Développement](#développement)

## 🌟 Vue d'ensemble

Linguify intègre maintenant **Tailwind CSS** et **HTMX** au niveau global pour accélérer le développement de toutes les applications. Cette intégration offre :

- **Tailwind CSS** : Framework CSS utilitaire pour un développement rapide et cohérent
- **HTMX** : Interactivité moderne sans écrire de JavaScript complexe
- **Composants prêts à l'emploi** : Spécialement conçus pour l'éducation linguistique
- **Configuration globale** : Disponible dans toutes les apps Linguify

## ⚙️ Installation et Configuration

### Prérequis

Le système est déjà configuré ! Vous n'avez besoin que de :

```bash
# Construire le CSS Tailwind
npm run build:tailwind

# Ou en mode watch pour le développement
npm run watch:tailwind
```

### Architecture

```
/linguify/
├── package.json                      # Dépendances npm globales
├── tailwind.config.js               # Configuration Tailwind globale
├── build-tailwind.js                # Script de build
├── backend/
│   ├── static/css/
│   │   ├── tailwind-global.css      # CSS source Tailwind
│   │   └── tailwind-built.css       # CSS compilé
│   ├── staticfiles/css/
│   │   └── tailwind-built.css       # CSS pour production
│   └── saas_web/templates/saas_web/
│       └── base.html                 # Template global avec Tailwind + HTMX
```

## 🚀 Utilisation dans l'App Revision

### Page d'Exemples

Visitez : `/revision/examples/tailwind-htmx/`

Cette page démontre toutes les fonctionnalités disponibles.

### Dans vos Templates

```html
{% extends "saas_web/base.html" %}

{% block content %}
<div class="container-linguify">
    <!-- Utilisation des composants Tailwind + HTMX -->
    <div class="card-linguify">
        <h2 class="text-2xl font-semibold mb-4">Ma Flashcard</h2>
        
        <button 
            class="btn-linguify"
            hx-get="/revision/load-card/"
            hx-target="#card-content"
        >
            Charger une carte
        </button>
        
        <div id="card-content" class="mt-4"></div>
    </div>
</div>
{% endblock %}
```

## 🎯 Composants Disponibles

### Cartes et Conteneurs

```html
<!-- Carte basique -->
<div class="card-linguify">Contenu</div>

<!-- Carte d'app -->
<div class="app-card-linguify">App card avec hover</div>

<!-- Conteneur responsive -->
<div class="container-linguify">Contenu centré</div>
```

### Boutons

```html
<!-- Bouton principal -->
<button class="btn-linguify">Action</button>

<!-- Bouton outline -->
<button class="btn-linguify-outline">Action secondaire</button>

<!-- Bouton accent -->
<button class="btn-linguify-accent">Action importante</button>
```

### Formulaires

```html
<!-- Input -->
<input type="text" class="input-linguify" placeholder="Votre texte">

<!-- Textarea -->
<textarea class="textarea-linguify" placeholder="Votre message"></textarea>
```

### Flashcards 3D

```html
<div class="flashcard-3d" onclick="this.classList.toggle('flipped')">
    <div class="flashcard-inner">
        <div class="flashcard-front">
            <h3>Question</h3>
        </div>
        <div class="flashcard-back">
            <h3>Réponse</h3>
        </div>
    </div>
</div>
```

### Navigation

```html
<nav class="nav-linguify">
    <a href="#" class="nav-link-linguify">Lien</a>
    <a href="#" class="nav-link-linguify active">Lien actif</a>
</nav>
```

### Modes d'Étude

```html
<div class="study-mode-card" hx-get="/mode/flashcards/" hx-target="#content">
    <div class="text-center">
        <div class="text-4xl mb-4">🃏</div>
        <h3>Flashcards</h3>
    </div>
</div>
```

### Indicateurs de Progression

```html
<div class="progress-linguify">
    <div class="progress-bar-linguify" style="width: 75%"></div>
</div>
```

### États de Chargement

```html
<!-- Spinner -->
<div class="spinner-linguify w-6 h-6"></div>

<!-- Skeleton -->
<div class="skeleton-linguify h-4 w-full"></div>
```

### Notifications

```html
<div class="notification-linguify notification-success">
    Succès !
</div>

<div class="notification-linguify notification-error">
    Erreur !
</div>
```

## ⚡ Patterns HTMX

### Configuration Automatique

HTMX est configuré globalement avec :
- **Token CSRF automatique** pour toutes les requêtes
- **Gestion d'erreurs** avec notifications
- **États de chargement** automatiques
- **Indicateurs visuels** pendant les requêtes

### Patterns Courants

#### Recherche en Temps Réel

```html
<input 
    type="text"
    class="input-linguify"
    hx-get="/search/"
    hx-target="#results"
    hx-trigger="input changed delay:300ms"
    hx-indicator="#spinner"
>
<div id="spinner" class="htmx-indicator">
    <div class="spinner-linguify w-4 h-4"></div>
</div>
<div id="results"></div>
```

#### Formulaire avec Validation

```html
<form 
    hx-post="/add-card/"
    hx-target="#card-list"
    hx-swap="afterbegin"
>
    <input name="front" class="input-linguify" required>
    <input name="back" class="input-linguify" required>
    <button class="btn-linguify">Ajouter</button>
</form>
```

#### Actions Destructives

```html
<button 
    class="text-red-600"
    hx-delete="/delete/123/"
    hx-target="closest .card-linguify"
    hx-swap="outerHTML"
    hx-confirm="Êtes-vous sûr ?"
>
    Supprimer
</button>
```

#### Chargement de Contenu Dynamique

```html
<div 
    hx-get="/stats/"
    hx-trigger="load, every 30s"
    hx-target="this"
    hx-swap="innerHTML"
>
    <div class="spinner-linguify w-8 h-8"></div>
</div>
```

## 💡 Exemples Pratiques

### Flashcard Interactive

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div 
        class="flashcard-3d cursor-pointer"
        hx-get="/card/{{ card.id }}/"
        hx-target="this"
        hx-trigger="click"
    >
        <div class="flashcard-inner">
            <div class="flashcard-front">
                <h3 class="text-lg font-semibold">{{ card.front }}</h3>
            </div>
            <div class="flashcard-back">
                <h3 class="text-lg font-semibold text-blue-800">{{ card.back }}</h3>
            </div>
        </div>
    </div>
</div>
```

### Système de Filtres

```html
<div class="flex gap-2 mb-6">
    <button 
        class="btn-linguify-outline"
        hx-get="/cards/all/"
        hx-target="#card-grid"
    >
        Toutes
    </button>
    <button 
        class="btn-linguify-outline"
        hx-get="/cards/recent/"
        hx-target="#card-grid"
    >
        Récentes
    </button>
    <button 
        class="btn-linguify-outline"
        hx-get="/cards/difficult/"
        hx-target="#card-grid"
    >
        Difficiles
    </button>
</div>

<div id="card-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Contenu chargé via HTMX -->
</div>
```

## 🛠️ Développement

### Commandes Utiles

```bash
# Développement avec watch
npm run watch:tailwind

# Build de production
npm run build:tailwind:prod

# Build simple
npm run build:tailwind

# Serveur Django + Tailwind watch simultanés
npm run dev:full
```

### Ajout de Nouveaux Composants

1. **Modifiez** `/backend/static/css/tailwind-global.css`
2. **Ajoutez** vos composants dans `@layer components`
3. **Reconstruisez** avec `npm run build:tailwind`

Exemple :

```css
@layer components {
  .quiz-card {
    @apply bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-blue-500 transition-all duration-300;
  }
  
  .answer-button {
    @apply w-full p-4 text-left border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-all duration-200;
  }
  
  .answer-button.correct {
    @apply bg-green-50 border-green-300 text-green-800;
  }
  
  .answer-button.incorrect {
    @apply bg-red-50 border-red-300 text-red-800;
  }
}
```

### Debugging

#### CSS Non Appliqué

1. Vérifiez que le CSS est construit : `ls -la backend/static/css/tailwind-built.css`
2. Reconstruisez si nécessaire : `npm run build:tailwind`
3. Vérifiez que le template extend `saas_web/base.html`

#### Classes Tailwind Manquantes

1. Ajoutez les nouveaux patterns dans `tailwind.config.js` → `content`
2. Reconstruisez le CSS

#### HTMX Non Fonctionnel

1. Vérifiez la console navigateur pour les erreurs
2. Vérifiez que les URLs Django existent
3. Testez les endpoints avec l'outil réseau du navigateur

### Bonnes Pratiques

1. **Utilisez les composants existants** avant de créer les vôtres
2. **Préfixez vos composants custom** avec le nom de votre app
3. **Testez sur mobile** - Tailwind est mobile-first
4. **Utilisez les classes Tailwind standards** quand possible
5. **Documentez vos nouveaux composants** dans ce guide

## 🎉 Conclusion

Cette intégration Tailwind CSS + HTMX permet de développer rapidement des interfaces modernes et interactives pour toutes les applications Linguify. 

**Avantages :**
- Développement 3x plus rapide
- Cohérence visuelle globale
- Interactivité sans JavaScript complexe
- Maintenance simplifiée
- Responsive design automatique

**Pour l'App Revision :**
- Flashcards 3D fluides
- Recherche en temps réel
- Modes d'étude interactifs
- Statistiques dynamiques
- Interface intuitive

Commencez par explorer la page d'exemples `/revision/examples/tailwind-htmx/` puis adaptez les patterns à vos besoins !

---

*Mise à jour : Août 2025 - Linguify Team*