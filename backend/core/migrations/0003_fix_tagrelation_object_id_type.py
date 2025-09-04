# Generated migration to fix TagRelation object_id field type

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_create_global_tags_system'),
    ]

    operations = [
        # Change object_id from CharField to UUIDField
        migrations.AlterField(
            model_name='tagrelation',
            name='object_id',
            field=models.UUIDField(help_text="ID de l'objet taggé"),
        ),
    ]