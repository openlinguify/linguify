#!/usr/bin/env python3
"""
Script pour créer une app Django complète avec tous les fichiers et configuration
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
    """Crée une app Django complète avec tous les fichiers standard"""
    
    if not app_name:
        print("❌ Usage: python scripts/create_complete_app.py <app_name> [display_name] [category]")
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
    print()
    
    # Vérifier si l'app existe déjà
    if app_dir.exists():
        print(f"❌ L'app '{app_name}' existe déjà dans apps/{app_name}")
        return False
    
    # Créer le dossier
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
    
    # 3. Créer models.py
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
    
    (app_dir / 'models.py').write_text(models_content)
    print(f"✅ models.py créé")
    
    # 4. Créer views.py
    views_content = f'''from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import {app_name.replace('_', '').title()}Item
from .forms import {app_name.replace('_', '').title()}ItemForm


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
    
    (app_dir / 'views.py').write_text(views_content)
    print(f"✅ views.py créé")
    
    # 5. Créer forms.py
    forms_content = f'''from django import forms
from .models import {app_name.replace('_', '').title()}Item


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
    
    (app_dir / 'forms.py').write_text(forms_content)
    print(f"✅ forms.py créé")
    
    # 6. Créer admin.py
    admin_content = f'''from django.contrib import admin
from .models import {app_name.replace('_', '').title()}Item


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
    
    (app_dir / 'admin.py').write_text(admin_content)
    print(f"✅ admin.py créé")
    
    # 7. Créer tests.py
    tests_content = f'''from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import {app_name.replace('_', '').title()}Item

User = get_user_model()


class {app_name.replace('_', '').title()}TestCase(TestCase):
    """Tests pour l'app {display_name}"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
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
    
    def test_home_view(self):
        """Test de la vue d'accueil"""
        response = self.client.get('/{app_name.replace('_', '-')}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '{display_name}')
    
    def test_create_view(self):
        """Test de la vue de création"""
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
    
    (app_dir / 'tests.py').write_text(tests_content)
    print(f"✅ tests.py créé")
    
    # 8. Créer le dossier templates
    templates_dir = app_dir / 'templates' / app_name
    templates_dir.mkdir(parents=True)
    print(f"✅ Dossier templates créé")
    
    # Template base
    base_template = f'''{{{{ extends "base.html" }}}}
{{{{ load static }}}}

{{{{ block title }}}}{display_name}{{{{ endblock }}}}

{{{{ block extra_head }}}}
    <link rel="stylesheet" href="{{{{ static '{app_name}/css/style.css' }}}}">
{{{{ endblock }}}}

{{{{ block content }}}}
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><i class="bi bi-app"></i> {display_name}</h1>
                    <a href="{{{{ url '{app_name}:create_item' }}}}" class="btn btn-primary">
                        <i class="bi bi-plus"></i> Nouveau
                    </a>
                </div>
                
                {{{{ block app_content }}}}
                {{{{ endblock }}}}
            </div>
        </div>
    </div>
{{{{ endblock }}}}

{{{{ block extra_js }}}}
    <script src="{{{{ static '{app_name}/js/app.js' }}}}"></script>
{{{{ endblock }}}}
'''
    
    (templates_dir / 'base.html').write_text(base_template)
    
    # Template home
    home_template = f'''{{{{ extends "{app_name}/base.html" }}}}

{{{{ block app_content }}}}
    {{{{ if messages }}}}
        {{{{ for message in messages }}}}
            <div class="alert alert-{{{{ message.tags }}}} alert-dismissible fade show" role="alert">
                {{{{ message }}}}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {{{{ endfor }}}}
    {{{{ endif }}}}

    <div class="row mb-3">
        <div class="col-md-6">
            <p class="text-muted">{{{{ total_items }}}} item{{{{ total_items|pluralize }}}} au total</p>
        </div>
        <div class="col-md-6 text-end">
            <div class="btn-group" role="group">
                <a href="{{{{ url '{app_name}:create_item' }}}}" class="btn btn-outline-primary">
                    <i class="bi bi-plus"></i> Ajouter
                </a>
            </div>
        </div>
    </div>

    {{{{ if items }}}}
        <div class="row">
            {{{{ for item in items }}}}
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">{{{{ item.title }}}}</h5>
                            <p class="card-text">{{{{ item.description|truncatewords:20 }}}}</p>
                            <small class="text-muted">
                                Créé le {{{{ item.created_at|date:"d/m/Y H:i" }}}}
                            </small>
                        </div>
                        <div class="card-footer">
                            <a href="{{{{ url '{app_name}:edit_item' item.id }}}}" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-pencil"></i> Modifier
                            </a>
                            <a href="{{{{ url '{app_name}:delete_item' item.id }}}}" class="btn btn-sm btn-outline-danger">
                                <i class="bi bi-trash"></i> Supprimer
                            </a>
                        </div>
                    </div>
                </div>
            {{{{ endfor }}}}
        </div>
        
        <!-- Pagination -->
        {{{{ if items.has_other_pages }}}}
            <nav>
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
        <div class="text-center py-5">
            <i class="bi bi-inbox display-1 text-muted"></i>
            <h3 class="mt-3">Aucun item</h3>
            <p class="text-muted">Commencez par créer votre premier item.</p>
            <a href="{{{{ url '{app_name}:create_item' }}}}" class="btn btn-primary">
                <i class="bi bi-plus"></i> Créer le premier item
            </a>
        </div>
    {{{{ endif }}}}
{{{{ endblock }}}}
'''
    
    (templates_dir / 'home.html').write_text(home_template)
    print(f"✅ Templates créés")
    
    # 9. Créer le dossier static
    static_dir = app_dir / 'static' / app_name
    css_dir = static_dir / 'css'
    js_dir = static_dir / 'js'
    img_dir = static_dir / 'images'
    desc_dir = static_dir / 'description'
    
    css_dir.mkdir(parents=True)
    js_dir.mkdir(parents=True)
    img_dir.mkdir(parents=True)
    desc_dir.mkdir(parents=True)
    
    # CSS général
    css_content = f'''/* Styles généraux pour {display_name} */
.{app_name}-container {{
    max-width: 1200px;
    margin: 0 auto;
}}

.{app_name}-card {{
    transition: transform 0.2s;
}}

.{app_name}-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}}

.{app_name}-header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
}}

.{app_name}-stats {{
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
}}

@media (max-width: 768px) {{
    .{app_name}-header {{
        padding: 1rem;
        text-align: center;
    }}
}}
'''
    (css_dir / 'style.css').write_text(css_content)
    
    # CSS spécifique à la page
    page_css_content = f'''/* Styles spécifiques pour la page {display_name} */
.{app_name}-page {{
    min-height: 100vh;
    background: #f8f9fa;
}}

.{app_name}-page-header {{
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    padding: 3rem 0;
    text-align: center;
    margin-bottom: 2rem;
}}

.{app_name}-page-title {{
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 1rem;
}}

.{app_name}-page-subtitle {{
    font-size: 1.2rem;
    opacity: 0.9;
}}

.{app_name}-content-wrapper {{
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}}

.{app_name}-action-buttons {{
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
}}

.{app_name}-btn-primary {{
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    transition: all 0.3s ease;
}}

.{app_name}-btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(79, 70, 229, 0.3);
}}

.{app_name}-item-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}}

.{app_name}-item-card {{
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}}

.{app_name}-item-card:hover {{
    border-color: #4f46e5;
    box-shadow: 0 8px 25px rgba(79, 70, 229, 0.15);
    transform: translateY(-4px);
}}

.{app_name}-empty-state {{
    text-align: center;
    padding: 4rem 2rem;
    color: #6b7280;
}}

.{app_name}-empty-icon {{
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}}

/* Animations */
@keyframes {app_name}FadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.{app_name}-animate-in {{
    animation: {app_name}FadeIn 0.6s ease forwards;
}}

/* Responsive */
@media (max-width: 768px) {{
    .{app_name}-page-header {{
        padding: 2rem 1rem;
    }}
    
    .{app_name}-page-title {{
        font-size: 2rem;
    }}
    
    .{app_name}-content-wrapper {{
        margin: 0 1rem 2rem;
        padding: 1.5rem;
    }}
    
    .{app_name}-item-grid {{
        grid-template-columns: 1fr;
        gap: 1rem;
    }}
}}
'''
    (css_dir / f'{app_name}_page.css').write_text(page_css_content)
    
    # JavaScript général
    js_content = f'''// JavaScript général pour {display_name}
document.addEventListener('DOMContentLoaded', function() {{
    console.log('{display_name} app loaded');
    
    // Confirmation de suppression
    const deleteButtons = document.querySelectorAll('.btn-outline-danger');
    deleteButtons.forEach(button => {{
        button.addEventListener('click', function(e) {{
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet item ?')) {{
                e.preventDefault();
            }}
        }});
    }});
    
    // Animation des cartes
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {{
        card.style.animationDelay = `${{index * 0.1}}s`;
        card.classList.add('animate-fade-in');
    }});
}});

// API Helper
class {app_name.replace('_', '').title()}API {{
    static async getItems() {{
        try {{
            const response = await fetch('/{app_name.replace('_', '-')}/api/items/');
            return await response.json();
        }} catch (error) {{
            console.error('Error fetching items:', error);
            return null;
        }}
    }}
    
    static async createItem(data) {{
        try {{
            const response = await fetch('/{app_name.replace('_', '-')}/api/items/', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }},
                body: JSON.stringify(data)
            }});
            return await response.json();
        }} catch (error) {{
            console.error('Error creating item:', error);
            return null;
        }}
    }}
    
    static async updateItem(id, data) {{
        try {{
            const response = await fetch(`/{app_name.replace('_', '-')}/api/items/${{id}}/`, {{
                method: 'PUT',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }},
                body: JSON.stringify(data)
            }});
            return await response.json();
        }} catch (error) {{
            console.error('Error updating item:', error);
            return null;
        }}
    }}
    
    static async deleteItem(id) {{
        try {{
            const response = await fetch(`/{app_name.replace('_', '-')}/api/items/${{id}}/`, {{
                method: 'DELETE',
                headers: {{
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }}
            }});
            return response.ok;
        }} catch (error) {{
            console.error('Error deleting item:', error);
            return false;
        }}
    }}
}}
'''
    (js_dir / 'app.js').write_text(js_content)
    
    # JavaScript spécifique à la page
    page_js_content = f'''// JavaScript spécifique pour la page {display_name}
class {app_name.replace('_', '').title()}Page {{
    constructor() {{
        this.init();
    }}
    
    init() {{
        console.log('{display_name} page initialized');
        this.setupEventListeners();
        this.loadInitialData();
        this.setupAnimations();
    }}
    
    setupEventListeners() {{
        // Gestionnaire pour les boutons d'action
        const actionButtons = document.querySelectorAll('.{app_name}-btn-primary');
        actionButtons.forEach(button => {{
            button.addEventListener('click', (e) => {{
                this.handleActionClick(e);
            }});
        }});
        
        // Gestionnaire pour les cartes d'items
        const itemCards = document.querySelectorAll('.{app_name}-item-card');
        itemCards.forEach(card => {{
            card.addEventListener('click', (e) => {{
                this.handleCardClick(e);
            }});
        }});
        
        // Gestionnaire pour la recherche
        const searchInput = document.querySelector('#{app_name}-search');
        if (searchInput) {{
            searchInput.addEventListener('input', (e) => {{
                this.handleSearch(e.target.value);
            }});
        }}
    }}
    
    async loadInitialData() {{
        try {{
            const data = await {app_name.replace('_', '').title()}API.getItems();
            if (data) {{
                this.renderItems(data.items);
            }}
        }} catch (error) {{
            console.error('Error loading initial data:', error);
        }}
    }}
    
    renderItems(items) {{
        const container = document.querySelector('.{app_name}-item-grid');
        if (!container) return;
        
        if (items.length === 0) {{
            this.showEmptyState();
            return;
        }}
        
        container.innerHTML = items.map(item => `
            <div class="{app_name}-item-card {app_name}-animate-in" data-item-id="${{item.id}}">
                <h5>${{item.title}}</h5>
                <p>${{item.description || 'Aucune description'}}</p>
                <small class="text-muted">
                    Créé le ${{new Date(item.created_at).toLocaleDateString('fr-FR')}}
                </small>
                <div class="mt-3">
                    <button class="btn btn-sm btn-outline-primary" onclick="{app_name}Page.editItem(${{item.id}})">
                        <i class="bi bi-pencil"></i> Modifier
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="{app_name}Page.deleteItem(${{item.id}})">
                        <i class="bi bi-trash"></i> Supprimer
                    </button>
                </div>
            </div>
        `).join('');
    }}
    
    showEmptyState() {{
        const container = document.querySelector('.{app_name}-item-grid');
        if (!container) return;
        
        container.innerHTML = `
            <div class="{app_name}-empty-state">
                <div class="{app_name}-empty-icon">
                    <i class="bi bi-inbox"></i>
                </div>
                <h3>Aucun item</h3>
                <p>Commencez par créer votre premier item.</p>
                <button class="{app_name}-btn-primary" onclick="{app_name}Page.createItem()">
                    <i class="bi bi-plus"></i> Créer le premier item
                </button>
            </div>
        `;
    }}
    
    setupAnimations() {{
        // Observer pour les animations d'apparition
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('{app_name}-animate-in');
                }}
            }});
        }}, {{ threshold: 0.1 }});
        
        // Observer tous les éléments avec la classe d'animation
        const animateElements = document.querySelectorAll('.{app_name}-item-card');
        animateElements.forEach(el => observer.observe(el));
    }}
    
    handleActionClick(e) {{
        const action = e.target.dataset.action;
        switch (action) {{
            case 'create':
                this.createItem();
                break;
            case 'refresh':
                this.loadInitialData();
                break;
            default:
                console.log('Action clicked:', action);
        }}
    }}
    
    handleCardClick(e) {{
        const card = e.target.closest('.{app_name}-item-card');
        if (!card) return;
        
        const itemId = card.dataset.itemId;
        console.log('Card clicked, item ID:', itemId);
        // Ajouter logique spécifique ici
    }}
    
    handleSearch(query) {{
        const cards = document.querySelectorAll('.{app_name}-item-card');
        cards.forEach(card => {{
            const title = card.querySelector('h5').textContent.toLowerCase();
            const description = card.querySelector('p').textContent.toLowerCase();
            const matches = title.includes(query.toLowerCase()) || description.includes(query.toLowerCase());
            
            card.style.display = matches ? 'block' : 'none';
        }});
    }}
    
    static async createItem() {{
        // Redirect to create page or open modal
        window.location.href = '/{app_name.replace('_', '-')}/create/';
    }}
    
    static async editItem(id) {{
        // Redirect to edit page or open modal
        window.location.href = `/{app_name.replace('_', '-')}/edit/${{id}}/`;
    }}
    
    static async deleteItem(id) {{
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet item ?')) {{
            return;
        }}
        
        const success = await {app_name.replace('_', '').title()}API.deleteItem(id);
        if (success) {{
            // Refresh the page or remove the item from DOM
            window.location.reload();
        }} else {{
            alert('Erreur lors de la suppression');
        }}
    }}
}}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {{
    if (document.querySelector('.{app_name}-page')) {{
        window.{app_name}Page = new {app_name.replace('_', '').title()}Page();
    }}
}});
'''
    (js_dir / f'{app_name}_page.js').write_text(page_js_content)
    print(f"✅ Fichiers static créés")
    
    # 10. Créer __manifest__.py
    create_manifest(app_dir, app_name, display_name, category)
    
    # 11. Créer urls.py
    create_urls_file(app_dir, app_name)
    
    # 12. Synchroniser les apps et URLs automatiquement
    sync_app_to_system(app_name)
    
    print(f"🎯 App {app_name} créée avec succès!")
    print()
    print("📁 Structure créée:")
    print(f"   ├── __manifest__.py (configuration complète)")
    print(f"   ├── apps.py")
    print(f"   ├── models.py (avec {app_name.replace('_', '').title()}Item)")
    print(f"   ├── views.py (vues complètes + API)")
    print(f"   ├── forms.py")
    print(f"   ├── admin.py") 
    print(f"   ├── tests.py")
    print(f"   ├── urls.py (routage automatique)")
    print(f"   ├── templates/{app_name}/")
    print(f"   └── static/{app_name}/")
    print(f"        ├── css/style.css (styles généraux)")
    print(f"        ├── css/{app_name}_page.css (styles page)")
    print(f"        ├── js/app.js (JavaScript général + API)")
    print(f"        └── js/{app_name}_page.js (JavaScript page)")
    print()
    
    # Add app to dashboard for all users
    add_app_to_all_dashboards(app_name, display_name)
    
    return True


def create_manifest(app_dir, app_name, display_name, category):
    """
    Crée le fichier __manifest__.py pour l'app.
    """
    manifest_content = f'''"""
Manifest for {display_name} app
Auto-generated by create_complete_app.py
"""

__manifest__ = {{
    # Basic Information
    'name': '{app_name}',
    'display_name': '{display_name}',
    'version': '1.0.0',
    'category': '{category}',
    'author': 'Linguify',
    'description': 'Application {display_name} pour gérer et organiser vos données.',
    'summary': '{display_name} - Gérez vos éléments efficacement',
    
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
    'data': [
        # Add any default data files here
    ],
    
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
        'search'
    ],
    
    # Technical information
    'django_app': True,
    'has_models': True,
    'has_views': True,
    'has_templates': True,
    'has_static': True,
    'has_api': True,
    'has_tests': True,
}}
'''
    
    (app_dir / '__manifest__.py').write_text(manifest_content)
    print(f"✅ __manifest__.py créé")


def create_urls_file(app_dir, app_name):
    """
    Crée le fichier urls.py pour l'app.
    """
    urls_content = f'''"""
URLs configuration for {app_name} app.
"""
from django.urls import path
from . import views

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
    print(f"✅ urls.py créé")


def sync_app_to_system(app_name):
    """
    Synchronise l'app avec le système (manifest, URLs, base de données).
    """
    try:
        print(f"🔄 Synchronisation de l'app {app_name} avec le système...")
        
        # Import des services nécessaires
        from app_manager.services.auto_manifest_service import AutoManifestService
        from app_manager.services.auto_url_service import AutoURLService
        from app_manager.models import App
        
        # 1. Synchroniser les manifests
        print("   📝 Synchronisation des manifests...")
        manifest_result = AutoManifestService.sync_all_apps()
        
        # 2. Synchroniser les URLs
        print("   🔗 Synchronisation des URLs...")
        url_result = AutoURLService.sync_all_urls()
        
        # 3. Découvrir et synchroniser les apps
        print("   🗃️  Synchronisation de la base de données...")
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
            print(f"   ⚠️  App {app_name} pas encore visible dans la base de données")
            print("      Cela peut prendre quelques secondes...")
            return None
            
    except Exception as e:
        print(f"   ❌ Erreur lors de la synchronisation: {e}")
        print("      Vous pourrez exécuter manuellement: poetry run python manage.py setup_auto_apps")
        return None


def add_app_to_all_dashboards(app_code, display_name):
    """
    Ajoute la nouvelle app au dashboard de tous les utilisateurs existants.
    """
    try:
        from django.contrib.auth import get_user_model
        from app_manager.models import App, UserAppSettings
        
        User = get_user_model()
        
        print(f"🔄 Ajout de l'app au dashboard des utilisateurs...")
        
        # Vérifier si l'app existe dans la base de données
        # (elle sera créée automatiquement par setup_auto_apps)
        try:
            app = App.objects.get(code=app_code)
            print(f"✅ App trouvée dans la base: {app.display_name}")
        except App.DoesNotExist:
            print(f"⚠️  App pas encore synchronisée dans la base de données.")
            print(f"   Elle sera automatiquement ajoutée après: poetry run python manage.py setup_auto_apps")
            return
        
        # Obtenir tous les utilisateurs
        users = User.objects.all()
        users_count = users.count()
        
        if users_count == 0:
            print("ℹ️  Aucun utilisateur trouvé - l'app sera automatiquement disponible pour les nouveaux utilisateurs")
            return
        
        added_count = 0
        
        # Ajouter l'app au dashboard de chaque utilisateur
        for user in users:
            user_settings, created = UserAppSettings.objects.get_or_create(user=user)
            
            # Vérifier si l'app n'est pas déjà activée
            if not user_settings.enabled_apps.filter(code=app_code).exists():
                user_settings.enabled_apps.add(app)
                added_count += 1
                print(f"   ✅ Ajoutée au dashboard de {user.username}")
            else:
                print(f"   ℹ️  Déjà dans le dashboard de {user.username}")
        
        print(f"🎉 App ajoutée au dashboard de {added_count}/{users_count} utilisateurs!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout au dashboard: {e}")
        print("   L'app sera disponible dans l'App Store pour installation manuelle.")


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
        print("✅ App créée avec tous les fichiers")
        print("✅ Manifest généré automatiquement")
        print("✅ URLs configurées automatiquement")
        print("✅ App synchronisée avec la base de données")
        print("✅ App ajoutée au dashboard des utilisateurs")
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