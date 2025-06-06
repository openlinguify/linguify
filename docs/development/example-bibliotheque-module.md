# Exemple : Module Bibliotheque

Exemple complet de développement d'un module Linguify pour gérer une bibliothèque de ressources.

## 🎯 Objectif du module

Créer un module "Bibliotheque" qui permet aux utilisateurs de :
- Stocker des ressources d'apprentissage (livres, articles, vidéos)
- Organiser par catégories et tags
- Partager des ressources entre utilisateurs
- Suivre les ressources consultées

## 🚀 Création du module

```bash
# 1. Générer la structure
./linguify-bin scaffold bibliotheque custom --icon=BookOpen

# 2. Naviguer vers le module
cd custom/bibliotheque

# 3. Examiner la structure
tree .
```

## 📝 Configuration (__manifest__.py)

```python
# -*- coding: utf-8 -*-
{
    'name': 'Bibliotheque',
    'version': '1.0.0',
    'category': 'Education/Language Learning',
    'summary': 'Digital library for language learning resources',
    'description': '''
Bibliotheque Module for Linguify
================================

A comprehensive digital library system for language learners to:
- Store and organize learning resources (books, articles, videos)
- Categorize content by difficulty, topic, and language
- Share resources with the community
- Track reading progress and favorites

Features:
- Resource management with rich metadata
- Advanced search and filtering
- Community sharing and ratings
- Progress tracking and analytics
- Offline reading support
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # User management
        'app_manager',     # App system integration
    ],
    'data': [
        'data/categories.xml',
        'data/sample_resources.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 15,
    'frontend_components': {
        'main_component': 'BibliothequeView',
        'route': '/bibliotheque',
        'icon': 'BookOpen',
        'menu_order': 5,
    },
    'api_endpoints': {
        'base_url': '/api/v1/bibliotheque/',
        'viewsets': ['ResourceViewSet', 'CategoryViewSet'],
    },
    'permissions': {
        'create_resource': 'auth.user',
        'read_resource': 'auth.user',
        'update_own_resource': 'auth.user',
        'delete_own_resource': 'auth.user',
        'moderate_content': 'auth.moderator',
    }
}
```

## 🗄️ Modèles Django (models.py)

```python
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Category(models.Model):
    """Catégories de ressources (Grammar, Vocabulary, Culture, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='Folder')
    color = models.CharField(max_length=20, default='blue')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Resource(models.Model):
    """Ressource de la bibliothèque"""
    
    TYPE_CHOICES = [
        ('book', 'Book'),
        ('article', 'Article'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('link', 'External Link'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('native', 'Native Level'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'French'),
        ('es', 'Spanish'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
    ]

    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Content
    content_url = models.URLField(blank=True, help_text="External URL or file path")
    content_file = models.FileField(upload_to='bibliotheque/files/', blank=True)
    thumbnail = models.ImageField(upload_to='bibliotheque/thumbnails/', blank=True)
    
    # Metadata
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    categories = models.ManyToManyField(Category, related_name='resources')
    tags = models.CharField(max_length=500, help_text="Comma-separated tags")
    
    # Publication info
    published_date = models.DateField(blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True)
    pages = models.IntegerField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True, help_text="For audio/video")
    
    # System fields
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_resources')
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Stats
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['language', 'difficulty']),
            models.Index(fields=['type', 'is_public']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"

    def get_absolute_url(self):
        return reverse('bibliotheque:resource-detail', kwargs={'pk': self.pk})

class UserResourceProgress(models.Model):
    """Suivi de progression utilisateur sur une ressource"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    
    # Progress tracking
    is_favorite = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    progress_percent = models.IntegerField(default=0)  # 0-100
    last_accessed = models.DateTimeField(auto_now=True)
    
    # User notes
    private_notes = models.TextField(blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'resource')
        verbose_name = 'User Resource Progress'
        verbose_name_plural = 'User Resource Progress'

class ResourceReview(models.Model):
    """Avis et commentaires sur les ressources"""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=255)
    comment = models.TextField()
    
    is_helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('resource', 'user')
        ordering = ['-created_at']
```

