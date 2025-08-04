# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues pour les termes et conditions
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
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
        user.terms_acceptance = timezone.now()
        user.save(update_fields=['terms_acceptance'])
        
        logger.info(f"User {user.id} accepted terms at {user.terms_acceptance}")
        
        return Response({
            'status': 'terms_accepted',
            'accepted_at': user.terms_acceptance.isoformat(),
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
        terms_accepted = user.terms_acceptance is not None
        
        response_data = {
            'terms_accepted': terms_accepted,
            'user_id': user.id,
            'username': user.username
        }
        
        # Ajouter la date d'acceptation si elle existe
        if terms_accepted:
            response_data['accepted_at'] = user.terms_acceptance.isoformat()
        
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
        user.terms_acceptance = timezone.now()
        user.save(update_fields=['terms_acceptance'])
        
        return JsonResponse({
            'status': 'terms_accepted',
            'accepted_at': user.terms_acceptance.isoformat()
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
        terms_accepted = user.terms_acceptance is not None
        
        response_data = {
            'terms_accepted': terms_accepted,
            'user_id': user.id
        }
        
        if terms_accepted:
            response_data['accepted_at'] = user.terms_acceptance.isoformat()
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error checking terms status for user {request.user.id}: {str(e)}")
        return JsonResponse(
            {'error': 'Internal server error'}, 
            status=500
        )