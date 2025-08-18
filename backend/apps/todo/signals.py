from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Task, Project, Category, Tag, PersonalStageType

User = get_user_model()


@receiver(post_save, sender=Task)
def update_project_progress(sender, instance, **kwargs):
    """Update project progress when a task is saved"""
    if instance.project:
        instance.project.update_progress()


@receiver(post_delete, sender=Task)
def update_project_progress_on_delete(sender, instance, **kwargs):
    """Update project progress when a task is deleted"""
    if instance.project:
        instance.project.update_progress()


@receiver(post_save, sender=User)
def create_default_categories_and_onboarding(sender, instance, created, **kwargs):
    """Create default categories and onboarding for new users - Open Linguify inspired"""
    if created:
        # Create personal stages first
        PersonalStageType.create_default_stages(instance)
        
        # Create default categories
        default_categories = [
            {'name': 'Personal', 'color': '#6366f1', 'icon': 'bi-person'},
            {'name': 'Work', 'color': '#059669', 'icon': 'bi-briefcase'},
            {'name': 'Study', 'color': '#dc2626', 'icon': 'bi-book'},
            {'name': 'Health', 'color': '#7c3aed', 'icon': 'bi-heart'},
            {'name': 'Finance', 'color': '#ea580c', 'icon': 'bi-currency-dollar'},
        ]
        
        for cat_data in default_categories:
            Category.objects.create(
                user=instance,
                **cat_data
            )
        
        # Create onboarding todo
        Task.ensure_onboarding_todo(instance)


@receiver(post_save, sender=User)
def create_default_tags(sender, instance, created, **kwargs):
    """Create default tags for new users"""
    if created:
        default_tags = [
            {'name': 'urgent', 'color': '#dc2626'},
            {'name': 'meeting', 'color': '#059669'},
            {'name': 'idea', 'color': '#7c3aed'},
            {'name': 'review', 'color': '#ea580c'},
            {'name': 'waiting', 'color': '#6b7280'},
            {'name': 'someday', 'color': '#06b6d4'},
        ]
        
        for tag_data in default_tags:
            Tag.objects.create(
                user=instance,
                **tag_data
            )