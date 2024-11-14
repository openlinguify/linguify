from django.apps import AppConfig

from backend.django_apps import course


class CourseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.django_apps.course'
