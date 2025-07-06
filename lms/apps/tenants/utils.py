"""
Utility functions for managing tenant databases
"""

import psycopg2
from psycopg2 import sql
from django.conf import settings
from django.core.management import call_command
from django.db import connections, transaction
import logging

logger = logging.getLogger(__name__)


def create_tenant_database(organization):
    """
    Create a new database for an organization
    """
    db_name = organization.database_name
    
    # Get connection parameters from default database
    default_db = settings.DATABASES['default']
    
    # Connect to PostgreSQL (to the postgres database)
    conn_params = {
        'host': default_db['HOST'],
        'port': default_db['PORT'],
        'user': default_db['USER'],
        'password': default_db['PASSWORD'],
        'database': 'postgres'  # Connect to postgres database to create new DB
    }
    
    conn = None
    cursor = None
    
    try:
        # Create database
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            [db_name]
        )
        
        if cursor.fetchone():
            logger.warning(f"Database {db_name} already exists")
            return False
        
        # Create the database
        cursor.execute(
            sql.SQL("CREATE DATABASE {} ENCODING 'UTF8'").format(
                sql.Identifier(db_name)
            )
        )
        
        logger.info(f"Created database {db_name}")
        
        # Add database configuration
        new_db_config = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': default_db['USER'],
            'PASSWORD': default_db['PASSWORD'],
            'HOST': default_db['HOST'],
            'PORT': default_db['PORT'],
            'TIME_ZONE': getattr(settings, 'TIME_ZONE', 'UTC'),
            'OPTIONS': {},
            'ATOMIC_REQUESTS': False,
            'AUTOCOMMIT': True,
            'CONN_MAX_AGE': 0,
            'CONN_HEALTH_CHECKS': False,
        }
        
        # Add database to Django settings
        settings.DATABASES[db_name] = new_db_config
        
        # Update connections
        connections.databases[db_name] = new_db_config
        
        # Run migrations on the new database (only tenant apps)
        logger.info(f"Running migrations for {db_name}")
        
        # First, migrate core Django apps
        try:
            call_command(
                'migrate',
                database=db_name,
                app_label='contenttypes',
                verbosity=0,
                interactive=False
            )
            call_command(
                'migrate',
                database=db_name,
                app_label='auth',
                verbosity=0,
                interactive=False
            )
            call_command(
                'migrate',
                database=db_name,
                app_label='sessions',
                verbosity=0,
                interactive=False
            )
            
            # Then migrate tenant-specific apps
            tenant_apps = ['institutions', 'courses', 'students', 'instructors', 
                          'assessments', 'analytics', 'content', 'administration']
            
            for app in tenant_apps:
                try:
                    call_command(
                        'migrate',
                        database=db_name,
                        app_label=app,
                        verbosity=0,
                        interactive=False
                    )
                except Exception as e:
                    logger.warning(f"Could not migrate {app} to {db_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Migration error for {db_name}: {e}")
            # Continue anyway, database was created
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating database {db_name}: {str(e)}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def delete_tenant_database(organization):
    """
    Delete an organization's database
    WARNING: This permanently deletes all data!
    """
    db_name = organization.database_name
    
    # Get connection parameters
    default_db = settings.DATABASES['default']
    
    conn_params = {
        'host': default_db['HOST'],
        'port': default_db['PORT'],
        'user': default_db['USER'],
        'password': default_db['PASSWORD'],
        'database': 'postgres'
    }
    
    conn = None
    cursor = None
    
    try:
        # Close all connections to the database
        if db_name in connections:
            connections[db_name].close()
        
        # Connect and drop database
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Terminate existing connections
        cursor.execute(
            sql.SQL("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
            """),
            [db_name]
        )
        
        # Drop the database
        cursor.execute(
            sql.SQL("DROP DATABASE IF EXISTS {}").format(
                sql.Identifier(db_name)
            )
        )
        
        logger.info(f"Deleted database {db_name}")
        
        # Remove from Django settings
        if db_name in settings.DATABASES:
            del settings.DATABASES[db_name]
        if db_name in connections.databases:
            del connections.databases[db_name]
        
        return True
        
    except Exception as e:
        logger.error(f"Error deleting database {db_name}: {str(e)}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def clone_tenant_database(source_org, target_org):
    """
    Clone a database from one organization to another
    Useful for creating demo/test environments
    """
    source_db = source_org.database_name
    target_db = target_org.database_name
    
    # Get connection parameters
    default_db = settings.DATABASES['default']
    
    conn_params = {
        'host': default_db['HOST'],
        'port': default_db['PORT'],
        'user': default_db['USER'],
        'password': default_db['PASSWORD'],
        'database': 'postgres'
    }
    
    conn = None
    cursor = None
    
    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create target database as a copy of source
        cursor.execute(
            sql.SQL("CREATE DATABASE {} WITH TEMPLATE {} ENCODING 'UTF8'").format(
                sql.Identifier(target_db),
                sql.Identifier(source_db)
            )
        )
        
        logger.info(f"Cloned database {source_db} to {target_db}")
        
        # Add to Django settings
        settings.DATABASES[target_db] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': target_db,
            'USER': default_db['USER'],
            'PASSWORD': default_db['PASSWORD'],
            'HOST': default_db['HOST'],
            'PORT': default_db['PORT'],
        }
        
        connections.databases[target_db] = settings.DATABASES[target_db]
        
        return True
        
    except Exception as e:
        logger.error(f"Error cloning database: {str(e)}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


class TenantContext:
    """
    Context manager for executing code in a specific tenant context
    
    Usage:
        with TenantContext(organization):
            # All database operations here will use the organization's database
            Course.objects.all()
    """
    
    def __init__(self, organization):
        self.organization = organization
        self.previous_db = None
        
    def __enter__(self):
        from .db_router import get_current_database, set_current_database
        self.previous_db = get_current_database()
        set_current_database(self.organization.database_name)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        from .db_router import set_current_database, clear_current_database
        if self.previous_db and self.previous_db != 'default':
            set_current_database(self.previous_db)
        else:
            clear_current_database()