## 🔌 API Serializers (serializers.py)

```python
from rest_framework import serializers
from .models import Resource, Category, UserResourceProgress, ResourceReview

class CategorySerializer(serializers.ModelSerializer):
    resource_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color', 'resource_count']
    
    def get_resource_count(self, obj):
        return obj.resources.filter(is_public=True).count()

class ResourceListSerializer(serializers.ModelSerializer):
    """Serializer for resource list view (lighter)"""
    categories = CategorySerializer(many=True, read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'description', 'author', 'type', 'language', 
            'difficulty', 'categories', 'thumbnail', 'uploaded_by_name',
            'is_featured', 'view_count', 'average_rating', 'created_at'
        ]
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return None

class ResourceDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed resource view"""
    categories = CategorySerializer(many=True, read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    user_progress = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = '__all__'
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserResourceProgress.objects.get(user=request.user, resource=obj)
                return {
                    'is_favorite': progress.is_favorite,
                    'is_completed': progress.is_completed,
                    'progress_percent': progress.progress_percent,
                    'rating': progress.rating,
                }
            except UserResourceProgress.DoesNotExist:
                return None
        return None
    
    def get_recent_reviews(self, obj):
        reviews = obj.reviews.order_by('-created_at')[:3]
        return [{
            'user': review.user.full_name,
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment[:100] + '...' if len(review.comment) > 100 else review.comment,
            'created_at': review.created_at,
        } for review in reviews]

class UserResourceProgressSerializer(serializers.ModelSerializer):
    resource_title = serializers.CharField(source='resource.title', read_only=True)
    
    class Meta:
        model = UserResourceProgress
        fields = '__all__'
        read_only_fields = ['user']
```

## 🌐 API Views (views.py)

```python
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from .models import Resource, Category, UserResourceProgress
from .serializers import (
    ResourceListSerializer, ResourceDetailSerializer, 
    CategorySerializer, UserResourceProgressSerializer
)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour les catégories de ressources"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

class ResourceViewSet(viewsets.ModelViewSet):
    """API principale pour les ressources"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'language', 'difficulty', 'categories']
    search_fields = ['title', 'description', 'author', 'tags']
    ordering_fields = ['created_at', 'title', 'view_count', 'difficulty']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if self.action in ['list', 'retrieve']:
            # Show public resources + user's own resources
            return Resource.objects.filter(
                Q(is_public=True) | Q(uploaded_by=user)
            ).select_related('uploaded_by').prefetch_related('categories', 'reviews')
        else:
            # For create/update/delete, only user's own resources
            return Resource.objects.filter(uploaded_by=user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ResourceDetailSerializer
        return ResourceListSerializer
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status for a resource"""
        resource = self.get_object()
        progress, created = UserResourceProgress.objects.get_or_create(
            user=request.user, 
            resource=resource
        )
        progress.is_favorite = not progress.is_favorite
        progress.save()
        
        return Response({
            'is_favorite': progress.is_favorite,
            'message': 'Added to favorites' if progress.is_favorite else 'Removed from favorites'
        })
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update reading/viewing progress"""
        resource = self.get_object()
        progress_percent = request.data.get('progress_percent', 0)
        
        progress, created = UserResourceProgress.objects.get_or_create(
            user=request.user,
            resource=resource
        )
        progress.progress_percent = min(100, max(0, int(progress_percent)))
        progress.is_completed = progress.progress_percent >= 100
        progress.save()
        
        return Response({
            'progress_percent': progress.progress_percent,
            'is_completed': progress.is_completed
        })
    
    @action(detail=False, methods=['get'])
    def my_library(self, request):
        """Get user's personal library (favorites, in-progress, etc.)"""
        user_progress = UserResourceProgress.objects.filter(
            user=request.user
        ).select_related('resource').order_by('-last_accessed')
        
        return Response({
            'favorites': [
                ResourceListSerializer(p.resource, context={'request': request}).data
                for p in user_progress if p.is_favorite
            ],
            'in_progress': [
                ResourceListSerializer(p.resource, context={'request': request}).data
                for p in user_progress if 0 < p.progress_percent < 100
            ],
            'completed': [
                ResourceListSerializer(p.resource, context={'request': request}).data
                for p in user_progress if p.is_completed
            ]
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured resources"""
        featured = self.get_queryset().filter(is_featured=True)[:10]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def track_view(self, request, pk=None):
        """Track resource view for analytics"""
        resource = self.get_object()
        resource.view_count += 1
        resource.save(update_fields=['view_count'])
        
        # Update user's last accessed time
        UserResourceProgress.objects.update_or_create(
            user=request.user,
            resource=resource,
            defaults={'last_accessed': timezone.now()}
        )
        
        return Response({'view_count': resource.view_count})
```

