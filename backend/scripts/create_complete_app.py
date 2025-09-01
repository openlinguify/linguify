#!/usr/bin/env python3
"""
Script pour créer une app Django complète avec la structure de dossiers correcte
Usage: python scripts/create_complete_app.py <app_name> [display_name] [category]
"""
import os
import sys
import django
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour pouvoir importer 'core'
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


def create_complete_app(app_name, display_name=None, category='productivity'):
    """Crée une app Django complète avec la structure de dossiers correcte"""
    
    if not app_name:
        print("❌ Usage: python scripts/create_complete_app_fixed.py <app_name> [display_name] [category]")
        return False
    
    # Validation du nom d'app
    if not app_name.isidentifier() or app_name.startswith('_'):
        print(f"❌ '{app_name}' n'est pas un nom d'app Python valide")
        return False
    
    # Configuration
    display_name = display_name or app_name.replace('_', ' ').title()
    base_dir = Path(__file__).parent.parent
    app_dir = base_dir / 'apps' / app_name
    
    print(f"🚀 CRÉATION DE L'APP COMPLÈTE: {app_name}")
    print("=" * 50)
    print(f"📱 Display name: {display_name}")
    print(f"📂 Category: {category}")
    print(f"📍 Directory: {app_dir}")
    print(f"👤 Author: LGPL")
    print()
    
    # Vérifier si l'app existe déjà
    if app_dir.exists():
        print(f"❌ L'app '{app_name}' existe déjà dans apps/{app_name}")
        return False
    
    # Créer le dossier principal
    app_dir.mkdir(parents=True)
    print(f"✅ Dossier créé: apps/{app_name}/")
    
    # 1. Créer apps.py
    apps_content = f'''from django.apps import AppConfig


class {app_name.replace('_', '').title()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    verbose_name = '{display_name}'
'''
    
    (app_dir / 'apps.py').write_text(apps_content)
    print(f"✅ apps.py créé")
    
    # 2. Créer __init__.py
    (app_dir / '__init__.py').write_text('')
    
    # 3. Créer le dossier models
    models_dir = app_dir / 'models'
    models_dir.mkdir()
    
    # Créer models/__init__.py
    (models_dir / '__init__.py').write_text('from .models import *\n')
    
    # Créer models/models.py
    models_content = f'''from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Exemple de modèle pour {display_name}
class {app_name.replace('_', '').title()}Item(models.Model):
    """Modèle de base pour {display_name}"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='{app_name}_items')
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "{display_name} Item"
        verbose_name_plural = "{display_name} Items"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
'''
    
    (models_dir / 'models.py').write_text(models_content)
    print(f"✅ models/ folder created with models.py")
    
    # 4. Créer le dossier views
    views_dir = app_dir / 'views'
    views_dir.mkdir()
    
    # Créer views/__init__.py
    (views_dir / '__init__.py').write_text('from .views import *\n')
    
    # Créer views/views.py
    views_content = f'''from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from ..models import {app_name.replace('_', '').title()}Item
from ..forms import {app_name.replace('_', '').title()}ItemForm


@login_required
def {app_name}_home(request):
    """Page d'accueil de {display_name}"""
    items = {app_name.replace('_', '').title()}Item.objects.filter(
        user=request.user,
        is_active=True
    )
    
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)
    
    context = {{
        'items': page_items,
        'total_items': items.count(),
        'app_name': '{display_name}',
    }}
    return render(request, '{app_name}/home.html', context)


@login_required
def create_item(request):
    """Créer un nouvel item"""
    if request.method == 'POST':
        form = {app_name.replace('_', '').title()}ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f'{{item.title}} créé avec succès!')
            return redirect('{app_name}_home')
    else:
        form = {app_name.replace('_', '').title()}ItemForm()
    
    return render(request, '{app_name}/create_item.html', {{'form': form}})


@login_required
def edit_item(request, item_id):
    """Modifier un item"""
    item = get_object_or_404({app_name.replace('_', '').title()}Item, id=item_id, user=request.user)
    
    if request.method == 'POST':
        form = {app_name.replace('_', '').title()}ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'{{item.title}} modifié avec succès!')
            return redirect('{app_name}_home')
    else:
        form = {app_name.replace('_', '').title()}ItemForm(instance=item)
    
    return render(request, '{app_name}/edit_item.html', {{'form': form, 'item': item}})


@login_required
def delete_item(request, item_id):
    """Supprimer un item"""
    item = get_object_or_404({app_name.replace('_', '').title()}Item, id=item_id, user=request.user)
    
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f'{{title}} supprimé avec succès!')
        return redirect('{app_name}_home')
    
    return render(request, '{app_name}/confirm_delete.html', {{'item': item}})


# API Views
@login_required
def api_items(request):
    """API pour récupérer les items"""
    items = {app_name.replace('_', '').title()}Item.objects.filter(
        user=request.user,
        is_active=True
    ).values('id', 'title', 'description', 'created_at')
    
    return JsonResponse({{
        'items': list(items),
        'count': len(items)
    }})
'''
    
    (views_dir / 'views.py').write_text(views_content)
    print(f"✅ views/ folder created with views.py")
    
    # 5. Créer le dossier forms
    forms_dir = app_dir / 'forms'
    forms_dir.mkdir()
    
    # Créer forms/__init__.py
    (forms_dir / '__init__.py').write_text('from .forms import *\n')
    
    # Créer forms/forms.py
    forms_content = f'''from django import forms
from ..models import {app_name.replace('_', '').title()}Item


class {app_name.replace('_', '').title()}ItemForm(forms.ModelForm):
    """Formulaire pour créer/modifier un item {display_name}"""
    
    class Meta:
        model = {app_name.replace('_', '').title()}Item
        fields = ['title', 'description', 'is_active']
        widgets = {{
            'title': forms.TextInput(attrs={{
                'class': 'form-control',
                'placeholder': 'Titre de l\\'item'
            }}),
            'description': forms.Textarea(attrs={{
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description de l\\'item'
            }}),
            'is_active': forms.CheckboxInput(attrs={{
                'class': 'form-check-input'
            }})
        }}
        labels = {{
            'title': 'Titre',
            'description': 'Description',
            'is_active': 'Actif'
        }}
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or len(title.strip()) < 3:
            raise forms.ValidationError('Le titre doit contenir au moins 3 caractères.')
        return title.strip()
'''
    
    (forms_dir / 'forms.py').write_text(forms_content)
    print(f"✅ forms/ folder created with forms.py")
    
    # 6. Créer le dossier admin
    admin_dir = app_dir / 'admin'
    admin_dir.mkdir()
    
    # Créer admin/__init__.py
    (admin_dir / '__init__.py').write_text('from .admin import *\n')
    
    # Créer admin/admin.py
    admin_content = f'''from django.contrib import admin
from ..models import {app_name.replace('_', '').title()}Item


@admin.register({app_name.replace('_', '').title()}Item)
class {app_name.replace('_', '').title()}ItemAdmin(admin.ModelAdmin):
    """Administration des items {display_name}"""
    
    list_display = ['title', 'user', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        (None, {{
            'fields': ('user', 'title', 'description', 'is_active')
        }}),
        ('Dates', {{
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
'''
    
    (admin_dir / 'admin.py').write_text(admin_content)
    print(f"✅ admin/ folder created with admin.py")
    
    # 7. Créer le dossier serializers
    serializers_dir = app_dir / 'serializers'
    serializers_dir.mkdir()
    
    # Créer serializers/__init__.py
    (serializers_dir / '__init__.py').write_text('from .serializers import *\n')
    
    # Créer serializers/serializers.py
    serializers_content = f'''from rest_framework import serializers
from ..models import {app_name.replace('_', '').title()}Item


class {app_name.replace('_', '').title()}ItemSerializer(serializers.ModelSerializer):
    """Serializer pour {display_name} Item"""
    
    class Meta:
        model = {app_name.replace('_', '').title()}Item
        fields = ['id', 'title', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError('Le titre doit contenir au moins 3 caractères.')
        return value.strip()


class {app_name.replace('_', '').title()}ItemCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'un {display_name} Item"""
    
    class Meta:
        model = {app_name.replace('_', '').title()}Item
        fields = ['title', 'description', 'is_active']
    
    def validate_title(self, value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError('Le titre doit contenir au moins 3 caractères.')
        return value.strip()
'''
    
    (serializers_dir / 'serializers.py').write_text(serializers_content)
    print(f"✅ serializers/ folder created with serializers.py")
    
    # 8. Créer le dossier tests
    tests_dir = app_dir / 'tests'
    tests_dir.mkdir()
    
    # Créer tests/__init__.py
    (tests_dir / '__init__.py').write_text('')
    
    # Créer tests/test_models.py
    test_models_content = f'''from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import {app_name.replace('_', '').title()}Item

User = get_user_model()


class {app_name.replace('_', '').title()}ItemModelTest(TestCase):
    """Tests pour le modèle {app_name.replace('_', '').title()}Item"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_item(self):
        """Test de création d'un item"""
        item = {app_name.replace('_', '').title()}Item.objects.create(
            user=self.user,
            title='Test Item',
            description='Test description'
        )
        self.assertEqual(item.title, 'Test Item')
        self.assertEqual(item.user, self.user)
        self.assertTrue(item.is_active)
        self.assertEqual(str(item), 'Test Item')
    
    def test_item_ordering(self):
        """Test de l'ordre des items"""
        item1 = {app_name.replace('_', '').title()}Item.objects.create(
            user=self.user,
            title='Item 1'
        )
        item2 = {app_name.replace('_', '').title()}Item.objects.create(
            user=self.user,
            title='Item 2'
        )
        
        items = {app_name.replace('_', '').title()}Item.objects.all()
        self.assertEqual(items[0], item2)  # Plus récent en premier
        self.assertEqual(items[1], item1)
'''
    
    (tests_dir / 'test_models.py').write_text(test_models_content)
    
    # Créer tests/test_views.py
    test_views_content = f'''from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import {app_name.replace('_', '').title()}Item

User = get_user_model()


class {app_name.replace('_', '').title()}ViewsTest(TestCase):
    """Tests pour les vues de {display_name}"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_home_view(self):
        """Test de la vue d'accueil"""
        response = self.client.get('/{app_name.replace('_', '-')}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '{display_name}')
    
    def test_create_view_get(self):
        """Test de la vue de création (GET)"""
        response = self.client.get('/{app_name.replace('_', '-')}/create/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_view_post(self):
        """Test de la vue de création (POST)"""
        response = self.client.post('/{app_name.replace('_', '-')}/create/', {{
            'title': 'New Item',
            'description': 'New description',
            'is_active': True
        }})
        self.assertEqual(response.status_code, 302)  # Redirect après création
        self.assertTrue({app_name.replace('_', '').title()}Item.objects.filter(title='New Item').exists())
    
    def test_api_items(self):
        """Test de l'API items"""
        {app_name.replace('_', '').title()}Item.objects.create(
            user=self.user,
            title='API Test Item',
            description='API test description'
        )
        
        response = self.client.get('/{app_name.replace('_', '-')}/api/items/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['items'][0]['title'], 'API Test Item')
'''
    
    (tests_dir / 'test_views.py').write_text(test_views_content)
    print(f"✅ tests/ folder created with test files")
    
    # 9. Créer le dossier templates
    templates_dir = app_dir / 'templates' / app_name
    templates_dir.mkdir(parents=True)
    
    # Créer components folder
    components_dir = app_dir / 'templates' / 'components'
    components_dir.mkdir(parents=True)
    
    print(f"✅ Templates directories created")
    
    # Template base avec navbar component
    base_template = f'''{{{{ extends "base.html" }}}}
{{{{ load static }}}}

{{{{ block title }}}}{display_name}{{{{ endblock }}}}

{{{{ block extra_head }}}}
    <link rel="stylesheet" href="{{{{ static '{app_name}/css/style.css' }}}}">
    <link rel="stylesheet" href="{{{{ static '{app_name}/css/{app_name}_page.css' }}}}">
{{{{ endblock }}}}

{{{{ block content }}}}
    <div class="{app_name}-page">
        <!-- Include navbar component -->
        {{{{ include 'components/{app_name}_navbar.html' with app_name='{display_name}' }}}}
        
        <div class="container-fluid">
            <div class="row">
                <div class="col-12">
                    {{{{ block app_content }}}}
                    {{{{ endblock }}}}
                </div>
            </div>
        </div>
    </div>
{{{{ endblock }}}}

{{{{ block extra_js }}}}
    <script src="{{{{ static '{app_name}/js/app.js' }}}}"></script>
    <script src="{{{{ static '{app_name}/js/{app_name}_page.js' }}}}"></script>
{{{{ endblock }}}}
'''
    
    (templates_dir / 'base.html').write_text(base_template)
    
    # Component navbar
    navbar_component = f'''{{{{ load static }}}}

<nav class="{app_name}-navbar navbar navbar-expand-lg">
    <div class="container-fluid">
        <a class="navbar-brand" href="{{{{ url '{app_name}:home' }}}}">
            <i class="bi bi-app me-2"></i>{{{{ app_name }}}}
        </a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#{app_name}NavbarContent">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="{app_name}NavbarContent">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item">
                    <a class="nav-link {{{{ request.resolver_match.url_name == 'home'|yesno:'active,,' }}}}" 
                       href="{{{{ url '{app_name}:home' }}}}">
                        <i class="bi bi-house me-1"></i>Accueil
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {{{{ request.resolver_match.url_name == 'create_item'|yesno:'active,,' }}}}" 
                       href="{{{{ url '{app_name}:create_item' }}}}">
                        <i class="bi bi-plus me-1"></i>Nouveau
                    </a>
                </li>
            </ul>
            
            <div class="navbar-nav">
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                        <i class="bi bi-gear me-1"></i>Actions
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="{{{{ url '{app_name}:api_items' }}}}">
                            <i class="bi bi-code me-2"></i>API
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="#" onclick="{app_name}Page.refreshData()">
                            <i class="bi bi-arrow-clockwise me-2"></i>Actualiser
                        </a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</nav>
'''
    
    (components_dir / f'{app_name}_navbar.html').write_text(navbar_component)
    
    # Template home
    home_template = f'''{{{{ extends "{app_name}/base.html" }}}}

{{{{ block app_content }}}}
    <div class="{app_name}-page-header">
        <div class="container">
            <h1 class="{app_name}-page-title">{display_name}</h1>
            <p class="{app_name}-page-subtitle">Gérez vos éléments efficacement</p>
        </div>
    </div>

    <div class="container">
        {{{{ if messages }}}}
            {{{{ for message in messages }}}}
                <div class="alert alert-{{{{ message.tags }}}} alert-dismissible fade show" role="alert">
                    {{{{ message }}}}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {{{{ endfor }}}}
        {{{{ endif }}}}

        <div class="{app_name}-content-wrapper">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2>Mes éléments</h2>
                    <p class="text-muted mb-0">{{{{ total_items }}}} élément{{{{ total_items|pluralize }}}} au total</p>
                </div>
                <div class="{app_name}-action-buttons">
                    <a href="{{{{ url '{app_name}:create_item' }}}}" class="{app_name}-btn-primary btn">
                        <i class="bi bi-plus me-2"></i>Nouveau
                    </a>
                </div>
            </div>

            {{{{ if items }}}}
                <div class="{app_name}-item-grid">
                    {{{{ for item in items }}}}
                        <div class="{app_name}-item-card">
                            <div class="card-header">
                                <h5 class="mb-0">{{{{ item.title }}}}</h5>
                            </div>
                            <div class="card-body">
                                <p class="card-text">{{{{ item.description|truncatewords:20|default:"Aucune description" }}}}</p>
                                <small class="text-muted">
                                    Créé le {{{{ item.created_at|date:"d/m/Y H:i" }}}}
                                </small>
                            </div>
                            <div class="card-footer">
                                <a href="{{{{ url '{app_name}:edit_item' item.id }}}}" class="btn btn-sm btn-outline-primary">
                                    <i class="bi bi-pencil me-1"></i>Modifier
                                </a>
                                <a href="{{{{ url '{app_name}:delete_item' item.id }}}}" class="btn btn-sm btn-outline-danger">
                                    <i class="bi bi-trash me-1"></i>Supprimer
                                </a>
                            </div>
                        </div>
                    {{{{ endfor }}}}
                </div>
                
                <!-- Pagination -->
                {{{{ if items.has_other_pages }}}}
                    <nav class="mt-4">
                        <ul class="pagination justify-content-center">
                            {{{{ if items.has_previous }}}}
                                <li class="page-item">
                                    <a class="page-link" href="?page={{{{ items.previous_page_number }}}}">Précédent</a>
                                </li>
                            {{{{ endif }}}}
                            
                            {{{{ for num in items.paginator.page_range }}}}
                                {{{{ if items.number == num }}}}
                                    <li class="page-item active">
                                        <span class="page-link">{{{{ num }}}}</span>
                                    </li>
                                {{{{ else }}}}
                                    <li class="page-item">
                                        <a class="page-link" href="?page={{{{ num }}}}">{{{{ num }}}}</a>
                                    </li>
                                {{{{ endif }}}}
                            {{{{ endfor }}}}
                            
                            {{{{ if items.has_next }}}}
                                <li class="page-item">
                                    <a class="page-link" href="?page={{{{ items.next_page_number }}}}">Suivant</a>
                                </li>
                            {{{{ endif }}}}
                        </ul>
                    </nav>
                {{{{ endif }}}}
            {{{{ else }}}}
                <div class="{app_name}-empty-state">
                    <div class="{app_name}-empty-icon">
                        <i class="bi bi-inbox"></i>
                    </div>
                    <h3>Aucun élément</h3>
                    <p>Commencez par créer votre premier élément.</p>
                    <a href="{{{{ url '{app_name}:create_item' }}}}" class="{app_name}-btn-primary btn">
                        <i class="bi bi-plus me-2"></i>Créer le premier élément
                    </a>
                </div>
            {{{{ endif }}}}
        </div>
    </div>
{{{{ endblock }}}}
'''
    
    (templates_dir / 'home.html').write_text(home_template)
    
    # Create form templates
    create_template = f'''{{{{ extends "{app_name}/base.html" }}}}

{{{{ block app_content }}}}
    <div class="container mt-4">
        <div class="{app_name}-content-wrapper">
            <h2><i class="bi bi-plus me-2"></i>Créer un nouvel élément</h2>
            
            <form method="post">
                {{{{ csrf_token }}}}
                {{{{ form.as_p }}}}
                <div class="d-flex gap-2 mt-4">
                    <button type="submit" class="{app_name}-btn-primary btn">
                        <i class="bi bi-check me-2"></i>Créer
                    </button>
                    <a href="{{{{ url '{app_name}:home' }}}}" class="btn btn-outline-secondary">
                        <i class="bi bi-x me-2"></i>Annuler
                    </a>
                </div>
            </form>
        </div>
    </div>
{{{{ endblock }}}}
'''
    
    (templates_dir / 'create_item.html').write_text(create_template)
    
    print(f"✅ Templates created with navbar component")
    
    # 10. Créer le dossier static
    static_dir = app_dir / 'static' / app_name
    css_dir = static_dir / 'css'
    js_dir = static_dir / 'js'
    img_dir = static_dir / 'images'
    
    css_dir.mkdir(parents=True)
    js_dir.mkdir(parents=True)
    img_dir.mkdir(parents=True)
    
    # CSS amélioré avec navbar styles
    css_content = f'''/* Styles pour {display_name} */
.{app_name}-navbar {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-bottom: 3px solid rgba(255,255,255,0.1);
    box-shadow: 0 2px 20px rgba(0,0,0,0.1);
}}

.{app_name}-navbar .navbar-brand {{
    color: white !important;
    font-weight: 600;
    font-size: 1.3rem;
}}

.{app_name}-navbar .nav-link {{
    color: rgba(255,255,255,0.9) !important;
    font-weight: 500;
    transition: all 0.3s ease;
    border-radius: 6px;
    margin: 0 0.25rem;
    padding: 0.5rem 1rem !important;
}}

.{app_name}-navbar .nav-link:hover,
.{app_name}-navbar .nav-link.active {{
    color: white !important;
    background: rgba(255,255,255,0.15);
    transform: translateY(-1px);
}}

.{app_name}-navbar .dropdown-menu {{
    border: none;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    border-radius: 8px;
}}

/* Page Styles */
.{app_name}-page {{
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}}

.{app_name}-page-header {{
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    padding: 4rem 0 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}}

.{app_name}-page-header::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grain)"/></svg>');
    opacity: 0.3;
}}

.{app_name}-page-title {{
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    position: relative;
    z-index: 1;
}}

.{app_name}-page-subtitle {{
    font-size: 1.3rem;
    opacity: 0.9;
    position: relative;
    z-index: 1;
}}

.{app_name}-content-wrapper {{
    background: white;
    border-radius: 16px;
    padding: 2.5rem;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
    border: 1px solid rgba(255,255,255,0.2);
}}

/* Action Buttons */
.{app_name}-action-buttons {{
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}}

.{app_name}-btn-primary {{
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 10px;
    color: white;
    font-weight: 600;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
}}

.{app_name}-btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.4);
    color: white;
}}

/* Item Grid */
.{app_name}-item-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}}

.{app_name}-item-card {{
    background: white;
    border: 2px solid #f1f5f9;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}}

.{app_name}-item-card:hover {{
    border-color: #4f46e5;
    box-shadow: 0 12px 30px rgba(79, 70, 229, 0.15);
    transform: translateY(-4px);
}}

.{app_name}-item-card .card-header {{
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-bottom: 1px solid #e2e8f0;
    padding: 1.25rem 1.5rem;
}}

.{app_name}-item-card .card-body {{
    padding: 1.5rem;
}}

.{app_name}-item-card .card-footer {{
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
    padding: 1rem 1.5rem;
    display: flex;
    gap: 0.75rem;
}}

/* Empty State */
.{app_name}-empty-state {{
    text-align: center;
    padding: 4rem 2rem;
    color: #64748b;
}}

.{app_name}-empty-icon {{
    font-size: 4rem;
    margin-bottom: 1.5rem;
    opacity: 0.4;
}}

.{app_name}-empty-state h3 {{
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #475569;
}}

/* Animations */
@keyframes {app_name}FadeIn {{
    from {{ opacity: 0; transform: translateY(30px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.{app_name}-animate-in {{
    animation: {app_name}FadeIn 0.6s ease forwards;
}}

/* Responsive */
@media (max-width: 768px) {{
    .{app_name}-page-header {{
        padding: 2rem 0;
    }}
    
    .{app_name}-page-title {{
        font-size: 2.2rem;
    }}
    
    .{app_name}-content-wrapper {{
        margin: 0 1rem 2rem;
        padding: 1.5rem;
        border-radius: 12px;
    }}
    
    .{app_name}-item-grid {{
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }}
    
    .{app_name}-action-buttons {{
        flex-direction: column;
    }}
    
    .{app_name}-btn-primary {{
        text-align: center;
        justify-content: center;
    }}
}}
'''
    
    (css_dir / 'style.css').write_text(css_content)
    
    # JavaScript amélioré
    js_content = f'''// JavaScript pour {display_name}
class {app_name.replace('_', '').title()}Page {{
    constructor() {{
        this.init();
    }}
    
    init() {{
        console.log('{display_name} page initialized');
        this.setupEventListeners();
        this.setupAnimations();
        this.setupNavbar();
    }}
    
    setupEventListeners() {{
        // Confirmation de suppression
        document.querySelectorAll('.btn-outline-danger').forEach(button => {{
            button.addEventListener('click', (e) => {{
                if (button.getAttribute('href').includes('/delete/')) {{
                    e.preventDefault();
                    this.confirmDelete(button.getAttribute('href'));
                }}
            }});
        }});
        
        // Gestionnaire pour les cartes d'items
        document.querySelectorAll('.{app_name}-item-card').forEach(card => {{
            card.addEventListener('mouseenter', () => {{
                card.style.transform = 'translateY(-6px)';
            }});
            card.addEventListener('mouseleave', () => {{
                card.style.transform = 'translateY(-4px)';
            }});
        }});
    }}
    
    setupAnimations() {{
        // Animation des cartes au chargement
        const cards = document.querySelectorAll('.{app_name}-item-card');
        cards.forEach((card, index) => {{
            card.style.animationDelay = `${{index * 0.1}}s`;
            card.classList.add('{app_name}-animate-in');
        }});
        
        // Observer pour les animations d'apparition
        if ('IntersectionObserver' in window) {{
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.classList.add('{app_name}-animate-in');
                    }}
                }});
            }}, {{ threshold: 0.1 }});
            
            // Observer tous les éléments avec l'animation
            document.querySelectorAll('.{app_name}-content-wrapper').forEach(el => {{
                observer.observe(el);
            }});
        }}
    }}
    
    setupNavbar() {{
        // Activer les dropdowns Bootstrap
        const dropdowns = document.querySelectorAll('.dropdown-toggle');
        dropdowns.forEach(dropdown => {{
            new bootstrap.Dropdown(dropdown);
        }});
    }}
    
    confirmDelete(url) {{
        if (confirm('Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.')) {{
            window.location.href = url;
        }}
    }}
    
    static refreshData() {{
        window.location.reload();
    }}
    
    static async loadItems() {{
        try {{
            const response = await fetch('/{app_name.replace('_', '-')}/api/items/');
            return await response.json();
        }} catch (error) {{
            console.error('Error loading items:', error);
            return null;
        }}
    }}
}}

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {{
    if (document.querySelector('.{app_name}-page')) {{
        window.{app_name}Page = new {app_name.replace('_', '').title()}Page();
    }}
}});

// Export for global access
window.{app_name}Page = {app_name.replace('_', '').title()}Page;
'''
    
    (js_dir / 'app.js').write_text(js_content)
    print(f"✅ Static files created with enhanced styling")
    
    # 11. Créer __manifest__.py
    create_manifest(app_dir, app_name, display_name, category)
    
    # 12. Créer urls.py
    create_urls_file(app_dir, app_name)
    
    # 13. Synchroniser avec le système
    sync_app_to_system(app_name)
    
    print(f"🎯 App {app_name} créée avec succès!")
    print()
    print("📁 Structure créée:")
    print(f"   ├── __manifest__.py")
    print(f"   ├── apps.py")
    print(f"   ├── models/")
    print(f"   │   └── models.py")
    print(f"   ├── views/")
    print(f"   │   └── views.py")
    print(f"   ├── forms/")
    print(f"   │   └── forms.py")
    print(f"   ├── admin/")
    print(f"   │   └── admin.py")
    print(f"   ├── serializers/")
    print(f"   │   └── serializers.py")
    print(f"   ├── tests/")
    print(f"   │   ├── test_models.py")
    print(f"   │   └── test_views.py")
    print(f"   ├── templates/")
    print(f"   │   ├── components/{app_name}_navbar.html")
    print(f"   │   └── {app_name}/")
    print(f"   │       ├── base.html")
    print(f"   │       ├── home.html")
    print(f"   │       └── create_item.html")
    print(f"   ├── static/{app_name}/")
    print(f"   │   ├── css/style.css")
    print(f"   │   └── js/app.js")
    print(f"   └── urls.py")
    print()
    
    add_app_to_all_dashboards(app_name, display_name)
    
    return True


