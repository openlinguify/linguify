"""
Create LMS database if it doesn't exist
"""
import psycopg2
from psycopg2 import sql

# Connect to PostgreSQL server
conn_params = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'azerty',
    'database': 'postgres'  # Connect to default database
}

def create_database():
    conn = None
    cursor = None
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            ['db_linguify_lms_dev']
        )
        
        if cursor.fetchone():
            print("Database 'db_linguify_lms_dev' already exists")
        else:
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {} ENCODING 'UTF8'").format(
                    sql.Identifier('db_linguify_lms_dev')
                )
            )
            print("Database 'db_linguify_lms_dev' created successfully")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()