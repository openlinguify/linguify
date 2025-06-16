# Generated manually to fix ID field sequence

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0020_alter_user_id'),
    ]

    operations = [
        # Change the id field from BigAutoField to AutoField
        migrations.RunSQL(
            # Forward SQL - convert BigAutoField to AutoField
            """
            -- First, check if we need to recreate the sequence
            DO $$
            BEGIN
                -- Drop the existing sequence if it exists
                IF EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'authentication_user_id_seq') THEN
                    DROP SEQUENCE authentication_user_id_seq CASCADE;
                END IF;
                
                -- Create a new sequence as regular integer (not bigint)
                CREATE SEQUENCE authentication_user_id_seq
                    AS integer
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
            """,
            # Reverse SQL - convert back to BigAutoField if needed
            """
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
            """
        ),
    ]