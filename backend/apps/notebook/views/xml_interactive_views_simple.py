# -*- coding: utf-8 -*-
"""
Vues interactives XML avec données réelles et navigation
Version simplifiée utilisant les templates Django
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import Note, NoteCategory, SharedNote
from ..utils.xml_parser import get_xml_view_data, render_xml_sidebar, reload_xml_parser


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

    # Générer le contenu HTML pour la vue
    if view_type == 'tree':
        content_html = generate_table_view(real_data, model_name)
    elif view_type == 'kanban':
        content_html = generate_kanban_view(real_data, model_name)
    elif view_type == 'form':
        content_html = generate_form_view(real_data, model_name)
    elif view_type == 'search':
        content_html = generate_search_view(real_data, model_name)
    else:
        content_html = f"<p>Type de vue '{view_type}' non encore supporté en mode interactif</p>"

    # Statistiques pour le notebook
    stats = {
        'total': Note.objects.filter(user=request.user).count(),
        'pinned': Note.objects.filter(user=request.user, is_pinned=True).count(),
        'archived': Note.objects.filter(user=request.user, is_archived=True).count()
    }

    # Recharger le parser XML pour détecter les nouveaux fichiers
    reload_xml_parser()

    # Générer la sidebar depuis XML
    sidebar_context = {
        'view_id': view_id,
        'model_name': model_name,
        'view_type': view_type,
        'stats': stats
    }
    sidebar_html = render_xml_sidebar(sidebar_context)

    # Passer les données au contexte du template
    context = {
        'view_id': view_id,
        'view_data': view_data,
        'model_name': model_name,
        'view_type': view_type,
        'content_html': content_html,
        'sidebar_html': sidebar_html,
        'stats': stats,
        'current_app': {
            'name': 'notebook',
            'display_name': 'Notes',
            'static_icon': '/static/notebook/icon.png',
            'code': 'notes'
        }
    }

    return render(request, 'notebook/base.html', context)


def get_real_data_for_model(user, model_name, view_type):
    """Récupère les vraies données selon le modèle"""
    if model_name == 'notebook.note':
        notes = Note.objects.filter(user=user).select_related('category').order_by('-updated_at')[:20]

        if view_type in ['tree', 'kanban']:
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
            }

    elif model_name == 'notebook.category':
        categories = NoteCategory.objects.filter(user=user).prefetch_related('note_set')
        return [
            {
                'id': cat.id,
                'name': cat.name,
                'description': cat.description or 'Aucune description',
                'note_count': cat.note_set.count(),
            }
            for cat in categories
        ]

    return []


def generate_kanban_view(data, model_name):
    """Génère des cartes kanban"""
    if not data:
        return "<p class='text-center text-muted'>Aucune donnée trouvée</p>"

    html = f"<h5>🎨 Vue Kanban ({len(data)} éléments)</h5>"
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
                    <button class='btn btn-outline-primary btn-sm' onclick="event.stopPropagation(); editItem('{item_id}', 'note')" title="Éditer">
                        ✏️
                    </button>
                    <button class='btn btn-outline-danger btn-sm' onclick="event.stopPropagation(); deleteItem('{item_id}', 'note')" title="Supprimer">
                        🗑️
                    </button>
                </div>
            </div>
        """

        # Contenu de la carte
        for key, value in item.items():
            if key not in ['id', 'title', 'name', 'is_pinned'] and value and value != '-':
                display_key = key.replace('_', ' ').title()
                html += f"<small class='text-muted'><strong>{display_key}:</strong> {value}</small><br>"

        html += "</div>"

    html += "</div>"
    return html


def generate_table_view(data, model_name):
    """Génère un tableau avec actions"""
    if not data:
        return "<p class='text-center text-muted'>Aucune donnée trouvée</p>"

    html = f"<h5>📊 Vue Tableau ({len(data)} éléments)</h5>"
    html += "<div class='table-responsive'>"
    html += "<table class='table table-hover'>"
    html += "<thead><tr>"

    # En-têtes
    if data:
        for key in data[0].keys():
            if key != 'id':
                display_key = key.replace('_', ' ').title()
                html += f"<th>{display_key}</th>"
        html += "<th>Actions</th>"
    html += "</tr></thead><tbody>"

    # Données
    for item in data:
        item_id = item.get('id', 'unknown')
        html += "<tr>"
        for key, value in item.items():
            if key != 'id':
                html += f"<td>{value}</td>"
        html += f"""
        <td>
            <div class='btn-group btn-group-sm'>
                <button class='btn btn-outline-primary' onclick="editItem('{item_id}', 'note')" title="Éditer">✏️</button>
                <button class='btn btn-outline-danger' onclick="deleteItem('{item_id}', 'note')" title="Supprimer">🗑️</button>
            </div>
        </td>
        """
        html += "</tr>"

    html += "</tbody></table></div>"
    return html


def generate_form_view(data, model_name):
    """Génère un formulaire"""
    html = "<h5>📝 Vue Formulaire</h5>"
    html += "<form class='row g-3'>"

    if isinstance(data, dict):
        for field, value in data.items():
            if field != 'id':
                field_label = field.replace('_', ' ').title()
                html += f"""
                <div class='col-md-6'>
                    <label for='{field}' class='form-label'>{field_label}</label>
                    <input type='text' class='form-control' id='{field}' name='{field}' value='{value}' readonly>
                </div>
                """
    else:
        html += "<p class='text-muted'>Sélectionnez une note pour voir ses détails</p>"

    html += "</form>"
    return html


def generate_search_view(data, model_name):
    """Génère une interface de recherche"""
    html = "<h5>🔍 Interface de Recherche</h5>"
    html += """
    <div class='row mb-4'>
        <div class='col-md-8'>
            <div class='input-group'>
                <input type='text' class='form-control' placeholder='Rechercher dans vos notes...' id='searchInput'>
                <button class='btn btn-primary'>🔍 Rechercher</button>
            </div>
        </div>
    </div>
    """

    if data:
        html += f"<h6>Résultats ({len(data)} trouvés):</h6>"
        html += generate_table_view(data[:5], model_name)

    return html


# === API ENDPOINTS ===

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_note_api(request, note_id):
    """API endpoint pour mettre à jour une note"""
    try:
        note = get_object_or_404(Note, id=note_id, user=request.user)

        # Mettre à jour les champs fournis
        for field in ['title', 'content', 'language', 'priority', 'is_pinned', 'is_archived']:
            if field in request.data:
                setattr(note, field, request.data[field])

        note.save()

        return Response({
            'success': True,
            'message': f'Note "{note.title}" mise à jour avec succès'
        })

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_note_api(request, note_id):
    """API endpoint pour supprimer une note"""
    try:
        note = get_object_or_404(Note, id=note_id, user=request.user)
        title = note.title
        note.delete()

        return Response({
            'success': True,
            'message': f'Note "{title}" supprimée avec succès'
        })

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def duplicate_note_api(request, note_id):
    """API endpoint pour dupliquer une note"""
    try:
        original_note = get_object_or_404(Note, id=note_id, user=request.user)

        # Créer une copie
        new_note = Note.objects.create(
            user=request.user,
            title=f"{original_note.title} (Copie)",
            content=original_note.content,
            note_type=original_note.note_type,
            language=original_note.language,
            difficulty=original_note.difficulty,
            priority=original_note.priority,
            category=original_note.category,
            is_pinned=False,
            is_archived=False
        )

        return Response({
            'success': True,
            'message': f'Note dupliquée avec succès',
            'new_note_id': new_note.id
        })

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)