# Template de Structure pour Nouvelles Apps Linguify

## 📋 Structure Backend Obligatoire

### Arborescence Minimale
```
backend/apps/custom/MON_APP/
├── __init__.py                 # ✅ Requis
├── __manifest__.py            # ✅ Configuration module
├── apps.py                    # ✅ Configuration Django
├── models.py                  # ✅ Modèles de données
├── serializers.py             # ✅ Serializers API
├── views.py                   # ✅ Vues API
├── urls.py                    # ✅ Routes URL
├── admin.py                   # ✅ Interface admin
├── tests.py                   # ✅ Tests unitaires
├── migrations/                # ✅ Auto-généré
│   └── __init__.py
├── management/                # 🔧 Optionnel
│   └── commands/
└── templates/                 # 🔧 Si nécessaire
    └── MON_APP/
```

## 📄 Templates de Fichiers

### 1. __manifest__.py
```python
{
    'name': 'Mon App Name',
    'version': '1.0.0',
    'description': 'Description de mon application',
    'author': 'Nom du développeur',
    'depends': ['authentication'],  # Dépendances vers autres apps
    'category': 'Custom',
    'installable': True,
    'auto_install': False,
    'frontend_enabled': True,
    'api_endpoints': [
        '/api/custom/mon-app/',
    ],
    'permissions': [
        'mon_app.add_monmodel',
        'mon_app.change_monmodel',
        'mon_app.delete_monmodel',
        'mon_app.view_monmodel',
    ]
}
```

### 2. apps.py
```python
from django.apps import AppConfig

class MonAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.custom.mon_app'
    verbose_name = 'Mon App'
    
    def ready(self):
        # Import signals ici si nécessaire
        pass
```

### 3. models.py
```python
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator

User = get_user_model()

class MonModel(models.Model):
    """
    Modèle principal de mon app
    """
    # ✅ Toujours inclure un lien user si pertinent
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='mon_app_items'
    )
    
    # ✅ Champs de base recommandés
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2)]
    )
    description = models.TextField(blank=True)
    
    # ✅ Timestamps automatiques
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ✅ Status/état si nécessaire
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'custom_mon_app_monmodel'  # ✅ Préfixe custom_
        ordering = ['-created_at']
        verbose_name = 'Mon Model'
        verbose_name_plural = 'Mes Models'
        
        # ✅ Index pour les requêtes fréquentes
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
```

### 4. serializers.py
```python
from rest_framework import serializers
from .models import MonModel

class MonModelSerializer(serializers.ModelSerializer):
    """
    Serializer pour MonModel
    """
    user_username = serializers.CharField(
        source='user.username', 
        read_only=True
    )
    
    class Meta:
        model = MonModel
        fields = [
            'id', 'title', 'description', 
            'created_at', 'updated_at', 'is_active',
            'user_username'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_username']
    
    def create(self, validated_data):
        # ✅ Assigner automatiquement l'utilisateur
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class MonModelListSerializer(serializers.ModelSerializer):
    """
    Serializer léger pour les listes
    """
    class Meta:
        model = MonModel
        fields = ['id', 'title', 'is_active', 'created_at']
```

### 5. views.py
```python
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import MonModel
from .serializers import MonModelSerializer, MonModelListSerializer

class MonModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour MonModel avec CRUD complet
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    
    # ✅ Filtres recommandés
    filterset_fields = ['is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # ✅ Filtrer par utilisateur automatiquement
        return MonModel.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        # ✅ Serializer différent pour list vs detail
        if self.action == 'list':
            return MonModelListSerializer
        return MonModelSerializer
    
    @action(detail=False, methods=['get'])
    def active_only(self, request):
        """
        Endpoint custom pour items actifs seulement
        """
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Toggle le statut actif/inactif
        """
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save()
        return Response({'is_active': obj.is_active})
```

### 6. urls.py
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'mon_app'

# ✅ Router pour API REST
router = DefaultRouter()
router.register(r'items', views.MonModelViewSet, basename='monmodel')

urlpatterns = [
    # ✅ Toutes les APIs sous /api/custom/mon-app/
    path('api/custom/mon-app/', include(router.urls)),
]
```

### 7. admin.py
```python
from django.contrib import admin
from .models import MonModel

