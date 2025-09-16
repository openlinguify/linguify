# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues pour les termes et conditions
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _, activate, get_language
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from ..models.models import User
import json
import logging

logger = logging.getLogger(__name__)

@extend_schema(
    summary="Accept Terms and Conditions",
    description="Accept the terms and conditions for the authenticated user",
    responses={
        200: OpenApiResponse(description="Terms accepted successfully"),
        400: OpenApiResponse(description="Bad request"),
        401: OpenApiResponse(description="Unauthorized"),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_terms(request):
    """Vue pour accepter les termes et conditions"""
    try:
        user = request.user
        
        # Vérifier si l'utilisateur est authentifié
        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Mettre à jour le statut d'acceptation des termes
        user.terms_accepted = True
        user.terms_accepted_at = timezone.now()
        user.terms_version = 'v1.0'
        user.save(update_fields=['terms_accepted', 'terms_accepted_at', 'terms_version'])
        
        logger.info(f"User {user.id} accepted terms at {user.terms_accepted_at}")

        return Response({
            'status': 'terms_accepted',
            'accepted_at': user.terms_accepted_at.isoformat(),
            'message': 'Terms and conditions accepted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error accepting terms for user {request.user.id}: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    summary="Check Terms Status",
    description="Check if the authenticated user has accepted terms and conditions",
    responses={
        200: OpenApiResponse(description="Terms status retrieved successfully"),
        401: OpenApiResponse(description="Unauthorized"),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def terms_status(request):
    """Vue pour vérifier le statut des termes et conditions"""
    try:
        user = request.user
        
        # Vérifier si l'utilisateur est authentifié
        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Vérifier si les termes ont été acceptés
        terms_accepted = user.terms_accepted
        
        response_data = {
            'terms_accepted': terms_accepted,
            'user_id': user.id,
            'username': user.username
        }
        
        # Ajouter la date d'acceptation si elle existe
        if terms_accepted and user.terms_accepted_at:
            response_data['accepted_at'] = user.terms_accepted_at.isoformat()
            response_data['terms_version'] = user.terms_version
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error checking terms status for user {request.user.id}: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Versions non-API pour compatibilité avec les URLs existantes
@login_required
@require_http_methods(["POST"])
def accept_terms_web(request):
    """Version web pour accepter les termes"""
    try:
        user = request.user
        user.terms_accepted = True
        user.terms_accepted_at = timezone.now()
        user.terms_version = 'v1.0'
        user.save(update_fields=['terms_accepted', 'terms_accepted_at', 'terms_version'])
        
        return JsonResponse({
            'status': 'terms_accepted',
            'accepted_at': user.terms_accepted_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error accepting terms for user {request.user.id}: {str(e)}")
        return JsonResponse(
            {'error': 'Internal server error'}, 
            status=500
        )

@login_required
@require_http_methods(["GET"])
def terms_status_web(request):
    """Version web pour vérifier le statut des termes"""
    try:
        user = request.user
        terms_accepted = user.terms_accepted
        
        response_data = {
            'terms_accepted': terms_accepted,
            'user_id': user.id
        }
        
        if terms_accepted and user.terms_accepted_at:
            response_data['accepted_at'] = user.terms_accepted_at.isoformat()
            response_data['terms_version'] = user.terms_version
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error checking terms status for user {request.user.id}: {str(e)}")
        return JsonResponse(
            {'error': 'Internal server error'},
            status=500
        )

# Nouvelle vue pour la page d'acceptation des conditions
@login_required
def terms_acceptance_view(request):
    """
    Page d'acceptation des conditions d'utilisation avec formulaire de confirmation
    """
    # Activer la langue de l'interface utilisateur
    current_language = get_language()
    user_language = getattr(request.user, 'interface_language', 'en')
    activate(user_language)

    try:
        # Vérifier si l'utilisateur a déjà accepté les conditions
        if request.user.terms_accepted:
            messages.info(request, _('You have already accepted the terms of use.'))
            return redirect('saas_web:dashboard')

        # URL du portal pour les conditions complètes
        portal_url = getattr(settings, 'PORTAL_URL', 'http://localhost:8080')
        full_terms_url = f"{portal_url}/annexes/terms"

        context = {
            'user': request.user,
            'full_terms_url': full_terms_url,
            'current_version': 'v1.0',
            'app_name': 'Open Linguify'
        }

        return render(request, 'authentication/terms_acceptance.html', context)

    except Exception as e:
        logger.error(f"Error in terms acceptance view: {str(e)}", exc_info=True)
        messages.error(request, _('An error occurred. Please try again.'))
        return redirect('saas_web:dashboard')
    finally:
        # Restaurer la langue originale
        activate(current_language)

@login_required
@require_http_methods(["POST"])
def accept_terms_ajax(request):
    """
    Vue AJAX pour accepter les conditions d'utilisation depuis la page d'acceptation
    """
    current_language = get_language()
    user_language = getattr(request.user, 'interface_language', 'en')
    activate(user_language)

    try:
        # Vérifier si l'utilisateur a déjà accepté
        if request.user.terms_accepted:
            return JsonResponse({
                'success': False,
                'message': _('Terms already accepted'),
                'redirect': '/dashboard/'
            })

        # Mettre à jour le statut de l'utilisateur
        request.user.terms_accepted = True
        request.user.terms_accepted_at = timezone.now()
        request.user.terms_version = 'v1.0'
        request.user.save(update_fields=['terms_accepted', 'terms_accepted_at', 'terms_version'])

        logger.info(f"User {request.user.id} ({request.user.email}) accepted terms v1.0 at {timezone.now()}")

        return JsonResponse({
            'success': True,
            'message': _('Terms accepted successfully!'),
            'redirect': '/dashboard/'
        })

    except Exception as e:
        logger.error(f"Error accepting terms for user {request.user.id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': _('An error occurred while accepting terms. Please try again.')
        })
    finally:
        activate(current_language)