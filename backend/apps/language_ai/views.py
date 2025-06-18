from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
import logging

from .models import ConversationTopic, AIConversation, ConversationMessage, ConversationFeedback
from .serializers import (
    ConversationTopicSerializer, AIConversationSerializer, ConversationMessageSerializer,
    ConversationFeedbackSerializer, ConversationDetailSerializer
)
from .ai_service import generate_ai_response  # Ce service sera défini plus tard

logger = logging.getLogger(__name__)

class ConversationTopicViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour les sujets de conversation disponibles."""
    queryset = ConversationTopic.objects.filter(is_active=True)
    serializer_class = ConversationTopicSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['language', 'difficulty']
    search_fields = ['name', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrer pour la langue cible de l'utilisateur connecté si spécifié
        user_target_language = self.request.query_params.get('user_language')
        if user_target_language:
            queryset = queryset.filter(language=user_target_language)
        return queryset


class AIConversationViewSet(viewsets.ModelViewSet):
    """API pour gérer les conversations avec l'IA."""
    serializer_class = AIConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'language', 'topic']
    ordering_fields = ['created_at', 'last_activity']
    ordering = ['-last_activity']

    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return AIConversationSerializer

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Envoyer un message à l'IA et obtenir une réponse."""
        conversation = self.get_object()
        
        # Valider que la conversation est active
        if conversation.status != 'active':
            return Response(
                {"detail": _("This conversation is not active.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Valider le contenu du message
        content = request.data.get('content')
        if not content or not content.strip():
            return Response(
                {"detail": _("Message content cannot be empty.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Enregistrer le message de l'utilisateur
        user_message = ConversationMessage.objects.create(
            conversation=conversation,
            message_type='user',
            content=content
        )
        
        try:
            # Générer la réponse de l'IA (appel à un service externe)
            ai_response = generate_ai_response(conversation, content)
            
            # Enregistrer la réponse de l'IA
            ai_message = ConversationMessage.objects.create(
                conversation=conversation,
                message_type='ai',
                content=ai_response.get('response', ''),
                detected_grammar_errors=ai_response.get('grammar_analysis', None),
                detected_vocabulary_level=ai_response.get('vocabulary_level', None)
            )
            
            # Préparer et renvoyer les deux messages
            messages = [
                ConversationMessageSerializer(user_message).data,
                ConversationMessageSerializer(ai_message).data
            ]
            
            return Response(messages, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            # Enregistrer un message d'erreur du système
            ConversationMessage.objects.create(
                conversation=conversation,
                message_type='system',
                content=_("Sorry, there was an error processing your request. Please try again.")
            )
            return Response(
                {"detail": _("Failed to generate AI response.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def end_conversation(self, request, pk=None):
        """Terminer une conversation et générer un résumé."""
        conversation = self.get_object()
        
        if conversation.status == 'completed':
            return Response(
                {"detail": _("This conversation is already completed.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le statut
        conversation.status = 'completed'
        
        # Générer un résumé de feedback si nécessaire
        if not conversation.feedback_summary and conversation.messages.count() > 1:
            try:
                # Ici nous pourrions appeler un service d'IA pour générer un résumé
                # conversation.feedback_summary = generate_feedback_summary(conversation)
                conversation.feedback_summary = _("Practice summary will be available soon.")
            except Exception as e:
                logger.error(f"Error generating feedback summary: {str(e)}")
        
        conversation.save()
        
        return Response(
            ConversationDetailSerializer(conversation).data,
            status=status.HTTP_200_OK
        )


class ConversationMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour accéder aux messages de conversation."""
    serializer_class = ConversationMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['message_type', 'conversation']

    def get_queryset(self):
        # N'autoriser l'accès qu'aux messages des conversations de l'utilisateur
        return ConversationMessage.objects.filter(
            conversation__user=self.request.user
        ).select_related('conversation')


class ConversationFeedbackViewSet(viewsets.ModelViewSet):
    """API pour les feedbacks sur les messages."""
    serializer_class = ConversationFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ConversationFeedback.objects.filter(
            message__conversation__user=self.request.user
        ).select_related('message', 'user')
    
    def create(self, request, *args, **kwargs):
        # Vérifier que l'utilisateur a accès au message
        message_id = request.data.get('message')
        try:
            message = ConversationMessage.objects.get(
                id=message_id,
                conversation__user=request.user
            )
        except ConversationMessage.DoesNotExist:
            return Response(
                {"detail": _("Message not found or not accessible.")},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return super().create(request, *args, **kwargs)