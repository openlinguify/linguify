# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Formulaires de profil utilisateur
# TODO: Migrer les formulaires depuis legacy_forms.py

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

# Placeholder - à implémenter
class ProfileForm(forms.ModelForm):
    """Formulaire de profil utilisateur"""
    pass

class ProfilePictureForm(forms.Form):
    """Formulaire de photo de profil"""
    pass