# Generated manually to fix ID field sequence

from django.db import migrations, models, connection


def fix_id_sequence_postgresql(apps, schema_editor):
    """Fix sequence for PostgreSQL databases - Minimal safe approach"""
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            # Very minimal approach - just ensure sequence value is correct
            cursor.execute("""
                DO $$
                BEGIN
                    -- Only fix the sequence value if it exists
                    IF EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'authentication_user_id_seq') THEN
                        -- Just update the sequence value to be safe
                        PERFORM setval('authentication_user_id_seq', GREATEST(COALESCE((SELECT MAX(id) FROM authentication_user), 0) + 1, 1), false);
                    END IF;
                END $$;
            """)


def reverse_id_sequence_postgresql(apps, schema_editor):
    """Reverse sequence for PostgreSQL databases"""
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("""
                DO $$
                BEGIN
                    -- Drop the existing sequence if it exists
                    IF EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'authentication_user_id_seq') THEN
                        DROP SEQUENCE authentication_user_id_seq CASCADE;
                    END IF;
                    
                    -- Create a new sequence as bigint
                    CREATE SEQUENCE authentication_user_id_seq
                        AS bigint
                        START WITH 1
                        INCREMENT BY 1
                        NO MINVALUE
                        NO MAXVALUE
                        CACHE 1;
                    
                    -- Set the sequence to the current max + 1
                    PERFORM setval('authentication_user_id_seq', COALESCE((SELECT MAX(id) FROM authentication_user), 0) + 1, false);
                    
                    -- Alter the table to use the new sequence
                    ALTER TABLE authentication_user ALTER COLUMN id SET DEFAULT nextval('authentication_user_id_seq'::regclass);
                    
                    -- Make sure the sequence is owned by the table
                    ALTER SEQUENCE authentication_user_id_seq OWNED BY authentication_user.id;
                END $$;
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0020_alter_user_id'),
    ]

    operations = [
        # Use RunPython instead of RunSQL for database-specific logic
        migrations.RunPython(
            fix_id_sequence_postgresql,
            reverse_id_sequence_postgresql,
        ),
    ]