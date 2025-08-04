from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('profile/', views.TeacherProfileView.as_view(), name='profile'),
    path('profile/edit/', views.TeacherProfileEditView.as_view(), name='profile_edit'),
]