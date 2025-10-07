# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cours'
    verbose_name = _('Cours')

    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.cours.signals  # noqa
        except ImportError:
            pass
