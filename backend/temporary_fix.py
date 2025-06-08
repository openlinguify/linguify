import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.core.management import call_command
from django.db import connection

print("Attempting to fix the migration issue...")

# First, let's try to manually create the content type entries
with connection.cursor() as cursor:
    try:
        # Check if quizz content types already exist
        cursor.execute("""
            SELECT id, app_label, model 
            FROM django_content_type 
            WHERE app_label = 'quizz'
        """)
        existing = cursor.fetchall()
        
        if existing:
            print(f"Found existing content types for quizz: {existing}")
            print("Deleting them to start fresh...")
            cursor.execute("DELETE FROM django_content_type WHERE app_label = 'quizz'")
        
        # Fix sequences before inserting
        cursor.execute("""
            SELECT setval(
                pg_get_serial_sequence('django_content_type', 'id'), 
                COALESCE((SELECT MAX(id) FROM django_content_type), 0) + 1, 
                false
            );
        """)
        
        print("Sequence fixed. Now try running migrations again.")
        
    except Exception as e:
        print(f"Error during fix: {e}")
        print("You may need to run these commands manually in dbshell:")
        print("DELETE FROM django_content_type WHERE app_label = 'quizz';")
        print("SELECT setval(pg_get_serial_sequence('django_content_type', 'id'), (SELECT MAX(id) FROM django_content_type) + 1);")