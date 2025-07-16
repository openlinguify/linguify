# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues pour les termes et conditions
from django.http import JsonResponse
from django.shortcuts import render

def accept_terms(request):
    """Vue pour accepter les termes - placeholder"""
    # TODO: Implémenter
    return JsonResponse({'status': 'terms_accepted'})

def terms_status(request):
    """Vue pour vérifier le statut des termes - placeholder"""
    # TODO: Implémenter
    return JsonResponse({'terms_accepted': True})