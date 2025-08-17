from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

app_name = 'todo_web'

# Web interface for todo app
urlpatterns = [
    path('', login_required(TemplateView.as_view(template_name='todo/main.html')), name='main'),
]