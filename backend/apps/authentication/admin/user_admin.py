# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Configuration admin pour les utilisateurs
# TODO: Migrer depuis admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

# Placeholder - à implémenter
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration admin pour User"""
    pass