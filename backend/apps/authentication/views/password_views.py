# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues de gestion des mots de passe
# TODO: Migrer les vues de mot de passe depuis les autres fichiers

from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView
from django.views.generic import View

# Placeholder - à implémenter
class PasswordChangeView(DjangoPasswordChangeView):
    """Vue de changement de mot de passe"""
    pass

class PasswordResetView(DjangoPasswordResetView):
    """Vue de réinitialisation de mot de passe"""
    pass

class PasswordResetConfirmView(View):
    """Vue de confirmation de réinitialisation"""
    pass