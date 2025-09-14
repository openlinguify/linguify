from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .views.todo_activity_views import *
from .views.todo_import_views import *
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
    path('', TodoKanbanView.as_view(), name='main'),
    path('kanban/', TodoKanbanView.as_view(), name='kanban'),
    path('list/', TodoListView.as_view(), name='list'),
    path('activity/', TodoActivityView.as_view(), name='activity'),
    path('activity/export/', ActivityExportView.as_view(), name='activity_export'),
    path('task/new/', TodoFormView.as_view(), name='task_new'),
    path('task/<uuid:task_id>/', TodoFormView.as_view(), name='task_edit'),

    # API endpoints (router includes all CRUD operations)
    path('', include(router.urls)),
    
    # Settings endpoints
    path('settings/', TodoSettingsAPI.as_view(), name='settings'),
    path('preferences/', TodoUserPreferencesAPI.as_view(), name='preferences'),
    path('dashboard/', TodoDashboardAPI.as_view(), name='dashboard'),
    
    # HTMX endpoints
    path('htmx/tasks/<uuid:task_id>/toggle/', TaskToggleHTMXView.as_view(), name='task_toggle_htmx'),
    path('htmx/tasks/<uuid:task_id>/move/', TaskMoveHTMXView.as_view(), name='task_move_htmx'),
    path('htmx/tasks/<uuid:task_id>/delete/', TaskDeleteHTMXView.as_view(), name='task_delete_htmx'),
    path('htmx/tasks/create/', TaskQuickCreateHTMXView.as_view(), name='task_quick_create_htmx'),
    path('htmx/tasks/table/', TaskListTableHTMXView.as_view(), name='task_list_table_htmx'),
    path('htmx/kanban/column/', KanbanColumnHTMXView.as_view(), name='kanban_column_htmx'),
    path('htmx/kanban/column/<uuid:stage_id>/', KanbanColumnHTMXView.as_view(), name='kanban_column_htmx_stage'),
    path('htmx/tasks/modal/', TaskFormModalHTMXView.as_view(), name='task_form_modal_htmx'),
    path('htmx/tasks/modal/<uuid:task_id>/', TaskFormModalHTMXView.as_view(), name='task_form_modal_edit_htmx'),
    path('htmx/stages/<uuid:stage_id>/delete/', StageDeleteHTMXView.as_view(), name='stage_delete_htmx'),
    path('htmx/stages/<uuid:stage_id>/reorder/', StageReorderHTMXView.as_view(), name='stage_reorder_htmx'),
    
    # New HTMX dropdown endpoints
    path('htmx/tasks/<uuid:task_id>/dropdown/', TaskDropdownToggleHTMXView.as_view(), name='task_dropdown_toggle_htmx'),
    path('htmx/tasks/<uuid:task_id>/edit/', TaskEditHTMXView.as_view(), name='task_edit_htmx'),
    path('htmx/tasks/<uuid:task_id>/duplicate/', TaskDuplicateHTMXView.as_view(), name='task_duplicate_htmx'),
    path('htmx/tasks/<uuid:task_id>/priority/', TaskPriorityToggleHTMXView.as_view(), name='task_priority_toggle_htmx'),
    path('htmx/tasks/<uuid:task_id>/status/', TaskStatusToggleHTMXView.as_view(), name='task_status_toggle_htmx'),
    path('htmx/tasks/autosave/', TaskAutoSaveHTMXView.as_view(), name='task_autosave_create_htmx'),
    path('htmx/tasks/<uuid:task_id>/autosave/', TaskAutoSaveHTMXView.as_view(), name='task_autosave_update_htmx'),
    
    # Form-specific HTMX endpoints
    path('htmx/tasks/<uuid:task_id>/toggle_form/', TaskToggleFormHTMXView.as_view(), name='task_toggle_form_htmx'),
    path('htmx/tasks/<uuid:task_id>/delete_form/', TaskDeleteFormHTMXView.as_view(), name='task_delete_form_htmx'),
    path('htmx/tags/search/', TagSearchHTMXView.as_view(), name='tag_search_htmx'),
    path('htmx/tags/add/', TagAddHTMXView.as_view(), name='tag_add_htmx'),
    path('htmx/tags/<uuid:tag_id>/remove/', TagRemoveHTMXView.as_view(), name='tag_remove_htmx'),
    path('htmx/character_count/', CharacterCountHTMXView.as_view(), name='character_count_htmx'),
    
    # Activity HTMX endpoints
    path('htmx/activity/timeline/', ActivityTimelineHTMXView.as_view(), name='activity_timeline_htmx'),
    path('htmx/activity/stats/', ActivityStatsHTMXView.as_view(), name='activity_stats_htmx'),
    
    # Import endpoints
    path('import/', TaskImportModalHTMXView.as_view(), name='import_modal'),
    path('import/process/', TaskImportProcessHTMXView.as_view(), name='import_process'),
]