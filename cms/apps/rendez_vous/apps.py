# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RendezVousConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rendez_vous'
    verbose_name = _('Rendez-vous')

    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.rendez_vous.signals  # noqa
        except ImportError:
            pass