def create_manifest(app_dir, app_name, display_name, category):
    """Crée le fichier __manifest__.py pour l'app."""
    manifest_content = f'''"""
Manifest for {display_name} app
Auto-generated by create_complete_app.py
Author: LGPL
"""

__manifest__ = {{
    # Basic Information
    'name': '{app_name}',
    'display_name': '{display_name}',
    'version': '1.0.0',
    'category': '{category}',
    'author': 'LGPL',
    'description': 'Application {display_name} pour gérer et organiser vos données efficacement.',
    'summary': '{display_name} - Gérez vos éléments avec style et efficacité',
    
    # App Configuration
    'application': True,  # This is a user application (visible in App Store)
    'installable': True,  # Ready for production use
    'auto_install': False,  # Don't install automatically
    'sequence': 100,  # Display order
    
    # Dependencies
    'depends': [
        'base',
        'authentication',
    ],
    
    # Data files and assets
    'data': [],
    
    # Frontend components
    'frontend_components': {{
        'icon': 'bi-app',  # Bootstrap icon
        'color': '#4f46e5',  # Primary color
        'routes': {{
            'home': '/{app_name.replace('_', '-')}/',
            'create': '/{app_name.replace('_', '-')}/create/',
            'api': '/{app_name.replace('_', '-')}/api/',
        }},
        'menu_items': [
            {{
                'name': 'home',
                'label': 'Accueil',
                'url': '/{app_name.replace('_', '-')}/',
                'icon': 'bi-house'
            }},
            {{
                'name': 'create',
                'label': 'Nouveau',
                'url': '/{app_name.replace('_', '-')}/create/',
                'icon': 'bi-plus'
            }}
        ]
    }},
    
    # Features and capabilities
    'features': [
        'crud_operations',
        'user_data',
        'responsive_design',
        'api_endpoints',
        'pagination',
        'search',
        'modern_ui',
        'navbar_component'
    ],
    
    # Technical information
    'django_app': True,
    'has_models': True,
    'has_views': True,
    'has_forms': True,
    'has_admin': True,
    'has_serializers': True,
    'has_templates': True,
    'has_static': True,
    'has_api': True,
    'has_tests': True,
    'has_components': True,
}}
'''
    
    (app_dir / '__manifest__.py').write_text(manifest_content)
    print(f"✅ __manifest__.py created (Author: LGPL)")


