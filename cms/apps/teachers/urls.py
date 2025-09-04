from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.TeacherDashboardView.as_view(), name='dashboard'),
    path('profile/', views.TeacherProfileView.as_view(), name='profile'),
    path('profile/edit/', views.TeacherProfileEditView.as_view(), name='profile_edit'),
    path('lessons/', views.TeacherLessonsView.as_view(), name='lessons'),
    path('availability/', views.TeacherAvailabilityView.as_view(), name='availability'),
    path('availability/add/', views.AddAvailabilitySlotView.as_view(), name='add_availability'),
    path('announcements/', views.TeacherAnnouncementsView.as_view(), name='announcements'),
    path('announcements/new/', views.CreateAnnouncementView.as_view(), name='create_announcement'),
    path('announcements/<int:pk>/edit/', views.EditAnnouncementView.as_view(), name='edit_announcement'),
]