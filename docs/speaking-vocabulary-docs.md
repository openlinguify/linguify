# Documentation: Association automatique de vocabulaire aux exercices de prononciation

## Aperçu

L'outil `speaking_auto_associate` permet d'associer automatiquement les éléments de vocabulaire pertinents aux exercices de prononciation (speaking) dans l'application Linguify. Cette commande évite d'avoir à associer manuellement chaque mot de vocabulaire à chaque exercice de prononciation, ce qui serait fastidieux et chronophage.

## Installation

L'outil est installé sous forme de commande Django dans le dossier:
```
backend/apps/course/management/commands/speaking_auto_associate.py
```

Les fichiers `__init__.py` doivent exister dans les dossiers `management/` et `management/commands/` pour que Django reconnaisse la commande.

## Utilisation

### Commande de base

Pour exécuter la commande avec les paramètres par défaut (traiter tous les exercices de prononciation sans effacer les associations existantes):

```bash
python manage.py speaking_auto_associate
```

### Options disponibles

| Option | Description |
|--------|-------------|
| `--lesson=ID` | Traiter uniquement l'exercice avec l'ID de leçon spécifié |
| `--force` | Remplacer les associations existantes au lieu de les préserver |

### Exemples d'utilisation

1. **Associer tous les mots de vocabulaire à tous les exercices de prononciation**
   ```bash
   python manage.py speaking_auto_associate --force
   ```

2. **Associer des mots de vocabulaire à un exercice spécifique**
   ```bash
   python manage.py speaking_auto_associate --lesson=24
   ```

3. **Mettre à jour un exercice spécifique en remplaçant les associations existantes**
   ```bash
   python manage.py speaking_auto_associate --lesson=24 --force
   ```

## Fonctionnement

Pour chaque exercice de prononciation, l'outil:

1. Vérifie si un objet `SpeakingExercise` existe pour cette leçon, et en crée un si nécessaire
2. Cherche d'abord des mots de vocabulaire dans la même leçon de contenu
3. Si aucun mot n'est trouvé, cherche dans toutes les leçons de vocabulaire appartenant à la même leçon parente
4. Associe tous les mots trouvés à l'exercice de prononciation

## Interface d'administration

En plus de la commande CLI, vous pouvez utiliser l'action d'administration dans l'interface Django:

1. Accédez à l'interface d'administration à `/admin/course/speakingexercise/`
2. Sélectionnez les exercices à mettre à jour
3. Dans le menu déroulant "Actions", choisissez "Associate vocabulary items from lessons"
4. Cliquez sur "Go"

## Bonnes pratiques

- **Créez d'abord vos leçons de vocabulaire**: L'outil ne peut associer que des mots existants
- **Utilisez l'option `--force` avec précaution**: Elle efface les associations existantes
- **Exécutez la commande après avoir ajouté de nouveaux mots**: Pour maintenir les associations à jour

## Dépannage

| Problème | Solution |
|----------|----------|
| "No vocabulary items found" | Vérifiez que des mots de vocabulaire existent dans la même unité et leçon |
| Aucun mot ajouté | Utilisez l'option `--force` pour remplacer les associations existantes |
| Erreur "Unknown command" | Vérifiez que les fichiers `__init__.py` existent dans les dossiers `management` |

## Maintenance

Pour modifier le comportement de l'outil:

1. Éditez le fichier `backend/apps/course/management/commands/speaking_auto_associate.py`
2. Vous pouvez ajuster la logique de recherche des mots de vocabulaire dans la méthode `handle()`
3. Pour modifier l'action admin, modifiez la méthode `associate_vocabulary_from_lesson()` dans `admin.py`

---

Utilisation recommandée pour le projet Linguify:
1. Créez d'abord toutes vos leçons et leur contenu de vocabulaire
2. Exécutez `python manage.py speaking_auto_associate --force` pour associer automatiquement tout le vocabulaire
3. En cas d'ajout de nouveaux mots de vocabulaire, exécutez à nouveau la commande