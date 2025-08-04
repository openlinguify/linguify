"""
Script to clean up migration issues for LMS project
"""
import psycopg2
from psycopg2 import sql
import os
from pathlib import Path

# Get database config from environment
db_config = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'azerty',  # Your postgres password
    'database': 'db_linguify_lms_dev'
}

def clean_database():
    """Drop all tables in the database"""
    conn = psycopg2.connect(**db_config)
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        # First, specifically drop django_migrations table
        print("Dropping django_migrations table...")
        cursor.execute("DROP TABLE IF EXISTS django_migrations CASCADE")
        
        # Get all table names
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()
        
        # Drop all tables
        for table in tables:
            table_name = table[0]
            print(f"Dropping table: {table_name}")
            cursor.execute(
                sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                    sql.Identifier(table_name)
                )
            )
        
        print("All tables dropped successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def delete_migration_files():
    """Delete all migration files except __init__.py"""
    lms_path = Path(__file__).parent
    apps_path = lms_path / 'apps'
    
    for app_dir in apps_path.iterdir():
        if app_dir.is_dir():
            migrations_dir = app_dir / 'migrations'
            if migrations_dir.exists():
                for migration_file in migrations_dir.iterdir():
                    if migration_file.name != '__init__.py' and migration_file.suffix == '.py':
                        print(f"Deleting migration: {migration_file}")
                        migration_file.unlink()

if __name__ == "__main__":
    print("Cleaning LMS database and migrations...")
    
    # Clean database
    clean_database()
    
    # Delete migration files
    delete_migration_files()
    
    print("\nDone! Now you can run:")
    print("1. python manage.py --project=lms makemigrations")
    print("2. python manage.py --project=lms migrate")