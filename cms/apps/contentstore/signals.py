"""
Content store signals following OpenEdX patterns.
Handles automatic actions when content is created, updated, or deleted.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import CMSUnit, CMSChapter, CMSLesson
from .models import CourseSettings, CourseAsset


@receiver(post_save, sender=CMSUnit)
def create_course_settings(sender, instance, created, **kwargs):
    """
    Automatically create course settings when a new course is created.
    """
    if created:
        CourseSettings.objects.get_or_create(
            course_id=str(instance.id),
            defaults={
                'display_name': instance.title,
                'short_description': instance.description or '',
                'language': 'fr',
            }
        )


@receiver(post_save, sender=CMSUnit)
def update_course_sync_status(sender, instance, **kwargs):
    """
    Mark course for sync when it's published.
    """
    if instance.is_published and instance.sync_status == 'draft':
        instance.sync_status = 'pending'
        instance.save(update_fields=['sync_status'])


@receiver(pre_save, sender=CMSUnit)
def track_course_changes(sender, instance, **kwargs):
    """
    Track when course content changes to mark for re-sync.
    """
    if instance.pk:  # Only for existing courses
        try:
            old_instance = CMSUnit.objects.get(pk=instance.pk)
            
            # Check if important fields changed
            important_fields = [
                'title_en', 'title_fr', 'title_es', 'title_nl',
                'description_en', 'description_fr', 'description_es', 'description_nl',
                'level', 'price'
            ]
            
            fields_changed = any(
                getattr(old_instance, field) != getattr(instance, field)
                for field in important_fields
            )
            
            # If course is published and important fields changed, mark for re-sync
            if fields_changed and instance.is_published and instance.sync_status == 'synced':
                instance.sync_status = 'pending'
                
        except CMSUnit.DoesNotExist:
            pass


@receiver(post_save, sender=CMSChapter)
def mark_course_for_sync_on_chapter_change(sender, instance, **kwargs):
    """
    Mark course for sync when chapters are added or modified.
    """
    if instance.unit.is_published and instance.unit.sync_status == 'synced':
        instance.unit.sync_status = 'pending'
        instance.unit.save(update_fields=['sync_status'])


@receiver(post_save, sender=CMSLesson) 
def mark_course_for_sync_on_lesson_change(sender, instance, **kwargs):
    """
    Mark course for sync when lessons are added or modified.
    """
    if instance.unit.is_published and instance.unit.sync_status == 'synced':
        instance.unit.sync_status = 'pending'
        instance.unit.save(update_fields=['sync_status'])


@receiver(post_delete, sender=CMSChapter)
def mark_course_for_sync_on_chapter_delete(sender, instance, **kwargs):
    """
    Mark course for sync when chapters are deleted.
    """
    if instance.unit.is_published and instance.unit.sync_status == 'synced':
        instance.unit.sync_status = 'pending'
        instance.unit.save(update_fields=['sync_status'])


@receiver(post_delete, sender=CMSLesson)
def mark_course_for_sync_on_lesson_delete(sender, instance, **kwargs):
    """
    Mark course for sync when lessons are deleted.
    """
    if instance.unit.is_published and instance.unit.sync_status == 'synced':
        instance.unit.sync_status = 'pending'  
        instance.unit.save(update_fields=['sync_status'])


@receiver(post_delete, sender=CourseAsset)
def cleanup_asset_files(sender, instance, **kwargs):
    """
    Clean up asset files when asset is deleted.
    """
    # Delete main file
    if instance.file_path:
        try:
            instance.file_path.delete(save=False)
        except:
            pass
    
    # Delete thumbnail
    if instance.thumbnail:
        try:
            instance.thumbnail.delete(save=False)
        except:
            pass


@receiver(post_save, sender=CourseAsset)
def track_asset_usage(sender, instance, created, **kwargs):
    """
    Track asset usage for analytics (placeholder for future implementation).
    """
    if created:
        # Could implement analytics tracking here
        pass