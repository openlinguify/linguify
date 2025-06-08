import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    print("Analyzing the problem...")
    
    # Check current max ID in django_content_type
    cursor.execute("SELECT MAX(id) FROM django_content_type;")
    max_id = cursor.fetchone()[0]
    print(f"Current max ID in django_content_type: {max_id}")
    
    # Get the sequence name
    cursor.execute("SELECT pg_get_serial_sequence('django_content_type', 'id');")
    seq_name = cursor.fetchone()[0]
    print(f"Sequence name: {seq_name}")
    
    # Check current sequence value
    cursor.execute(f"SELECT last_value FROM {seq_name};")
    last_value = cursor.fetchone()[0]
    print(f"Current sequence value: {last_value}")
    
    # Fix the sequence
    new_value = max(max_id + 1, 1) if max_id else 1
    cursor.execute(f"SELECT setval('{seq_name}', {new_value}, false);")
    print(f"Reset sequence to: {new_value}")
    
    # Do the same for auth_permission
    cursor.execute("SELECT MAX(id) FROM auth_permission;")
    max_id_perm = cursor.fetchone()[0]
    if max_id_perm:
        cursor.execute("SELECT pg_get_serial_sequence('auth_permission', 'id');")
        seq_name_perm = cursor.fetchone()[0]
        if seq_name_perm:
            new_value_perm = max_id_perm + 1
            cursor.execute(f"SELECT setval('{seq_name_perm}', {new_value_perm}, false);")
            print(f"Fixed auth_permission sequence to: {new_value_perm}")
    
    print("\nSequences fixed! Try running migrations again.")