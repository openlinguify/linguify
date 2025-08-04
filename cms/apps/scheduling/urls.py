from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('lessons/', views.LessonListView.as_view(), name='lessons'),
    path('availability/', views.AvailabilityView.as_view(), name='availability'),
]