from django.urls import path, re_path
from . import views

app_name = 'docs'

urlpatterns = [
    # Documentation home
    path('', views.docs_home, name='home'),
    
    # Specific documentation pages
    path('quick-start/', views.quick_start, name='quick_start'),
    path('environment-setup/', views.environment_setup, name='environment_setup'),
    path('developer-guidelines/', views.developer_guidelines, name='developer_guidelines'),
    path('translation-guide/', views.translation_guide, name='translation_guide'),
    path('api/', views.api_reference, name='api_reference'),
    
    # Dynamic page serving - catch all other documentation pages
    re_path(r'^(?P<page_path>.+)/$', views.docs_page, name='page'),
]