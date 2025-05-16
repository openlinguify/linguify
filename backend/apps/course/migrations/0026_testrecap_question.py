from django.db import migrations, models
from django.db.utils import ProgrammingError


def check_question_field_exists(apps, schema_editor):
    """Check if question field already exists in the TestRecap table."""
    db = schema_editor.connection.alias
    cursor = schema_editor.connection.cursor()
    
    try:
        # First check if the field exists
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'course_testrecap' AND column_name = 'question'"
        )
        question_exists = bool(cursor.fetchone())
        
        # If field doesn't exist, create it
        if not question_exists:
            cursor.execute(
                "ALTER TABLE course_testrecap ADD COLUMN question VARCHAR(255) DEFAULT 'Test' NOT NULL"
            )
            cursor.execute(
                "UPDATE course_testrecap SET question = title_en WHERE question IS NULL"
            )
    except ProgrammingError:
        # Table might not exist yet, in which case we'll let the standard migration handle it
        pass


class Migration(migrations.Migration):
    """Migration to add question field to TestRecap model if it doesn't exist."""
    
    dependencies = [
        ('course', '0025_alter_testrecap_title'),
    ]

    operations = [
        migrations.RunPython(check_question_field_exists, migrations.RunPython.noop),
    ]