from django.urls import path
from django.views.generic import TemplateView

app_name = 'language_ai_web'

urlpatterns = [
    path('', TemplateView.as_view(template_name='language_ai/app.html'), name='app'),
]