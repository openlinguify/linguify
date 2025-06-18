# -*- coding: utf-8 -*-
# Part of Linguify. See the LICENSE file for full copyright and license details.

from django.apps import AppConfig

class CourseConfig(AppConfig):
    """
    Configuration for the 'course' application.
    Defines core settings for the course app.
    """
    default_auto_field = 'django.db.models.BigAutoField'  # Default AutoField for models
    name = 'apps.course'                                  # Python path to the application module
    label = 'course'                                      # Unique short identifier for the app
    verbose_name = "Courses"                              # Human-readable name in Django admin

    def ready(self):
        """
        Called once the application is ready.
        Useful for connecting signals and performing initial setups.
        """
        import apps.course.signals  # Import signals so their handlers are registered