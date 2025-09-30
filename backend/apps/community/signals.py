# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ChatMessage, Notification, Profile
try:
    from app_manager.models import App, UserAppSettings
except ImportError:
    # Fallback if app_manager is not available
    App = None
    UserAppSettings = None

User = get_user_model()


@receiver(post_save, sender=ChatMessage)
def notify_receiver(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.receiver,
            content=f"New message from {instance.sender.user.username}: {instance.message[:50]}{'...' if len(instance.message) > 50 else ''}"
        )


@receiver(post_save, sender=User)
def create_community_profile_and_enable_apps(sender, instance, created, **kwargs):
    """
    Signal to create community profile and enable social apps for new users
    """
    if created and instance.is_active:
        # Create community profile
        profile, profile_created = Profile.objects.get_or_create(user=instance)
        
        if profile_created:
            # Set default bio
            name = instance.first_name or instance.username
            profile.bio = f"Hi! I'm {name}. I'm learning languages with Linguify and looking forward to connecting with other learners!"
            
            # Set default learning/teaching languages from user learning profile
            try:
                learning_profile = instance.learning_profile
                if learning_profile.target_language:
                    from apps.language_learning.models import LANGUAGE_CHOICES
                    lang_dict = dict(LANGUAGE_CHOICES)
                    target_lang_name = lang_dict.get(learning_profile.target_language, learning_profile.target_language)
                    profile.learning_languages = [target_lang_name]

                if learning_profile.native_language:
                    from apps.language_learning.models import LANGUAGE_CHOICES
                    lang_dict = dict(LANGUAGE_CHOICES)
                    native_lang_name = lang_dict.get(learning_profile.native_language, learning_profile.native_language)
                    profile.teaching_languages = [native_lang_name]
            except AttributeError:
                # Si pas de profil d'apprentissage, ignorer
                pass
            
            profile.save()
        
        # Enable Community and Chat apps by default
        if App is not None and UserAppSettings is not None:
            try:
                # Get or create apps
                community_app, _ = App.objects.get_or_create(
                    code='community',
                    defaults={
                        'display_name': 'Community',
                        'description': 'Connect with other language learners',
                        'icon_name': 'users',
                        'color': '#3B82F6',
                        'route_path': '/community',
                        'category': 'social',
                        'installable': True,
                        'is_enabled': True,
                    }
                )
                
                chat_app, _ = App.objects.get_or_create(
                    code='chat',
                    defaults={
                        'display_name': 'Chat',
                        'description': 'Real-time messaging with language partners',
                        'icon_name': 'message-circle',
                        'color': '#10B981',
                        'route_path': '/chat',
                        'category': 'communication',
                        'installable': True,
                        'is_enabled': True,
                    }
                )
                
                # Enable apps for user
                user_settings, _ = UserAppSettings.objects.get_or_create(user=instance)
                user_settings.enabled_apps.add(community_app, chat_app)
                
            except Exception as e:
                # Log error but don't fail user creation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to enable community apps for user {instance.username}: {e}")


@receiver(post_save, sender=User)
def update_community_profile_on_user_change(sender, instance, created, **kwargs):
    """
    Signal to update community profile when user language settings change
    """
    if not created and instance.is_active:
        try:
            profile = Profile.objects.get(user=instance)
            
            # Update teaching/learning languages if they changed
            updated = False
            
            # Get language information from UserLearningProfile
            try:
                learning_profile = instance.learning_profile

                if learning_profile.target_language:
                    from apps.language_learning.models import LANGUAGE_CHOICES
                    lang_dict = dict(LANGUAGE_CHOICES)
                    target_lang_name = lang_dict.get(learning_profile.target_language, learning_profile.target_language)
                    if not profile.learning_languages or target_lang_name not in profile.learning_languages:
                        profile.learning_languages = [target_lang_name]
                        updated = True

                if learning_profile.native_language:
                    from apps.language_learning.models import LANGUAGE_CHOICES
                    lang_dict = dict(LANGUAGE_CHOICES)
                    native_lang_name = lang_dict.get(learning_profile.native_language, learning_profile.native_language)
                    if not profile.teaching_languages or native_lang_name not in profile.teaching_languages:
                        profile.teaching_languages = [native_lang_name]
                        updated = True

            except Exception:
                # UserLearningProfile doesn't exist yet or other error
                pass
            
            if updated:
                profile.save()
                
        except Profile.DoesNotExist:
            # Create profile if it doesn't exist
            create_community_profile_and_enable_apps(sender, instance, True, **kwargs)
