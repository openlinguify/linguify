"""
Database router for LMS multi-tenant architecture.
Each organization gets its own database.
"""
import os
from django.conf import settings

class LMSMultiTenantRouter:
    """
    Database router for LMS multi-tenant system.
    Routes queries to organization-specific databases.
    """
    
    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        if hasattr(model._meta, 'app_label'):
            app_label = model._meta.app_label
            
            # LMS apps use tenant-specific databases
            if app_label in ['students', 'instructors', 'institutions', 'courses', 'assessments', 'analytics']:
                return self._get_tenant_db()
                
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        if hasattr(model._meta, 'app_label'):
            app_label = model._meta.app_label
            
            # LMS apps use tenant-specific databases
            if app_label in ['students', 'instructors', 'institutions', 'courses', 'assessments', 'analytics']:
                return self._get_tenant_db()
                
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same database."""
        db_set = {'default'}
        if hasattr(obj1, '_state'):
            db_set.add(obj1._state.db)
        if hasattr(obj2, '_state'):
            db_set.add(obj2._state.db)
        return len(db_set) == 1
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        
        # LMS apps only migrate to tenant databases
        if app_label in ['students', 'instructors', 'institutions', 'courses', 'assessments', 'analytics']:
            # Allow migration only if we're targeting a tenant database
            return db != 'default' and db.startswith('tenant_')
            
        # Default Django apps go to default database
        if app_label in ['auth', 'contenttypes', 'sessions', 'admin']:
            return db == 'default'
            
        # Tenant management goes to default
        if app_label == 'tenants':
            return db == 'default'
            
        return db == 'default'
    
    def _get_tenant_db(self):
        """Get the current tenant's database identifier."""
        # This would be set by middleware based on subdomain/request
        # For now, return a default tenant database
        from django.core.cache import cache
        
        tenant_id = cache.get('current_tenant_id', 'default')
        if tenant_id == 'default':
            return 'default'
        
        return f'tenant_{tenant_id}'


class TenantMiddleware:
    """
    Middleware to detect tenant from request and set database routing.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract tenant from subdomain or domain
        host = request.get_host().lower()
        
        # Example: harvard.lms.openlinguify.com -> tenant: harvard
        if '.lms.openlinguify.com' in host:
            tenant_subdomain = host.split('.lms.openlinguify.com')[0]
            tenant_id = tenant_subdomain
        else:
            tenant_id = 'default'
        
        # Store tenant context
        from django.core.cache import cache
        cache.set('current_tenant_id', tenant_id, 300)  # 5 minutes
        
        # Set tenant in request for views
        request.tenant_id = tenant_id
        
        response = self.get_response(request)
        return response


def get_tenant_database_config(tenant_id):
    """
    Generate database configuration for a specific tenant.
    In production, this would create/connect to tenant-specific databases.
    """
    if tenant_id == 'default':
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('LMS_DEFAULT_DB_NAME', 'lms_default'),
            'USER': os.environ.get('LMS_DEFAULT_DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('LMS_DEFAULT_DB_PASSWORD', ''),
            'HOST': os.environ.get('LMS_DEFAULT_DB_HOST', 'localhost'),
            'PORT': os.environ.get('LMS_DEFAULT_DB_PORT', '5432'),
        }
    
    # For production: create/connect to tenant-specific database
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': f'lms_tenant_{tenant_id}',
        'USER': os.environ.get('SUPABASE_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('SUPABASE_DB_PASSWORD', ''),
        'HOST': os.environ.get('SUPABASE_DB_HOST', 'localhost'),
        'PORT': os.environ.get('SUPABASE_DB_PORT', '5432'),
    }


def setup_tenant_database(tenant_id):
    """
    Create a new database for a tenant organization.
    This would be called when a new organization signs up.
    """
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    # Connect to default database to create new one
    default_config = get_tenant_database_config('default')
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=default_config['HOST'],
            port=default_config['PORT'],
            user=default_config['USER'],
            password=default_config['PASSWORD'],
            database='postgres'  # Connect to postgres to create new DB
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Create new database for tenant
        db_name = f'lms_tenant_{tenant_id}'
        cursor.execute(f'CREATE DATABASE "{db_name}"')
        
        print(f"✅ Created database: {db_name}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database for tenant {tenant_id}: {e}")
        return False