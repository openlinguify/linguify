# Guide des Bonnes Pratiques Développeur - Linguify

## 🎯 Objectif
Ce guide établit les règles et bonnes pratiques pour éviter de "défoncer" le projet Linguify lors du développement de nouvelles fonctionnalités.

## 📁 Structure de Développement Recommandée

### ✅ FAIRE : Utiliser le dossier `custom/`

Toutes les nouvelles apps et fonctionnalités doivent être créées dans le dossier `custom/` :

```
backend/apps/custom/
├── mon_nouveau_module/          # ✅ Nouveau module ici
├── bibliotheque/               # ✅ Exemple d'app custom
└── autre_feature/              # ✅ Autre développement
```

### ❌ NE PAS FAIRE : Modifier les apps core

```
backend/apps/
├── authentication/            # ❌ NE PAS MODIFIER
├── course/                   # ❌ NE PAS MODIFIER  
├── notification/             # ❌ NE PAS MODIFIER
└── ...                      # ❌ Apps core = interdites
```

## 🛠️ Workflow de Développement Sécurisé

### 1. Créer une Nouvelle App Linguify

**Étape 1 : Utiliser le générateur de modules**
```bash
./linguify-bin scaffold nom_de_mon_app custom
```

**Étape 2 : Vérifier la structure générée**
```
backend/apps/custom/nom_de_mon_app/
├── __init__.py
├── __manifest__.py          # ✅ Configuration du module
├── models.py               # ✅ Vos modèles
├── views.py                # ✅ Vos vues API
├── serializers.py          # ✅ Vos serializers
├── urls.py                 # ✅ Vos routes
├── admin.py                # ✅ Admin Django
└── tests.py                # ✅ Vos tests
```

### 2. Configuration Frontend

**Structure recommandée pour le frontend :**
```
frontend/src/addons/custom/
├── nom_de_mon_app/
│   ├── components/          # ✅ Composants React
│   ├── api/                # ✅ Calls API
│   ├── types/              # ✅ Types TypeScript
│   └── hooks/              # ✅ Hooks personnalisés
```

### 3. Intégration Backend

**Dans `backend/core/settings.py` :**
```python
# ✅ Ajouter votre app custom ici
CUSTOM_APPS = [
    'apps.custom.bibliotheque',
    'apps.custom.nom_de_mon_app',  # ✅ Nouvelle app
]

DJANGO_APPS = [
    # Apps core - NE PAS MODIFIER
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS + CUSTOM_APPS
```

## 📋 Règles de Développement

### 🔒 Règles OBLIGATOIRES

1. **Isolation des développements**
   - ✅ Toujours développer dans `custom/`
   - ❌ Jamais modifier les apps core existantes
   - ✅ Utiliser des modèles séparés

2. **Gestion des dépendances**
   - ✅ Utiliser `ForeignKey` vers les modèles core si nécessaire
   - ✅ Importer les serializers/views core si besoin
   - ❌ Ne jamais modifier directement un modèle core

3. **Base de données**
   - ✅ Créer vos propres migrations dans votre app
   - ❌ Jamais modifier les migrations core
   - ✅ Utiliser des tables séparées avec préfixe

### 🎨 Bonnes Pratiques Frontend

1. **Structure des composants**
```tsx
// ✅ Structure recommandée
frontend/src/addons/custom/mon_app/
├── components/
│   ├── MonAppMain.tsx       # Composant principal
│   ├── MonAppList.tsx       # Liste
│   └── shared/              # Composants partagés
├── api/
│   └── monAppAPI.ts         # Calls API
└── types/
    └── index.ts             # Types TypeScript
```

2. **Nommage des composants**
```tsx
// ✅ Bon nommage
export const BibliothequeMain = () => { ... }
export const BibliothequeBookList = () => { ... }

// ❌ Mauvais nommage
export const Main = () => { ... }
export const List = () => { ... }
```

### 🔧 Gestion des APIs

**Structure API recommandée :**
```python
# backend/apps/custom/mon_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'items', views.MonAppViewSet)

urlpatterns = [
    path('api/custom/mon-app/', include(router.urls)),
]
```

**Calls API Frontend :**
```typescript
// frontend/src/addons/custom/mon_app/api/monAppAPI.ts
import { apiClient } from '@/core/api/apiClient';

export const monAppAPI = {
  getItems: () => apiClient.get('/api/custom/mon-app/items/'),
  createItem: (data) => apiClient.post('/api/custom/mon-app/items/', data),
};
```

## 🚨 Signalements d'Erreurs Communes

### ❌ Erreur : Modifier une app core
```python
# ❌ NE JAMAIS FAIRE
# Dans backend/apps/authentication/models.py
class User(AbstractUser):
    mon_nouveau_champ = models.CharField(...)  # ❌ INTERDIT
```

**✅ Solution :**
```python
# ✅ Dans votre app custom
class MonAppProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mon_nouveau_champ = models.CharField(...)
```

### ❌ Erreur : Imports incorrects
```python
# ❌ Mauvais import
from apps.authentication.models import User
```

**✅ Solution :**
```python
# ✅ Bon import
from django.contrib.auth import get_user_model
User = get_user_model()
```

## 🧪 Tests et Validation

### Tests obligatoires
```python
# backend/apps/custom/mon_app/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model

class MonAppTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test', password='test'
        )
    
    def test_mon_app_functionality(self):
        # ✅ Tester votre fonctionnalité
        pass
```

### Commandes de validation
```bash
# ✅ Lancer avant chaque commit
cd backend
python manage.py test apps.custom.mon_app
python manage.py check
python manage.py makemigrations --dry-run
```

## 📚 Exemples de Développement

### Exemple 1 : Module Bibliothèque
```
backend/apps/custom/bibliotheque/
├── models.py              # Book, Author models
├── serializers.py         # API serializers
├── views.py              # CRUD views
└── urls.py               # /api/custom/bibliotheque/
```

### Exemple 2 : Module Analytics  
```
backend/apps/custom/analytics/
├── models.py              # UserStats, Report models
├── tasks.py              # Celery tasks
├── services.py           # Business logic
└── views.py              # Analytics endpoints
```

## 🔄 Workflow Git Recommandé

1. **Créer une branche pour votre feature**
```bash
git checkout -b feature/mon-nouveau-module
```

2. **Développer dans custom/ uniquement**
```bash
./linguify-bin scaffold mon_module custom
# Développer votre code...
```

3. **Tester avant commit**
```bash
cd backend && python manage.py test apps.custom.mon_module
cd frontend && npm run build
```

4. **Commit et push**
```bash
git add backend/apps/custom/mon_module/
git add frontend/src/addons/custom/mon_module/
git commit -m "feat: add mon_module functionality"
```

## 📞 Support et Questions

Si vous avez des questions ou rencontrez des problèmes :

1. **Vérifiez ce guide en premier**
2. **Consultez les exemples dans `custom/bibliotheque/`**
3. **Utilisez le générateur : `./linguify-bin scaffold`**
4. **Testez toujours dans l'environnement de dev**

## 🎯 Résumé des Bonnes Pratiques

| ✅ À FAIRE | ❌ À ÉVITER |
|------------|-------------|
| Développer dans `custom/` | Modifier les apps core |
| Utiliser le générateur de modules | Créer des apps manuellement |
| Tester avant commit | Commit sans tests |
| Suivre la structure recommandée | Inventer sa propre structure |
| Utiliser des imports corrects | Imports directs des apps core |
| Documenter son code | Code sans documentation |

---

**Rappel Important** : Le respect de ces règles garantit la stabilité du projet et facilite la maintenance. Toute modification des apps core doit être discutée en équipe avant implémentation.