from django.urls import path
from django.contrib.auth.decorators import login_required
from .views.todo_web_views import TodoMainView, TodoKanbanView, TodoListView, TodoActivityView, TodoFormView

app_name = 'todo_web'

# Web interface for todo app
urlpatterns = [
    path('', TodoMainView.as_view(), name='main'),
    path('kanban/', TodoKanbanView.as_view(), name='kanban'),
    path('list/', TodoListView.as_view(), name='list'),
    path('activity/', TodoActivityView.as_view(), name='activity'),
    path('task/new/', TodoFormView.as_view(), name='task_new'),
    path('task/<uuid:task_id>/', TodoFormView.as_view(), name='task_edit'),
]