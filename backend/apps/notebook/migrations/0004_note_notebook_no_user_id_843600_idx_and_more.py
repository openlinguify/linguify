# Generated by Django 5.1.2 on 2025-05-17 23:46

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notebook', '0003_alter_note_content'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='note',
            index=models.Index(fields=['user', 'is_archived'], name='notebook_no_user_id_843600_idx'),
        ),
        migrations.AddIndex(
            model_name='note',
            index=models.Index(fields=['user', 'is_pinned'], name='notebook_no_user_id_9c7857_idx'),
        ),
        migrations.AddIndex(
            model_name='note',
            index=models.Index(fields=['user', 'last_reviewed_at'], name='notebook_no_user_id_f0b7a1_idx'),
        ),
        migrations.AddIndex(
            model_name='note',
            index=models.Index(fields=['user', 'note_type'], name='notebook_no_user_id_c016e3_idx'),
        ),
        migrations.AddIndex(
            model_name='note',
            index=models.Index(fields=['language'], name='notebook_no_languag_76a521_idx'),
        ),
    ]
