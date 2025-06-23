from django.urls import path
from .views_web import QuizzMainView

app_name = 'quizz_web'

urlpatterns = [
    path('', QuizzMainView.as_view(), name='app'),
]