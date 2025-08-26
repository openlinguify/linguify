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
    
    # CSS
    css_content = f'''/* Styles pour {display_name} */
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
    
    # JavaScript
    js_content = f'''// JavaScript pour {display_name}
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
}}
'''
    (js_dir / 'app.js').write_text(js_content)
    print(f"✅ Fichiers static créés")
    
    print(f"🎯 App {app_name} créée avec succès!")
    print()
    print("📁 Structure créée:")
    print(f"   ├── apps.py")
    print(f"   ├── models.py (avec {app_name.replace('_', '').title()}Item)")
    print(f"   ├── views.py (vues complètes + API)")
    print(f"   ├── forms.py")
    print(f"   ├── admin.py") 
    print(f"   ├── tests.py")
    print(f"   ├── templates/{app_name}/")
    print(f"   └── static/{app_name}/")
    print()
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Usage: python scripts/create_complete_app.py <app_name> [display_name] [category]")
        print("📝 Exemple: python scripts/create_complete_app.py task_manager 'Task Manager' 'productivity'")
        sys.exit(1)
    
    app_name = sys.argv[1]
    display_name = sys.argv[2] if len(sys.argv) > 2 else None
    category = sys.argv[3] if len(sys.argv) > 3 else 'productivity'
    
    if create_complete_app(app_name, display_name, category):
        print("✅ Maintenant exécutez: poetry run python manage.py setup_auto_apps")
        print("🎯 Votre app apparaîtra automatiquement dans l'App Store!")
    else:
        sys.exit(1)