from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Public API endpoints
    path('departments/', views.DepartmentListView.as_view(), name='department-list'),
    path('positions/', views.JobPositionListView.as_view(), name='position-list'),
    path('positions/<int:pk>/', views.JobPositionDetailView.as_view(), name='position-detail'),
    path('apply/', views.JobApplicationCreateView.as_view(), name='application-create'),
    path('stats/', views.job_stats, name='job-stats'),
    
    # Admin-only endpoints
    path('admin/applications/<int:application_id>/download-resume/', views.download_resume, name='download-resume'),
]