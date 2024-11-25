from django.db.models.signals import post_save
from django.dispatch import receiver
from authentication.models import User, UserSetting, StudentProfile, TeacherProfile


# Signal to create user profiles and settings automatically
@receiver(post_save, sender=User)
def handle_user_creation(sender, instance, created, **kwargs):
    if created:
        # Create the appropriate profile based on the user type
        if instance.user_type == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.user_type == 'teacher':
            TeacherProfile.objects.create(user=instance)

        # Create user settings
        UserSetting.objects.create(user=instance)
    else:
        # Save the existing profile and settings if user is updated
        if instance.user_type == 'student' and hasattr(instance, 'student_profile'):
            instance.student_profile.save()
        elif instance.user_type == 'teacher' and hasattr(instance, 'teacher_profile'):
            instance.teacher_profile.save()

        # Save settings if they already exist, or create them if missing
        if not hasattr(instance, 'settings'):
            UserSetting.objects.create(user=instance)
        else:
            instance.settings.save()
