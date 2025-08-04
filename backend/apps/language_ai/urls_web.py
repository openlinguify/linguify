from django.urls import path
from .views_web import LanguageAIChatView

app_name = 'language_ai_web'

urlpatterns = [
    path('', LanguageAIChatView.as_view(), name='chat'),
]