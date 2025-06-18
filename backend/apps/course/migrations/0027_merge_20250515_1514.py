from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration merges the parallel migration paths:
    - 0025_alter_testrecap_title -> 0026_testrecap_question
    - 0025_testrecapquestion_testrecapresult
    
    It ensures both model changes and database schema are properly aligned.
    """

    dependencies = [
        ('course', '0025_testrecapquestion_testrecapresult'),
        ('course', '0026_testrecap_question'),
    ]

    operations = [
        # No operations needed - just merging migration paths
    ]