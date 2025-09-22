# -*- coding: utf-8 -*-
"""
Vues interactives XML avec données réelles et navigation
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Q
import json

from ..models import Note, NoteCategory, SharedNote
from ..utils.xml_parser import xml_parser, get_xml_view_data


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def interactive_xml_view(request, view_id):
    """Vue XML interactive avec vraies données et navigation"""
    view_data = get_xml_view_data(view_id)

    if not view_data:
        return Response(
            {'error': f'Vue {view_id} non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Récupérer les vraies données selon le modèle
    model_name = view_data.get('model', '')
    view_type = view_data.get('arch', {}).get('type', 'unknown')

    # Récupérer les données selon le modèle
    real_data = get_real_data_for_model(request.user, model_name, view_type)

    # Générer le HTML avec navigation et CSRF token
    csrf_token = get_token(request)
    html_content = generate_interactive_html(view_id, view_data, real_data, request.user, csrf_token)

    return HttpResponse(html_content, content_type='text/html')


def get_real_data_for_model(user, model_name, view_type):
    """Récupère les vraies données selon le modèle"""
    if model_name == 'notebook.note':
        notes = Note.objects.filter(user=user).select_related('category').order_by('-updated_at')[:20]

        if view_type == 'tree' or view_type == 'kanban':
            return [
                {
                    'id': note.id,
                    'title': note.title,
                    'content': note.content[:100] + '...' if len(note.content) > 100 else note.content,
                    'note_type': note.get_note_type_display(),
                    'language': note.language or 'Non spécifiée',
                    'priority': note.get_priority_display(),
                    'difficulty': note.get_difficulty_display() if note.difficulty else 'Non spécifiée',
                    'category': note.category.name if note.category else 'Sans catégorie',
                    'is_pinned': '📌' if note.is_pinned else '',
                    'is_archived': '🗄️' if note.is_archived else '',
                    'created_at': note.created_at.strftime('%d/%m/%Y %H:%M'),
                    'updated_at': note.updated_at.strftime('%d/%m/%Y %H:%M'),
                    'review_count': note.review_count,
                    'last_reviewed_at': note.last_reviewed_at.strftime('%d/%m/%Y') if note.last_reviewed_at else 'Jamais',
                }
                for note in notes
            ]
        elif view_type == 'form' and notes.exists():
            note = notes.first()
            return {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'note_type': note.note_type,
                'language': note.language or '',
                'priority': note.priority,
                'difficulty': note.difficulty or '',
                'category': note.category.name if note.category else '',
                'is_pinned': note.is_pinned,
                'is_archived': note.is_archived,
                'pronunciation': getattr(note, 'pronunciation', '') or '',
                'translation': note.translation or '',
                'example_sentences': str(note.example_sentences) if note.example_sentences else '',
                'related_words': str(note.related_words) if note.related_words else '',
            }

    elif model_name == 'notebook.category':
        categories = NoteCategory.objects.filter(user=user).prefetch_related('note_set')

        if view_type == 'tree' or view_type == 'kanban':
            return [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'description': cat.description or 'Aucune description',
                    'parent': cat.parent.name if cat.parent else 'Racine',
                    'notes_count': cat.note_set.count(),
                    'created_at': cat.created_at.strftime('%d/%m/%Y'),
                    'user': cat.user.username,
                }
                for cat in categories
            ]

    elif model_name == 'notebook.sharednote':
        shared_notes = SharedNote.objects.filter(
            Q(shared_with=user) | Q(note__user=user)
        ).select_related('note', 'shared_with')

        if view_type == 'tree' or view_type == 'kanban':
            return [
                {
                    'id': sn.id,
                    'note_title': sn.note.title,
                    'shared_with': sn.shared_with.username,
                    'shared_at': sn.shared_at.strftime('%d/%m/%Y'),
                    'can_edit': '✏️ Édition' if sn.can_edit else '👁️ Lecture',
                    'note_owner': sn.note.user.username,
                    'note_type': sn.note.get_note_type_display(),
                    'note_language': sn.note.language or 'Non spécifiée',
                    'note_content': sn.note.content[:50] + '...' if len(sn.note.content) > 50 else sn.note.content,
                }
                for sn in shared_notes
            ]

    return []


def generate_interactive_html(view_id, view_data, data, user, csrf_token):
    """Génère le HTML interactif avec navigation et actions"""
    model_name = view_data.get('model', '')
    view_type = view_data.get('arch', {}).get('type', 'unknown')

    # Navigation entre les vues
    navigation_html = generate_navigation_html(model_name)

    # Contenu principal selon le type
    if view_type == 'tree':
        content_html = generate_table_with_actions(view_id, data, model_name)
    elif view_type == 'kanban':
        content_html = generate_kanban_with_actions(view_id, data, model_name)
    elif view_type == 'form':
        content_html = generate_form_with_actions(view_id, data, model_name)
    elif view_type == 'search':
        content_html = generate_search_with_results(view_id, data, model_name)
    else:
        content_html = f"<p>Type de vue '{view_type}' non encore supporté en mode interactif</p>"

    # Actions globales
    actions_html = generate_global_actions(model_name, user)

    # HTML complet avec navbar app header
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vue Interactive: {view_id}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
        <link href="/static/notebook/css/xml_interactive.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body>
        <!-- App Header avec Navigation -->
        <header class="notebook-fixed-header" id="mainHeader">
            <nav class="navbar navbar-expand-lg">
                <div class="container-fluid">
                    <!-- Brand -->
                    <a class="navbar-brand app-brand-icon" href="/dashboard/" aria-label="Return to dashboard">
                        <span class="app-brand-gradient">📓 Notebook XML</span>
                    </a>

                    <div class="ms-auto d-flex align-items-center gap-2 ps-3 pe-2">
                        <!-- Navigation items -->
                        <div class="d-flex align-items-center gap-2">
                            <a href="/dashboard/"
                               class="btn btn-outline-secondary btn-sm header-btn d-flex justify-content-center align-items-center"
                               aria-label="Go to dashboard">
                                <i class="bi bi-house" style="font-size: 18px;"></i>
                            </a>

                            <a href="/app-store/"
                               class="btn btn-outline-secondary btn-sm header-btn d-flex justify-content-center align-items-center"
                               aria-label="Browse app store">
                                <i class="bi bi-shop" style="font-size: 18px;"></i>
                            </a>
                        </div>

                        <!-- User Menu -->
                        <div class="dropdown">
                            <button class="btn btn-outline-secondary dropdown-toggle btn-sm header-btn"
                                    type="button"
                                    data-bs-toggle="dropdown"
                                    aria-expanded="false"
                                    aria-label="User menu">
                                <i class="bi bi-person-circle me-1"></i>
                                <span class="d-inline">{user.username}</span>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li>
                                    <a class="dropdown-item" href="/settings/">
                                        <i class="bi bi-gear me-2"></i>
                                        Paramètres
                                    </a>
                                </li>
                                <li><hr class="dropdown-divider"></li>
                                <li>
                                    <a class="dropdown-item text-danger" href="/en/auth/logout/">
                                        <i class="bi bi-box-arrow-right me-2"></i>
                                        Déconnexion
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </nav>
        </header>

        <!-- Page Content avec Sidebar -->
        <div class="container-fluid h-100">
            <div class="row h-100">
                <!-- Sidebar gauche -->
                <div class="col-md-3 sidebar">
                    <div class="sidebar-content">
                        <div class="page-header-sidebar">
                            <h5>🔍 Vue: {view_id}</h5>
                            <small class="text-muted">{model_name} | {view_type}</small>
                        </div>

                        {navigation_html}
                        {actions_html}

                        <!-- Note Editor Form -->
                        <div class="note-editor mt-4">
                            <h6>✏️ Éditeur de Notes</h6>
                            <form id="noteForm" class="mt-3">
                                <input type="hidden" id="noteId" value="">
                                <div class="mb-3">
                                    <label for="noteTitle" class="form-label">Titre</label>
                                    <input type="text" class="form-control form-control-sm" id="noteTitle" placeholder="Titre de la note">
                                </div>
                                <div class="mb-3">
                                    <label for="noteContent" class="form-label">Contenu</label>
                                    <textarea class="form-control form-control-sm" id="noteContent" rows="4" placeholder="Contenu de la note"></textarea>
                                </div>
                                <div class="row">
                                    <div class="col-6">
                                        <label for="noteLanguage" class="form-label">Langue</label>
                                        <select class="form-select form-select-sm" id="noteLanguage">
                                            <option value="">Choisir...</option>
                                            <option value="FR">Français</option>
                                            <option value="EN">Anglais</option>
                                            <option value="ES">Espagnol</option>
                                            <option value="DE">Allemand</option>
                                        </select>
                                    </div>
                                    <div class="col-6">
                                        <label for="notePriority" class="form-label">Priorité</label>
                                        <select class="form-select form-select-sm" id="notePriority">
                                            <option value="LOW">Basse</option>
                                            <option value="MEDIUM" selected>Moyenne</option>
                                            <option value="HIGH">Haute</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="mt-3 d-grid gap-2">
                                    <button type="button" class="btn btn-primary btn-sm" onclick="saveNote()">
                                        💾 Sauvegarder
                                    </button>
                                    <button type="button" class="btn btn-secondary btn-sm" onclick="clearForm()">
                                        🗑️ Nouveau
                                    </button>
                                </div>
                                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                            </form>
                        </div>
                    </div>
                </div>

                <!-- Zone principale droite -->
                <div class="col-md-9 main-content">
                    <div class="content-area h-100">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h4>📊 {view_type.title()} View</h4>
                            <div class="view-actions">
                                <button class="btn btn-sm btn-outline-primary" onclick="refreshData()">
                                    🔄 Actualiser
                                </button>
                            </div>
                        </div>
                        {content_html}
                    </div>
                </div>
            </div>
        </div>

        <script src="/static/notebook/js/xml_interactive.js"></script>

        <!-- Ajouter le token CSRF -->
        <div style="display: none;">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
        </div>
    </body>
    </html>
    """

    return full_html


