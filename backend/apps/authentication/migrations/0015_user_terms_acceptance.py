# Generated manually for terms acceptance tracking

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0014_ensure_deletion_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='terms_accepted',
            field=models.BooleanField(default=False, help_text='Whether the user has accepted the terms and conditions'),
        ),
        migrations.AddField(
            model_name='user',
            name='terms_accepted_at',
            field=models.DateTimeField(blank=True, help_text='When the user accepted the terms and conditions', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='terms_version',
            field=models.CharField(blank=True, default='v1.0', help_text='Version of terms that was accepted', max_length=10, null=True),
        ),
    ]