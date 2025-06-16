# Règles de Développement Linguify

## 🚨 Règles CRITIQUES (Non-négociables)

### 1. Isolation du Code Custom
```bash
# ✅ TOUJOURS développer ici
backend/apps/custom/
frontend/src/addons/custom/

# ❌ JAMAIS toucher aux apps core
backend/apps/authentication/  # INTERDIT
backend/apps/course/          # INTERDIT
backend/apps/notification/    # INTERDIT
```

### 2. Gestion de la Base de Données
```python
# ✅ BON : Modèles dans custom avec préfixes
class MonModel(models.Model):
    class Meta:
        db_table = 'custom_mon_app_monmodel'  # ✅ Préfixe obligatoire

# ❌ INTERDIT : Modifier modèles core
class User(AbstractUser):  # ❌ Ne jamais modifier User directement
    nouveau_champ = models.CharField(...)
```

### 3. Migrations
```bash
# ✅ Migrations custom seulement
python manage.py makemigrations mon_app_custom

# ❌ INTERDIT : Modifier migrations core
backend/apps/authentication/migrations/  # NE PAS TOUCHER
```

## 📋 Standards de Code

### Nommage des Fichiers et Classes
```python
# ✅ Backend - Convention Django
class BibliothequeBook(models.Model):      # PascalCase
    title = models.CharField()             # snake_case

def get_user_books(user):                  # snake_case
    return BibliothequeBook.objects.filter(user=user)
```

```typescript
// ✅ Frontend - Convention React/TypeScript
export const BibliothequeMain = () => {}   // PascalCase composants
export const useBookList = () => {}        // camelCase hooks
export interface BookItem {                // PascalCase interfaces
  id: number;
  title: string;                           // camelCase propriétés
}
```

### Structure des Imports
```python
# ✅ Ordre des imports Python
# 1. Standard library
from datetime import datetime
import json

# 2. Third party
from django.db import models
from rest_framework import serializers

# 3. Local/Custom
from .models import MonModel
from apps.authentication.models import User  # ✅ Import autorisé en lecture
```

```typescript
// ✅ Ordre des imports TypeScript
// 1. React/Next
import React from 'react';
import { useState } from 'react';

// 2. Third party
import { Button } from '@/components/ui/button';

// 3. Core Linguify
import { apiClient } from '@/core/api/apiClient';

// 4. Custom/Local
import { MonAppAPI } from './api/monAppAPI';
```

## 🔒 Sécurité et Permissions

### Authentication Backend
```python
# ✅ Toujours vérifier l'authentification
from rest_framework.permissions import IsAuthenticated

class MonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # ✅ Obligatoire
    
    def get_queryset(self):
        # ✅ Filtrer par utilisateur
        return MonModel.objects.filter(user=self.request.user)
```

### Validation des Données
```python
# ✅ Validation côté backend
class MonModelSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        max_length=200,
        min_length=2,
        required=True
    )
    
    def validate_title(self, value):
        # ✅ Validation custom
        if 'spam' in value.lower():
            raise serializers.ValidationError("Contenu non autorisé")
        return value
```

```typescript
// ✅ Validation côté frontend
const validateForm = (data: BookForm) => {
  const errors: Record<string, string> = {};
  
  if (!data.title || data.title.length < 2) {
    errors.title = 'Titre requis (min 2 caractères)';
  }
  
  return errors;
};
```

## 🧪 Tests Obligatoires

### Tests Backend
```python
# ✅ Structure de test minimale
class MonAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_item(self):
        """Test création d'un item"""
        data = {'title': 'Test Item'}
        response = self.client.post('/api/custom/mon-app/items/', data)
        self.assertEqual(response.status_code, 201)
    
    def test_user_isolation(self):
        """Test que les users ne voient que leurs données"""
        # Créer item pour autre user
        other_user = User.objects.create_user(username='other')
        MonModel.objects.create(user=other_user, title='Other Item')
        
        # Vérifier isolation
        response = self.client.get('/api/custom/mon-app/items/')
        self.assertEqual(len(response.data), 0)  # Ne voit pas les autres
```

