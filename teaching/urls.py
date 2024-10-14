# teaching/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('teaching/', views.teaching, name='teaching_dashboard'),
    path('teaching_dashboard/', views.teaching_dashboard, name='teaching_dashboard'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('confirm_reservation/', views.confirm_reservation, name='confirm_reservation'),
    path('cancel_reservation/', views.cancel_reservation, name='cancel_reservation'),
    path('teacher_profile/', views.teacher_profile, name='teacher_profile'),
    path('selection_history/', views.selection_history, name='selection_history'),
]