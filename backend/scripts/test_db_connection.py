#!/usr/bin/env python
"""
Script to test database connection
Usage: python test_db_connection.py

This script reads DATABASE_URL from environment variables
"""
import os
import sys
import psycopg2
from psycopg2 import OperationalError

def test_database_connection():
    """Test database connection using DATABASE_URL from environment"""

    # Get DATABASE_URL from environment
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("✗ DATABASE_URL not found in environment variables")
        print("  Set it with: export DATABASE_URL='your_database_url'")
        return False

    # Don't print the actual URL for security
    print("Testing database connection...")
    print(f"Database URL found: [HIDDEN FOR SECURITY]")

    try:
        # Parse DATABASE_URL
        import re
        pattern = r'postgresql://([^:]+):([^@]+)@([^/]+)/(.+)'
        match = re.match(pattern, database_url)

        if not match:
            print("✗ Invalid DATABASE_URL format")
            return False

        user, password, host_port, dbname = match.groups()
        host = host_port.split(':')[0] if ':' in host_port else host_port
        port = host_port.split(':')[1] if ':' in host_port else '5432'

        print(f"Connecting to {host}/{dbname}...")

        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port,
            connect_timeout=10
        )

        cur = conn.cursor()

        # Test basic query
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✓ Connected successfully!")
        print(f"  PostgreSQL version: {version[0][:50]}...")

        # Check tables
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        table_count = cur.fetchone()[0]
        print(f"✓ Found {table_count} tables in database")

        # Check for Django tables
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'django_migrations'
            );
        """)
        django_exists = cur.fetchone()[0]

        if django_exists:
            print("✓ Django tables found")

            # Count migrations
            cur.execute("SELECT COUNT(*) FROM django_migrations;")
            migration_count = cur.fetchone()[0]
            print(f"  {migration_count} migrations applied")
        else:
            print("⚠ Django tables not found (migrations may need to be run)")

        cur.close()
        conn.close()

        return True

    except OperationalError as e:
        print(f"✗ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)

    success = test_database_connection()

    print("=" * 60)
    if success:
        print("✓ Test completed successfully!")
    else:
        print("✗ Test failed")
        print("\nTo set DATABASE_URL:")
        print("  export DATABASE_URL='postgresql://user:pass@host/dbname'")

    sys.exit(0 if success else 1)