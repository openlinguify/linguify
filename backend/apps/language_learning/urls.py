"""
URLs configuration for language_learning app.
"""
from django.urls import path
from . import views

app_name = 'language_learning'

urlpatterns = [
    # Main pages
    path('', views.language_learning_home, name='home'),
    path('create/', views.create_item, name='create_item'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    
    # API endpoints
    path('api/items/', views.api_items, name='api_items'),
]
