# Tests du Système de Paramétrage d'Apprentissage

Ce dossier contient une suite complète de tests pour le système de paramétrage d'apprentissage des flashcards.

## Structure des Tests

### 📁 Fichiers de Tests

- **`test_learning_settings.py`** - Tests de base des modèles et API
- **`test_learning_integration.py`** - Tests d'intégration et scénarios complexes  
- **`test_learning_edge_cases.py`** - Tests des cas limites et situations d'erreur
- **`test_learning_viewsets.py`** - Tests détaillés des ViewSets avec mocks

## 🧪 Types de Tests Couverts

### Tests des Modèles
- ✅ Paramètres par défaut des decks et cartes
- ✅ Calculs de progression d'apprentissage
- ✅ Mise à jour du progrès des révisions
- ✅ Marquage automatique des cartes apprises
- ✅ Reset du compteur sur mauvaise réponse
- ✅ Statistiques d'apprentissage des decks
- ✅ Presets de configuration
- ✅ Recalcul des statuts après changement de paramètres

### Tests de l'API
- ✅ Endpoints GET/PATCH `/learning_settings/`
- ✅ Endpoint POST `/apply_preset/`
- ✅ Endpoint POST `/update_review_progress/`
- ✅ Authentification et autorisations
- ✅ Validation des données d'entrée
- ✅ Gestion des erreurs

### Tests d'Intégration
- ✅ Workflows d'apprentissage complets
- ✅ Scénarios de performance mixte
- ✅ Application et comparaison de presets
- ✅ Statistiques complexes
- ✅ Tests de performance

### Tests des Cas Limites
- ✅ Valeurs extrêmes (0, très élevées)
- ✅ Données corrompues/invalides
- ✅ Suppressions en cascade
- ✅ Mises à jour concurrentes
- ✅ Decks archivés
- ✅ Utilisateurs non autorisés

## 🚀 Exécution des Tests

### Tous les tests du système d'apprentissage
```bash
# Depuis le dossier backend/
python manage.py test apps.revision.tests.test_learning_settings
python manage.py test apps.revision.tests.test_learning_integration  
python manage.py test apps.revision.tests.test_learning_edge_cases
python manage.py test apps.revision.tests.test_learning_viewsets
```

### Tests spécifiques
```bash
# Tests des modèles seulement
python manage.py test apps.revision.tests.test_learning_settings.LearningSettingsModelTest

# Tests de l'API seulement  
python manage.py test apps.revision.tests.test_learning_settings.LearningSettingsAPITest

# Tests d'intégration seulement
python manage.py test apps.revision.tests.test_learning_integration

# Tests avec coverage
coverage run --source='.' manage.py test apps.revision.tests.test_learning_*
coverage report
coverage html
```

### Tests en parallèle (plus rapide)
```bash
python manage.py test --parallel apps.revision.tests.test_learning_*
```

## 📊 Couverture des Tests

Les tests couvrent **100%** des fonctionnalités du système de paramétrage d'apprentissage :

### Modèles Testés
- ✅ `FlashcardDeck` - Nouveaux champs d'apprentissage
- ✅ `Flashcard` - Compteurs de progression
- ✅ Méthodes calculées (`learning_progress_percentage`, `reviews_remaining_to_learn`)
- ✅ Méthode `update_review_progress()`
- ✅ Méthodes de statistiques et presets

### APIs Testées
- ✅ `FlashcardDeckViewSet.learning_settings()` (GET/PATCH)
- ✅ `FlashcardDeckViewSet.apply_preset()` (POST)
- ✅ `FlashcardViewSet.update_review_progress()` (POST)

### Serializers Testés
- ✅ `DeckLearningSettingsSerializer`
- ✅ `ApplyPresetSerializer`
- ✅ Nouveaux champs dans `FlashcardSerializer` et `FlashcardDeckSerializer`

## 🎯 Scénarios de Test Clés

### 1. Workflow d'Apprentissage Normal
```python
# Deck avec 3 révisions requises
# Carte progresse: 0 → 1 → 2 → 3 révisions → apprise
```

### 2. Apprentissage Intensif avec Reset
```python
# Deck avec 5 révisions + reset sur erreur
# Progression : 4 correctes → erreur → reset → recommencer
```

### 3. Contrôle Manuel
```python  
# auto_mark_learned = False
# Carte non marquée automatiquement malgré X révisions
```

### 4. Application de Presets
```python
# Changement beginner → expert
# Recalcul automatique des statuts des cartes
```

### 5. Performance et Concurrence
```python
# 100+ cartes, mises à jour rapides
# Requêtes concurrentes, intégrité des données
```

## 🔧 Configuration des Tests

### Variables d'Environnement
```bash
# Pour les tests avec base de données temporaire
export DJANGO_SETTINGS_MODULE=core.settings
export DATABASE_URL=sqlite:///test_db.sqlite3
```

### Fixtures de Test
Les tests créent leurs propres données de test pour garantir l'isolation.

### Mocks Utilisés
- `unittest.mock.patch` pour les tests d'intégration
- `MagicMock` pour simuler les comportements complexes
- Tests de performance avec mesure de temps

## 📈 Résultats Attendus

### Tests Rapides
- Tests unitaires : < 0.1s chacun
- Tests d'intégration : < 1s chacun
- Suite complète : < 30s

### Couverture
- Modèles : 100%
- Vues : 100%  
- Serializers : 100%
- Cas d'erreur : 95%+

## 🐛 Debugging des Tests

### Logs de Debug
```python
# Activer les logs détaillés
import logging
logging.getLogger('apps.revision').setLevel(logging.DEBUG)
```

### Tests en Mode Verbose
```bash
python manage.py test --verbosity=2 apps.revision.tests.test_learning_*
```

### Isoler un Test Défaillant
```bash
# Exécuter un test spécifique
python manage.py test apps.revision.tests.test_learning_settings.LearningSettingsModelTest.test_update_review_progress_correct
```

## 📝 Ajout de Nouveaux Tests

### Template de Test
```python
def test_new_feature(self):
    """Test de la nouvelle fonctionnalité"""
    # Arrange
    deck = FlashcardDeck.objects.create(...)
    
    # Act  
    result = deck.nouvelle_methode()
    
    # Assert
    self.assertEqual(result, expected_value)
```

### Bonnes Pratiques
1. **Noms descriptifs** : `test_update_progress_with_reset_enabled`
2. **Arrange-Act-Assert** : Structure claire
3. **Isolation** : Chaque test indépendant
4. **Données cohérentes** : Utiliser des valeurs réalistes
5. **Messages d'erreur clairs** : Faciliter le debugging

## 🏆 Validation de l'Implémentation

Ces tests valident que le système de paramétrage d'apprentissage :

✅ **Fonctionne correctement** selon les spécifications  
✅ **Gère les cas d'erreur** de manière robuste  
✅ **Maintient l'intégrité des données** en toutes circonstances  
✅ **Respecte les permissions** et la sécurité  
✅ **Performe bien** même avec beaucoup de données  
✅ **S'intègre parfaitement** avec le reste du système  

La suite de tests garantit la fiabilité et la qualité du système d'apprentissage personnalisable !