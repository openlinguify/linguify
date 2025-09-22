# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
"""
URLs pour l'interface web du Notebook
"""

from django.urls import path
from . import views_web

app_name = 'notebook_web'

urlpatterns = [
    # Vue principale de l'application - redirige vers XML kanban
    path('', views_web.redirect_to_xml_view, {'view_id': 'vocabulary_kanban_view'}, name='main'),
    
    # Vue legacy (pour compatibilité)
    path('app/', views_web.notebook_app, name='app'),
    
    # Configuration de l'application
    path('config/', views_web.get_app_config, name='config'),
    
    # === API DJANGO POUR LES NOTES ===
    # Remplace l'API REST Framework
    path('ajax/csrf/', views_web.get_csrf_token, name='ajax_csrf_token'),
    path('ajax/notes/', views_web.get_notes, name='ajax_get_notes'),
    path('ajax/notes/create/', views_web.create_note, name='ajax_create_note'),
    path('ajax/notes/<int:note_id>/update/', views_web.update_note, name='ajax_update_note'),
    path('ajax/notes/<int:note_id>/delete/', views_web.delete_note, name='ajax_delete_note'),
    path('ajax/notes/bulk-delete/', views_web.bulk_delete_notes, name='ajax_bulk_delete'),
    path('ajax/notes/bulk-update/', views_web.bulk_update_notes, name='ajax_bulk_update'),

    # === VUES XML INTERACTIVES (URLs courtes) ===
    path('kanban/', views_web.redirect_to_xml_view, {'view_id': 'vocabulary_kanban_view'}, name='kanban'),
    path('table/', views_web.redirect_to_xml_view, {'view_id': 'note_tree_view'}, name='table'),
    path('form/', views_web.redirect_to_xml_view, {'view_id': 'note_form_view'}, name='form'),
    path('search/', views_web.redirect_to_xml_view, {'view_id': 'note_search_advanced_view'}, name='search'),
]