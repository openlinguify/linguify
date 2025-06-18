# Jobs Module

Ce module gère toute la fonctionnalité de recrutement et carrières pour Linguify.

## Structure

```
core/jobs/
├── models.py                 # Modèles Django (Department, JobPosition, JobApplication)
├── views.py                  # Vues API REST
├── serializers.py           # Serializers DRF
├── admin.py                 # Interface d'administration
├── urls.py                  # Routes API
├── migrations/              # Migrations Django
├── tests/                   # Tests unitaires
├── management/              # Commandes de gestion
│   └── commands/
├── static/                  # Assets statiques (source)
│   └── src/
│       ├── css/
│       │   └── careers.css  # Styles de la page carrières
│       ├── js/
│       │   └── careers.js   # JavaScript de la page carrières
│       └── templates/       # Templates carrières
│           ├── careers.html # Page principale
│           ├── careers_position_detail.html     # Détail poste
│           ├── careers_position_not_found.html  # Page 404
│           └── careers_position_closed.html     # Poste fermé
└── export_assets.py        # Script d'export vers public_web
```

## Fonctionnalités

### API REST
- `GET /api/v1/jobs/departments/` - Liste des départements
- `GET /api/v1/jobs/positions/` - Liste des postes avec filtrage
- `GET /api/v1/jobs/positions/{id}/` - Détails d'un poste
- `POST /api/v1/jobs/apply/` - Soumettre une candidature
- `GET /api/v1/jobs/stats/` - Statistiques générales

### Page Carrières
La page carrières est intégrée dans `public_web` mais gérée depuis ce module :

#### Assets
- **CSS** : Styles modernes avec animations et responsive design
- **JavaScript** : Filtrage par département, modal de candidature, smooth scrolling
- **Template** : Template Django avec i18n et structure sémantique

#### Fonctionnalités
- Affichage des postes ouverts avec filtrage par département
- Modal de candidature avec instructions détaillées
- Design responsive et accessible
- Animations et transitions fluides
- Intégration email (mailto + copie dans le presse-papiers)

## Utilisation

### Build System
Le module dispose d'un système de build automatisé :

```bash
cd backend/core/jobs

# Build complet (recommandé)
python build.py

# Actions spécifiques
python build.py --export        # Export assets uniquement
python build.py --test          # Tests uniquement
python build.py --validate      # Validation assets
python build.py --sample-data   # Créer données d'exemple
python build.py --dev-setup     # Setup environnement dev
```

### Workflow de développement
1. **Développer** : Modifier les assets dans `core/jobs/static/src/`
2. **Tester** : `python build.py --export && python manage.py runserver`
3. **Valider** : `python build.py --build`
4. **Commiter** : Git commit des deux emplacements (source + export)

### Assets exportés automatiquement
- `static/src/css/careers.css` → `public_web/static/src/css/careers.css`
- `static/src/js/careers.js` → `public_web/static/src/js/careers.js`
- `static/src/templates/*.html` → `public_web/templates/public_web/*.html`
  - `careers.html` - Page principale carrières
  - `careers_position_detail.html` - Détail d'un poste
  - `careers_position_not_found.html` - Page 404 poste  
  - `careers_position_closed.html` - Poste fermé

### Administration
L'interface d'administration permet de :
- Gérer les départements et postes
- Voir les candidatures reçues
- Marquer les postes comme "en vedette"
- Suivre les statistiques de candidature

### Commandes de gestion
```bash
# Créer des postes d'exemple
python manage.py create_sample_jobs

# Tester le module
python manage.py test_jobs_module
```

## Configuration

### Email
Les candidatures sont envoyées par email à `careers@linguify.com`. 
Configurer les paramètres SMTP dans Django settings.

### Base de données
Les modèles utilisent les tables existantes :
- `jobs_department`
- `jobs_jobposition` 
- `jobs_jobapplication`

## Tests

```bash
# Tests du module complet
python manage.py test core.jobs

# Tests spécifiques
python manage.py test core.jobs.tests.test_models
python manage.py test core.jobs.tests.test_api
```

## Contribution

1. Développer dans `core/jobs/static/src/`
2. Tester localement
3. Exporter avec le script
4. Créer une PR avec les deux emplacements

## Notes techniques

- Les modèles utilisent `db_table` pour maintenir la compatibilité avec l'ancienne structure
- Le JavaScript utilise des classes ES6 pour une meilleure organisation
- Le CSS utilise une approche BEM pour la nomenclature
- Les templates sont entièrement i18n-ready