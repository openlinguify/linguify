# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.notebook_views import *

app_name = 'notebook'

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'categories', NoteCategoryViewSet, basename='category')
router.register(r'shared-notes', SharedNoteViewSet, basename='shared-note')

urlpatterns = [
    # API REST endpoints
    path('', include(router.urls)),

    # Configuration de l'application
    path('config/', get_app_config, name='config'),

    path('ajax/csrf/', get_csrf_token, name='ajax_csrf_token'),
    path('ajax/notes/', get_notes, name='ajax_get_notes'),
    path('ajax/notes/create/', create_note, name='ajax_create_note'),
    path('ajax/notes/<int:note_id>/update/', update_note, name='ajax_update_note'),
    path('ajax/notes/<int:note_id>/delete/', delete_note, name='ajax_delete_note'),
    path('ajax/notes/bulk-delete/', bulk_delete_notes, name='ajax_bulk_delete'),
    path('ajax/notes/bulk-update/', bulk_update_notes, name='ajax_bulk_update'),
]