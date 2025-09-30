# Generated manually to add marketing_emails field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_email_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='marketing_emails',
            field=models.BooleanField(default=True, verbose_name='Receive the marketing emails'),
            preserve_default=True,
        ),
    ]