def create_urls_file(app_dir, app_name):
    """Crée le fichier urls.py pour l'app."""
    urls_content = f'''"""
URLs configuration for {app_name} app.
Generated by create_complete_app.py
"""
from django.urls import path
from .views import views

app_name = '{app_name}'

urlpatterns = [
    # Main pages
    path('', views.{app_name}_home, name='home'),
    path('create/', views.create_item, name='create_item'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    
    # API endpoints
    path('api/items/', views.api_items, name='api_items'),
]
'''
    
    (app_dir / 'urls.py').write_text(urls_content)
    print(f"✅ urls.py created")


def sync_app_to_system(app_name):
    """Synchronise l'app avec le système."""
    try:
        print(f"🔄 Synchronisation de l'app {app_name} avec le système...")
        
        from app_manager.services.auto_manifest_service import AutoManifestService
        from app_manager.services.auto_url_service import AutoURLService
        from app_manager.models import App
        
        # Synchroniser les manifests
        print("   📝 Synchronisation des manifests...")
        AutoManifestService.sync_all_apps()
        
        # Synchroniser les URLs
        print("   🔗 Synchronisation des URLs...")
        AutoURLService.sync_all_urls()
        
        # Synchroniser avec la base de données
        print("   🗃️ Synchronisation de la base de données...")
        discovery_result = App.sync_apps()
        
        print(f"   ✅ Apps découvertes: {discovery_result.get('total_discovered', 0)}")
        print(f"   ✅ Apps créées: {discovery_result.get('newly_created', 0)}")
        print(f"   ✅ Apps mises à jour: {discovery_result.get('updated', 0)}")
        
        # Vérifier que l'app a été créée
        try:
            app = App.objects.get(code=app_name)
            print(f"   🎯 App {app.display_name} synchronisée avec succès!")
            return app
        except App.DoesNotExist:
            print(f"   ⚠️ App {app_name} pas encore visible dans la base de données")
            return None
            
    except Exception as e:
        print(f"   ❌ Erreur lors de la synchronisation: {e}")
        print("      Vous pourrez exécuter manuellement: poetry run python manage.py setup_auto_apps")
        return None


