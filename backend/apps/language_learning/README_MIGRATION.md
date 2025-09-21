# Migration des données d'apprentissage des langues

## Vue d'ensemble

Cette migration transfère les champs liés à l'apprentissage des langues du modèle `User` (dans `authentication`) vers un nouveau modèle `UserLearningProfile` (dans `language_learning`).

## Raison de la migration

- **Séparation des responsabilités** : Les données d'apprentissage doivent être gérées dans l'app `language_learning`
- **Modularité** : Facilite l'extension des fonctionnalités d'apprentissage
- **Performance** : Réduit la taille du modèle User principal
- **Maintenabilité** : Code mieux organisé par domaine fonctionnel

## Champs migrés

Les champs suivants sont transférés depuis `User` vers `UserLearningProfile`:

### Langues et objectifs
- `native_language` → Langue maternelle
- `target_language` → Langue cible d'apprentissage
- `language_level` → Niveau actuel
- `objectives` → Objectifs d'apprentissage

### Préférences d'exercices
- `speaking_exercises` → Exercices d'expression orale
- `listening_exercises` → Exercices d'écoute
- `reading_exercises` → Exercices de lecture
- `writing_exercises` → Exercices d'écriture

### Paramètres de rappel
- `daily_goal` → Objectif quotidien en minutes
- `weekday_reminders` → Rappels en semaine
- `weekend_reminders` → Rappels le week-end
- `reminder_time` → Heure de rappel

## Structure du nouveau modèle

```python
class UserLearningProfile(models.Model):
    user = models.OneToOneField(User, related_name='learning_profile')
    # Tous les champs d'apprentissage...

    # Nouveaux champs ajoutés
    streak_count = models.PositiveIntegerField(default=0)
    total_time_spent = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
```

## Étapes de migration

### 1. Appliquer les migrations Django

```bash
python manage.py makemigrations language_learning
python manage.py migrate
```

### 2. Migrer les données existantes

```bash
# Migration automatique
python manage.py shell < apps/language_learning/migrations/migrate_learning_data.py

# Ou utilisation du script
python apps/language_learning/migrations/migrate_learning_data.py
```

### 3. Vérifier la migration

```bash
python apps/language_learning/migrations/migrate_learning_data.py --verify
```

### 4. (Optionnel) Annuler la migration

```bash
python apps/language_learning/migrations/migrate_learning_data.py --rollback
```

## Accès aux données

### Avant la migration
```python
user = User.objects.get(id=1)
level = user.language_level
target = user.target_language
```

### Après la migration

#### Méthode 1 : Via le profil
```python
user = User.objects.get(id=1)
profile = user.learning_profile  # Relation OneToOne
level = profile.language_level
target = profile.target_language
```

#### Méthode 2 : Via les propriétés de compatibilité
```python
user = User.objects.get(id=1)
level = user.learning_language_level  # Propriété qui accède au profil
target = user.learning_target_language
```

#### Méthode 3 : Get or create
```python
user = User.objects.get(id=1)
profile = user.get_learning_profile()  # Crée automatiquement si n'existe pas
```

## API et Serializers

Les serializers doivent être mis à jour pour utiliser les nouvelles relations:

```python
class UserSerializer(serializers.ModelSerializer):
    # Inclure les données du profil
    learning_profile = UserLearningProfileSerializer(read_only=True)

    # Ou utiliser les propriétés pour compatibilité
    language_level = serializers.CharField(source='learning_language_level')
    target_language = serializers.CharField(source='learning_target_language')
```

## Phase de transition

Pendant la phase de transition:

1. Les anciens champs restent dans le modèle User (marqués comme deprecated)
2. Les propriétés de compatibilité permettent l'accès transparent
3. Les nouvelles fonctionnalités utilisent `UserLearningProfile`
4. Migration progressive des vues et APIs

## Checklist post-migration

- [ ] Toutes les données migrées
- [ ] Tests unitaires passent
- [ ] APIs fonctionnelles
- [ ] Documentation mise à jour
- [ ] Monitoring des erreurs
- [ ] Plan de rollback prêt

## Support

Pour toute question sur cette migration, contactez l'équipe de développement.