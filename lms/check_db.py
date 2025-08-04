"""
Check what tables exist in the database
"""
import psycopg2

db_config = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'azerty',
    'database': 'db_linguify_lms_dev'
}

def check_tables():
    """List all tables in the database"""
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        # Get all table names
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        tables = cursor.fetchall()
        
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Check django_migrations content
        cursor.execute("SELECT COUNT(*) FROM django_migrations")
        count = cursor.fetchone()[0]
        print(f"\ndjango_migrations has {count} entries")
        
        if count > 0:
            cursor.execute("SELECT app, name FROM django_migrations ORDER BY id")
            migrations = cursor.fetchall()
            print("\nMigrations applied:")
            for app, name in migrations:
                print(f"  - {app}: {name}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_tables()