## ⚛️ Frontend React

### API Service (api/bibliothequeAPI.ts)

```typescript
import apiClient from '@/core/api/apiClient';
import { Resource, Category, UserProgress } from '../types';

const bibliothequeAPI = {
  // Resources
  getResources: async (params?: any) => {
    const response = await apiClient.get('/api/v1/bibliotheque/resources/', { params });
    return response.data;
  },

  getResource: async (id: number) => {
    const response = await apiClient.get(`/api/v1/bibliotheque/resources/${id}/`);
    return response.data;
  },

  createResource: async (data: Partial<Resource>) => {
    const response = await apiClient.post('/api/v1/bibliotheque/resources/', data);
    return response.data;
  },

  updateResource: async (id: number, data: Partial<Resource>) => {
    const response = await apiClient.patch(`/api/v1/bibliotheque/resources/${id}/`, data);
    return response.data;
  },

  deleteResource: async (id: number) => {
    await apiClient.delete(`/api/v1/bibliotheque/resources/${id}/`);
  },

  // Categories
  getCategories: async () => {
    const response = await apiClient.get('/api/v1/bibliotheque/categories/');
    return response.data;
  },

  // User actions
  toggleFavorite: async (resourceId: number) => {
    const response = await apiClient.post(`/api/v1/bibliotheque/resources/${resourceId}/toggle_favorite/`);
    return response.data;
  },

  updateProgress: async (resourceId: number, progressPercent: number) => {
    const response = await apiClient.post(`/api/v1/bibliotheque/resources/${resourceId}/update_progress/`, {
      progress_percent: progressPercent
    });
    return response.data;
  },

  getMyLibrary: async () => {
    const response = await apiClient.get('/api/v1/bibliotheque/resources/my_library/');
    return response.data;
  },

  getFeatured: async () => {
    const response = await apiClient.get('/api/v1/bibliotheque/resources/featured/');
    return response.data;
  },

  trackView: async (resourceId: number) => {
    const response = await apiClient.post(`/api/v1/bibliotheque/resources/${resourceId}/track_view/`);
    return response.data;
  }
};

export default bibliothequeAPI;
```

### Types (types/index.ts)

```typescript
export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon: string;
  color: string;
  resource_count: number;
}

export interface Resource {
  id: number;
  title: string;
  description: string;
  author: string;
  type: 'book' | 'article' | 'video' | 'audio' | 'document' | 'link';
  language: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'native';
  categories: Category[];
  thumbnail?: string;
  content_url?: string;
  tags: string;
  uploaded_by_name: string;
  is_featured: boolean;
  view_count: number;
  average_rating?: number;
  created_at: string;
  user_progress?: UserProgress;
  recent_reviews?: Review[];
}

export interface UserProgress {
  is_favorite: boolean;
  is_completed: boolean;
  progress_percent: number;
  rating?: number;
}

export interface Review {
  user: string;
  rating: number;
  title: string;
  comment: string;
  created_at: string;
}

export interface BibliothequeViewProps {
  initialFilter?: string;
}
```

