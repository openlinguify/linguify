# Guide d'exécution des tests pour Linguify

Ce document explique comment exécuter les tests unitaires pour le projet Linguify.

## Structure des tests

Les tests sont organisés dans les répertoires suivants :

- `backend/tests/` - Tests généraux pour les fonctionnalités de base
- `backend/apps/authentication/tests/` - Tests pour le module d'authentification
- `backend/apps/course/tests/` - Tests pour le module de cours

Chaque répertoire peut contenir :
- Des tests standards (`test_*.py`)
- Des tests simplifiés (`test_*_simple.py`) qui évitent les problèmes d'importation

## Exécution de tous les tests

Pour exécuter tous les tests du projet, utilisez le script `run_all_tests.py` :

```bash
cd backend
poetry run python run_all_tests.py
```

Ce script :
1. Recherche automatiquement tous les fichiers de test dans les trois répertoires mentionnés ci-dessus
2. Privilégie les versions simplifiées des tests quand elles existent
3. Configure correctement l'environnement Django avant d'exécuter les tests

## Exécution des tests spécifiques

Si vous souhaitez exécuter des tests spécifiques, plusieurs scripts sont disponibles :

### Tests d'Authentication

```bash
cd backend
poetry run python run_test_authentication.py
```

### Tests de Course

```bash
cd backend
poetry run python run_test_course.py
```

### Tests simplifiés uniquement

```bash
cd backend
poetry run python run_simple_tests_all.py
```

## Problèmes connus et solutions

### Conflit de modèles

Le problème principal rencontré lors de l'exécution des tests est un conflit entre les modèles Django importés de différentes manières :

```
RuntimeError: Conflicting 'unit' models in application 'course': <class 'apps.course.models.Unit'> and <class 'backend.apps.course.models.Unit'>.
```

**Solution** : 
1. Utiliser les versions simplifiées des tests qui évitent d'importer directement les modèles
2. Utiliser les scripts fournis qui configurent correctement l'environnement Django

### Dépendances manquantes

Si vous obtenez une erreur du type `ModuleNotFoundError: No module named 'drf_spectacular'`, vous devez installer les dépendances manquantes :

```bash
cd backend
poetry add drf-spectacular
```

## Tests dans CI/CD

La configuration CI/CD (dans `.github/workflows/ci.yml`) est configurée pour exécuter automatiquement les tests avec le script `run_all_tests.py` à chaque push ou pull request sur les branches `main` et `develop`.

## Bonnes pratiques

1. **Nommage des tests** :
   - Préfixez tous les fichiers de test par `test_`
   - Utilisez le suffixe `_simple` pour les tests qui évitent les importations directes de modèles

2. **Tests isolés** :
   - Chaque test doit être indépendant et ne pas dépendre de l'état créé par d'autres tests
   - Utilisez des fixtures pour créer les données de test nécessaires

3. **Base de données** :
   - Utilisez la décoration `@pytest.mark.django_db` pour les tests qui nécessitent accès à la base de données
   - Nettoyez toujours les données créées pendant vos tests

4. **Ajout de nouveaux tests** :
   - Si vos nouveaux tests provoquent des conflits d'importation, créez une version simplifiée qui utilise `get_user_model()` au lieu d'importer directement les modèles