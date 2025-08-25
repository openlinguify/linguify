# Generated migration for transitioning to global tags system

from django.db import migrations, models
import uuid


def migrate_tags_to_global_system(apps, schema_editor):
    """
    Migrate existing notebook tags to the global tag system
    """
    # Get models from the current migration state
    NotebookTag = apps.get_model('notebook', 'Tag')
    Note = apps.get_model('notebook', 'Note')
    GlobalTag = apps.get_model('core', 'Tag')
    TagRelation = apps.get_model('core', 'TagRelation')
    
    # Create a mapping from old tags to new global tags
    tag_mapping = {}
    
    # Migrate all existing notebook tags to global tags
    for old_tag in NotebookTag.objects.all():
        # Check if a global tag with the same name already exists for this user
        global_tag, created = GlobalTag.objects.get_or_create(
            user=old_tag.user,
            name=old_tag.name,
            defaults={
                'color': old_tag.color,
                'description': f'Migrated from notebook app'
            }
        )
        
        # Update usage counter for notebook app
        if created:
            global_tag.usage_count_notebook = old_tag.note_set.count()
            global_tag.usage_count_total = global_tag.usage_count_notebook
            global_tag.save()
        else:
            # If tag already exists, add to the notebook usage counter
            global_tag.usage_count_notebook += old_tag.note_set.count()
            global_tag.usage_count_total += old_tag.note_set.count()
            global_tag.save()
        
        tag_mapping[old_tag.id] = global_tag
    
    # Create TagRelations for all note-tag relationships
    for note in Note.objects.prefetch_related('tags').all():
        for old_tag in note.tags.all():
            global_tag = tag_mapping[old_tag.id]
            
            # Create TagRelation
            TagRelation.objects.get_or_create(
                tag=global_tag,
                app_name='notebook',
                model_name='Note',
                object_id=str(note.id),
                defaults={'created_by': note.user}
            )


def reverse_migration(apps, schema_editor):
    """
    Reverse migration - recreate local tags from global system
    This is complex and may result in data loss, so we'll keep it simple
    """
    # We'll just clear the TagRelations for notebook
    TagRelation = apps.get_model('core', 'TagRelation')
    TagRelation.objects.filter(app_name='notebook', model_name='Note').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('notebook', '0006_alter_note_example_sentences_and_more'),
        ('core', '0002_create_global_tags_system'),  # Depends on the global tags system
    ]

    operations = [
        # First, run the data migration before removing the field
        migrations.RunPython(migrate_tags_to_global_system, reverse_migration),
        
        # Remove the ManyToMany field
        migrations.RemoveField(
            model_name='note',
            name='tags',
        ),
        
        # Delete the Tag model
        migrations.DeleteModel(
            name='Tag',
        ),
    ]