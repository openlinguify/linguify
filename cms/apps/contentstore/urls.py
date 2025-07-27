"""
Content store URLs following OpenEdX patterns.
Replaces course_builder URLs completely.
"""
from django.urls import path
from .views import course, assets, dashboard

app_name = 'contentstore'

urlpatterns = [
    # Main dashboard and course management (replaces course_builder)
    path('', dashboard.dashboard_view, name='dashboard'),
    path('courses/', dashboard.CourseListView.as_view(), name='course_list'),
    path('courses/create/', dashboard.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/', dashboard.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/edit/', dashboard.CourseEditView.as_view(), name='course_edit'),
    
    # Course studio (advanced editing)
    path('courses/<int:course_id>/studio/', course.CourseStudioView.as_view(), name='course_studio'),
    
    # Course management API endpoints
    path('api/courses/', course.course_handler, name='courses_api'),
    path('api/courses/<int:course_id>/', course.course_handler, name='course_api'),
    path('api/courses/<int:course_id>/settings/', course.course_settings_handler, name='course_settings_api'),
    
    # Asset management endpoints
    path('api/courses/<int:course_id>/assets/', assets.assets_handler, name='assets_api'),
    path('api/courses/<int:course_id>/assets/<int:asset_id>/', assets.assets_handler, name='asset_api'),
    path('api/courses/<int:course_id>/assets/<int:asset_id>/usage/', assets.asset_usage_handler, name='asset_usage_api'),
]