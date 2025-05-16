from django.db import migrations


class Migration(migrations.Migration):
    """Migration to recognize the existing title field in TestRecap model."""
    
    dependencies = [
        ('course', '0022_alter_matchingexercise_id_alter_vocabularylist_id'),
    ]

    operations = [
        # No operations needed - title field already exists in the database
    ]