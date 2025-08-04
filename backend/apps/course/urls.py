from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('', views.CourseDashboardView.as_view(), name='dashboard'),
    path('redirect/', views.learning_redirect, name='learning_redirect'),
    path('test-data/', views.test_marketplace_view, name='test_marketplace'),
    path('demo/', views.demo_dashboard_view, name='demo_dashboard'),
    path('lesson/<int:lesson_id>/', views.lesson_detail_view, name='lesson_detail'),
    path('course/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('course/<int:course_id>/buy/', views.course_buy_view, name='course_buy'),
]