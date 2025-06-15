# Commande fix_translations

Cette commande Django permet de corriger et compiler les traductions de l'application Linguify.

## Usage

```bash
python manage.py fix_translations [options]
```

## Options disponibles

### `--languages LANG1 LANG2 ...`
Spécifie les langues à traiter (par défaut: fr en es nl)

```bash
python manage.py fix_translations --languages fr en
```

### `--skip-makemessages`
Ignore l'extraction des messages traduisibles (makemessages)

```bash
python manage.py fix_translations --skip-makemessages
```

### `--skip-compilemessages`
Ignore la compilation des messages

```bash
python manage.py fix_translations --skip-compilemessages
```

### `--fix-encoding-only`
Corrige uniquement l'encodage des fichiers sans autre traitement

```bash
python manage.py fix_translations --fix-encoding-only
```

## Exemples d'utilisation

### Correction complète (recommandé)
```bash
python manage.py fix_translations
```

### Correction d'encodage uniquement
```bash
python manage.py fix_translations --fix-encoding-only
```

### Compilation sans extraction
```bash
python manage.py fix_translations --skip-makemessages
```

### Traitement de langues spécifiques
```bash
python manage.py fix_translations --languages fr en --fix-encoding-only
```

## Ce que fait la commande

1. **Correction d'encodage** :
   - Supprime les fichiers .mo corrompus
   - Vérifie et corrige l'encodage UTF-8 des fichiers .po
   - Corrige les déclarations charset incorrectes

2. **Extraction des messages** (si pas skippée) :
   - Exécute `makemessages` pour extraire les chaînes traduisibles
   - Ignore les répertoires env, venv, staticfiles, node_modules

3. **Compilation** (si pas skippée) :
   - Compile les fichiers .po en .mo
   - Affiche les instructions pour redémarrer le serveur

## Résolution des problèmes

### Erreur "Can't find msgfmt"
Cette erreur indique que les outils GNU gettext ne sont pas installés :

- **Ubuntu/Debian** : `sudo apt-get install gettext`
- **MacOS** : `brew install gettext`
- **Windows** : installer gettext via MSYS2 ou WSL

### Fichiers .po corrompus
Utilisez l'option `--fix-encoding-only` pour corriger uniquement l'encodage sans compilation.

## Intégration

Cette commande remplace l'ancien script `fix_translations.py` et est maintenant intégrée au système de management de Django, permettant une meilleure intégration avec les settings et la configuration du projet.