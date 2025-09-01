# Generated manually for adding Archive stage to existing users

from django.db import migrations
from django.db import models


def add_archive_stage_to_users(apps, schema_editor):
    """Add Archive stage to all existing users who don't have one"""
    PersonalStageType = apps.get_model('todo', 'PersonalStageType')
    User = apps.get_model('authentication', 'User')
    
    for user in User.objects.all():
        # Check if user already has Archive stage
        if not PersonalStageType.objects.filter(user=user, name='Archive').exists():
            # Get the highest sequence number for this user
            max_sequence = PersonalStageType.objects.filter(user=user).aggregate(
                max_seq=models.Max('sequence')
            )['max_seq'] or 0
            
            # Create Archive stage
            PersonalStageType.objects.create(
                user=user,
                name='Archive',
                sequence=max_sequence + 1,
                color='#6f42c1',
                is_closed=True,
                fold=True  # Default to folded
            )


def remove_archive_stage_from_users(apps, schema_editor):
    """Remove Archive stage from all users (reverse operation)"""
    PersonalStageType = apps.get_model('todo', 'PersonalStageType')
    PersonalStageType.objects.filter(name='Archive').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_alter_task_options_task_active_task_color_and_more'),
    ]

    operations = [
        migrations.RunPython(
            add_archive_stage_to_users,
            remove_archive_stage_from_users
        ),
    ]