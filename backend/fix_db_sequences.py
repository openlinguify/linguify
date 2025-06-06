#!/usr/bin/env python
"""
Script to fix PostgreSQL sequences that are causing null ID constraint violations
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

def fix_sequences():
    """Fix all auto-increment sequences in the database"""
    with connection.cursor() as cursor:
        print("Fixing database sequences...")
        
        # Get all tables with auto-increment IDs
        cursor.execute("""
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE column_default LIKE 'nextval%' 
            AND table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables_with_sequences = cursor.fetchall()
        
        for table_name, column_name in tables_with_sequences:
            print(f"Fixing sequence for {table_name}.{column_name}")
            
            # Get the sequence name
            cursor.execute(f"SELECT pg_get_serial_sequence('{table_name}', '{column_name}');")
            sequence_result = cursor.fetchone()
            if sequence_result and sequence_result[0]:
                sequence_name = sequence_result[0]
                
                # Get the current max ID
                cursor.execute(f"SELECT COALESCE(MAX({column_name}), 0) FROM {table_name};")
                max_id = cursor.fetchone()[0]
                
                # Reset the sequence
                cursor.execute(f"SELECT setval('{sequence_name}', {max_id + 1}, false);")
                print(f"  - Set {sequence_name} to {max_id + 1}")
            else:
                print(f"  - No sequence found for {table_name}.{column_name}")
        
        print("\nSequence fix completed!")
        
        # Show current sequence values
        print("\nCurrent sequence values:")
        cursor.execute("""
            SELECT schemaname, sequencename, last_value 
            FROM pg_sequences 
            WHERE schemaname = 'public' 
            ORDER BY sequencename;
        """)
        
        for schema, seq_name, last_val in cursor.fetchall():
            print(f"  {seq_name}: {last_val}")

if __name__ == "__main__":
    try:
        fix_sequences()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)