@admin.register(MonModel)
class MonModelAdmin(admin.ModelAdmin):
    """
    Interface admin pour MonModel
    """
    list_display = [
        'title', 'user', 'is_active', 
        'created_at', 'updated_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    # ✅ Filtrer par utilisateur
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs
    
    # ✅ Auto-assigner l'utilisateur
    def save_model(self, request, obj, form, change):
        if not change:  # Nouvelle création
            obj.user = request.user
        super().save_model(request, obj, form, change)
```

### 8. tests.py
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import MonModel

User = get_user_model()

class MonModelTests(TestCase):
    """
    Tests unitaires pour MonModel
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_create_mon_model(self):
        """Test création d'un MonModel"""
        obj = MonModel.objects.create(
            user=self.user,
            title='Test Title',
            description='Test Description'
        )
        self.assertEqual(obj.title, 'Test Title')
        self.assertEqual(obj.user, self.user)
        self.assertTrue(obj.is_active)
    
    def test_str_representation(self):
        """Test représentation string"""
        obj = MonModel.objects.create(
            user=self.user,
            title='Test Title'
        )
        expected = f"Test Title ({self.user.username})"
        self.assertEqual(str(obj), expected)

class MonModelAPITests(APITestCase):
    """
    Tests API pour MonModel
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_item_via_api(self):
        """Test création via API"""
        data = {
            'title': 'New Item',
            'description': 'New Description'
        }
        response = self.client.post('/api/custom/mon-app/items/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Item')
    
    def test_list_items_filtered_by_user(self):
        """Test que les items sont filtrés par utilisateur"""
        # Créer item pour user actuel
        MonModel.objects.create(
            user=self.user,
            title='My Item'
        )
        
        # Créer autre user et son item
        other_user = User.objects.create_user(
            username='other', password='pass'
        )
        MonModel.objects.create(
            user=other_user,
            title='Other Item'
        )
        
        response = self.client.get('/api/custom/mon-app/items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'My Item')
```

## 📱 Structure Frontend Recommandée

```
frontend/src/addons/custom/MON_APP/
├── components/
│   ├── MonAppMain.tsx         # ✅ Composant principal
│   ├── MonAppList.tsx         # ✅ Liste des items
│   ├── MonAppForm.tsx         # ✅ Formulaire create/edit
│   ├── MonAppDetail.tsx       # ✅ Détail d'un item
│   └── shared/                # ✅ Composants partagés
│       ├── MonAppCard.tsx
│       └── MonAppModal.tsx
├── api/
│   └── monAppAPI.ts           # ✅ Appels API
├── types/
│   └── index.ts               # ✅ Types TypeScript
├── hooks/
│   ├── useMonApp.ts           # ✅ Hook principal
│   └── useMonAppForm.ts       # ✅ Hook formulaire
└── styles/                    # 🔧 Si CSS spécifique
    └── MonApp.module.css
```

## 🔧 Intégration dans le Projet

### Ajouter dans settings.py
```python
# backend/core/settings.py
CUSTOM_APPS = [
    'apps.custom.bibliotheque',
    'apps.custom.mon_app',  # ✅ Ajouter ici
]
```

### Ajouter dans urls.py principal
```python
# backend/core/urls.py
from django.urls import path, include

urlpatterns = [
    # ... autres patterns
    path('', include('apps.custom.mon_app.urls')),  # ✅ Ajouter
]
```

### Commandes de mise en place
```bash
# 1. Créer les migrations
cd backend
python manage.py makemigrations mon_app

# 2. Appliquer les migrations
python manage.py migrate

# 3. Créer un superuser si nécessaire
python manage.py createsuperuser

# 4. Tester l'API
python manage.py runserver
# Aller sur http://localhost:8000/api/custom/mon-app/items/
```

## ✅ Checklist de Validation

Avant de soumettre votre nouvelle app :

- [ ] Structure respectée dans `custom/`
- [ ] `__manifest__.py` rempli correctement
- [ ] Modèles avec préfixe `custom_` dans db_table
- [ ] Tests unitaires écrits et passants
- [ ] API endpoints testés
- [ ] Interface admin fonctionnelle
- [ ] Frontend intégré (si applicable)
- [ ] Documentation ajoutée
- [ ] Migrations créées et appliquées

## 📚 Exemples Complets

Consultez le module `bibliotheque` pour un exemple complet :
- `backend/apps/custom/bibliotheque/`
- `frontend/src/addons/custom/bibliotheque/`

Cet exemple montre toutes les bonnes pratiques en action.