# Generated for adding phone number field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_add_username_case_insensitive_constraint'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Phone number with country code (e.g., +32 123 456 789)', max_length=20, null=True),
        ),
    ]