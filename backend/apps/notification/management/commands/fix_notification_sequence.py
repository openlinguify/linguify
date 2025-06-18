"""
Management command to fix PostgreSQL sequence for notification tables
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix PostgreSQL sequence for notification tables'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # Fix notification_notificationsetting table
                self.fix_table_sequence(cursor, 'notification_notificationsetting')
                
                # Fix notification_notification table if it exists
                try:
                    self.fix_table_sequence(cursor, 'notification_notification')
                except Exception as e:
                    self.stdout.write(f"Skipping notification_notification: {e}")
                
                # Fix notification_notificationdevice table if it exists
                try:
                    self.fix_table_sequence(cursor, 'notification_notificationdevice')
                except Exception as e:
                    self.stdout.write(f"Skipping notification_notificationdevice: {e}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error fixing sequences: {str(e)}")
                )
                raise e

    def fix_table_sequence(self, cursor, table_name):
        """Fix sequence for a specific table"""
        self.stdout.write(f"🔧 Fixing sequence for {table_name}...")
        
        # Get the current max ID from the table
        cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}")
        max_id = cursor.fetchone()[0]
        
        self.stdout.write(f"📊 Current max ID in {table_name}: {max_id}")
        
        # Check if sequence exists
        cursor.execute(f"SELECT pg_get_serial_sequence('{table_name}', 'id')")
        sequence_name = cursor.fetchone()[0]
        
        if sequence_name:
            self.stdout.write(f"🔍 Found sequence: {sequence_name}")
            
            # Get current sequence value
            cursor.execute(f"SELECT last_value FROM {sequence_name}")
            current_seq_value = cursor.fetchone()[0]
            self.stdout.write(f"📈 Current sequence value: {current_seq_value}")
            
            # Reset sequence to max_id + 1
            new_seq_value = max_id + 1
            cursor.execute(f"SELECT setval('{sequence_name}', {new_seq_value}, false)")
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Successfully reset {table_name} sequence to {new_seq_value}")
            )
        else:
            self.stdout.write(f"⚠️  No sequence found for {table_name}. Creating sequence...")
            
            # Create sequence if it doesn't exist
            sequence_name = f"{table_name}_id_seq"
            cursor.execute(f"""
                CREATE SEQUENCE IF NOT EXISTS {sequence_name}
                AS integer
                START WITH 1
                INCREMENT BY 1
                NO MINVALUE
                NO MAXVALUE
                CACHE 1;
            """)
            
            # Set the sequence value
            new_seq_value = max_id + 1
            cursor.execute(f"SELECT setval('{sequence_name}', {new_seq_value}, false)")
            
            # Alter the table to use the sequence
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                ALTER COLUMN id SET DEFAULT nextval('{sequence_name}'::regclass);
            """)
            
            # Make sure the sequence is owned by the table
            cursor.execute(f"ALTER SEQUENCE {sequence_name} OWNED BY {table_name}.id;")
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Successfully created and set {table_name} sequence to {new_seq_value}")
            )