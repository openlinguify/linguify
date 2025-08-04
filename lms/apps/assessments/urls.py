from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('', views.assessments_list, name='list'),
]
