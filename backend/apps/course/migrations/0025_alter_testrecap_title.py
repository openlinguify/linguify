from django.db import migrations


class Migration(migrations.Migration):
    """Migration to recognize title field is already non-nullable."""
    
    dependencies = [
        ('course', '0024_update_testrecap_title_values'),
    ]

    operations = [
        # No operations needed - title field is already NOT NULL
    ]