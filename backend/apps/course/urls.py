from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('', views.CourseDashboardView.as_view(), name='dashboard'),
    path('redirect/', views.learning_redirect, name='learning_redirect'),
    path('test-data/', views.test_marketplace_view, name='test_marketplace'),
    path('demo/', views.demo_dashboard_view, name='demo_dashboard'),
]