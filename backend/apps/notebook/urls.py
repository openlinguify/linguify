# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.notebook_views import (
    NoteViewSet,
    NoteCategoryViewSet,
    SharedNoteViewSet,
)
from .views.xml_views import (
    list_xml_views,
    get_xml_view,
    render_xml_view_html,
    create_from_xml_view,
    xml_view_fields,
    reload_xml_templates,
    xml_demo_page,
    xml_index_page,
)
from .views.xml_interactive_views_simple import (
    interactive_xml_view,
    update_note_api,
    delete_note_api,
    duplicate_note_api,
)
from .views.xml_export_views import (
    export_notes_xml,
    export_single_note_xml,
    export_notes_odoo_style,
)
app_name = 'notebook'

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'categories', NoteCategoryViewSet, basename='category')
router.register(r'shared-notes', SharedNoteViewSet, basename='shared-note')

urlpatterns = [
    # API REST endpoints
    path('', include(router.urls)),

    # XML Template endpoints
    path('xml/views/', list_xml_views, name='xml-views-list'),
    path('xml/views/<str:view_id>/', get_xml_view, name='xml-view-detail'),
    path('xml/views/<str:view_id>/html/', render_xml_view_html, name='xml-view-html'),
    path('xml/views/<str:view_id>/interactive/', interactive_xml_view, name='xml-interactive-view'),
    path('xml/views/<str:view_id>/create/', create_from_xml_view, name='xml-view-create'),
    path('xml/views/<str:view_id>/fields/', xml_view_fields, name='xml-view-fields'),
    path('xml/reload/', reload_xml_templates, name='xml-reload'),

    # XML Interactive API endpoints
    path('xml/api/notes/<int:note_id>/update/', update_note_api, name='xml-api-note-update'),
    path('xml/api/notes/<int:note_id>/delete/', delete_note_api, name='xml-api-note-delete'),
    path('xml/api/notes/<int:note_id>/duplicate/', duplicate_note_api, name='xml-api-note-duplicate'),

    # Raccourcis URLs pour les vues interactives
    path('views/<str:view_id>/', interactive_xml_view, name='xml-view-interactive'),
    path('kanban/', interactive_xml_view, {'view_id': 'vocabulary_kanban_view'}, name='notebook-kanban'),
    path('table/', interactive_xml_view, {'view_id': 'note_tree_view'}, name='notebook-table'),
    path('form/', interactive_xml_view, {'view_id': 'note_form_view'}, name='notebook-form'),
    path('search/', interactive_xml_view, {'view_id': 'note_search_advanced_view'}, name='notebook-search'),

    # Pages XML
    path('xml/', xml_index_page, name='xml-index'),
    path('xml/demo/', xml_demo_page, name='xml-demo'),

    # XML Export endpoints
    path('xml/export/', export_notes_xml, name='xml-export-all'),
    path('xml/export/<int:note_id>/', export_single_note_xml, name='xml-export-single'),
    path('xml/export/odoo/', export_notes_odoo_style, name='xml-export-odoo'),
]


# Endpoints disponibles :

# /api/v1/notebook/notes/ - CRUD des notes
# /api/v1/notebook/notes/due_for_review/ - Notes à réviser
# /api/v1/notebook/categories/ - Gestion des catégories
# /api/v1/notebook/shared-notes/ - Gestion des notes partagées
# /api/v1/core/tags/ - Gestion des tags (système global)

# XML Template endpoints:
# /api/v1/notebook/xml/views/ - Liste toutes les vues XML
# /api/v1/notebook/xml/views/{view_id}/ - Détails d'une vue XML
# /api/v1/notebook/xml/views/{view_id}/html/ - Rendu HTML d'une vue XML
# /api/v1/notebook/xml/views/{view_id}/create/ - Créer un objet via vue XML
# /api/v1/notebook/xml/views/{view_id}/fields/ - Liste des champs d'une vue
# /api/v1/notebook/xml/reload/ - Recharger les templates XML





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