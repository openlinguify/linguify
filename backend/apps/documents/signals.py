from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Document, DocumentShare, DocumentComment, DocumentVersion
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=DocumentShare)
def notify_document_shared(sender, instance, created, **kwargs):
    """Send notification when document is shared"""
    if not created:
        return
        
    try:
        # Import here to avoid circular imports
        from apps.notification.services import NotificationService
        
        # Create notification for the user who received the share
        NotificationService.create_notification(
            user=instance.user,
            notification_type='document_shared',
            title=f'Document partagé: {instance.document.title}',
            message=f'{instance.shared_by.get_full_name() or instance.shared_by.username} a partagé le document "{instance.document.title}" avec vous.',
            data={
                'document_id': instance.document.id,
                'document_title': instance.document.title,
                'shared_by': instance.shared_by.username,
                'permission_level': instance.permission_level,
                'share_id': instance.id,
            }
        )
        
        logger.info(f"Notification sent for document share: {instance.id}")
        
    except ImportError:
        logger.warning("Notification service not available")
    except Exception as e:
        logger.error(f"Error sending notification for document share: {e}")


@receiver(post_save, sender=DocumentComment)
def notify_document_comment(sender, instance, created, **kwargs):
    """Send notification when comment is added to document"""
    if not created:
        return
        
    try:
        from apps.notification.services import NotificationService
        
        # Notify document owner if they're not the comment author
        if instance.document.owner != instance.author:
            NotificationService.create_notification(
                user=instance.document.owner,
                notification_type='document_comment',
                title=f'Nouveau commentaire: {instance.document.title}',
                message=f'{instance.author.get_full_name() or instance.author.username} a ajouté un commentaire sur "{instance.document.title}".',
                data={
                    'document_id': instance.document.id,
                    'document_title': instance.document.title,
                    'comment_id': instance.id,
                    'comment_author': instance.author.username,
                }
            )
        
        # Notify other collaborators (with edit or admin permissions)
        collaborators = User.objects.filter(
            document_shares__document=instance.document,
            document_shares__permission_level__in=['edit', 'admin']
        ).exclude(
            id__in=[instance.author.id, instance.document.owner.id]
        ).distinct()
        
        for collaborator in collaborators:
            NotificationService.create_notification(
                user=collaborator,
                notification_type='document_comment',
                title=f'Nouveau commentaire: {instance.document.title}',
                message=f'{instance.author.get_full_name() or instance.author.username} a ajouté un commentaire sur "{instance.document.title}".',
                data={
                    'document_id': instance.document.id,
                    'document_title': instance.document.title,
                    'comment_id': instance.id,
                    'comment_author': instance.author.username,
                }
            )
        
        logger.info(f"Notifications sent for document comment: {instance.id}")
        
    except ImportError:
        logger.warning("Notification service not available")
    except Exception as e:
        logger.error(f"Error sending notification for document comment: {e}")


@receiver(pre_save, sender=Document)
def create_document_version(sender, instance, **kwargs):
    """Create version snapshot before document content changes"""
    if not instance.pk:  # New document, no version needed
        return
        
    try:
        # Get the old document content
        old_document = Document.objects.get(pk=instance.pk)
        
        # Check if content has actually changed
        if old_document.content != instance.content:
            # Get next version number
            version_number = instance.versions.count() + 1
            
            # Create version snapshot
            DocumentVersion.objects.create(
                document=instance,
                content=old_document.content,
                version_number=version_number,
                created_by=instance.last_edited_by or instance.owner,
                notes=f'Version automatique #{version_number}'
            )
            
            logger.info(f"Created version {version_number} for document: {instance.id}")
            
    except Document.DoesNotExist:
        # Document doesn't exist yet, skip version creation
        pass
    except Exception as e:
        logger.error(f"Error creating document version: {e}")


@receiver(post_save, sender=Document)
def notify_document_updated(sender, instance, created, **kwargs):
    """Notify collaborators when document is updated"""
    if created:  # Don't notify on document creation
        return
        
    try:
        from apps.notification.services import NotificationService
        
        # Don't notify if the document was just created
        if not hasattr(instance, '_old_updated_at'):
            return
            
        # Notify collaborators about the update
        collaborators = User.objects.filter(
            document_shares__document=instance
        ).exclude(
            id=instance.last_edited_by.id if instance.last_edited_by else None
        ).distinct()
        
        for collaborator in collaborators:
            NotificationService.create_notification(
                user=collaborator,
                notification_type='document_updated',
                title=f'Document mis à jour: {instance.title}',
                message=f'Le document "{instance.title}" a été modifié par {instance.last_edited_by.get_full_name() or instance.last_edited_by.username}.',
                data={
                    'document_id': instance.id,
                    'document_title': instance.title,
                    'updated_by': instance.last_edited_by.username if instance.last_edited_by else 'Inconnu',
                }
            )
        
        logger.info(f"Update notifications sent for document: {instance.id}")
        
    except ImportError:
        logger.warning("Notification service not available")
    except Exception as e:
        logger.error(f"Error sending update notifications: {e}")


@receiver(post_delete, sender=DocumentShare)
def notify_document_unshared(sender, instance, **kwargs):
    """Send notification when document access is revoked"""
    try:
        from apps.notification.services import NotificationService
        
        # Notify the user whose access was revoked
        NotificationService.create_notification(
            user=instance.user,
            notification_type='document_unshared',
            title=f'Accès révoqué: {instance.document.title}',
            message=f'Votre accès au document "{instance.document.title}" a été révoqué.',
            data={
                'document_title': instance.document.title,
                'permission_level': instance.permission_level,
            }
        )
        
        logger.info(f"Unshare notification sent for document share: {instance.id}")
        
    except ImportError:
        logger.warning("Notification service not available")
    except Exception as e:
        logger.error(f"Error sending unshare notification: {e}")


# Signal to track document updates for notifications
@receiver(pre_save, sender=Document)
def track_document_changes(sender, instance, **kwargs):
    """Track changes to determine if notifications should be sent"""
    if instance.pk:
        try:
            old_instance = Document.objects.get(pk=instance.pk)
            instance._old_updated_at = old_instance.updated_at
        except Document.DoesNotExist:
            pass