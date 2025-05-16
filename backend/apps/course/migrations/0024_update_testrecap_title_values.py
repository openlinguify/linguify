from django.db import migrations


class Migration(migrations.Migration):
    """Migration to recognize title field values (already populated)."""
    
    dependencies = [
        ('course', '0023_testrecap_title'),
    ]

    operations = [
        # No operations needed - values are already populated
    ]