# backend/apps/course/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Lesson, Unit, LearningPath
from authentication.models import User

@receiver(post_save, sender=User)
def update_learning_path(sender, instance, **kwargs):
    learning_path, created = LearningPath.objects.get_or_create(user=instance)
    if learning_path.language != instance.target_language:
        learning_path.language = instance.target_language
        learning_path.save()

@receiver(post_save, sender=Lesson)
def update_unit_description_on_lesson_change(sender, instance, **kwargs):
    """
    Met à jour les descriptions de l'unité quand une leçon est ajoutée ou modifiée
    """
    if instance.unit:
        instance.unit.update_all_descriptions()

@receiver(post_delete, sender=Lesson)
def update_unit_description_on_lesson_delete(sender, instance, **kwargs):
    """
    Met à jour les descriptions de l'unité quand une leçon est supprimée
    """
    if instance.unit_id:
        try:
            unit = Unit.objects.get(id=instance.unit_id)
            unit.update_all_descriptions()
        except Unit.DoesNotExist:
            pass  # L'unité a peut-être été supprimée en cascade