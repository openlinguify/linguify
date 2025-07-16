"""
Vues pour la gestion des profils utilisateur.
"""

import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..profile import (
    process_uploaded_profile_picture,
    delete_profile_picture,
    get_profile_picture_urls,
    migrate_legacy_profile_picture,
    clean_old_versions
)
from ..models import User

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# API Views
# -----------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    """
    API pour télécharger une photo de profil.
    """
    if 'file' not in request.FILES:
        return Response({
            'success': False,
            'error': _('No file provided')
        }, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    
    # Vérifier le type MIME
    content_type = file.content_type.lower()
    if not content_type.startswith('image/'):
        return Response({
            'success': False,
            'error': _('File is not an image')
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Traiter la photo
    result = process_uploaded_profile_picture(request.user, file)
    
    if not result['success']:
        return Response({
            'success': False,
            'error': result.get('error', _('Failed to process profile picture'))
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Renvoyer les URLs
    urls = get_profile_picture_urls(request.user, use_cache=False)
    
    return Response({
        'success': True,
        'urls': urls
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile_picture_api(request):
    """
    API pour supprimer une photo de profil.
    """
    result = delete_profile_picture(request.user)
    
    return Response({
        'success': result
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_picture_urls_api(request, user_id=None):
    """
    API pour obtenir les URLs des photos de profil.
    """
    # Utiliser l'utilisateur connecté par défaut
    user = request.user
    
    # Si un ID est fourni et que l'utilisateur connecté est staff, utiliser cet utilisateur
    if user_id and request.user.is_staff:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': _('User not found')
            }, status=status.HTTP_404_NOT_FOUND)
    
    urls = get_profile_picture_urls(user)
    
    return Response({
        'success': True,
        'urls': urls
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def migrate_profile_picture(request, user_id=None):
    """
    API pour migrer une photo de profil legacy vers le nouveau format.
    Accessible uniquement aux administrateurs sauf pour son propre compte.
    """
    # Par défaut, l'utilisateur connecté
    user = request.user
    
    # Si un ID est fourni, vérifier les permissions
    if user_id:
        if not request.user.is_staff and str(request.user.id) != str(user_id):
            return Response({
                'success': False,
                'error': _('Permission denied')
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': _('User not found')
            }, status=status.HTTP_404_NOT_FOUND)
    
    # Vérifier si la photo est au format legacy
    profile_picture_path = str(user.profile_picture)
    if not profile_picture_path or ('profile_pictures' not in profile_picture_path):
        return Response({
            'success': False,
            'error': _('User does not have a legacy profile picture')
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Migrer la photo
    new_path = migrate_legacy_profile_picture(user, profile_picture_path, user.id)
    
    if not new_path:
        return Response({
            'success': False,
            'error': _('Failed to migrate profile picture')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Renvoyer les nouvelles URLs
    urls = get_profile_picture_urls(user, use_cache=False)
    
    return Response({
        'success': True,
        'old_path': profile_picture_path,
        'new_path': new_path,
        'urls': urls
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_cleanup_profile_pictures(request):
    """
    API pour nettoyer les anciennes versions des photos de profil.
    Accessible uniquement aux administrateurs.
    """
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': _('Permission denied')
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Récupérer les paramètres
    max_versions = int(request.data.get('max_versions', 5))
    user_id = request.data.get('user_id', None)
    
    if user_id:
        # Nettoyer pour un utilisateur spécifique
        try:
            user = User.objects.get(id=user_id)
            deleted = clean_old_versions(user.id, max_versions)
            
            return Response({
                'success': True,
                'user_id': user.id,
                'deleted_count': deleted
            })
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': _('User not found')
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        # Nettoyer pour tous les utilisateurs
        total_deleted = 0
        processed = 0
        
        for user in User.objects.exclude(profile_picture=''):
            deleted = clean_old_versions(user.id, max_versions)
            total_deleted += deleted
            processed += 1
        
        return Response({
            'success': True,
            'users_processed': processed,
            'total_deleted': total_deleted
        })


# -----------------------------------------------------------------------------
# Django Traditional Views
# -----------------------------------------------------------------------------

@login_required
def profile_picture_management(request):
    """
    Page de gestion des photos de profil (vue traditionnelle Django).
    """
    context = {
        'user': request.user,
        'profile_urls': get_profile_picture_urls(request.user)
    }
    
    return render(request, 'authentication/profile_picture_management.html', context)


@login_required
@require_POST
def upload_profile_picture_form(request):
    """
    Vue pour le téléchargement de photo de profil via un formulaire HTML.
    """
    if 'profile_picture' not in request.FILES:
        return HttpResponseBadRequest(_('No file provided'))
    
    file = request.FILES['profile_picture']
    
    # Traiter la photo
    result = process_uploaded_profile_picture(request.user, file)
    
    if not result['success']:
        return HttpResponseBadRequest(result.get('error', _('Failed to process profile picture')))
    
    # Rediriger vers la page de gestion
    return redirect('profile_picture_management')


@login_required
def delete_profile_picture_form(request):
    """
    Vue pour la suppression de photo de profil.
    """
    result = delete_profile_picture(request.user)
    
    # Rediriger vers la page de gestion
    return redirect('profile_picture_management')