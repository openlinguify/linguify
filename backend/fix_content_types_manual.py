import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction

def fix_content_types():
    with transaction.atomic():
        with connection.cursor() as cursor:
            # Get current max ID
            cursor.execute("SELECT MAX(id) FROM django_content_type;")
            max_id = cursor.fetchone()[0] or 0
            next_id = max_id + 1
            
            print(f"Current max content type ID: {max_id}")
            print(f"Starting from ID: {next_id}")
            
            # Define the content types we need to create
            content_types = [
                ('quizz', 'quiz'),
                ('quizz', 'question'),
                ('quizz', 'answer'),
                ('quizz', 'quizsession'),
                ('quizz', 'quizresult'),
            ]
            
            # Create content types manually with explicit IDs
            for app_label, model in content_types:
                # Check if it already exists
                cursor.execute(
                    "SELECT id FROM django_content_type WHERE app_label = %s AND model = %s",
                    [app_label, model]
                )
                exists = cursor.fetchone()
                
                if not exists:
                    cursor.execute(
                        "INSERT INTO django_content_type (id, app_label, model) VALUES (%s, %s, %s)",
                        [next_id, app_label, model]
                    )
                    print(f"Created content type: {app_label}.{model} with ID {next_id}")
                    next_id += 1
                else:
                    print(f"Content type {app_label}.{model} already exists with ID {exists[0]}")
            
            # Update the sequence to the correct next value
            cursor.execute(f"SELECT setval('django_content_type_id_seq', {next_id}, false);")
            print(f"Updated sequence to start from {next_id}")
            
            print("Content types fixed!")

if __name__ == "__main__":
    try:
        fix_content_types()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()