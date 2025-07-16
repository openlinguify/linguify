# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Formulaires d'authentification
# TODO: Migrer les formulaires depuis legacy_forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Placeholder - à implémenter
class LoginForm(AuthenticationForm):
    """Formulaire de connexion"""
    pass

class RegisterForm(UserCreationForm):
    """Formulaire d'inscription"""
    pass