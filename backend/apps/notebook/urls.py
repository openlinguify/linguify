# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, NoteCategoryViewSet, TagViewSet, SharedNoteViewSet, NotebookSettingsView

app_name = 'notebook'

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'categories', NoteCategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'shared-notes', SharedNoteViewSet, basename='shared-note')


urlpatterns = [
    # API REST endpoints
    path('', include(router.urls)),
    
    # Settings endpoint
    path('settings/', NotebookSettingsView.as_view(), name='notebook-settings'),
]


# Endpoints disponibles :

# /api/notes/ - CRUD des notes
# /api/notes/due_for_review/ - Notes à réviser
# /api/notes/by_language/ - Notes par langue
# /api/categories/ - Gestion des catégories
# /api/tags/ - Gestion des tags
# /api/shared/ - Gestion des notes partagées