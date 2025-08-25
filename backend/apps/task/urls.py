from django.urls import path
from django.http import HttpResponse

# Placeholder view for task app
def task_placeholder(request):
    return HttpResponse("""
    <h1>Task</h1>
    <p>Cette application Task est en cours de développement.</p>
    <p><a href="/dashboard/">Retour au Dashboard</a></p>
    """)

app_name = 'task'

urlpatterns = [
    path('', task_placeholder, name='task_home'),
]