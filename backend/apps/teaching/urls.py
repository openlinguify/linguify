"""
URLs for Teaching app.
"""
from django.urls import path
from . import views

app_name = 'teaching'

urlpatterns = [
    # Web views
    path('', views.TeachingDashboardView.as_view(), name='dashboard'),
    
    # Teacher discovery
    path('api/teachers/', views.AvailableTeachersAPIView.as_view(), name='api_teachers'),
    path('api/teachers/<int:pk>/', views.TeacherDetailAPIView.as_view(), name='api_teacher_detail'),
    path('api/teachers/<int:teacher_id>/availability/', views.teacher_availability, name='api_teacher_availability'),
    path('api/recommendations/', views.TeacherRecommendationsAPIView.as_view(), name='api_recommendations'),
    
    # Lesson booking
    path('api/book/', views.BookLessonAPIView.as_view(), name='api_book_lesson'),
    path('api/lessons/', views.StudentLessonsAPIView.as_view(), name='api_student_lessons'),
    path('api/lessons/<int:pk>/', views.LessonDetailAPIView.as_view(), name='api_lesson_detail'),
    path('api/lessons/<int:lesson_id>/cancel/', views.cancel_lesson, name='api_cancel_lesson'),
    path('api/lessons/<int:lesson_id>/start/', views.start_lesson, name='api_start_lesson'),
    
    # Ratings
    path('api/lessons/<int:lesson_id>/rating/', views.CreateLessonRatingAPIView.as_view(), name='api_create_rating'),
]