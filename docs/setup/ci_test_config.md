# Configuration des tests pour le CI

Ce document décrit les étapes nécessaires pour configurer correctement les tests unitaires à exécuter dans le workflow CI.

## Structure du projet

Le projet Linguify utilise une architecture Django avec plusieurs applications. Les tests sont organisés par module:

- `backend/apps/authentication/tests/` - Tests pour le module d'authentification
- `backend/apps/course/tests/` - Tests pour le module de cours

## Configuration de pytest

Le fichier `backend/pytest.ini` est configuré pour utiliser les paramètres suivants:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = core.settings
python_files = test_*.py
pythonpath = . apps
```

## Problèmes connus et solutions

### 1. Conflit de modèles

Lors de l'exécution des tests, il peut y avoir des conflits de modèles dus à la structure d'importation:

```
RuntimeError: Conflicting 'unit' models in application 'course'
```

**Solution**: Ajouter la ligne suivante au début des fichiers de test pour résoudre les conflits d'importation:

```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
```

### 2. Compatibilité avec PyJWT

Dans le fichier `auth0_auth.py`, il y a un problème avec l'importation de `InvalidKeyError`:

```
ImportError: cannot import name 'InvalidKeyError' from 'jwt.exceptions'
```

**Solution**: Mettre à jour le code pour être compatible avec les versions récentes de PyJWT:

```python
# Fix for newer versions of PyJWT
try:
    from jwt.exceptions import InvalidKeyError
except ImportError:
    # Use InvalidKeyTypeError as InvalidKeyError for newer PyJWT versions
    from jwt.exceptions import InvalidKeyTypeError as InvalidKeyError
```

## Exécution des tests dans le CI

Le workflow CI utilise les commandes suivantes pour exécuter les tests:

1. Installation des dépendances:
   ```yaml
   - name: Install the project dependencies
     run: poetry install
   ```

2. Exécution des tests:
   ```yaml
   - name: Run the automated tests
     run: poetry run pytest -v
   ```

## Fixtures personnalisées

Des fixtures personnalisées ont été ajoutées pour faciliter la création d'objets de test:

1. Pour le module Authentication:
   - `create_user` - Pour créer des utilisateurs de test
   - `create_coach` - Pour créer des profils de coach de test

2. Pour le module Course:
   - `create_unit` - Pour créer des unités de cours
   - `create_lesson` - Pour créer des leçons
   - `create_content_lesson` - Pour créer des contenus de leçon
   - `create_vocabulary` - Pour créer des éléments de vocabulaire

## Tests créés

### Tests d'Authentication

- Tests de gestion de compte (suppression, planification et annulation)
- Tests d'acceptation des conditions d'utilisation
- Tests de validation des langues natives et cibles

### Tests de Course

- Tests des exercices d'association (MatchingExercise)
- Tests des exercices à trous (FillBlankExercise)
- Tests des exercices de prononciation (SpeakingExercise)
- Tests du contenu théorique et de sa migration au format JSON
- Tests des exercices de nombres (Numbers)

## Recommandations pour le développement futur

1. Résoudre les conflits d'importation en normalisant la structure du projet
2. Mettre à jour les dépendances pour assurer la compatibilité (notamment PyJWT)
3. Améliorer la configuration de test pour une isolation des tests
4. Ajouter un service de base de données dans le workflow CI pour les tests qui nécessitent une base de données

## Base de données pour les tests

Les tests utilisent une base de données SQLite en mémoire par défaut. Pour les tests CI, il est recommandé d'utiliser une base de données PostgreSQL:

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: test_linguify
    ports:
      - 5432:5432
```