# Composants Partagés - Linguify Frontend

Ce dossier contient tous les composants HTML réutilisables pour l'interface web de Linguify.

## Composants Disponibles

### Header (`header.html`)
Navigation principale uniforme pour toutes les pages.

**Utilisation :**
```html
{% include "components/header.html" %}
```

**Fonctionnalités :**
- Navigation responsive
- Sélecteur de langue
- Liens d'authentification adaptatifs
- Indicateur de page active
- Effets de défilement

### Styles Header (`header_styles.html`)
Styles CSS et JavaScript pour le header.

**Utilisation :**
```html
{% include "components/header_styles.html" %}
```

### Footer (`footer.html`)
Footer uniforme avec liens organisés et informations légales.

**Utilisation :**
```html
{% include "components/footer.html" %}
```

**Fonctionnalités :**
- Liens organisés par catégories
- Liens sociaux
- Informations légales
- Design responsive

### Styles Footer (`footer_styles.html`)
Styles CSS pour le footer.

**Utilisation :**
```html
{% include "components/footer_styles.html" %}
```

## Guide d'Utilisation

### Dans un nouveau template

1. **Pour les pages standard :**
   ```html
   {% extends "frontend/base_page.html" %}
   {% load i18n %}

   {% block title %}{{ page_title }}{% endblock %}

   {% block content %}
   <!-- Votre contenu ici -->
   {% endblock %}
   ```

2. **Pour des pages spéciales :**
   ```html
   {% load static %}
   {% load i18n %}
   <!DOCTYPE html>
   <html>
   <head>
       <!-- head content -->
       {% include "components/header_styles.html" %}
       {% include "components/footer_styles.html" %}
   </head>
   <body>
       {% include "components/header.html" %}
       
       <!-- Votre contenu -->
       
       {% include "components/footer.html" %}
   </body>
   </html>
   ```

## Création de Nouveaux Composants

### Nomenclature
- `nom_composant.html` - Template HTML
- `nom_composant_styles.html` - Styles CSS et JS (optionnel)

### Structure recommandée
```html
{% load i18n %}

<!-- Nom du Composant - Description -->
<div class="nom-composant">
    <!-- Contenu du composant -->
</div>
```

### Styles
```html
<!-- Nom du Composant - Styles -->
<style>
    /* Styles spécifiques au composant */
    .nom-composant {
        /* propriétés CSS */
    }
</style>

<!-- JavaScript optionnel -->
<script>
    // JavaScript spécifique au composant
</script>
```

## Avantages du Système

1. **Centralisation** : Un seul endroit pour modifier chaque composant
2. **Cohérence** : Design uniforme sur toutes les pages
3. **Maintenabilité** : Modifications rapides et propagées partout
4. **Réutilisabilité** : Composants utilisables dans n'importe quel template
5. **Évolutivité** : Facilité d'ajout de nouveaux composants

## Notes Importantes

- Tous les composants utilisent le système d'internationalisation Django (`{% trans %}`)
- Les styles utilisent les variables CSS définies dans les templates de base
- Les composants sont responsive et compatibles Bootstrap 5
- JavaScript inclus pour les interactions (scrolling, dropdowns, etc.)

## Maintenance

Pour modifier un composant :
1. Éditer le fichier approprié dans `/components/`
2. Tester sur plusieurs pages
3. Vérifier la compatibilité mobile
4. Vérifier l'internationalisation