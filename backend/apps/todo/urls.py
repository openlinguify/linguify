from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TodoMainView, TodoKanbanView, TodoListView, TodoActivityView, TodoFormView,
    PersonalStageTypeViewSet, CategoryViewSet, TagViewSet, ProjectViewSet, TaskViewSet,
    NoteViewSet, ReminderViewSet, TaskTemplateViewSet,
    TodoSettingsAPI, TodoUserPreferencesAPI, TodoDashboardAPI
)
from django.urls import path
from django.contrib.auth.decorators import login_required

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
    path('', TodoMainView.as_view(), name='main'),
    path('kanban/', TodoKanbanView.as_view(), name='kanban'),
    path('list/', TodoListView.as_view(), name='list'),
    path('activity/', TodoActivityView.as_view(), name='activity'),
    path('task/new/', TodoFormView.as_view(), name='task_new'),
    path('task/<uuid:task_id>/', TodoFormView.as_view(), name='task_edit'),

    # API endpoints (router includes all CRUD operations)
    path('', include(router.urls)),
    
    # Settings endpoints
    path('settings/', TodoSettingsAPI.as_view(), name='settings'),
    path('preferences/', TodoUserPreferencesAPI.as_view(), name='preferences'),
    path('dashboard/', TodoDashboardAPI.as_view(), name='dashboard'),
]