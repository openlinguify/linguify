from django.db import migrations, models
from django.db.utils import ProgrammingError, OperationalError


def check_question_field_exists(apps, schema_editor):
    """Check if question field already exists in the TestRecap table."""
    db = schema_editor.connection.alias
    cursor = schema_editor.connection.cursor()
    
    try:
        # Use database-agnostic approach to check if field exists
        if schema_editor.connection.vendor == 'sqlite':
            # SQLite approach
            cursor.execute("PRAGMA table_info(course_testrecap)")
            columns = cursor.fetchall()
            question_exists = any(col[1] == 'question' for col in columns)
        else:
            # PostgreSQL/MySQL approach
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
    except (ProgrammingError, OperationalError):
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