### Tests Frontend
```typescript
// ✅ Tests React avec Jest/Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { MonAppMain } from './MonAppMain';

describe('MonAppMain', () => {
  test('renders correctly', () => {
    render(<MonAppMain />);
    expect(screen.getByText('Mon App')).toBeInTheDocument();
  });
  
  test('creates new item', async () => {
    render(<MonAppMain />);
    
    fireEvent.click(screen.getByText('Ajouter'));
    fireEvent.change(screen.getByLabelText('Titre'), {
      target: { value: 'Nouveau Item' }
    });
    fireEvent.click(screen.getByText('Sauvegarder'));
    
    await screen.findByText('Nouveau Item');
  });
});
```

## 📁 Organisation des Fichiers

### Backend - Règles de Structure
```
backend/apps/custom/mon_app/
├── __init__.py                 # ✅ Vide ou imports de base
├── __manifest__.py            # ✅ Métadonnées du module
├── models/                    # ✅ Si >1 modèle, créer dossier
│   ├── __init__.py           # from .book import Book
│   ├── book.py               # 1 modèle par fichier
│   └── author.py
├── views/                     # ✅ Si >3 vues, créer dossier
│   ├── __init__.py
│   ├── book_views.py
│   └── author_views.py
├── serializers/               # ✅ Si >3 serializers
├── services/                  # ✅ Business logic complexe
│   ├── __init__.py
│   ├── book_service.py        # Logique métier
│   └── export_service.py
└── utils/                     # ✅ Utilitaires
    ├── __init__.py
    ├── helpers.py
    └── validators.py
```

### Frontend - Règles de Structure
```
frontend/src/addons/custom/mon_app/
├── components/
│   ├── MonAppMain.tsx         # 1 composant = 1 fichier
│   ├── forms/                 # Grouper par fonctionnalité
│   │   ├── BookForm.tsx
│   │   └── AuthorForm.tsx
│   ├── lists/
│   │   ├── BookList.tsx
│   │   └── AuthorList.tsx
│   └── shared/                # Composants réutilisables
│       ├── ItemCard.tsx
│       └── EmptyState.tsx
├── hooks/
│   ├── useBooks.ts            # 1 hook par fonctionnalité
│   ├── useBookForm.ts
│   └── useBookFilters.ts
├── types/
│   ├── index.ts               # Exports principaux
│   ├── book.types.ts          # Types par domaine
│   └── api.types.ts
└── constants/
    ├── index.ts
    └── validation.ts
```

## 🚦 Git Workflow

### Branches
```bash
# ✅ Convention de nommage
feature/mon-app-creation          # Nouvelle fonctionnalité
fix/mon-app-bug-title            # Correction de bug
refactor/mon-app-api-cleanup     # Refactoring
docs/mon-app-documentation       # Documentation

# ❌ Éviter
main                             # Branch protégée
develop                          # Branch protégée
```

### Commits
```bash
# ✅ Convention Conventional Commits
feat(mon-app): add book creation functionality
fix(mon-app): resolve title validation issue
docs(mon-app): add API documentation
test(mon-app): add unit tests for book service

# ❌ Messages vagues
git commit -m "fix"
git commit -m "update"
git commit -m "work in progress"
```

### Pull Requests
```markdown
# ✅ Template de PR
## Description
Ajout du module Bibliothèque avec gestion des livres et auteurs.

## Changes
- ✅ Modèles Book et Author créés
- ✅ API CRUD complète
- ✅ Interface React avec formulaires
- ✅ Tests unitaires (backend + frontend)
- ✅ Documentation mise à jour

## Testing
- [ ] Tests backend passent
- [ ] Tests frontend passent
- [ ] Build frontend réussit
- [ ] Migrations appliquées

## Screenshots
[Captures d'écran si pertinent]
```