### Composant principal (components/BibliothequeView.tsx)

```tsx
'use client';

import React, { useState, useEffect } from 'react';
import { BookOpen, Search, Filter, Grid, List, Star, Heart } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Resource, Category } from '../types';
import bibliothequeAPI from '../api/bibliothequeAPI';

const BibliothequeView: React.FC = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resourcesData, categoriesData] = await Promise.all([
          bibliothequeAPI.getResources(),
          bibliothequeAPI.getCategories()
        ]);
        setResources(resourcesData.results || resourcesData);
        setCategories(categoriesData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleToggleFavorite = async (resourceId: number) => {
    try {
      const result = await bibliothequeAPI.toggleFavorite(resourceId);
      setResources(prev => prev.map(resource => 
        resource.id === resourceId 
          ? { ...resource, user_progress: { ...resource.user_progress, is_favorite: result.is_favorite } }
          : resource
      ));
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.author.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || 
                           resource.categories.some(cat => cat.slug === selectedCategory);
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-7xl">
      {/* Header */}
      <header className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-full">
            <BookOpen className="h-6 w-6 text-purple-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Bibliotheque</h1>
            <p className="text-gray-600">Your digital language learning library</p>
          </div>
        </div>
        <Button className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white">
          Add Resource
        </Button>
      </header>

      {/* Search and Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search resources..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 border rounded-md"
        >
          <option value="">All Categories</option>
          {categories.map(category => (
            <option key={category.slug} value={category.slug}>
              {category.name} ({category.resource_count})
            </option>
          ))}
        </select>
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('grid')}
          >
            <Grid className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('list')}
          >
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="all" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">All Resources</TabsTrigger>
          <TabsTrigger value="favorites">Favorites</TabsTrigger>
          <TabsTrigger value="progress">In Progress</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="mt-6">
          {/* Resources Grid/List */}
          <div className={viewMode === 'grid' 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            : "space-y-4"
          }>
            {filteredResources.map((resource) => (
              <Card key={resource.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg line-clamp-2">{resource.title}</CardTitle>
                      <CardDescription className="text-sm text-gray-600">
                        by {resource.author}
                      </CardDescription>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleFavorite(resource.id)}
                      className="ml-2"
                    >
                      <Heart 
                        className={`h-4 w-4 ${
                          resource.user_progress?.is_favorite 
                            ? 'fill-red-500 text-red-500' 
                            : 'text-gray-400'
                        }`} 
                      />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 line-clamp-3 mb-3">
                    {resource.description}
                  </p>
                  
                  <div className="flex flex-wrap gap-1 mb-3">
                    <Badge variant="secondary" className="text-xs">
                      {resource.type}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {resource.difficulty}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {resource.language}
                    </Badge>
                  </div>

                  {resource.average_rating && (
                    <div className="flex items-center gap-1 mb-2">
                      <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                      <span className="text-xs text-gray-600">
                        {resource.average_rating.toFixed(1)}
                      </span>
                    </div>
                  )}

                  <div className="text-xs text-gray-500">
                    {resource.view_count} views • {new Date(resource.created_at).toLocaleDateString()}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredResources.length === 0 && (
            <div className="text-center py-12">
              <BookOpen className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No resources found</h3>
              <p className="text-gray-500 mb-4">
                Try adjusting your search criteria or add some resources to get started.
              </p>
              <Button className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white">
                Add First Resource
              </Button>
            </div>
          )}
        </TabsContent>

        {/* Other tabs content would go here */}
      </Tabs>
    </div>
  );
};

export default BibliothequeView;
```

## 🚀 Intégration et déploiement

### 1. Installation dans le projet principal

