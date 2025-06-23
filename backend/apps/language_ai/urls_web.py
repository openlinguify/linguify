from django.urls import path
from .views_web import LanguageAIMainView

app_name = 'language_ai_web'

urlpatterns = [
    path('', LanguageAIMainView.as_view(), name='app'),
]