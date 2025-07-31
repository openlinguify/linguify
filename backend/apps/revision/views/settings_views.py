"""
Vues pour les paramètres de l'application Révision
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from datetime import timedelta
import logging

from ..models.settings_models import RevisionSettings, RevisionSessionConfig
from ..serializers.settings_serializers import (
    RevisionSettingsSerializer, 
    RevisionSessionConfigSerializer,
    ApplyPresetSerializer,
    RevisionStatsSerializer
)

logger = logging.getLogger(__name__)

class RevisionSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les paramètres de révision des utilisateurs
    """
    serializer_class = RevisionSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les paramètres par utilisateur connecté"""
        return RevisionSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Récupère ou crée les paramètres pour l'utilisateur connecté"""
        settings, created = RevisionSettings.objects.get_or_create(user=self.request.user)
        if created:
            logger.info(f"Created revision settings for user {self.request.user.username}")
        return settings
    
    def list(self, request):
        """Liste les paramètres de l'utilisateur (retourne un seul objet)"""
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Récupère les paramètres (ignore pk, retourne les paramètres de l'utilisateur)"""
        return self.list(request)
    
    def update(self, request, pk=None, partial=True):
        """Met à jour les paramètres"""
        logger.info(f"Updating revision settings for user {request.user.username}")
        settings = self.get_object()
        serializer = self.get_serializer(settings, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Revision settings updated successfully for user {request.user.username}")
            return Response(serializer.data)
        else:
            logger.warning(f"Revision settings update failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request):
        """Crée les paramètres (retourne les paramètres existants ou nouvellement créés)"""
        return self.list(request)
    
    def destroy(self, request, pk=None):
        """Remet les paramètres par défaut"""
        logger.info(f"Resetting revision settings for user {request.user.username}")
        settings = self.get_object()
        
        # Sauvegarder les paramètres actuels pour le log
        old_settings = {
            'study_mode': settings.default_study_mode,
            'difficulty': settings.default_difficulty,
            'cards_per_session': settings.cards_per_session,
        }
        
        # Supprimer et recréer avec les valeurs par défaut
        settings.delete()
        new_settings = RevisionSettings.objects.create(user=request.user)
        
        logger.info(f"Revision settings reset for user {request.user.username}")
        logger.debug(f"Old settings: {old_settings}")
        
        serializer = self.get_serializer(new_settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def apply_preset(self, request):
        """Applique un preset de configuration"""
        serializer = ApplyPresetSerializer(data=request.data)
        
        if serializer.is_valid():
            preset_name = serializer.validated_data['preset_name']
            override = serializer.validated_data['override_user_settings']
            
            logger.info(f"Applying preset '{preset_name}' for user {request.user.username}")
            
            settings = self.get_object()
            success = settings.apply_preset(preset_name)
            
            if success:
                # Retourner les paramètres mis à jour
                response_serializer = self.get_serializer(settings)
                return Response({
                    'success': True,
                    'message': f"Preset '{preset_name}' appliqué avec succès",
                    'preset_applied': preset_name,
                    'settings': response_serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'error': f"Erreur lors de l'application du preset '{preset_name}'"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retourne les statistiques de révision de l'utilisateur"""
        try:
            # Importer les modèles de révision pour les stats
            from ..models import FlashcardDeck, Flashcard
            from django.db.models import Q
            
            user = request.user
            now = timezone.now()
            
            # Statistiques de base
            total_decks = FlashcardDeck.objects.filter(user=user, is_active=True).count()
            total_cards = Flashcard.objects.filter(deck__user=user, deck__is_active=True).count()
            
            # Cartes apprises (simulation - à adapter selon la logique métier)
            cards_learned = Flashcard.objects.filter(
                deck__user=user,
                deck__is_active=True,
                # Ajoutez ici la logique pour déterminer si une carte est "apprise"
            ).count()
            
            # Cartes en cours
            cards_in_progress = total_cards - cards_learned
            
            # Calcul du streak (simulation)
            daily_streak = 7  # À calculer selon la logique métier
            
            # Temps d'étude total (simulation)
            total_study_time = 450  # minutes - à calculer depuis les sessions
            
            # Taux de succès moyen
            success_rate = 0.85 if total_cards > 0 else 0.0
            
            # Dernière date d'étude
            last_study_date = now - timedelta(hours=6)  # Simulation
            
            stats_data = {
                'total_cards': total_cards,
                'cards_learned': cards_learned,
                'cards_in_progress': cards_in_progress,
                'daily_streak': daily_streak,
                'total_study_time': total_study_time,
                'average_session_duration': 22.5,
                'success_rate': success_rate,
                'last_study_date': last_study_date,
                'cards_by_difficulty': {
                    'easy': total_cards // 3,
                    'normal': total_cards // 2,
                    'hard': total_cards // 6,
                },
                'performance_trend': [0.7, 0.75, 0.8, 0.85, 0.83, 0.87, 0.85],
                'upcoming_reviews': 12,
            }
            
            serializer = RevisionStatsSerializer(data=stats_data)
            serializer.is_valid()
            return Response(serializer.data)
            
        except ImportError:
            # Si les modèles de révision ne sont pas disponibles
            logger.warning("Revision models not available for stats")
            return Response({
                'error': 'Statistiques non disponibles'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"Error calculating revision stats: {e}")
            return Response({
                'error': 'Erreur lors du calcul des statistiques'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def session_config(self, request):
        """Retourne la configuration recommandée pour une session"""
        settings = self.get_object()
        config = settings.get_session_config()
        
        # Ajouter des informations contextuelles
        now = timezone.now()
        config.update({
            'recommended_time': now.strftime('%H:%M'),
            'optimal_duration': min(settings.default_session_duration, 25),  # Pomodoro technique
            'break_reminder': settings.default_session_duration > 20,
        })
        
        return Response(config)


class RevisionSessionConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les configurations de session de révision
    """
    serializer_class = RevisionSessionConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les configurations par utilisateur connecté"""
        return RevisionSessionConfig.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Associe la configuration à l'utilisateur connecté"""
        logger.info(f"Creating session config for user {self.request.user.username}")
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Log de mise à jour"""
        logger.info(f"Updating session config '{serializer.instance.name}' for user {self.request.user.username}")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Log de suppression"""
        logger.info(f"Deleting session config '{instance.name}' for user {self.request.user.username}")
        super().perform_destroy(instance)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Définit cette configuration comme celle par défaut"""
        config = self.get_object()
        
        # Retirer le défaut des autres configurations
        RevisionSessionConfig.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Définir cette configuration comme défaut
        config.is_default = True
        config.save()
        
        logger.info(f"Set default session config to '{config.name}' for user {request.user.username}")
        
        serializer = self.get_serializer(config)
        return Response({
            'success': True,
            'message': f"Configuration '{config.name}' définie par défaut",
            'config': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Retourne la configuration par défaut"""
        try:
            config = self.get_queryset().get(is_default=True)
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except RevisionSessionConfig.DoesNotExist:
            return Response({
                'error': 'Aucune configuration par défaut définie'
            }, status=status.HTTP_404_NOT_FOUND)