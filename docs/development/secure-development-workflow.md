# Workflow de Développement Sécurisé - Linguify

## 🎯 Objectif

Ce document établit un workflow de développement sécurisé pour éviter que les développeurs "défoncent" le projet Linguify. Il comprend des scripts automatisés, des hooks Git et des procédures de validation.

## 🔧 Configuration Initiale

### 1. Setup de l'Environnement

Pour configurer un nouvel environnement de développement :

```bash
# Cloner le projet
git clone <url-du-projet>
cd linguify

# Configurer l'environnement automatiquement
./scripts/setup-dev-environment.sh
```

Ce script configure :
- ✅ Environnement virtuel Python
- ✅ Dépendances backend et frontend
- ✅ Git hooks de sécurité
- ✅ Configuration IDE
- ✅ Validation de l'installation

### 2. Git Hooks Automatiques

Un **pre-commit hook** est automatiquement installé pour :
- ❌ Bloquer les modifications de fichiers core
- ✅ Autoriser uniquement `custom/`, `docs/`, `scripts/`
- 🔍 Vérifier la conformité des commits

## 🚀 Workflow de Développement

### Étape 1 : Créer un Nouveau Module

```bash
# Utiliser le générateur de modules
./linguify-bin scaffold mon_nouveau_module custom

# Le module est créé dans :
# ✅ backend/apps/custom/mon_nouveau_module/
# ✅ frontend/src/addons/custom/mon_nouveau_module/ (optionnel)
```

### Étape 2 : Développer dans l'Isolation

```bash
# Créer une branche feature
git checkout -b feature/mon-nouveau-module

# Développer UNIQUEMENT dans custom/
# ✅ backend/apps/custom/mon_nouveau_module/
# ✅ frontend/src/addons/custom/mon_nouveau_module/
# ❌ NE JAMAIS modifier backend/apps/course/ ou autres apps core
```

### Étape 3 : Validation Continue

```bash
# Valider le module avant commit
./scripts/validate-development.sh mon_nouveau_module

# Ce script vérifie :
# ✅ Emplacement correct (custom/)
# ✅ Fichiers obligatoires présents
# ✅ Manifest valide
# ✅ Permissions sécurisées
# ✅ Pas de secrets hardcodés
# ✅ Tests passants
# ✅ Build frontend réussi
```

### Étape 4 : Commit Sécurisé

```bash
# Le pre-commit hook vérifie automatiquement
git add backend/apps/custom/mon_nouveau_module/
git commit -m "feat(mon-nouveau-module): add new functionality"

# Format de commit obligatoire :
# type(scope): description
# Types: feat, fix, docs, style, refactor, test, chore
```

### Étape 5 : Tests et CI/CD

```bash
# Tests backend
cd backend
python manage.py test apps.custom.mon_nouveau_module

# Tests frontend
cd frontend
npm test -- --testPathPattern="mon_nouveau_module"

# Build complet
npm run build
```

## 🛡️ Sécurité et Validation

### Scripts de Validation Automatique

#### `validate-development.sh`
Script principal de validation qui vérifie :

1. **Emplacement** : Module dans `custom/`
2. **Fichiers** : Tous les fichiers obligatoires présents
3. **Manifest** : Configuration valide
4. **Modèles** : Préfixe `custom_` pour les tables
5. **Permissions** : `IsAuthenticated` dans les vues
6. **Sécurité** : Pas de secrets hardcodés
7. **Tests** : Backend et frontend passants
8. **Build** : Frontend build sans erreur
9. **Commits** : Format conforme

#### `setup-dev-environment.sh`
Script d'installation qui configure :

1. **Prérequis** : Python, Node.js, Git
2. **Git Hooks** : Pre-commit automatique
3. **Backend** : Virtual env, dépendances, migrations
4. **Frontend** : npm install, configuration
5. **IDE** : Configuration VS Code
6. **Validation** : Tests de l'installation

### Git Hooks de Protection

