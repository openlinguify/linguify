#!/usr/bin/env python3
"""
Script to fix user registration ID sequence issue
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

def fix_user_sequence():
    """Fix the PostgreSQL sequence for authentication_user table"""
    
    print("🔧 Fixing PostgreSQL sequence for authentication_user table...")
    
    with connection.cursor() as cursor:
        try:
            # Get the current max ID from the table
            cursor.execute("SELECT COALESCE(MAX(id), 0) FROM authentication_user")
            max_id = cursor.fetchone()[0]
            
            print(f"📊 Current max ID in authentication_user: {max_id}")
            
            # Check if sequence exists
            cursor.execute("SELECT pg_get_serial_sequence('authentication_user', 'id')")
            sequence_name = cursor.fetchone()[0]
            
            if sequence_name:
                print(f"🔍 Found sequence: {sequence_name}")
                
                # Get current sequence value
                cursor.execute(f"SELECT last_value FROM {sequence_name}")
                current_seq_value = cursor.fetchone()[0]
                print(f"📈 Current sequence value: {current_seq_value}")
                
                # Reset sequence to max_id + 1
                new_seq_value = max_id + 1
                cursor.execute(f"SELECT setval('{sequence_name}', {new_seq_value}, false)")
                
                print(f"✅ Successfully reset sequence to {new_seq_value}")
            else:
                print("⚠️  No sequence found. Creating sequence...")
                
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
                
                print(f"✅ Successfully created and set sequence to {new_seq_value}")
            
            # Verify the fix by testing sequence generation
            cursor.execute("SELECT nextval('authentication_user_id_seq')")
            next_id = cursor.fetchone()[0]
            print(f"🆔 Next ID will be: {next_id}")
            
            # Reset the sequence back to where it should be
            cursor.execute(f"SELECT setval('authentication_user_id_seq', {max_id + 1}, false)")
            
            print("🎉 PostgreSQL sequence has been fixed!")
            
        except Exception as e:
            print(f"❌ Error fixing sequence: {str(e)}")
            raise e

if __name__ == "__main__":
    fix_user_sequence()