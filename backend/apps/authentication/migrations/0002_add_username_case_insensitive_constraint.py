# Generated manually for username case-insensitive constraint

from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),  # Ajustez selon votre dernière migration
    ]

    operations = [
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(
                Lower('username'),
                name='unique_username_case_insensitive',
                violation_error_message='Username already exists.'
            ),
        ),
    ]