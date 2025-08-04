from django.urls import path, include
from . import views
from .admin_views import TenantStudentAdmin

app_name = 'students'

def get_admin_urls(org_slug, db_name):
    """Générer les URLs admin pour une organisation"""
    admin_instance = TenantStudentAdmin(org_slug, db_name)
    return admin_instance.get_urls()

urlpatterns = [
    # Legacy route
    path('', views.students_list, name='list'),
    
    # Organization-specific routes 
    path('list/', views.student_list, name='student_list'),
    path('<str:student_id>/', views.student_detail, name='detail'),
    
    # Admin interface for students
    path('admin/', views.students_admin_interface, name='admin_interface'),
]
