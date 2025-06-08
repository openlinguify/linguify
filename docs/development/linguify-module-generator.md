# Linguify Module Generator

Guide complet pour créer de nouveaux modules dans l'écosystème Linguify.

## Vue d'ensemble

Le système de génération de modules Linguify permet de créer rapidement des modules complets avec :
- Structure backend Django
- Structure frontend React/Next.js  
- Configuration automatique
- Documentation incluse

## Installation

Le générateur est inclus dans le projet Linguify. Aucune installation supplémentaire n'est requise.

## Utilisation

### Commande de base

```bash
./linguify-bin scaffold <module_name> [output_directory] [options]
```

### Exemples d'utilisation

#### 1. Créer un module standalone (recommandé pour développement externe)

```bash
# Crée un module dans le dossier custom/
./linguify-bin scaffold bibliotheque custom

# Résultat : custom/bibliotheque/ avec structure complète
```

#### 2. Créer un module dans le projet principal

```bash
# Crée directement dans backend/apps/ et frontend/src/addons/
./linguify-bin scaffold quiz --icon=Brain
```

#### 3. Créer un module avec icône personnalisée

```bash
./linguify-bin scaffold flashcards --icon=Zap custom
```

### Options disponibles

| Option | Description | Exemple |
|--------|-------------|---------|
| `--icon=<IconName>` | Icône Lucide (PascalCase) | `--icon=BookOpen` |
| `output_directory` | Dossier de destination | `custom`, `modules`, etc. |

## Structure générée

Quand vous exécutez `./linguify-bin scaffold bibliotheque custom`, voici ce qui est créé :

```
custom/bibliotheque/
├── __manifest__.py              # ⭐ Configuration du module
├── README.md                    # Documentation
├── backend/
│   └── apps/bibliotheque/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── tests.py
│       ├── management/
│       │   └── commands/        # Commandes Django custom
│       ├── migrations/
│       │   └── __init__.py
│       ├── templates/bibliotheque/
│       ├── static/bibliotheque/
│       │   ├── css/
│       │   └── js/
│       └── tests/
└── frontend/
    └── src/addons/bibliotheque/
        ├── components/          # Composants React
        ├── api/                # Services API
        ├── hooks/              # Hooks React
        └── types/              # Types TypeScript
```

## Configuration du module (__manifest__.py)

Le fichier `__manifest__.py` est le cœur de la configuration du module :

```python
# -*- coding: utf-8 -*-
{
    'name': 'Bibliotheque',
    'version': '1.0.0',
    'category': 'Education/Language Learning',
    'summary': 'Bibliotheque module for Linguify',
    'description': '''
Bibliotheque Module for Linguify
================================

This module provides bibliotheque functionality for the Linguify language learning platform.

Features:
- CRUD operations for bibliotheque entities
- REST API endpoints
- Frontend React components
- Integration with Linguify core systems
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',      # Authentification Linguify
        'app_manager',        # Gestionnaire d'applications
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
```

### Propriétés importantes

| Propriété | Description | Exemple |
|-----------|-------------|---------|
| `name` | Nom affiché du module | `'Bibliotheque'` |
| `version` | Version du module | `'1.0.0'` |
| `depends` | Modules requis | `['authentication', 'app_manager']` |
| `installable` | Module installable | `True` |
| `application` | Module autonome | `True` |

## Intégration dans Linguify

### 1. Module standalone (développement externe)

```bash
# 1. Créer le module
./linguify-bin scaffold bibliotheque custom

# 2. Développer dans custom/bibliotheque/

# 3. Quand prêt, copier dans le projet principal
cp -r custom/bibliotheque/backend/apps/bibliotheque backend/apps/
cp -r custom/bibliotheque/frontend/src/addons/bibliotheque frontend/src/addons/
```

### 2. Module intégré (développement interne)

```bash
# 1. Créer directement dans le projet
./linguify-bin scaffold quiz --icon=Brain

# 2. Le module est automatiquement intégré
# - Ajouté à INSTALLED_APPS
# - URLs configurées
# - Menu dashboard mis à jour
```

## Développement du module

### Backend Django

#### 1. Modèles (models.py)

```python
from django.db import models
from authentication.models import User

class BibliothequeItem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Bibliotheque Item'
        verbose_name_plural = 'Bibliotheque Items'
```

#### 2. API (views.py)

