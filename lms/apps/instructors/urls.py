from django.urls import path
from . import views

app_name = 'instructors'

urlpatterns = [
    path('', views.instructors_list, name='list'),
]
