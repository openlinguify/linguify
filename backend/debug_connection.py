#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_dev')
django.setup()

from django.db import connections
from django.conf import settings

print("=== DEBUG INFORMATION ===")
print(f"Database settings: {settings.DATABASES}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

# Get the database connection
db_conn = connections['default']

# Print connection parameters
print("\n=== CONNECTION PARAMS ===")
print(f"Engine: {db_conn.settings_dict['ENGINE']}")
print(f"Name: {db_conn.settings_dict['NAME']}")
print(f"User: {db_conn.settings_dict['USER']}")
print(f"Host: {db_conn.settings_dict['HOST']}")
print(f"Port: {db_conn.settings_dict['PORT']}")
print(f"Options: {db_conn.settings_dict.get('OPTIONS', {})}")

# Try to get connection parameters that psycopg2 will use
try:
    import psycopg2
    
    # Build connection parameters
    conn_params = {
        'database': db_conn.settings_dict['NAME'],
        'user': db_conn.settings_dict['USER'],
        'password': db_conn.settings_dict['PASSWORD'],
        'host': db_conn.settings_dict['HOST'],
        'port': db_conn.settings_dict['PORT'],
    }
    
    print(f"\n=== PSYCOPG2 CONNECTION PARAMS ===")
    for key, value in conn_params.items():
        if key == 'password':
            print(f"{key}: [HIDDEN]")
        else:
            print(f"{key}: {value} (type: {type(value)}, repr: {repr(value)})")
    
    # Create DSN string manually to see what's at position 84
    dsn_parts = []
    for key, value in conn_params.items():
        dsn_parts.append(f"{key}={value}")
    dsn = " ".join(dsn_parts)
    
    print(f"\n=== DSN STRING ===")
    print(f"DSN: {dsn}")
    print(f"DSN length: {len(dsn)}")
    
    if len(dsn) > 84:
        print(f"Character at position 84: {repr(dsn[84])}")
        print(f"Characters around position 84: {repr(dsn[80:90])}")
    
    # Try to connect
    print(f"\n=== ATTEMPTING CONNECTION ===")
    conn = psycopg2.connect(**conn_params)
    print("Connection successful!")
    conn.close()
    
except Exception as e:
    print(f"\n=== ERROR ===")
    print(f"Error type: {type(e)}")
    print(f"Error message: {e}")
    
    # Try to get more details about the error
    if hasattr(e, 'args') and e.args:
        print(f"Error args: {e.args}")