# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotebookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notebook'
    label = 'notebook'
    verbose_name = _('Notes')
