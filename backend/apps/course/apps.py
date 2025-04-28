# backend/apps/course/apps.py
from django.apps import AppConfig

class CourseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.course' 
    verbose_name = "Courses"
    
    def ready(self):
        import apps.course.signals 