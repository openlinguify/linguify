"""
URLs pour l'interface web du Notebook
"""

from django.urls import path
from . import views_web

app_name = 'notebook_web'

urlpatterns = [
    # Vue principale de l'application
    path('', views_web.NotebookMainView.as_view(), name='main'),
    
    # Vue legacy (pour compatibilité)
    path('app/', views_web.notebook_app, name='app'),
    
    # Configuration de l'application
    path('config/', views_web.get_app_config, name='config'),
]