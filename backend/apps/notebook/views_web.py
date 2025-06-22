# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
"""
Vues Django pour l'interface web du Notebook
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Note
import json

@method_decorator(login_required, name='dispatch')
class NotebookMainView(TemplateView):
    """
    Vue principale pour l'interface notebook
    """
    template_name = 'notebook/main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajouter les informations de l'app courante pour l'icône du header
        current_app_info = {
            'name': 'notebook',
            'display_name': 'Notes',
            'static_icon': '/app-icons/notebook/icon.png',
            'route_path': '/notebook/'
        }
        
        context.update({
            'page_title': 'Notebook',
            'debug': self.request.GET.get('debug', 'false').lower() == 'true',
            'current_app': current_app_info,
        })
        return context

def notebook_app(request):
    """
    Vue principale pour charger l'application Notebook (legacy)
    """
    context = {
        'debug': request.GET.get('debug', 'false').lower() == 'true',
    }
    return render(request, 'notebook/main.html', context)


@require_http_methods(["GET"])
def get_app_config(request):
    """
    Retourne la configuration de l'application pour le frontend
    """
    config = {
        'features': {
            'sharing': True,
            'tags': True,
            'search': True,
            'export': True,
        },
        'limits': {
            'max_note_size': 1024 * 1024,  # 1MB
            'max_notes': 1000,
        },
        'user_preferences': {
            'theme': request.user.theme if hasattr(request.user, 'theme') else 'light',
            'language': request.user.language if hasattr(request.user, 'language') else 'fr',
        }
    }
    return JsonResponse(config)


# === VUES AJAX POUR LES NOTES ===

@login_required
@require_http_methods(["GET"])
def get_notes(request):
    """
    Récupérer les notes avec filtrage et pagination
    """
    # Paramètres de filtrage
    search = request.GET.get('search', '')
    language = request.GET.get('language', '')
    archive_status = request.GET.get('archive_status', 'active')
    sort = request.GET.get('sort', 'updated_desc')
    page = int(request.GET.get('page', 1))
    
    # Query de base
    queryset = Note.objects.filter(user=request.user)
    
    # Filtrage par statut d'archivage
    if archive_status == 'archived':
        queryset = queryset.filter(is_archived=True)
    elif archive_status == 'active':
        queryset = queryset.filter(is_archived=False)
    # Si "all", pas de filtre
    
    # Filtrage par recherche
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )
    
    # Filtrage par langue
    if language:
        queryset = queryset.filter(language=language)
    
    # Tri
    if sort == 'updated_desc':
        queryset = queryset.order_by('-is_pinned', '-updated_at')
    elif sort == 'updated_asc':
        queryset = queryset.order_by('-is_pinned', 'updated_at')
    elif sort == 'title_asc':
        queryset = queryset.order_by('-is_pinned', 'title')
    elif sort == 'title_desc':
        queryset = queryset.order_by('-is_pinned', '-title')
    else:
        queryset = queryset.order_by('-is_pinned', '-updated_at')
    
    # Pagination
    paginator = Paginator(queryset, 50)
    page_obj = paginator.get_page(page)
    
    # Sérialisation simple des notes
    notes_data = []
    for note in page_obj:
        notes_data.append({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'language': note.language,
            'translation': note.translation,
            'pronunciation': note.pronunciation,
            'example_sentences': note.example_sentences,
            'related_words': note.related_words,
            'difficulty': note.difficulty,
            'note_type': note.note_type,
            'priority': note.priority,
            'is_pinned': note.is_pinned,
            'is_archived': note.is_archived,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'review_count': note.review_count,
        })
    
    return JsonResponse({
        'results': notes_data,
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    })


@login_required
@require_http_methods(["GET"])
def get_csrf_token(request):
    """
    Récupérer le token CSRF
    """
    return JsonResponse({'csrf_token': get_token(request)})


@login_required
@require_http_methods(["POST"])
def create_note(request):
    """
    Créer une nouvelle note
    """
    try:
        data = json.loads(request.body)
        
        note = Note.objects.create(
            user=request.user,
            title=data.get('title', 'Nouvelle note'),
            content=data.get('content', ''),
            language=data.get('language', ''),
            translation=data.get('translation', ''),
            pronunciation=data.get('pronunciation', ''),
            example_sentences=data.get('example_sentences', []),
            related_words=data.get('related_words', []),
            difficulty=data.get('difficulty', ''),
            note_type=data.get('note_type', 'NOTE'),
            priority=data.get('priority', 'MEDIUM'),
            is_pinned=data.get('is_pinned', False),
            is_archived=data.get('is_archived', False),
        )
        
        return JsonResponse({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'language': note.language,
            'translation': note.translation,
            'pronunciation': note.pronunciation,
            'example_sentences': note.example_sentences,
            'related_words': note.related_words,
            'difficulty': note.difficulty,
            'note_type': note.note_type,
            'priority': note.priority,
            'is_pinned': note.is_pinned,
            'is_archived': note.is_archived,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'review_count': note.review_count,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def update_note(request, note_id):
    """
    Mettre à jour une note
    """
    try:
        note = get_object_or_404(Note, id=note_id, user=request.user)
        data = json.loads(request.body)
        
        # Mettre à jour les champs
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        note.language = data.get('language', note.language)
        note.translation = data.get('translation', note.translation)
        note.pronunciation = data.get('pronunciation', note.pronunciation)
        note.example_sentences = data.get('example_sentences', note.example_sentences)
        note.related_words = data.get('related_words', note.related_words)
        note.difficulty = data.get('difficulty', note.difficulty)
        note.note_type = data.get('note_type', note.note_type)
        note.priority = data.get('priority', note.priority)
        note.is_pinned = data.get('is_pinned', note.is_pinned)
        note.is_archived = data.get('is_archived', note.is_archived)
        
        note.save()
        
        return JsonResponse({
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'language': note.language,
            'translation': note.translation,
            'pronunciation': note.pronunciation,
            'example_sentences': note.example_sentences,
            'related_words': note.related_words,
            'difficulty': note.difficulty,
            'note_type': note.note_type,
            'priority': note.priority,
            'is_pinned': note.is_pinned,
            'is_archived': note.is_archived,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'review_count': note.review_count,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_note(request, note_id):
    """
    Supprimer une note
    """
    try:
        note = get_object_or_404(Note, id=note_id, user=request.user)
        note.delete()
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def bulk_delete_notes(request):
    """
    Supprimer plusieurs notes
    """
    try:
        data = json.loads(request.body)
        note_ids = data.get('note_ids', [])
        
        deleted_count = Note.objects.filter(
            id__in=note_ids, 
            user=request.user
        ).delete()[0]
        
        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def bulk_update_notes(request):
    """
    Mettre à jour plusieurs notes (archivage/désarchivage en lot)
    """
    try:
        data = json.loads(request.body)
        note_ids = data.get('note_ids', [])
        updates = data.get('updates', {})
        
        updated_count = Note.objects.filter(
            id__in=note_ids,
            user=request.user
        ).update(**updates)
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)