def generate_navigation_html(model_name):
    """Génère la navigation entre les vues avec navbar interne"""
    views = xml_parser.get_views_by_model(model_name)

    # Navbar spécialisée pour le module
    html = """
    <div class='navigation'>
        <nav class="navbar navbar-expand-lg navbar-light bg-white border rounded mb-3">
            <div class="container-fluid">
                <span class="navbar-brand mb-0 h1">
                    <i class="bi bi-journal-text text-primary"></i>
                    Vues Notebook
                </span>

                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#notebookNav">
                    <span class="navbar-toggler-icon"></span>
                </button>

                <div class="collapse navbar-collapse" id="notebookNav">
                    <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                📊 Vues Données
                            </a>
                            <ul class="dropdown-menu">
    """

    # Ajouter les vues dans le dropdown
    for view_id, view_data in views.items():
        view_type = view_data.get('arch', {}).get('type', 'unknown')
        icon = {
            'form': '📝',
            'tree': '📊',
            'kanban': '🎨',
            'search': '🔍',
            'calendar': '📅',
            'graph': '📈'
        }.get(view_type, '⚙️')

        view_type_display = view_type.title() if view_type else 'Unknown'
        # Utiliser les URLs courtes pour les vues principales
        short_urls = {
            'vocabulary_kanban_view': '/api/v1/notebook/kanban/',
            'note_tree_view': '/api/v1/notebook/table/',
            'note_form_view': '/api/v1/notebook/form/',
            'note_search_advanced_view': '/api/v1/notebook/search/'
        }
        url = short_urls.get(view_id, f"/api/v1/notebook/views/{view_id}/")

        html += f"""
                                <li><a class="dropdown-item" href="{url}">
                                    {icon} {view_type_display}
                                </a></li>
        """

    # Fermer le dropdown et ajouter actions rapides
    html += """
                            </ul>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/notebook/">
                                <i class="bi bi-house"></i> Accueil Notebook
                            </a>
                        </li>
                    </ul>

                    <div class="d-flex">
                        <a href="/api/v1/notebook/xml/" class="btn btn-outline-secondary btn-sm me-2">
                            ⚙️ Index XML
                        </a>
                        <a href="/notebook/" class="btn btn-primary btn-sm">
                            📝 Nouvelle Note
                        </a>
                    </div>
                </div>
            </div>
        </nav>
    </div>
    """

    return html


