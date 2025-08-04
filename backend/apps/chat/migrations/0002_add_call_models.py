# Generated migration for call models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('call_type', models.CharField(choices=[('audio', 'Audio'), ('video', 'Video')], default='audio', max_length=10)),
                ('status', models.CharField(choices=[('initiated', 'Initiated'), ('ringing', 'Ringing'), ('answered', 'Answered'), ('declined', 'Declined'), ('missed', 'Missed'), ('ended', 'Ended')], default='initiated', max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('duration', models.IntegerField(blank=True, help_text='Duration in seconds', null=True)),
                ('room_id', models.CharField(max_length=255, unique=True)),
                ('caller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calls_made', to=settings.AUTH_USER_MODEL)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calls', to='chat.conversation')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calls_received', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CallParticipant',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
                ('is_muted_audio', models.BooleanField(default=False)),
                ('is_muted_video', models.BooleanField(default=False)),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='chat.call')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]