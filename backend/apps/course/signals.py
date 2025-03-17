from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LearningPath
from authentication.models import User

@receiver(post_save, sender=User)
def update_learning_path(sender, instance, **kwargs):
    learning_path, created = LearningPath.objects.get_or_create(user=instance)
    if learning_path.language != instance.target_language:
        learning_path.language = instance.target_language
        learning_path.save()