# Generated by Django 5.1.2 on 2025-05-06 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_alter_user_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='deletion_date',
            field=models.DateTimeField(blank=True, help_text='When the account will be permanently deleted', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='deletion_scheduled_at',
            field=models.DateTimeField(blank=True, help_text='When the account deletion was requested', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_pending_deletion',
            field=models.BooleanField(default=False, help_text='Whether the account is scheduled for deletion'),
        ),
    ]
