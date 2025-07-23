"""
URLs for Learning app.
"""
from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    # Web views
    path('', views.LearningDashboardView.as_view(), name='dashboard'),
    
    # API endpoints - Course management
    path('api/courses/', views.StudentCoursesAPIView.as_view(), name='api_courses'),
    path('api/courses/<int:course_id>/', views.CourseDetailAPIView.as_view(), name='api_course_detail'),
    path('api/courses/available/', views.AvailableCoursesAPIView.as_view(), name='api_available_courses'),
    path('api/recommendations/', views.CourseRecommendationsAPIView.as_view(), name='api_recommendations'),
    
    # API endpoints - Learning progress
    path('api/courses/<int:course_id>/lessons/', views.LessonProgressAPIView.as_view(), name='api_lesson_progress'),
    path('api/courses/<int:course_id>/lessons/<int:lesson_id>/start/', views.StartLessonAPIView.as_view(), name='api_start_lesson'),
    path('api/courses/<int:course_id>/lessons/<int:lesson_id>/complete/', views.CompleteLessonAPIView.as_view(), name='api_complete_lesson'),
    path('api/courses/<int:course_id>/lessons/<int:lesson_id>/content/<int:content_id>/progress/', views.update_content_progress, name='api_content_progress'),
    
    # API endpoints - Sessions and analytics
    path('api/sessions/<int:session_id>/end/', views.end_learning_session, name='api_end_session'),
    path('api/analytics/', views.LearningAnalyticsAPIView.as_view(), name='api_analytics'),
    path('api/dashboard/', views.LearningDashboardAPIView.as_view(), name='api_dashboard'),
    
    # API endpoints - Reviews
    path('api/reviews/', views.StudentReviewsAPIView.as_view(), name='api_reviews'),
]