Le **pre-commit hook** bloque automatiquement :

```bash
# ❌ BLOQUÉ - Modification core
git add backend/apps/authentication/models.py

# ✅ AUTORISÉ - Modification custom
git add backend/apps/custom/mon_module/models.py
```

## 📋 Checklist de Développement

### Avant de Commencer
- [ ] Environnement configuré avec `setup-dev-environment.sh`
- [ ] Branche feature créée
- [ ] Module généré avec `linguify-bin scaffold`

### Pendant le Développement
- [ ] Code développé uniquement dans `custom/`
- [ ] Tests écrits et passants
- [ ] Pas de secrets hardcodés
- [ ] Permissions correctement configurées

### Avant le Commit
- [ ] Validation avec `validate-development.sh`
- [ ] Build frontend réussi
- [ ] Format de commit respecté
- [ ] Git hooks passent automatiquement

### Avant la Pull Request
- [ ] Tous les tests passent
- [ ] Documentation mise à jour
- [ ] Code review effectuée
- [ ] Aucune modification de fichier core

## 🚨 Violations et Remédiation

### Violation Détectée : Modification Core

Si le pre-commit hook détecte une modification core :

```bash
❌ Modification interdite de fichier core: backend/apps/authentication/models.py
🚨 Commit bloqué: modifications de fichiers core détectées
```

**Remédiation :**
1. Annuler les modifications core
2. Créer le modèle dans votre app custom
3. Utiliser des relations pour connecter aux modèles core

### Validation Échouée

Si `validate-development.sh` échoue :

```bash
❌ Permissions manquantes: utilisez IsAuthenticated dans vos vues
```

**Remédiation :**
1. Corriger le problème identifié
2. Relancer la validation
3. Commit uniquement après validation réussie

## 📊 Métriques et Monitoring

### Indicateurs de Qualité

Le workflow impose :
- **Couverture Tests** : Minimum 80% backend, 70% frontend
- **Sécurité** : 0 secret hardcodé
- **Isolation** : 100% développement dans `custom/`
- **Performance** : Build frontend < 2 minutes

### Rapports Automatiques

Les scripts génèrent des rapports sur :
- ✅ Modules validés avec succès
- ❌ Violations de sécurité détectées
- 📊 Couverture de tests
- ⚡ Performance des builds

## 🔄 Intégration Continue

### Pipeline de Validation

```yaml
# .github/workflows/custom-module-validation.yml
name: Validate Custom Modules

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Environment
        run: ./scripts/setup-dev-environment.sh
        
      - name: Validate Custom Modules
        run: |
          for module in backend/apps/custom/*/; do
            module_name=$(basename "$module")
            ./scripts/validate-development.sh "$module_name"
          done
```

## 📚 Documentation et Formation

### Ressources pour Développeurs

1. **Guide Principal** : `docs/development/developer-guidelines.md`
2. **Structure Template** : `docs/development/app-structure-template.md`
3. **Règles de Code** : `docs/development/development-rules.md`
4. **Workflow Sécurisé** : Ce document

### Formation des Nouveaux Développeurs

1. **Setup** : Exécuter `setup-dev-environment.sh`
2. **Tutorial** : Créer un module de test
3. **Validation** : Utiliser `validate-development.sh`
4. **Review** : Code review du premier module

## 🎯 Résumé des Bonnes Pratiques

### ✅ À FAIRE ABSOLUMENT
1. Développer dans `custom/` uniquement
2. Utiliser les scripts de génération et validation
3. Écrire des tests pour chaque fonctionnalité
4. Respecter les conventions de nommage
5. Valider avant chaque commit

### ❌ À ÉVITER ABSOLUMENT
1. Modifier les apps core existantes
2. Bypasser les git hooks
3. Hardcoder des secrets
4. Commit sans validation
5. Ignorer les erreurs de build

---

**Le respect de ce workflow garantit la stabilité, la sécurité et la maintenabilité du projet Linguify.** 🚀