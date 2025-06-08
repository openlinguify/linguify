#!/usr/bin/env python3
"""
Simple script to fix PostgreSQL sequences without Django
"""
import os
import psycopg2
from urllib.parse import urlparse

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', '')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    print("Please set DATABASE_URL or create a .env file")
    exit(1)

# Parse DATABASE_URL
url = urlparse(DATABASE_URL)

# Connect to database
try:
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        database=url.path[1:],
        user=url.username,
        password=url.password
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Connected to database successfully")
    
    # Read and execute the SQL script
    with open('fix_sequences.sql', 'r') as f:
        sql_script = f.read()
    
    cursor.execute(sql_script)
    print("Sequences fixed successfully!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)