# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.notebook_views import (
    NoteViewSet,
    NoteCategoryViewSet,
    SharedNoteViewSet,
    get_app_config,
    NotebookMainView
)

app_name = 'notebook'

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'categories', NoteCategoryViewSet, basename='category')
router.register(r'shared-notes', SharedNoteViewSet, basename='shared-note')

urlpatterns = [
    # Configuration de l'application
    path('config/', get_app_config, name='config'),

    # API REST endpoints
    path('api/', include(router.urls)),

    # Interface web moderne (priorité pour dashboard)
    path('', NotebookMainView.as_view(), name='notebook_app'),
]