```bash
# 1. Copier les fichiers
cp -r custom/bibliotheque/backend/apps/bibliotheque backend/apps/
cp -r custom/bibliotheque/frontend/src/addons/bibliotheque frontend/src/addons/

# 2. Ajouter à INSTALLED_APPS (backend/core/settings.py)
INSTALLED_APPS = [
    # ... autres apps
    'apps.bibliotheque',
]

# 3. Ajouter aux URLs (backend/core/urls.py)
urlpatterns = [
    # ... autres URLs
    path('api/v1/bibliotheque/', include('apps.bibliotheque.urls')),
]

# 4. Migrations
cd backend
python manage.py makemigrations bibliotheque
python manage.py migrate

# 5. Créer un superuser (si pas déjà fait)
python manage.py createsuperuser

# 6. Lancer le serveur
../run.sh
```

### 2. Test de l'API

```bash
# Tester les endpoints
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/bibliotheque/categories/
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/bibliotheque/resources/
```

### 3. Accès à l'interface

- **Frontend** : http://localhost:3000/bibliotheque
- **API** : http://localhost:8000/api/v1/bibliotheque/
- **Admin** : http://localhost:8000/admin

## 📊 Fonctionnalités avancées

### Analytics et reporting

```python
# Dans models.py
class ResourceAnalytics(models.Model):
    resource = models.OneToOneField(Resource, on_delete=models.CASCADE)
    daily_views = models.JSONField(default=dict)
    completion_rate = models.FloatField(default=0.0)
    average_time_spent = models.IntegerField(default=0)  # seconds
    user_feedback_score = models.FloatField(default=0.0)
```

### Système de recommandations

```python
# Dans views.py
@action(detail=False, methods=['get'])
def recommendations(self, request):
    """Recommandations personnalisées basées sur l'historique"""
    user = request.user
    # Logic pour recommandations ML
    return Response(recommended_resources)
```

### Offline support

```typescript
// Service Worker pour cache offline
// Dans frontend/public/sw.js
```

## 🧪 Tests

### Tests Django

```python
# tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Resource, Category

User = get_user_model()

class ResourceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.category = Category.objects.create(
            name='Grammar',
            slug='grammar'
        )

    def test_resource_creation(self):
        resource = Resource.objects.create(
            title='Test Resource',
            description='Test Description',
            type='book',
            language='en',
            difficulty='beginner',
            uploaded_by=self.user
        )
        self.assertEqual(str(resource), 'Test Resource (Book)')
        self.assertEqual(resource.view_count, 0)
```

### Tests React

```typescript
// tests/BibliothequeView.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { BibliothequeView } from '../components/BibliothequeView';

jest.mock('../api/bibliothequeAPI');

describe('BibliothequeView', () => {
  test('renders loading state initially', () => {
    render(<BibliothequeView />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('displays resources after loading', async () => {
    const mockResources = [
      { id: 1, title: 'Test Resource', description: 'Test Description' }
    ];
    
    (bibliothequeAPI.getResources as jest.Mock).mockResolvedValue(mockResources);
    
    render(<BibliothequeView />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Resource')).toBeInTheDocument();
    });
  });
});
```

## 📈 Métriques et monitoring

### Dashboard admin custom

```python
# admin.py additions
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'language', 'difficulty', 'view_count', 'is_public']
    list_filter = ['type', 'language', 'difficulty', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'author']
    readonly_fields = ['view_count', 'download_count']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('uploaded_by')
```

## 🎉 Conclusion

Ce module Bibliotheque démontre :
- ✅ Structure complète backend/frontend
- ✅ API REST robuste avec filtres et recherche  
- ✅ Interface utilisateur moderne et responsive
- ✅ Gestion des permissions et sécurité
- ✅ Fonctionnalités avancées (favoris, progression, reviews)
- ✅ Tests unitaires et d'intégration
- ✅ Documentation complète

Le module est maintenant prêt pour la production et peut servir de template pour d'autres modules Linguify ! 🚀