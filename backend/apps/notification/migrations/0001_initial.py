# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_enabled', models.BooleanField(default=True)),
                ('email_frequency', models.CharField(choices=[('immediately', 'Immediately'), ('daily', 'Daily Digest'), ('weekly', 'Weekly Digest'), ('never', 'Never')], default='immediately', max_length=20)),
                ('push_enabled', models.BooleanField(default=True)),
                ('web_enabled', models.BooleanField(default=True)),
                ('lesson_reminders', models.BooleanField(default=True, help_text='Reminders to complete lessons')),
                ('flashcard_reminders', models.BooleanField(default=True, help_text='Reminders to review flashcards')),
                ('achievement_notifications', models.BooleanField(default=True, help_text='Notifications for achievements')),
                ('streak_notifications', models.BooleanField(default=True, help_text='Notifications about streaks')),
                ('system_notifications', models.BooleanField(default=True, help_text='System notifications')),
                ('quiet_hours_enabled', models.BooleanField(default=False)),
                ('quiet_hours_start', models.TimeField(default='22:00')),
                ('quiet_hours_end', models.TimeField(default='08:00')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['user'], name='notificatio_user_id_06a9b0_idx')],
            },
        ),
        migrations.CreateModel(
            name='NotificationDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_token', models.TextField(unique=True)),
                ('device_type', models.CharField(choices=[('ios', 'iOS'), ('android', 'Android'), ('web', 'Web')], max_length=20)),
                ('device_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_devices', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'device_token')},
                'indexes': [models.Index(fields=['user', 'is_active'], name='notificatio_user_id_a0ca64_idx')],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('info', 'Informational'), ('success', 'Success'), ('warning', 'Warning'), ('error', 'Error'), ('lesson_reminder', 'Lesson Reminder'), ('flashcard', 'Flashcard Reminder'), ('streak', 'Streak'), ('achievement', 'Achievement'), ('system', 'System'), ('progress', 'Progress')], default='info', max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', max_length=10)),
                ('data', models.JSONField(blank=True, help_text='Optional additional data related to the notification', null=True)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', 'is_read'], name='notificatio_user_id_f18226_idx'), 
                    models.Index(fields=['user', 'created_at'], name='notificatio_user_id_b86e44_idx'), 
                    models.Index(fields=['user', 'type'], name='notificatio_user_id_3e44eb_idx')
                ],
            },
        ),
    ]