```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import BibliothequeItem
from .serializers import BibliothequeItemSerializer

class BibliothequeItemViewSet(viewsets.ModelViewSet):
    serializer_class = BibliothequeItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BibliothequeItem.objects.filter(user=self.request.user)
```

### Frontend React

#### 1. API Service (api/bibliothequeAPI.ts)

```typescript
import apiClient from '@/core/api/apiClient';

const bibliothequeAPI = {
  getAll: async () => {
    const response = await apiClient.get('/api/v1/bibliotheque/items/');
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await apiClient.post('/api/v1/bibliotheque/items/', data);
    return response.data;
  }
};

export default bibliothequeAPI;
```

#### 2. Composant principal (components/BibliothequeView.tsx)

```tsx
'use client';

import React, { useState, useEffect } from 'react';
import { BookOpen } from 'lucide-react';
import bibliothequeAPI from '../api/bibliothequeAPI';

const BibliothequeView: React.FC = () => {
  const [items, setItems] = useState([]);
  
  useEffect(() => {
    const fetchItems = async () => {
      try {
        const data = await bibliothequeAPI.getAll();
        setItems(data);
      } catch (err) {
        console.error('Error fetching items:', err);
      }
    };
    
    fetchItems();
  }, []);
  
  return (
    <div className="container mx-auto p-4">
      <header className="mb-8 flex items-center gap-3">
        <BookOpen className="h-8 w-8 text-purple-600" />
        <h1 className="text-3xl font-bold">Bibliotheque</h1>
      </header>
      
      {/* Votre contenu ici */}
    </div>
  );
};

export default BibliothequeView;
```

## Migration et déploiement

### 1. Migrations Django

```bash
cd backend
python manage.py makemigrations bibliotheque
python manage.py migrate
```

### 2. Tests

```bash
# Tests backend
python manage.py test apps.bibliotheque

# Tests frontend
cd frontend
npm test -- bibliotheque
```

### 3. Intégration au menu

Le module sera automatiquement ajouté au dashboard si créé via le script Python complet.

## Icônes disponibles

Le système utilise les icônes [Lucide](https://lucide.dev/icons/). Exemples populaires :

| Module | Icône recommandée |
|--------|-------------------|
| Quiz | `Brain`, `HelpCircle` |
| Flashcards | `Zap`, `RotateCcw` |
| Bibliotheque | `BookOpen`, `Library` |
| Chat | `MessageCircle`, `Bot` |
| Notebook | `NotebookPen`, `FileText` |
| Settings | `Settings`, `Cog` |

## Dépannage

### Problème : Script non exécutable

```bash
# Solution : Fixer les permissions et fins de ligne
chmod +x linguify-bin
sed -i 's/\r$//' linguify-bin
```

### Problème : Module non reconnu

1. Vérifiez que `__manifest__.py` est correct
2. Ajoutez le module à `INSTALLED_APPS` manuellement si nécessaire
3. Relancez les migrations

### Problème : Erreur d'import frontend

1. Vérifiez la structure des dossiers
2. Assurez-vous que `index.ts` exporte les composants
3. Redémarrez le serveur de développement

## Scripts utiles

### Démarrer l'environnement de développement

```bash
# Lance Django + Next.js
./run.sh
```

### Créer plusieurs modules rapidement

```bash
./linguify-bin scaffold quiz custom
./linguify-bin scaffold flashcards custom  
./linguify-bin scaffold notebook custom
```

## Bonnes pratiques

### 1. Nommage des modules
- Utilisez des noms descriptifs en minuscules
- Évitez les espaces et caractères spéciaux
- Exemples : `quiz`, `flashcards`, `voice_recording`

### 2. Structure du code
- Gardez la logique métier dans les modèles Django
- Utilisez les serializers pour la validation
- Créez des composants React réutilisables

### 3. Documentation
- Mettez à jour le `__manifest__.py`
- Documentez les APIs dans les docstrings
- Ajoutez des exemples d'utilisation

### 4. Tests
- Écrivez des tests pour chaque fonctionnalité
- Testez les APIs et les composants
- Utilisez les factories pour les données de test

## Ressources

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation React](https://react.dev/)
- [Icônes Lucide](https://lucide.dev/icons/)
- [Documentation Linguify](/docs/)

## Support

Pour toute question ou problème :
1. Consultez cette documentation
2. Vérifiez les logs d'erreur
3. Consultez les exemples de modules existants
4. Ouvrez une issue GitHub si nécessaire

---

**Créé avec ❤️ pour l'écosystème Linguify**