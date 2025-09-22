# -*- coding: utf-8 -*-
"""
XML Template Views for Notebook App
Utilise les templates XML pour générer des vues dynamiques
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_exempt
import json

from ..models import Note, NoteCategory
from ..utils.xml_parser import xml_parser, render_xml_view_as_html, get_xml_view_data, reload_xml_parser


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_xml_views(request):
    """Liste toutes les vues XML disponibles"""
    views = xml_parser.get_all_views()

    # Formater les données pour l'API
    formatted_views = {}
    for view_id, view_data in views.items():
        formatted_views[view_id] = {
            'id': view_id,
            'name': view_data.get('name', 'Vue sans nom'),
            'model': view_data.get('model', 'Modèle non spécifié'),
            'type': view_data.get('arch', {}).get('type', 'unknown'),
            'fields': xml_parser.generate_django_form_fields(view_id)
        }

    return Response({
        'views': formatted_views,
        'count': len(formatted_views)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_xml_view(request, view_id):
    """Récupère une vue XML spécifique"""
    view_data = get_xml_view_data(view_id)

    if not view_data:
        return Response(
            {'error': f'Vue {view_id} non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({
        'view_id': view_id,
        'data': view_data,
        'fields': xml_parser.generate_django_form_fields(view_id)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def render_xml_view_html(request, view_id):
    """Rend une vue XML en HTML"""
    view_data = get_xml_view_data(view_id)

    if not view_data:
        return HttpResponse(
            f'<p>Vue {view_id} non trouvée</p>',
            content_type='text/html',
            status=404
        )

    # Récupérer les données selon le modèle de la vue
    model_name = view_data.get('model', '')
    data = None

    if model_name == 'notebook.note':
        # Récupérer les notes de l'utilisateur
        notes = Note.objects.filter(user=request.user)[:10]  # Limiter à 10 pour l'exemple

        view_type = view_data.get('arch', {}).get('type', 'unknown')
        if view_type == 'tree':
            # Pour une vue liste, convertir en liste de dictionnaires
            data = []
            for note in notes:
                data.append({
                    'title': note.title,
                    'note_type': note.get_note_type_display(),
                    'language': note.language or '-',
                    'created_at': note.created_at.strftime('%Y-%m-%d %H:%M') if note.created_at else '-'
                })
        elif view_type == 'form' and notes.exists():
            # Pour une vue formulaire, utiliser la première note
            note = notes.first()
            data = {
                'title': note.title,
                'content': note.content,
                'category': note.category.name if note.category else '',
                'note_type': note.get_note_type_display(),
                'language': note.language or '',
                'difficulty': note.get_difficulty_display() if note.difficulty else '',
                'priority': note.get_priority_display(),
                'is_pinned': 'Oui' if note.is_pinned else 'Non',
                'is_archived': 'Oui' if note.is_archived else 'Non',
            }

    # Générer le HTML
    html_content = render_xml_view_as_html(view_id, data)

    # Ajouter des styles CSS complets pour tous les types de vues
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vue XML: {view_id}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}

            /* Styles pour les formulaires */
            .xml-generated-form {{ max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; font-weight: bold; margin-bottom: 5px; color: #333; }}
            .form-control {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}

            /* Styles pour les tableaux */
            .xml-generated-table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .xml-generated-table th, .xml-generated-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            .xml-generated-table th {{ background-color: #f8f9fa; font-weight: bold; }}
            .xml-generated-table tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .xml-generated-table tr:hover {{ background-color: #e9ecef; }}

            /* Styles pour le kanban */
            .xml-generated-kanban {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .kanban-board {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
            .kanban-card {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s; }}
            .kanban-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
            .kanban-card-title {{ font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; }}
            .kanban-card-content {{ color: #666; }}
            .kanban-field {{ margin-bottom: 8px; font-size: 14px; }}
            .kanban-empty {{ text-align: center; color: #999; padding: 40px; }}

            /* Styles pour la recherche */
            .xml-generated-search {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .search-form {{ margin-bottom: 20px; }}
            .search-fields {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
            .search-field label {{ margin-bottom: 5px; font-weight: bold; }}
            .search-actions {{ text-align: center; margin-bottom: 20px; }}
            .btn {{ padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 0 5px; }}
            .btn-primary {{ background-color: #007bff; color: white; }}
            .btn-secondary {{ background-color: #6c757d; color: white; }}
            .btn-outline-primary {{ background-color: transparent; color: #007bff; border: 1px solid #007bff; }}
            .btn-sm {{ padding: 4px 8px; font-size: 12px; }}
            .filter-buttons {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }}

            /* Styles pour le calendrier */
            .xml-generated-calendar {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .calendar-events {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
            .calendar-event {{ padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; }}
            .event-high {{ border-left-color: #dc3545; background-color: #f8d7da; }}
            .event-medium {{ border-left-color: #ffc107; background-color: #fff3cd; }}
            .event-low {{ border-left-color: #28a745; background-color: #d4edda; }}
            .event-title {{ font-weight: bold; margin-bottom: 5px; }}
            .event-date {{ color: #666; font-size: 14px; }}
            .event-priority {{ color: #888; font-size: 12px; }}

            /* Styles pour les graphiques */
            .xml-generated-graph {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}

            /* Styles pour le dashboard */
            .xml-generated-dashboard {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .dashboard-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #e9ecef; }}
            .stat-number {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #666; margin-top: 5px; }}
            .chart-container {{ margin-top: 20px; }}

            /* Header styles */
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; }}
            .header p {{ margin: 5px 0 0; opacity: 0.9; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Vue XML: {view_id}</h1>
            <p><strong>Modèle:</strong> {view_data.get('model', 'Non spécifié')} | <strong>Type:</strong> {view_data.get('arch', {}).get('type', 'unknown')} | <strong>Source:</strong> {view_data.get('source_file', 'unknown')}</p>
        </div>
        {html_content}
    </body>
    </html>
    """

    return HttpResponse(full_html, content_type='text/html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_from_xml_view(request, view_id):
    """Crée un objet à partir d'une vue XML formulaire"""
    view_data = get_xml_view_data(view_id)

    if not view_data:
        return Response(
            {'error': f'Vue {view_id} non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )

    view_type = view_data.get('arch', {}).get('type')
    if view_type != 'form':
        return Response(
            {'error': 'Cette vue n\'est pas un formulaire'},
            status=status.HTTP_400_BAD_REQUEST
        )

    model_name = view_data.get('model', '')

    if model_name == 'notebook.note':
        # Créer une nouvelle note
        try:
            # Récupérer les champs du formulaire XML
            fields = xml_parser.generate_django_form_fields(view_id)
            note_data = {}

            for field in fields:
                if field in request.data:
                    note_data[field] = request.data[field]

            # Ajouter l'utilisateur
            note_data['user'] = request.user

            # Traitement spécial pour certains champs
            if 'category' in note_data and note_data['category']:
                try:
                    category = NoteCategory.objects.get(
                        name=note_data['category'],
                        user=request.user
                    )
                    note_data['category'] = category
                except NoteCategory.DoesNotExist:
                    # Créer la catégorie si elle n'existe pas
                    category = NoteCategory.objects.create(
                        name=note_data['category'],
                        user=request.user
                    )
                    note_data['category'] = category

            # Convertir les booléens
            for bool_field in ['is_pinned', 'is_archived']:
                if bool_field in note_data:
                    note_data[bool_field] = note_data[bool_field].lower() in ['true', 'oui', '1', 'yes']

            # Créer la note
            note = Note.objects.create(**note_data)

            return Response({
                'success': True,
                'message': 'Note créée avec succès',
                'note_id': note.id,
                'created_fields': list(note_data.keys())
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': f'Erreur lors de la création: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(
            {'error': f'Modèle {model_name} non supporté'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def xml_view_fields(request, view_id):
    """Récupère la liste des champs d'une vue XML"""
    view_data = get_xml_view_data(view_id)

    if not view_data:
        return Response(
            {'error': f'Vue {view_id} non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )

    fields = xml_parser.generate_django_form_fields(view_id)

    return Response({
        'view_id': view_id,
        'fields': fields,
        'count': len(fields)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reload_xml_templates(request):
    """Recharge les templates XML (utile pour le développement)"""
    try:
        # Recharger le parser
        new_parser = reload_xml_parser()

        stats = new_parser.get_statistics()

        return Response({
            'success': True,
            'message': 'Templates XML rechargés avec succès',
            'statistics': stats
        })
    except Exception as e:
        return Response({
            'error': f'Erreur lors du rechargement: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@xframe_options_exempt
def xml_demo_page(request):
    """Page de démonstration des vues XML"""
    return render(request, 'notebook/xml_demo.html')


@xframe_options_exempt
def xml_index_page(request):
    """Page d'accueil XML avec toutes les options"""
    return render(request, 'notebook/xml_index.html')