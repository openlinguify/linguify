# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues d'authentification
from django.contrib.auth import views as auth_views, login
from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from ..forms.auth_forms import RegisterForm

class LoginView(auth_views.LoginView):
    """Vue de connexion"""
    template_name = 'authentication/login.html'

class RegisterView(View):
    """Vue d'inscription"""
    
    def get(self, request):
        form = RegisterForm()
        return render(request, 'authentication/register.html', {'form': form})
    
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Connecter automatiquement l'utilisateur après inscription
                login(request, user)
                messages.success(request, 'Votre compte a été créé avec succès!')
                return redirect('saas_web:dashboard')
            except Exception as e:
                messages.error(request, f'Erreur lors de la création du compte: {str(e)}')
        
        return render(request, 'authentication/register.html', {'form': form})

def logout_view(request):
    """Vue de deconnexion"""
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    from django.contrib import messages
    from django.conf import settings
    
    # Effectuer la déconnexion
    logout(request)
    
    # Message de succès
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    
    # Rediriger vers le portal
    portal_url = 'http://127.0.0.1:8080' if settings.DEBUG else 'https://openlinguify.com'
    return redirect(portal_url)