from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PersonalStageTypeViewSet, CategoryViewSet, TagViewSet, ProjectViewSet, TaskViewSet,
    NoteViewSet, ReminderViewSet, TaskTemplateViewSet,
    TodoSettingsView, TodoUserPreferencesView, TodoDashboardView
)

app_name = 'todo'

# API Router for ViewSets
router = DefaultRouter()
router.register(r'stages', PersonalStageTypeViewSet, basename='stage')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'reminders', ReminderViewSet, basename='reminder')
router.register(r'templates', TaskTemplateViewSet, basename='template')

urlpatterns = [
    # API endpoints (router includes all CRUD operations)
    path('', include(router.urls)),
    
    # Settings endpoints
    path('settings/', TodoSettingsView.as_view(), name='settings'),
    path('preferences/', TodoUserPreferencesView.as_view(), name='preferences'),
    path('dashboard/', TodoDashboardView.as_view(), name='dashboard'),
]