from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ConversationMessage, AIConversation

@receiver(post_save, sender=ConversationMessage)
def update_conversation_timestamp(sender, instance, created, **kwargs):
    """Met à jour le timestamp de dernière activité de la conversation quand un nouveau message est créé."""
    if created:
        conversation = instance.conversation
        conversation.save()  # This will update the `last_activity` field via auto_now
        
        # Si c'est un message de l'utilisateur, nous pourrions déclencher une analyse linguistique ici
        if instance.message_type == 'user':
            # Placeholder for future language analysis function
            pass