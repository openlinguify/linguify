# Auto App Discovery & App Store System 🔍

Ce système découvre automatiquement toutes les applications Django dans le dossier `backend/apps/` et les intègre complètement dans Linguify :
1. **INSTALLED_APPS** : Pour que Django reconnaisse l'app 
2. **App Store** : Pour que l'app apparaisse dans votre marketplace

## Comment ça fonctionne

### Détection automatique
- **Scan automatique** : Le système scanne tous les dossiers dans `backend/apps/`
- **Critère de validation** : Une app est considérée comme valide si elle contient un fichier `apps.py`
- **Tri alphabétique** : Les apps sont automatiquement triées par ordre alphabétique
- **Configuration centralisée** : Toute la logique est dans `core/utils.py`

### Structure actuelle
```
backend/
├── apps/
│   ├── authentication/     ✅ Auto-découverte
│   ├── calendar_app/       ✅ Auto-découverte
│   ├── chat/               ✅ Auto-découverte
│   ├── coaching/           ❌ Exclue (commentée)
│   ├── community/          ✅ Auto-découverte
│   ├── payments/           ❌ Exclue (commentée)
│   └── ...
└── core/
    ├── settings.py         # Utilise get_installed_apps()
    └── utils.py            # Contient la logique de découverte
```

## Utilisation

### Créer une nouvelle app complète

#### Méthode automatique avec validation (recommandée) 🚀
```bash
# 1. Créer l'app avec Django
poetry run python manage.py startapp nom_app apps/nom_app

# 2. Configurer automatiquement tout + vérifier la préparation
poetry run python manage.py setup_auto_apps --check-readiness

# 3. C'est tout ! L'app est:
#    ✅ Dans INSTALLED_APPS
#    ✅ A un __manifest__.py généré
#    ✅ Status installable basé sur la préparation
#    ✅ Visible dans l'App Store (si prête)
```

#### Méthode automatique simple 🔧
```bash
# 1. Créer l'app avec Django
poetry run python manage.py startapp nom_app apps/nom_app

# 2. Configurer automatiquement (INSTALLED_APPS + App Store)
poetry run python manage.py setup_auto_apps

# 3. L'app est configurée avec installable: True par défaut
```

#### Méthode manuelle (si vous préférez)
```bash
# 1. Créer l'app avec Django
poetry run python manage.py startapp nom_app apps/nom_app

# 2. L'app est automatiquement dans INSTALLED_APPS ✅
# 3. Créer manuellement apps/nom_app/__manifest__.py
# 4. Exécuter : poetry run python manage.py setup_auto_apps --no-manifests
```

### Commandes disponibles

#### Vérifier les apps découvertes
```bash
# Tester le système de découverte INSTALLED_APPS
poetry run python core/utils.py

# Voir le statut des manifests
poetry run python manage.py setup_auto_apps --dry-run
```

#### Commande setup_auto_apps
```bash
# Configuration complète automatique
poetry run python manage.py setup_auto_apps

# Configuration avec validation de préparation
poetry run python manage.py setup_auto_apps --check-readiness

# Options disponibles
poetry run python manage.py setup_auto_apps --dry-run         # Simulation
poetry run python manage.py setup_auto_apps --no-manifests   # Pas de création de manifests
poetry run python manage.py setup_auto_apps --no-sync        # Pas de sync BDD
```

#### Commande check_app_readiness (nouveau!)
```bash
# Vérifier la préparation de toutes les apps
poetry run python manage.py check_app_readiness

# Vérifier une app spécifique avec détails
poetry run python manage.py check_app_readiness --app revision --detailed

# Mettre à jour automatiquement les statuts installable
poetry run python manage.py check_app_readiness --update-manifests

# Résumé global seulement
poetry run python manage.py check_app_readiness --summary-only
```

### Exclure une app de la découverte
Si vous voulez exclure temporairement une app (équivalent à la commenter), modifiez `core/utils.py` :

```python
# Dans core/utils.py, fonction get_installed_apps()
exclude_from_discovery = [
    'coaching',      # Commentée dans l'ancienne config
    'payments',      # Commentée dans l'ancienne config  
    'task',          # Commentée dans l'ancienne config
    'screen',        # App incomplète
    'subscription',  # Commentée dans l'ancienne config
    'votre_app',     # Ajoutez ici pour exclure
]
```

## Configuration dans settings.py

