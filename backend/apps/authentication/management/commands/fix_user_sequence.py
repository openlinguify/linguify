"""
Management command to fix PostgreSQL sequence for authentication_user table
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix PostgreSQL sequence for authentication_user table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # Get the current max ID from the table
                cursor.execute("SELECT COALESCE(MAX(id), 0) FROM authentication_user")
                max_id = cursor.fetchone()[0]
                
                self.stdout.write(f"Current max ID in authentication_user: {max_id}")
                
                # Check if sequence exists
                cursor.execute("SELECT pg_get_serial_sequence('authentication_user', 'id')")
                sequence_name = cursor.fetchone()[0]
                
                if sequence_name:
                    self.stdout.write(f"Found sequence: {sequence_name}")
                    
                    # Get current sequence value
                    cursor.execute(f"SELECT last_value FROM {sequence_name}")
                    current_seq_value = cursor.fetchone()[0]
                    self.stdout.write(f"Current sequence value: {current_seq_value}")
                    
                    # Reset sequence to max_id + 1
                    new_seq_value = max_id + 1
                    cursor.execute(f"SELECT setval('{sequence_name}', {new_seq_value}, false)")
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully reset sequence to {new_seq_value}")
                    )
                else:
                    self.stdout.write("No sequence found. Creating sequence...")
                    
                    # Create sequence if it doesn't exist
                    cursor.execute("""
                        CREATE SEQUENCE IF NOT EXISTS authentication_user_id_seq
                        AS integer
                        START WITH 1
                        INCREMENT BY 1
                        NO MINVALUE
                        NO MAXVALUE
                        CACHE 1;
                    """)
                    
                    # Set the sequence value
                    new_seq_value = max_id + 1
                    cursor.execute(f"SELECT setval('authentication_user_id_seq', {new_seq_value}, false)")
                    
                    # Alter the table to use the sequence
                    cursor.execute("""
                        ALTER TABLE authentication_user 
                        ALTER COLUMN id SET DEFAULT nextval('authentication_user_id_seq'::regclass);
                    """)
                    
                    # Make sure the sequence is owned by the table
                    cursor.execute("ALTER SEQUENCE authentication_user_id_seq OWNED BY authentication_user.id;")
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully created and set sequence to {new_seq_value}")
                    )
                
                # Verify the fix by testing sequence generation
                cursor.execute("SELECT nextval('authentication_user_id_seq')")
                next_id = cursor.fetchone()[0]
                self.stdout.write(f"Next ID will be: {next_id}")
                
                # Reset the sequence back to where it should be
                cursor.execute(f"SELECT setval('authentication_user_id_seq', {max_id + 1}, false)")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error fixing sequence: {str(e)}")
                )
                raise e