# Guide de création d'un nouveau module

Ce guide explique comment créer un nouveau module (app Django) dans le backend de Linguify en se basant sur la structure de projet existante.

## Structure d'un module Django

Dans notre architecture, chaque module est une application Django située dans le dossier `backend/apps/`. Chaque module contient généralement les éléments suivants :

```
backend/apps/nom_module/
├── __init__.py
├── admin.py          # Configuration de l'interface d'administration
├── apps.py           # Configuration de l'application
├── models.py         # Modèles de données
├── serializers.py    # Sérialiseurs pour l'API REST
├── urls.py           # Définition des URL
├── views.py          # Vues et endpoints API
├── tests.py          # Tests unitaires
└── migrations/       # Migrations de base de données
    └── __init__.py
```

## Étapes pour créer un nouveau module

### 1. Création des fichiers de base

Créez un nouveau répertoire pour votre module dans `backend/apps/` et ajoutez les fichiers de base :

```bash
mkdir -p backend/apps/nouveau_module/migrations
touch backend/apps/nouveau_module/__init__.py
touch backend/apps/nouveau_module/migrations/__init__.py
touch backend/apps/nouveau_module/admin.py
touch backend/apps/nouveau_module/apps.py
touch backend/apps/nouveau_module/models.py
touch backend/apps/nouveau_module/serializers.py
touch backend/apps/nouveau_module/urls.py
touch backend/apps/nouveau_module/views.py
touch backend/apps/nouveau_module/tests.py
```

### 2. Configuration de l'application dans `apps.py`

```python
# backend/apps/nouveau_module/apps.py
from django.apps import AppConfig

class NouveauModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nouveau_module'
    verbose_name = "Nouveau Module"  # Nom affiché dans l'admin
```

### 3. Définition des modèles dans `models.py`

Créez vos modèles en vous inspirant de la structure des autres modules comme `notebook` ou `course` :

```python
# backend/apps/nouveau_module/models.py
from django.db import models
from django.conf import settings
from authentication.models import User

class ExempleModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exemples')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
```

### 4. Création des sérialiseurs dans `serializers.py`

```python
# backend/apps/nouveau_module/serializers.py
from rest_framework import serializers
from .models import ExempleModel

class ExempleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExempleModel
        fields = ['id', 'title', 'description', 'created_at']
        read_only_fields = ['created_at']
```

### 5. Création des vues dans `views.py`

En vous inspirant du fichier `notebook/views.py` :

```python
# backend/apps/nouveau_module/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import ExempleModel
from .serializers import ExempleModelSerializer

class ExempleModelViewSet(viewsets.ModelViewSet):
    serializer_class = ExempleModelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        return ExempleModel.objects.filter(user=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

### 6. Configuration des URLs dans `urls.py`

```python
# backend/apps/nouveau_module/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExempleModelViewSet

app_name = 'nouveau_module'

router = DefaultRouter()
router.register(r'exemples', ExempleModelViewSet, basename='exemple')

urlpatterns = [
    path('', include(router.urls)),
]
```

### 7. Configuration de l'admin dans `admin.py`

```python
# backend/apps/nouveau_module/admin.py
from django.contrib import admin
from .models import ExempleModel

@admin.register(ExempleModel)
class ExempleModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
```

### 8. Enregistrer l'application dans les paramètres Django

Ouvrez `backend/core/settings.py` et ajoutez votre application à la liste `INSTALLED_APPS` :

```python
INSTALLED_APPS = [
    # ...
    'apps.nouveau_module',
    # ...
]
```

### 9. Ajouter les URLs de votre module aux URLs du projet

Ouvrez `backend/core/urls.py` et ajoutez vos URLs :

```python
urlpatterns = [
    # ...
    path('api/v1/nouveau-module/', include('nouveau_module.urls', namespace='nouveau_module')),
    # ...
]
```

### 10. Migrations de base de données

Créez et appliquez les migrations pour votre nouveau module :

```bash
cd backend
python manage.py makemigrations nouveau_module
python manage.py migrate nouveau_module
```

## Intégration avec le frontend

Une fois votre module backend créé, vous devrez créer les fichiers correspondants pour l'intégration frontend :

1. Créez un dossier pour votre module dans `frontend/src/addons/`
2. Ajoutez les fichiers pour les composants, API clients et types
3. Intégrez vos nouveaux composants dans l'application frontend

## Bonnes pratiques

- Respectez les conventions de nommage du projet
- Utilisez les mixins et classes de base existants (comme `TargetLanguageMixin`)
- Implémentez des tests pour les modèles et les API
- Documentez vos endpoints API pour une utilisation plus facile

En suivant ces étapes, vous pouvez créer un nouveau module complet qui s'intègre parfaitement avec le reste de l'application Linguify.