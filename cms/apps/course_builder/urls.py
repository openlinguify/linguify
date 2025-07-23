from django.urls import path
from . import views

app_name = 'course_builder'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/edit/', views.CourseEditView.as_view(), name='course_edit'),
    path('<int:pk>/chapters/', views.ChapterListView.as_view(), name='chapter_list'),
    path('<int:pk>/lessons/', views.LessonListView.as_view(), name='lesson_list'),
]