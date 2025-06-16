# Guide d'intégration OWL dans Django pour Linguify

## Vue d'ensemble

Cette documentation explique comment intégrer le framework OWL (utilisé par Odoo) dans le backend Django de Linguify pour créer des interfaces utilisateur riches côté serveur.

## Architecture

### Structure des fichiers

Chaque application Django peut avoir son propre frontend OWL :

```
backend/apps/[app_name]/
├── static/
│   ├── src/
│   │   ├── js/           # Code JavaScript/OWL
│   │   ├── scss/         # Styles SCSS
│   │   └── xml/          # Templates OWL
│   └── lib/              # Librairies externes
├── templates/
│   └── [app_name]/       # Templates Django
├── views_web.py          # Vues pour servir le frontend
└── urls_web.py           # Routes frontend
```

### Configuration Django

1. **Installer les dépendances** :
```bash
pip install django-compressor django-sass-processor libsass
```

2. **Ajouter dans settings.py** :
```python
INSTALLED_APPS = [
    # ...
    'compressor',
    'sass_processor',
]

# Configuration des fichiers statiques
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    'sass_processor.finders.CssFinder',
]

# Django Compressor
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'sass_processor.compressor.SassCompiler',
]
```

## Créer une application OWL

### 1. Point d'entrée JavaScript

`static/src/js/app.js` :
```javascript
import { mount, whenReady } from "@odoo/owl";
import { MyApp } from "./views/MyApp";

whenReady(async () => {
    const app = new MyApp();
    await mount(app, document.getElementById('app-root'));
});
```

### 2. Composant principal

`static/src/js/views/MyApp.js` :
```javascript
import { Component, useState } from "@odoo/owl";

export class MyApp extends Component {
    static template = "myapp.MyApp";
    
    setup() {
        this.state = useState({
            // État de l'application
        });
    }
}
```

### 3. Templates OWL

`static/src/xml/templates.xml` :
```xml
<templates>
    <template id="myapp.MyApp">
        <div class="my-app">
            <!-- Contenu de l'application -->
        </div>
    </template>
</templates>
```

### 4. Vue Django

`views_web.py` :
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def app_view(request):
    return render(request, 'myapp/app.html')
```

### 5. Template Django

`templates/myapp/app.html` :
```html
{% extends "base.html" %}
{% load static compress %}

{% block content %}
<div id="app-root"></div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/@odoo/owl@2.1.1/dist/owl.iife.js"></script>
{% compress js %}
    <script type="module" src="{% static 'myapp/src/js/app.js' %}"></script>
{% endcompress %}
{% endblock %}
```

## Services et API

### Service JavaScript

```javascript
export class ApiService {
    constructor() {
        this.baseUrl = '/api/v1/myapp';
        this.csrfToken = this.getCsrfToken();
    }
    
    async request(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken,
                ...options.headers,
            },
        });
        return response.json();
    }
}
```

## Avantages de cette approche

1. **Code organisé** : Chaque app a son propre frontend
2. **Réutilisabilité** : Composants OWL réutilisables
3. **Performance** : Moins de requêtes réseau, rendu côté serveur
4. **Intégration Django** : Utilise les templates et l'authentification Django
5. **Développement rapide** : Structure similaire à Odoo

## Migration progressive

Pour migrer progressivement depuis React :

1. Commencer par une app simple (ex: notebook)
2. Créer l'interface OWL en parallèle
3. Basculer les utilisateurs progressivement
4. Migrer app par app

## Commandes utiles

```bash
# Collecter les fichiers statiques
python manage.py collectstatic

# Compiler SCSS en développement
python manage.py sass_processor

# Lancer le serveur de développement
python manage.py runserver
```

## Exemple complet

L'application Notebook a été implémentée avec cette architecture. Voir :
- `/backend/apps/notebook/static/` - Frontend OWL
- `/backend/apps/notebook/views_web.py` - Vues Django
- `/backend/apps/notebook/templates/` - Templates