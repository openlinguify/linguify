# authentication/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
from authentication.views import UploadProfilePhotoView, choose_user_type, signup, student_dashboard, teacher_dashboard, delete_account, register_teacher

urlpatterns = [
    path('login/', LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('choose-user-type/', views.choose_user_type, name='choose_user_type'),
    path('register-student/', views.signup, name='register_student'),
    path('register-teacher/', views.register_teacher, name='register_teacher'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('upload-profile-photo/', UploadProfilePhotoView.as_view(), name='upload_profile_photo'),
]
