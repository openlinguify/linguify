from django.urls import path
from .views import QuizzMainView, QuizSettingsView

app_name = 'quizz_web'

urlpatterns = [
    path('', QuizzMainView.as_view(), name='main'),
    path('settings/', QuizSettingsView.as_view(), name='settings'),
]