def generate_global_actions(model_name, user):
    """Génère les actions globales"""
    html = "<div class='actions-bar'><h5>⚡ Actions</h5><div class='btn-group'>"

    if model_name == 'notebook.note':
        note_count = Note.objects.filter(user=user).count()
        archived_count = Note.objects.filter(user=user, is_archived=True).count()
        pinned_count = Note.objects.filter(user=user, is_pinned=True).count()

        html += f"""
        <button class="btn btn-success" onclick="alert('Créer une nouvelle note')">
            ➕ Nouvelle Note
        </button>
        <button class="btn btn-info" onclick="alert('Export XML')">
            📤 Exporter
        </button>
        <button class="btn btn-warning" onclick="alert('Import de données')">
            📥 Importer
        </button>
        """

        # Statistiques
        html += f"""
        </div>
        <div class='stats-cards mt-3'>
            <div class='stat-card'>
                <h6>Total</h6>
                <h4>{note_count}</h4>
            </div>
            <div class='stat-card'>
                <h6>Épinglées</h6>
                <h4>{pinned_count}</h4>
            </div>
            <div class='stat-card'>
                <h6>Archivées</h6>
                <h4>{archived_count}</h4>
            </div>
        """

    html += "</div></div>"
    return html


def generate_table_with_actions(view_id, data, model_name):
    """Génère un tableau avec actions pour chaque ligne"""
    if not data:
        return "<p class='text-center text-muted'>Aucune donnée trouvée</p>"

    fields = xml_parser.generate_django_form_fields(view_id)

    html = f"<div class='table-actions'><h5>📊 Vue Tableau ({len(data)} éléments)</h5></div>"
    html += "<div class='table-responsive'><table class='table table-hover'><thead class='table-dark'><tr>"

    # Headers
    for field in fields[:6]:  # Limiter le nombre de colonnes
        html += f"<th>{field.replace('_', ' ').title()}</th>"
    html += "<th>Actions</th></tr></thead><tbody>"

    # Données
    for item in data:
        html += "<tr>"
        for field in fields[:6]:
            value = str(item.get(field, '-'))[:50]
            if len(str(item.get(field, ''))) > 50:
                value += '...'
            html += f"<td>{value}</td>"

        # Actions
        item_id = item.get('id', 'unknown')
        html += f"""
        <td>
            <div class='btn-group btn-group-sm'>
                <button class='btn btn-primary btn-sm' onclick="editItem('{item_id}', 'note')" title="Éditer">
                    ✏️
                </button>
                <button class='btn btn-secondary btn-sm' onclick="duplicateItem('{item_id}', 'note')" title="Dupliquer">
                    📋
                </button>
                <button class='btn btn-info btn-sm' onclick="shareItem('{item_id}')" title="Partager">
                    👥
                </button>
                <button class='btn btn-danger btn-sm' onclick="deleteItem('{item_id}', 'note')" title="Supprimer">
                    🗑️
                </button>
            </div>
        </td>
        """
        html += "</tr>"

    html += "</tbody></table></div>"
    return html


