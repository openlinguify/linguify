from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging

from ..services.translation_service import translation_service

logger = logging.getLogger(__name__)

class TranslationAPIView(APIView):
    """API pour la traduction automatique de texte."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Traduit un texte d'une langue source vers une langue cible.
        
        Body parameters:
        - text (str, required): Texte à traduire
        - source_language (str, optional): Code langue source (auto-détection si absent)
        - target_language (str, required): Code langue cible
        """
        try:
            # Récupération des paramètres
            text = request.data.get('text', '').strip()
            source_language = request.data.get('source_language', None)
            target_language = request.data.get('target_language', 'en')
            
            # Validation des paramètres requis
            if not text:
                return Response({
                    'success': False,
                    'error': 'Le paramètre "text" est requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not target_language:
                return Response({
                    'success': False,
                    'error': 'Le paramètre "target_language" est requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validation de la longueur du texte
            if len(text) > 1000:
                return Response({
                    'success': False,
                    'error': 'Le texte ne peut pas dépasser 1000 caractères'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validation de la langue cible
            if not translation_service.is_language_supported(target_language):
                return Response({
                    'success': False,
                    'error': f'Langue cible non supportée: {target_language}',
                    'supported_languages': translation_service.get_supported_languages()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validation de la langue source si fournie
            if source_language and not translation_service.is_language_supported(source_language):
                return Response({
                    'success': False,
                    'error': f'Langue source non supportée: {source_language}',
                    'supported_languages': translation_service.get_supported_languages()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Effectuer la traduction
            result = translation_service.translate_text(
                text=text,
                source_lang=source_language,
                target_lang=target_language
            )
            
            if result['success']:
                # Traduction réussie
                return Response({
                    'success': True,
                    'data': {
                        'original_text': text,
                        'translated_text': result['translated_text'],
                        'source_language': result['source_language'],
                        'target_language': result['target_language'],
                        'detected_language': result.get('detected_language'),
                        'confidence': result.get('confidence', 0),
                        'provider': result.get('provider', 'Unknown')
                    }
                })
            else:
                # Erreur de traduction
                return Response({
                    'success': False,
                    'error': result.get('error', 'Erreur de traduction inconnue')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Erreur lors de la traduction pour l'utilisateur {request.user.id}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Erreur interne du serveur'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @method_decorator(cache_page(60 * 15))  # Cache pendant 15 minutes
    def get(self, request):
        """
        Retourne la liste des langues supportées pour la traduction.
        """
        try:
            return Response({
                'success': True,
                'supported_languages': translation_service.get_supported_languages()
            })
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des langues supportées: {str(e)}")
            return Response({
                'success': False,
                'error': 'Erreur interne du serveur'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TranslationDetectAPIView(APIView):
    """API pour la détection automatique de langue."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Détecte automatiquement la langue d'un texte.
        
        Body parameters:
        - text (str, required): Texte à analyser
        """
        try:
            text = request.data.get('text', '').strip()
            
            if not text:
                return Response({
                    'success': False,
                    'error': 'Le paramètre "text" est requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if len(text) > 500:
                return Response({
                    'success': False,
                    'error': 'Le texte ne peut pas dépasser 500 caractères pour la détection'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Détection de la langue
            detected_language = translation_service.detect_language(text)
            language_name = translation_service.get_supported_languages().get(
                detected_language, 
                'Inconnue'
            )
            
            return Response({
                'success': True,
                'data': {
                    'text': text,
                    'detected_language': detected_language,
                    'language_name': language_name,
                    'supported_languages': translation_service.get_supported_languages()
                }
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection de langue pour l'utilisateur {request.user.id}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Erreur interne du serveur'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)