def add_app_to_all_dashboards(app_code, display_name):
    """Ajoute la nouvelle app au dashboard de tous les utilisateurs."""
    try:
        from django.contrib.auth import get_user_model
        from app_manager.models import App, UserAppSettings
        
        User = get_user_model()
        
        print(f"🔄 Ajout de l'app au dashboard des utilisateurs...")
        
        try:
            app = App.objects.get(code=app_code)
            print(f"✅ App trouvée dans la base: {app.display_name}")
        except App.DoesNotExist:
            print(f"⚠️ App pas encore synchronisée dans la base de données.")
            return
        
        users = User.objects.all()
        users_count = users.count()
        
        if users_count == 0:
            print("ℹ️ Aucun utilisateur trouvé")
            return
        
        added_count = 0
        
        for user in users:
            user_settings, created = UserAppSettings.objects.get_or_create(user=user)
            
            if not user_settings.enabled_apps.filter(code=app_code).exists():
                user_settings.enabled_apps.add(app)
                added_count += 1
                print(f"   ✅ Ajoutée au dashboard de {user.username}")
        
        print(f"🎉 App ajoutée au dashboard de {added_count}/{users_count} utilisateurs!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout au dashboard: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Usage: python scripts/create_complete_app.py <app_name> [display_name] [category]")
        print("📝 Exemple: python scripts/create_complete_app.py task_manager 'Task Manager' 'productivity'")
        sys.exit(1)
    
    app_name = sys.argv[1]
    display_name = sys.argv[2] if len(sys.argv) > 2 else None
    category = sys.argv[3] if len(sys.argv) > 3 else 'productivity'
    
    if create_complete_app(app_name, display_name, category):
        print()
        print("🎉 APP COMPLÈTEMENT CONFIGURÉE!")
        print("="*50)
        print("✅ App créée avec la structure de dossiers correcte")
        print("✅ Navbar component inclus dans les templates")
        print("✅ Serializers créés pour l'API")
        print("✅ Tests séparés par fonctionnalité")
        print("✅ CSS moderne avec animations")
        print("✅ JavaScript amélioré")
        print("✅ Manifest avec author LGPL")
        print("✅ App synchronisée avec la base de données")
        print()
        print("🌐 Votre app est maintenant disponible à:")
        print(f"   👉 http://localhost:8000/{app_name.replace('_', '-')}/")
        print()
        print("📱 Elle apparaît aussi dans:")
        print("   👉 App Store (pour installation)")
        print("   👉 Dashboard (déjà installée)")
        print()
        print("🚀 Prêt à développer!")
    else:
        sys.exit(1)