def generate_kanban_with_actions(view_id, data, model_name):
    """Génère des cartes kanban avec actions"""
    if not data:
        return "<p class='text-center text-muted'>Aucune donnée trouvée</p>"

    html = f"<div class='table-actions'><h5>🎨 Vue Kanban ({len(data)} éléments)</h5></div>"
    html += "<div class='kanban-grid'>"

    for item in data:
        priority_class = {
            'Haute': 'border-danger',
            'Moyenne': 'border-warning',
            'Basse': 'border-success'
        }.get(item.get('priority', ''), 'border-secondary')

        item_id = item.get('id', 'unknown')
        title = item.get('title', item.get('name', 'Sans titre'))

        html += f"""
        <div class='kanban-card {priority_class}' data-note-id='{item_id}' onclick="editItem('{item_id}', 'note')">
            <div class='d-flex justify-content-between align-items-start mb-2'>
                <h6 class='card-title mb-0'>{item.get('is_pinned', '')}{title}</h6>
                <div class='btn-group btn-group-sm'>
                    <button class='btn btn-outline-primary btn-sm' onclick="editItem('{item_id}', 'note')" title="Éditer">
                        ✏️
                    </button>
                    <button class='btn btn-outline-secondary btn-sm' onclick="duplicateItem('{item_id}', 'note')" title="Dupliquer">
                        📋
                    </button>
                </div>
            </div>
        """

        # Contenu de la carte
        for key, value in item.items():
            if key not in ['id', 'title', 'name', 'is_pinned'] and value and value != '-':
                display_key = key.replace('_', ' ').title()
                html += f"<small class='text-muted'><strong>{display_key}:</strong> {value}</small><br>"

        html += f"""
            <div class='mt-2'>
                <button class='btn btn-sm btn-outline-info' onclick="shareItem('{item_id}')" title="Partager">
                    👥 Partager
                </button>
                {f'<button class="btn btn-sm btn-outline-success" onclick="markReviewed(\'{item_id}\')" title="Marquer révisé">🔄 Réviser</button>' if 'review_count' in item else ''}
            </div>
        </div>
        """

    html += "</div>"
    return html


