from django.urls import path
from django.views.generic import TemplateView

app_name = 'quizz_web'

urlpatterns = [
    path('', TemplateView.as_view(template_name='quizz/app.html'), name='app'),
]