## 🔍 Code Review Checklist

### Backend Review
- [ ] Modèles dans `custom/` avec bon préfixe
- [ ] Permissions `IsAuthenticated` présentes
- [ ] Filtrage par user implémenté
- [ ] Validation des données côté serveur
- [ ] Tests unitaires écrits
- [ ] Admin interface configurée
- [ ] Migrations créées proprement

### Frontend Review
- [ ] Composants dans `addons/custom/`
- [ ] Types TypeScript définis
- [ ] Gestion d'erreur implémentée
- [ ] Loading states gérés
- [ ] Tests React écrits
- [ ] Responsive design respecté
- [ ] Accessibility (a11y) considérée

### Security Review
- [ ] Pas de hardcoded secrets
- [ ] Validation input/output
- [ ] Pas d'exposition de données sensibles
- [ ] CSRF protection en place
- [ ] SQL injection prevention
- [ ] XSS prevention

## ⚡ Performance Guidelines

### Backend
```python
# ✅ Optimisation des requêtes
# Utiliser select_related pour ForeignKey
books = Book.objects.select_related('author').all()

# Utiliser prefetch_related pour ManyToMany
authors = Author.objects.prefetch_related('books').all()

# ✅ Pagination automatique
class BookViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    page_size = 20
```

### Frontend
```typescript
// ✅ Lazy loading des composants
const BookDetail = lazy(() => import('./BookDetail'));

// ✅ Memoization pour éviter re-renders
const BookList = memo(({ books }: BookListProps) => {
  return (
    <div>
      {books.map(book => <BookCard key={book.id} book={book} />)}
    </div>
  );
});

// ✅ useMemo pour calculs coûteux
const filteredBooks = useMemo(() => {
  return books.filter(book => book.title.includes(searchTerm));
}, [books, searchTerm]);
```

## 📊 Monitoring et Logging

### Backend Logging
```python
import logging

logger = logging.getLogger('apps.custom.mon_app')

class MonAppViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        logger.info(f"User {request.user.id} creating new item")
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Item {response.data['id']} created successfully")
            return response
        except Exception as e:
            logger.error(f"Error creating item: {str(e)}")
            raise
```

### Frontend Error Handling
```typescript
const useMonApp = () => {
  const [error, setError] = useState<string | null>(null);
  
  const createItem = async (data: CreateItemData) => {
    try {
      setError(null);
      const result = await monAppAPI.createItem(data);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur inconnue';
      setError(message);
      console.error('Error creating item:', err);
      throw err;
    }
  };
  
  return { createItem, error };
};
```

## 📈 Métriques de Qualité

### Objectifs de Couverture
- **Backend Tests**: Minimum 80% de couverture
- **Frontend Tests**: Minimum 70% de couverture
- **API Response Time**: < 200ms pour 95% des requêtes
- **Frontend Bundle Size**: Éviter d'augmenter de >10%

### Commandes de Validation
```bash
# Backend
cd backend
python manage.py test apps.custom.mon_app --verbosity=2
coverage run --source='apps.custom.mon_app' manage.py test
coverage report

# Frontend
cd frontend
npm test -- --coverage --watchAll=false
npm run build  # Vérifier que build passe
npm run type-check  # Vérifier TypeScript
```

---

## 🎯 Résumé des Règles Essentielles

1. **🔒 ISOLATION** : Tout développement dans `custom/`
2. **🧪 TESTS** : Tests obligatoires avant merge
3. **🔐 SÉCURITÉ** : Authentification et validation partout
4. **📊 QUALITÉ** : Code review et standards respectés
5. **📝 DOCUMENTATION** : Documenter les APIs et composants
6. **⚡ PERFORMANCE** : Optimiser les requêtes et renders
7. **🚦 GIT** : Workflow propre avec commits descriptifs

Le respect de ces règles garantit la stabilité et la maintenabilité du projet Linguify.