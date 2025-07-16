# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues de debug pour l'authentification
# TODO: Migrer les vues de debug depuis les autres fichiers

from django.http import JsonResponse

def cors_debug(request):
    """Vue de debug pour les CORS"""
    return JsonResponse({'cors_debug': 'placeholder'})

def test_token_verification(request):
    """Test de verification des tokens"""
    return JsonResponse({'token_verification': 'placeholder'})

def debug_auth_headers(request):
    """Debug des headers d'authentification"""
    return JsonResponse({'auth_headers': 'placeholder'})

def debug_apps_system(request):
    """Debug du systeme d'applications"""
    return JsonResponse({'apps_system': 'placeholder'})

def test_token(request):
    """Test des tokens"""
    return JsonResponse({'test_token': 'placeholder'})