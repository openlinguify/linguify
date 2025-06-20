# 🗄️ Scripts de Gestion de Base de Données

Ce dossier contient les scripts pour gérer les bases de données de développement et production.

## 📋 Scripts Disponibles

### 🔄 **Synchronisation Production → Développement**

#### `export_production_data.py`
Exporte toutes les données depuis Supabase (production) vers un fichier JSON.
- **Usage**: Lancez avec `DJANGO_ENV="production"`
- **Sortie**: `production_export.json`

#### `import_to_development.py`
Importe les données de production dans la base locale de développement.
- **Usage**: Lancez avec `DJANGO_ENV="development"`
- **Prérequis**: Fichier `production_export.json`

#### `sync_prod_to_dev.py`
Script tout-en-un qui fait export + import automatiquement.
- **Usage**: Lance automatiquement export et import
- **Recommandé**: Pour synchronisation complète

### 🚀 **Déploiement Développement → Production**

#### `deploy_to_production.py`
**NOUVEAU** - Déploie sélectivement le contenu du développement vers la production.
- **Usage**: Menu interactif pour choisir quoi déployer
- **Cible**: Applications, cours, contenu spécifique
- **Sécurité**: Confirmation obligatoire avant déploiement

#### `selective_sync.py`
**NOUVEAU** - Synchronisation sélective et bidirectionnelle.
- **Usage**: Synchronise les changements récents ou éléments spécifiques
- **Fonctions**: Export des nouveautés, sync d'apps spécifiques

### 🛠️ **Utilitaires de Base de Données**

#### `setup_postgresql.sh`
Configure PostgreSQL pour le développement local.
- **Fonctions**: Installation, création des bases, configuration utilisateur

#### `clean_database.py`
Nettoie complètement la base de développement.
- **Usage**: Supprime et recrée `db_linguify_dev`

## 🎯 **Workflow Recommandé**

### Synchronisation Complète (Production → Développement)
```bash
# Option 1: Script automatique (recommandé)
python scripts/database/sync_prod_to_dev.py

# Option 2: Étapes manuelles
# 1. Export depuis production
python scripts/database/export_production_data.py  # avec DJANGO_ENV="production"

# 2. Import en développement
python scripts/database/import_to_development.py   # avec DJANGO_ENV="development"
```

### Déploiement de Nouvelles Fonctionnalités (Développement → Production)
```bash
# Option 1: Déploiement interactif complet
python scripts/database/deploy_to_production.py

# Option 2: Synchronisation sélective
python scripts/database/selective_sync.py

# Option 3: Déploiement d'une app spécifique
python scripts/database/selective_sync.py
# Choisir option 2, puis entrer le nom de l'app
```

### Cas d'usage typiques

#### Vous avez créé une nouvelle application "quiz_avance"
```bash
python scripts/database/selective_sync.py
# Choisir option 2: "Synchroniser une application spécifique"
# Entrer: quiz_avance
```

#### Vous avez ajouté de nouveaux cours cette semaine
```bash
python scripts/database/selective_sync.py
# Choisir option 1: "Export des changements depuis X jours"
# Entrer: 7
```

#### Déploiement complet d'une nouvelle version
```bash
python scripts/database/deploy_to_production.py
# Choisir ce qui doit être déployé via le menu interactif
```

### Configuration Initiale
```bash
# 1. Installer PostgreSQL
bash scripts/database/setup_postgresql.sh

# 2. Configurer .env
# DJANGO_ENV="development"

# 3. Synchroniser les données
python scripts/database/sync_prod_to_dev.py

# 4. Créer superuser local
python manage.py createsuperuser
```

## ⚙️ **Configuration**

### Variables d'environnement (.env)
```env
# Pour développement local
DJANGO_ENV="development"
DEV_DB_NAME="db_linguify_dev"
DEV_DB_USER="postgres"
DEV_DB_PASSWORD="azerty"

# Pour accès production (temporaire)
DJANGO_ENV="production"
SUPABASE_DB_HOST="aws-0-eu-west-3.pooler.supabase.com"
SUPABASE_DB_USER="postgres.bfsxhrpyotstyhddkvrf"
SUPABASE_DB_PASSWORD="owI0tzkNTLR9TVaB"
```

## 📊 **Données Synchronisées**

- **Utilisateurs** (`authentication.User`)
- **Applications** (`app_manager.App`)
- **Cours** (Unités, Leçons, Vocabulaire, Exercices)
- **Jobs** (Postes, Candidatures, CVs)
- **Notebooks** (Notes, Catégories)
- **Révision** (Flashcards, Decks)

**Données exclues** (pour éviter les conflits):
- Sessions Django
- Tokens d'authentification
- Logs admin
- Notifications (tables problématiques)

## 🔍 **Dépannage**

### Erreurs courantes

#### "UniqueViolation: clé dupliquée"
```bash
# Nettoyer complètement la base
python scripts/database/clean_database.py
# Puis relancer l'import
```

#### "Connection refused"
```bash
# Vérifier PostgreSQL
sudo service postgresql start
# Ou installer si nécessaire
bash scripts/database/setup_postgresql.sh
```

#### "DJANGO_ENV non détecté"
```bash
# Vérifier le fichier .env
cat .env | grep DJANGO_ENV
# Doit afficher: DJANGO_ENV="development" ou "production"
```

## 🎯 **Accès aux CVs de Production**

Pour consulter les CVs réels des candidatures :

1. **Changer temporairement** dans `.env` :
   ```env
   DJANGO_ENV="production"
   ```

2. **Lancer le serveur** :
   ```bash
   python manage.py runserver
   ```

3. **Accéder à l'admin** :
   ```
   http://localhost:8000/admin/jobs/jobapplication/
   ```

4. **Revenir en développement** :
   ```env
   DJANGO_ENV="development"
   ```

## ✅ **Validation**

Après synchronisation, vérifiez que les données sont présentes :
```bash
python manage.py shell
>>> from apps.authentication.models import User
>>> from apps.course.models import Lesson
>>> print(f"Users: {User.objects.count()}")
>>> print(f"Lessons: {Lesson.objects.count()}")
```

---

**Note**: Ces scripts maintiennent une séparation claire entre développement et production, permettant un développement sécurisé avec des données réelles.