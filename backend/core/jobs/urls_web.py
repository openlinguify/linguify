from django.urls import path
from . import views_web

app_name = 'jobs'

urlpatterns = [
    # Page principale des carrières
    path('', views_web.CareersView.as_view(), name='careers'),
    
    # Détail d'une position
    path('position/<int:position_id>/', views_web.CareersPositionDetailView.as_view(), name='position_detail'),
]