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
    path('config/', views.get_app_config, name='config'),

    path('ajax/csrf/', views_web.get_csrf_token, name='ajax_csrf_token'),
    path('ajax/notes/', views_web.get_notes, name='ajax_get_notes'),
    path('ajax/notes/create/', views_web.create_note, name='ajax_create_note'),
    path('ajax/notes/<int:note_id>/update/', views_web.update_note, name='ajax_update_note'),
    path('ajax/notes/<int:note_id>/delete/', views_web.delete_note, name='ajax_delete_note'),
    path('ajax/notes/bulk-delete/', views_web.bulk_delete_notes, name='ajax_bulk_delete'),
    path('ajax/notes/bulk-update/', views_web.bulk_update_notes, name='ajax_bulk_update'),
]