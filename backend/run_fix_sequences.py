import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    print("Fixing django_content_type sequence...")
    cursor.execute("SELECT setval(pg_get_serial_sequence('django_content_type', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM django_content_type;")
    
    print("Fixing auth_permission sequence...")
    cursor.execute("SELECT setval(pg_get_serial_sequence('auth_permission', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM auth_permission;")
    
    print("Sequences fixed!")