# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues d'authentification
# TODO: Migrer les vues d'authentification depuis les autres fichiers

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import View

# Placeholder - à implémenter
class LoginView(View):
    """Vue de connexion"""
    pass

class LogoutView(View):
    """Vue de déconnexion"""
    pass

class RegisterView(View):
    """Vue d'inscription"""
    pass