def generate_form_with_actions(view_id, data, model_name):
    """Génère un formulaire avec actions"""
    fields = xml_parser.generate_django_form_fields(view_id)

    html = "<div class='table-actions'><h5>📝 Vue Formulaire</h5></div>"
    html += "<form class='row g-3'>"

    for field in fields:
        value = data.get(field, '') if data else ''
        field_label = field.replace('_', ' ').title()

        html += f"""
        <div class='col-md-6'>
            <label for='{field}' class='form-label'>{field_label}</label>
            <input type='text' class='form-control' id='{field}' name='{field}' value='{value}'>
        </div>
        """

    html += """
    <div class='col-12'>
        <div class='btn-group'>
            <button type='button' class='btn btn-primary' onclick="alert('Sauvegarder les modifications')">
                💾 Sauvegarder
            </button>
            <button type='button' class='btn btn-secondary' onclick="alert('Annuler les modifications')">
                ❌ Annuler
            </button>
            <button type='button' class='btn btn-info' onclick="alert('Créer une copie')">
                📋 Dupliquer
            </button>
        </div>
    </div>
    </form>
    """

    return html


def generate_search_with_results(view_id, data, model_name):
    """Génère une interface de recherche avec résultats"""
    fields = xml_parser.generate_django_form_fields(view_id)

    html = "<div class='table-actions'><h5>🔍 Interface de Recherche</h5></div>"

    # Formulaire de recherche
    html += """
    <div class='row mb-4'>
        <div class='col-md-8'>
            <div class='input-group'>
                <input type='text' class='form-control' placeholder='Rechercher dans vos notes...' id='searchInput'>
                <button class='btn btn-primary' onclick="alert('Recherche en cours...')">🔍 Rechercher</button>
            </div>
        </div>
        <div class='col-md-4'>
            <select class='form-select' id='filterType'>
                <option value=''>Tous les types</option>
                <option value='VOCABULARY'>Vocabulaire</option>
                <option value='GRAMMAR'>Grammaire</option>
                <option value='EXPRESSION'>Expression</option>
            </select>
        </div>
    </div>
    """

    # Filtres rapides
    html += """
    <div class='mb-3'>
        <h6>Filtres rapides:</h6>
        <div class='btn-group' role='group'>
            <button class='btn btn-outline-primary btn-sm' onclick="alert('Filtrer les notes épinglées')">📌 Épinglées</button>
            <button class='btn btn-outline-warning btn-sm' onclick="alert('Filtrer les notes à réviser')">🔄 À réviser</button>
            <button class='btn btn-outline-success btn-sm' onclick="alert('Filtrer par langue')">🌍 Par langue</button>
            <button class='btn btn-outline-info btn-sm' onclick="alert('Filtrer par priorité')">⭐ Priorité haute</button>
        </div>
    </div>
    """

    # Résultats simulés
    if data:
        html += f"<h6>Résultats ({len(data)} trouvés):</h6>"
        html += generate_table_with_actions(view_id, data[:5], model_name)  # Afficher les 5 premiers résultats

    return html


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_note_api(request, note_id):
    """API endpoint pour mettre à jour une note via AJAX"""
    try:
        note = get_object_or_404(Note, id=note_id, user=request.user)

        # Mettre à jour les champs fournis
        update_data = {}
        allowed_fields = ['title', 'content', 'note_type', 'language', 'difficulty', 'priority', 'is_pinned', 'is_archived']

        for field in allowed_fields:
            if field in request.data:
                if field in ['is_pinned', 'is_archived']:
                    # Convertir les booléens
                    update_data[field] = str(request.data[field]).lower() in ['true', '1', 'yes', 'oui']
                else:
                    update_data[field] = request.data[field]

        # Gestion spéciale pour la catégorie
        if 'category' in request.data and request.data['category']:
            try:
                category = NoteCategory.objects.get(
                    name=request.data['category'],
                    user=request.user
                )
                update_data['category'] = category
            except NoteCategory.DoesNotExist:
                # Créer la catégorie si elle n'existe pas
                category = NoteCategory.objects.create(
                    name=request.data['category'],
                    user=request.user
                )
                update_data['category'] = category

        # Appliquer les mises à jour
        for field, value in update_data.items():
            setattr(note, field, value)

        note.save()

        return Response({
            'success': True,
            'message': f'Note "{note.title}" mise à jour avec succès',
            'updated_fields': list(update_data.keys())
        })

    except Exception as e:
        return Response({
            'error': f'Erreur lors de la mise à jour: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_note_api(request, note_id):
    """API endpoint pour supprimer une note via AJAX"""
    try:
        note = get_object_or_404(Note, id=note_id, user=request.user)
        note_title = note.title
        note.delete()

        return Response({
            'success': True,
            'message': f'Note "{note_title}" supprimée avec succès'
        })

    except Exception as e:
        return Response({
            'error': f'Erreur lors de la suppression: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def duplicate_note_api(request, note_id):
    """API endpoint pour dupliquer une note via AJAX"""
    try:
        original_note = get_object_or_404(Note, id=note_id, user=request.user)

        # Créer une copie de la note
        new_note = Note.objects.create(
            title=f"{original_note.title} (Copie)",
            content=original_note.content,
            user=request.user,
            category=original_note.category,
            note_type=original_note.note_type,
            language=original_note.language,
            difficulty=original_note.difficulty,
            priority=original_note.priority,
            is_pinned=False,  # Les copies ne sont pas épinglées par défaut
            is_archived=False  # Les copies ne sont pas archivées par défaut
        )

        return Response({
            'success': True,
            'message': f'Note "{original_note.title}" dupliquée avec succès',
            'new_note_id': new_note.id,
            'new_note_title': new_note.title
        })

    except Exception as e:
        return Response({
            'error': f'Erreur lors de la duplication: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)