### Nouvelle configuration (automatique)
```python
# core/settings.py
from .utils import get_installed_apps

INSTALLED_APPS = get_installed_apps()
```

### Ancienne configuration (manuelle) - désormais commentée
```python
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'apps.authentication',  # Maintenant auto-découvert
#     'apps.chat',            # Maintenant auto-découvert
#     # ...
# ]
```

## App Store Integration 🏪

### Système de manifests automatique
Chaque app peut avoir un fichier `__manifest__.py` qui définit ses métadonnées pour l'App Store :

```python
# apps/mon_app/__manifest__.py
__manifest__ = {
    'name': 'Mon App',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Description courte pour l\'App Store',
    'description': 'Description détaillée avec fonctionnalités...',
    'installable': True,
    'frontend_components': {
        'route': '/mon-app',
        'icon': 'bi-app',
        'static_icon': '/static/mon_app/description/icon.png',
        'display_category': 'productivity',
        'category_label': 'Productivité',
    },
    # ... plus d'options disponibles
}
```

### Génération automatique
- Si une app n'a pas de `__manifest__.py`, il sera généré automatiquement
- Les apps avec manifest apparaissent dans l'App Store
- Synchronisation automatique avec la base de données

### Système de validation de préparation 🔍

Le système évalue automatiquement si une app est prête pour la production :

#### Critères de validation
- **Structure des fichiers** (60 pts) : `apps.py`, `__manifest__.py`, `models.py`, `views.py`, etc.
- **Qualité du manifest** (100 pts) : Métadonnées complètes, descriptions, config frontend
- **Intégration Django** (100 pts) : App dans INSTALLED_APPS, modèles, URLs
- **Fichiers statiques** (50 pts) : Icône, dossier static

#### Niveaux de préparation
- **🚀 PRODUCTION_READY** (90%+) : `installable: True` automatiquement
- **⚠️ ALMOST_READY** (70-89%) : `installable: True` mais améliorations conseillées  
- **🔧 DEVELOPMENT** (50-69%) : `installable: False` - en développement
- **❌ NOT_READY** (<50%) : `installable: False` - développement incomplet

#### Mise à jour automatique
Le système peut automatiquement mettre à jour `installable: True/False` dans les manifests basé sur le score de préparation.

## Avantages

- ✅ **Plus d'oublis** : Toute nouvelle app est automatiquement configurée partout
- ✅ **INSTALLED_APPS automatique** : Plus besoin de modifier settings.py
- ✅ **App Store automatique** : Manifests générés et synchronisés automatiquement
- ✅ **Validation intelligente** : Statut `installable` basé sur la préparation réelle
- ✅ **Contrôle qualité** : Seules les apps prêtes apparaissent en production
- ✅ **Configuration DRY** : Plus besoin de dupliquer les noms d'apps
- ✅ **Cohérence** : Tri alphabétique et configuration standardisée
- ✅ **Flexibilité** : System d'exclusion pour les apps en développement
- ✅ **Rétrocompatibilité** : L'ancienne config reste en commentaire pour référence

## Structure des apps découvertes

Le système génère automatiquement cette structure dans `INSTALLED_APPS` :

```python
INSTALLED_APPS = [
    # Apps Django de base
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    
    # Apps du projet (auto-découvertes)
    'apps.authentication',
    'apps.calendar_app', 
    'apps.chat',
    'apps.cms_sync',
    'apps.community',
    'apps.course',
    'apps.data',
    'apps.documents',
    'apps.language_ai',
    'apps.notebook',
    'apps.notification',
    'apps.quizz',
    'apps.revision',
    'apps.teaching',
    'apps.todo',
    
    # Modules spéciaux
    'app_manager',
    'saas_web',
    'core.apps.CoreConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
]
```

## Dépannage

### App non détectée ?
- Vérifiez que l'app a un fichier `apps.py`
- Vérifiez qu'elle n'est pas dans la liste `exclude_from_discovery`
- Testez avec `poetry run python core/utils.py`

### Erreur au démarrage Django ?
- Vérifiez que l'app a une configuration valide dans `apps.py`
- Vérifiez les imports et dépendances de l'app

### Rollback vers l'ancienne configuration
Si besoin, vous pouvez revenir à l'ancienne configuration :

```python
# Dans core/settings.py
# from .utils import get_installed_apps
# INSTALLED_APPS = get_installed_apps()

# Décommentez l'ancienne liste INSTALLED_APPS manuelle
```