# authentication/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserSetting, StudentProfile, TeacherProfile

# Signals for creating user profiles automatically
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.user_type == 'teacher':
            TeacherProfile.objects.create(user=instance)
        UserSetting.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'student':
            instance.student_profile.save()
        elif instance.user_type == 'teacher':
            instance.teacher_profile.save()

        # Ensure settings are properly created if they don't exist
        if not hasattr(instance, 'settings'):
            UserSetting.objects.create(user=instance)
        else:
            instance.settings.save()