# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Configuration admin pour les utilisateurs
# TODO: Migrer depuis admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

# Basic User admin configuration for autocomplete
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration admin pour User"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']